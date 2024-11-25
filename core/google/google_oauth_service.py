import logging
from datetime import datetime

import requests
from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow

from core.config import config
from core.jwt import jwt_service
from models.database_models.identity import Identity
from models.user import GoogleUser

log = logging.getLogger(__name__)

flow = Flow.from_client_secrets_file(
  client_secrets_file=config['auth']['google']['client_secret_file'],
  scopes=[
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
  ]
)
flow.redirect_uri = config['auth']['google']['redirect_uri']


def start_authentication():
  authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true'
  )

  return authorization_url, state


def get_access_token(code: str) -> str:
  return flow.fetch_token(code=code)['access_token']


def get_google_user(access_token: str) -> GoogleUser:
  response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", params={"access_token": access_token})
  if response.status_code != 200:
    log.error(
      "Failed to get user profile from Google. status_code={status_code}".format(status_code=response.status_code))
    raise HTTPException(status_code=500, detail="Failed to get user profile from Google")

  profile = response.json()

  log.debug("Got user profile from Google. profile=\"{profile}\"".format(profile=profile))
  google_user = GoogleUser(
    username=profile['name'],
    email=profile['email'],
    email_verified=profile['email_verified'],
    google_id=profile['sub'],
    picture=profile['picture'],
  )

  return google_user


def get_google_id(access_token: str) -> str:
  response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", params={"access_token": access_token})
  if response.status_code != 200:
    log.error(
      "Failed to get user profile from Google. status_code={status_code}".format(status_code=response.status_code))
    raise HTTPException(status_code=500, detail="Failed to get user profile from Google")

  profile = response.json()

  log.debug("Got user profile from Google. id=\"{id}\"".format(id=profile['sub']))

  return profile['sub']


def complete_authentication(identity: Identity) -> str:
  log.debug("Completing authentication. user_id=\"{user_id}\"".format(user_id=identity.user_id))
  identity.last_login = datetime.now()
  identity.auth_lookup.google_method.last_used = datetime.now()

  log.debug("Issued JWT. user_id=\"{user_id}\", role=\"{role}\"".format(user_id=identity.user_id, role=identity.role))
  return jwt.create_token(identity.user_id, identity.role)
