import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Security, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.google.recaptcha_service import verify_recaptcha
from core.sv.sv import withdraw_verification_sub
from core.user import user_info_service
from database.database import create_connection
from models.database_models import Identity
from models.request_models.school_verification_requests import WithdrawVerificationRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv',
  tags=['sv']
)


@router.get(
  path='/get',
  tags=['user']
)
def get_verification_info(
  auth: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Getting school school_verification data upon JWT. jwt=\"{}\"".format(auth))

  token = authorize_jwt(auth)
  sub = token.get("sub")

  identity: Identity = user_info.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug("Identity specified by JWT was not found. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=400, detail="Identity not found")

  if identity.student_verified:
    school = {
      "name": identity.school.school_name,
      "id": identity.school.school_id,
      "grade": identity.grade
    }
  else:
    school = None

  return JSONResponse(
    content={
      'verified': identity.student_verified,
      'school': school
    }
  )


@router.post(
  path='/withdraw'
)
def withdraw_verification(
  body: WithdrawVerificationRequest,
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug('Withdraw verification upon JWT. jwt=\"{}\"'.format(jwt))

  if verify_recaptcha(body.recaptcha, request.client.host, 'sv/withdraw') is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  token = authorize_jwt(jwt)
  sub = token.get('sub')

  withdraw_verification_sub(sub, body, db)
  db.commit()

  log.debug('Verification was withdrawn. user_uid=\"{}\"'.format(sub))

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK'
    }
  )
