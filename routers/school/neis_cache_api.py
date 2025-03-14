from fastapi import APIRouter, Request, Security, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.school import neis_school_service
from core.user import user_info_service
from core.user.user_info_service import check_role
from database.database import create_connection
from models.database_models.relational.user_preference import UserPreference

router = APIRouter(
  prefix='/api/school/neis/cached',
  tags=['school', 'neis']
)

@router.get(
  path='/meal',
  description='Get cached meal data from NEIS API'
)
def get_cached_meal_data(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  aud = get_aud(token)

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  neis_code = request.query_params.get('neis-code')

  if neis_code is None:
    raise HTTPException(status_code=400, detail='query parameter \'neis-code\' is required')
  if len(neis_code) != 10:
    raise HTTPException(status_code=400, detail='malformed query parameter \'neis-code\'')

  meal_info = neis_school_service.get_meal_data(neis_code)

  sub = get_sub(token)
  identity = user_info_service.get_identity_by_userid(sub, db)
  preference: UserPreference = identity.preference
  allergy_pref = preference.allergy

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'meal': meal_info,
      'allergy': allergy_pref
    }
  )

@router.get(
  path='/timetable',
  description='Get cached timetable data from NEIS API'
)
def get_cached_timetable_data(
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  if not check_role(aud, 'core:user'):
    raise HTTPException(status_code=403, detail='Forbidden')

  timetable = neis_school_service.get_timetable_data(sub, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'timetable': timetable
    }
  )
