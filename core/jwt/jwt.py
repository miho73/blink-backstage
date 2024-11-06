from datetime import datetime, timedelta

import jwt
from jwt import InvalidTokenError

from models.user import Role

from core.config import config

DB_ROLE_CODE_TO_ROLE = {
    Role.USER: ['blink:user'],
    Role.ADMIN: ['blink:user', 'blink:admin']
}

def create_token(user_id: int, role: Role) -> str:
    payload = {
        'aud': DB_ROLE_CODE_TO_ROLE[role],
        'sub': user_id,
        'exp': datetime.now() + timedelta(weeks=5),
        'iat': datetime.now(),
        'iss': 'with',
    }

    return jwt.encode(
        payload = payload,
        key = config['security']['jwt_secret'],
        algorithm ='HS256',
    )

def validate_token(token: str) -> bool:
    try:
        jwt.decode(
            jwt = token,
            key = config['security']['jwt_secret'],
            algorithms = ['HS256'],
            verify_signature=True,
            issuer='with',
            require=['aud', 'exp', 'iat', 'iss'],
            audience=['with:user', 'with:admin']
        )
    except InvalidTokenError as e:
        return False

    return True

def decode(token: str) -> dict:
    return jwt.decode(
        jwt = token,
        key = config['security']['jwt_secret'],
        algorithms = ['HS256'],
        verify_signature=True,
        issuer='with',
        require=['aud', 'exp', 'iat', 'iss'],
        audience=['with:user', 'with:admin'],
    )

def validate_authentication(token: str) -> bool:
    try:
        jwt.decode(
            jwt = token,
            key = config['security']['jwt_secret'],
            algorithms = ['HS256'],
            verify_signature=True,
            issuer='with',
            require=['aud', 'exp', 'iat', 'iss'],
            audience=['with:user', 'with:admin'],
        )
    except InvalidTokenError:
        return False

    return True
