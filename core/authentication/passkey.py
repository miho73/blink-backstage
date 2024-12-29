import base64
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Type

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from webauthn import generate_registration_options, generate_authentication_options, options_to_json, \
  verify_registration_response, verify_authentication_response
from webauthn.helpers.structs import UserVerificationRequirement, AuthenticatorSelectionCriteria

from core.authentication.aaguid import get_authenticator
from core.config import config
from core.jwt import jwt_service
from database.database import redis_db
from models.database_models.relational.identity import Identity
from models.database_models.relational.passkey_auth import PasskeyAuth
from models.request_models.passkey_request import RegisterPasskeyRequest, SignInPasskeyRequest

from uuid import UUID as PyUUID

log = logging.getLogger(__name__)

def begin_authentication() -> (str, dict):
  challenge = os.urandom(32)
  authentication_id = str(uuid.uuid4())
  if redis_db.exists(authentication_id):
    log.warning("Authentication ID duplicated")
    raise HTTPException(status_code=400, detail="Registration ID already exists")

  auth_option = generate_authentication_options(
    rp_id=config['security']['webauthn']['rp_id'],
    challenge=challenge,
    user_verification=UserVerificationRequirement.REQUIRED,
    timeout=300,
  )

  log.debug("Generated passkey auth option. redis_pk=\"{}\"".format(authentication_id))
  redis_db.set(authentication_id, base64.encodebytes(challenge).decode('ascii'))

  return (
    authentication_id,
    json.loads(options_to_json(auth_option))
  )


def begin_registration(identity: Type[Identity]) -> (str, dict):
  challenge = os.urandom(32)
  registration_id = str(uuid.uuid4())
  if redis_db.exists(registration_id):
    log.warning("Registration ID duplicated. user_uid=\"{}\"".format(identity.user_id))
    raise HTTPException(status_code=400, detail="Registration ID already exists")

  reg_option = generate_registration_options(
    rp_id=config['security']['webauthn']['rp_id'],
    rp_name=config['security']['webauthn']['rp_name'],
    challenge=challenge,
    user_name=identity.username,
    user_id=identity.user_id.bytes,
    user_display_name=identity.username,
    timeout=300,
  )

  log.debug("Generated passkey register option. redis_pk=\"{}\"".format(registration_id))
  redis_db.set(registration_id, base64.encodebytes(challenge).decode('ascii'))

  return (
    registration_id,
    json.loads(options_to_json(reg_option))
  )

def add_passkey(user_id: int, request: RegisterPasskeyRequest, register_option: str, db: Session):
  identity = db.query(Identity).filter(Identity.user_id == user_id).first()

  if identity is None:
    log.debug("Identity not found. user_uid=\"{}\"".format(user_id))
    raise HTTPException(status_code=404, detail="Identity not found")

  challenge_b64 = redis_db.get(register_option)
  redis_db.delete(register_option)

  if challenge_b64 is None:
    log.debug("Register option not found. user_uid=\"{}\"".format(identity.user_id))
    raise HTTPException(status_code=400, detail="Register option not found")

  challenge = base64.decodebytes(challenge_b64.encode('ascii'))

  log.debug("Verifying registration. user_uid=\"{}\"".format(identity.user_id))
  registration = verify_registration_response(
    credential=request.attestation,
    expected_rp_id=config['security']['webauthn']['rp_id'],
    expected_challenge=challenge,
    expected_origin=config['security']['webauthn']['rp_origin'],
  )

  log.debug("Registration verified. user_uid=\"{}\"".format(identity.user_id))

  authenticator = get_authenticator(registration.aaguid)

  if authenticator is None:
    log.debug("Authenticator not found. aaguid=\"{}\"".format(registration.aaguid))
    raise HTTPException(status_code=400, detail="Authenticator not found")

  log.debug("Creating passkey auth. aaguid=\"{}\", credential_id=\"{}\"".format(registration.aaguid, registration.credential_id))

  passkey_auth = PasskeyAuth(
    credential_id=registration.credential_id,
    lookup_id=identity.auth_lookup.lookup_id,
    public_key=registration.credential_public_key,
    counter=registration.sign_count,
    passkey_name=authenticator.name,
    aaguid=registration.aaguid,
  )
  db.add(passkey_auth)
  identity.auth_lookup.passkey += 1
  db.commit()

