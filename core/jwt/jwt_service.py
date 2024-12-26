from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import InvalidTokenError

from core.config import config

KST = timezone(timedelta(hours=9))

def create_token(user_id: int, role: list[str]) -> str:
  payload = {
    'aud': role,
    'sub': str(user_id),
    'exp': datetime.now(KST) + timedelta(weeks=5),
    'iat': datetime.now(KST),
    'iss': 'blink',
  }

  return jwt.encode(
    payload=payload,
    key=config['security']['jwt_secret'],
    algorithm='HS256',
  )


def validate_token(token: str) -> bool:
  try:
    jwt.decode(
      jwt=token,
      key=config['security']['jwt_secret'],
      algorithms=['HS256'],
      verify_signature=True,
      issuer='blink',
      require=['aud', 'exp', 'iat', 'iss'],
      audience=['core:user']
    )
  except InvalidTokenError as e:
    return False

  return True


def decode(token: str) -> dict:
  return jwt.decode(
    jwt=token,
    key=config['security']['jwt_secret'],
    algorithms=['HS256'],
    verify_signature=True,
    issuer='blink',
    require=['aud', 'exp', 'iat', 'iss'],
    audience=['core:user'],
  )


def validate_authentication(token: str) -> bool:
  try:
    jwt.decode(
      jwt=token,
      key=config['security']['jwt_secret'],
      algorithms=['HS256'],
      verify_signature=True,
      issuer='blink',
      require=['aud', 'exp', 'iat', 'iss'],
      audience=['core:user'],
    )
  except InvalidTokenError:
    return False

  return True

def get_sub(token: dict) -> Optional[int]:
  sub = token.get('sub')
  if sub is None:
    return None
  return int(sub)

def get_aud(token: dict) -> Optional[list[str]]:
  aud = token.get('aud')
  if aud is None:
    return []
  return aud
