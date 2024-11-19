import logging

from fastapi import APIRouter, HTTPException
from fastapi.params import Security, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization import authorization_header, authorize_jwt
from core.user import user_info
from database.database import create_connection
from models.database_models import Identity

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv'
)


@router.get(
  path='/get'
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

  return JSONResponse(
    content={
      'verified': identity.student_verified
    }
  )
