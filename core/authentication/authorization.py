import logging

from fastapi import HTTPException
from fastapi.security import APIKeyHeader
from jwt import InvalidTokenError

from core.jwt import jwt

log = logging.getLogger(__name__)

class APIKeyHeaderBearer(APIKeyHeader):
    def __init__(self):
        super().__init__(name="Authorization")

authorization_header = APIKeyHeaderBearer()

def authorize_jwt(token: str):
    if token is None:
        log.debug("Auth failed: Authorization header is missing")
        raise HTTPException(status_code=400, detail="Authorization header is missing")

    if not token.startswith("Bearer "):
        log.debug("Auth failed: Authorization must be Bearer token")
        raise HTTPException(status_code=400, detail="Authorization must be Bearer token")

    jwt_token = token[7:]
    if not jwt_token:
        log.debug("Auth failed: JWT token is missing")
        raise HTTPException(status_code=400, detail="JWT token is missing")

    try:
        jwt_body = jwt.decode(jwt_token)
    except (InvalidTokenError, Exception) as e:
        log.debug("Auth failed: JWT is invalid or unauthorized[{}]".format(e))
        raise HTTPException(status_code=401, detail="JWT is invalid or unauthorized")

    if not jwt_body:
        log.debug("Auth failed: JWT is invalid or unauthorized")
        raise HTTPException(status_code=401, detail="JWT is invalid or unauthorized")

    log.debug("Authorized JWT token. jwt=\"{}\"".format(token))
    return jwt_body
