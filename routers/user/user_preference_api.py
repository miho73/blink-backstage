import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.user import user_info_service
from core.user.user_info_service import check_role
from database.database import create_connection
from models.database_models.relational.user_preference import UserPreference
from models.request_models.user_requests import UpdateUserAllergyInformationRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/user/preference',
  tags=['user', 'preference']
)


@router.get(
  path='/allergy',
  summary='Get user allergy preference'
)
def get_user_allergy_preference(
  token: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  jwt = authorize_jwt(token)
  sub = get_sub(jwt)
  aud = get_aud(jwt)

  log.debug("Getting user allergy code. sub=\"{}\"".format(sub))

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  identity = user_info_service.get_identity_by_userid(sub, db)
  preference: UserPreference = identity.preference
  allergy_code = preference.allergy

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'allergy': allergy_code
    }
  )


@router.patch(
  path='/allergy',
  summary='Update user allergy preference'
)
def update_allergy_preference(
  body: UpdateUserAllergyInformationRequest,
  token: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  jwt = authorize_jwt(token)
  sub = get_sub(jwt)
  aud = get_aud(jwt)

  log.debug("Updating user allergy code. sub=\"{}\" new_code=\"{}\"".format(sub, body.allergy))

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  identity = user_info_service.get_identity_by_userid(sub, db)
  preference: UserPreference = identity.preference
  preference.allergy = body.allergy

  db.commit()

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'allergy': body.allergy
    }
  )