def auth_passkey(body: SignInPasskeyRequest, PSK_AUTH_SEK: str, db: Session) -> str:
  response = body.attestation.get("response", {})
  if response is None:
    log.debug("Response not found in request body")
    raise HTTPException(status_code=400, detail="Malformed request")

  credential_id_b64: str = str(body.attestation.get('rawId'))
  credential_id = base64.urlsafe_b64decode(credential_id_b64 + "==")
  log.debug("Authenticating passkey. credential_id=\"{}\"".format(credential_id))

  passkey_auth: PasskeyAuth = db.query(PasskeyAuth).filter(PasskeyAuth.credential_id == credential_id).first()
  if passkey_auth is None:
    log.debug("Passkey auth not found. credential_id=\"{}\"".format(credential_id))
    raise HTTPException(status_code=400, detail="Passkey not found")

  identity = passkey_auth.auth_lookup.identity
  if identity is None:
    log.debug("Identity not found. credential_id=\"{}\"".format(credential_id))
    raise HTTPException(status_code=400, detail="Identity not found")
  log.debug("Found passkey principle. user_uid=\"{}\"".format(identity.user_id))

  challenge_b64 = redis_db.get(PSK_AUTH_SEK)
  redis_db.delete(PSK_AUTH_SEK)

  if challenge_b64 is None:
    log.debug("Authentication option not found")
    raise HTTPException(status_code=400, detail="Authentication option not found")

  challenge = base64.decodebytes(challenge_b64.encode('ascii'))
  log.debug("Challenge was loaded from redis. redis_pk=\"{}\"".format(PSK_AUTH_SEK))

  log.debug("Verifying authentication")
  auth = verify_authentication_response(
    credential=body.attestation,
    expected_rp_id=config['security']['webauthn']['rp_id'],
    expected_challenge=challenge,
    expected_origin=config['security']['webauthn']['rp_origin'],
    credential_public_key=passkey_auth.public_key,
    credential_current_sign_count=passkey_auth.counter,
  )

  passkey_auth.counter = auth.new_sign_count
  passkey_auth.last_used = datetime.now()
  log.debug("Passkey authenticated. user_uid=\"{}\"".format(identity.user_id))

  jwt = jwt_service.create_token(identity.user_id, identity.role)
  log.debug("Issued JWT. user_uid=\"{}\"".format(identity.user_id))

  db.commit()

  return jwt


def delete_passkey(passkey_uuid: str, sub: PyUUID, db: Session):
  uuid = PyUUID(passkey_uuid)
  passkey_auth = db.query(PasskeyAuth).filter(PasskeyAuth.passkey_id == uuid).first()

  if passkey_auth is None:
    log.debug("Passkey not found. passkey_id=\"{}\"".format(passkey_uuid))
    raise HTTPException(status_code=400, detail="Passkey not found")

  if passkey_auth.auth_lookup.identity.user_id != sub:
    log.debug("Passkey does not belong to user. passkey_id=\"{}\", user_uid=\"{}\"".format(passkey_uuid, sub))
    raise HTTPException(status_code=400, detail="Passkey not found")

  db.delete(passkey_auth)
  passkey_auth.auth_lookup.passkey -= 1
  db.commit()
  log.debug("Passkey deleted. passkey_id=\"{}\"".format(passkey_uuid))


def rename_passkey(passkey_uuid, sub, name, db):
  uuid = PyUUID(passkey_uuid)
  passkey_auth = db.query(PasskeyAuth).filter(PasskeyAuth.passkey_id == uuid).first()

  if passkey_auth is None:
    log.debug("Passkey not found. passkey_id=\"{}\"".format(passkey_uuid))
    raise HTTPException(status_code=400, detail="Passkey not found")


  if passkey_auth.auth_lookup.identity.user_id != sub:
    log.debug("Passkey does not belong to user. passkey_id=\"{}\", user_uid=\"{}\"".format(passkey_uuid, sub))
    raise HTTPException(status_code=400, detail="Passkey not found")

  passkey_auth.passkey_name = name
  db.commit()
  log.debug("Passkey renamed. passkey_id=\"{}\"".format(passkey_uuid))
