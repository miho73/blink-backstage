import logging

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.school.school_access_service import get_school_list, add_school, delete_school, add_school
from database.database import create_connection
from models.request_models.school_requests import AddSchoolRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/school/access',
  tags=['school', 'access api']
)


@router.post(
  path='',
  summary='Add a new school to the database'
)
def add_school_api(
  body: AddSchoolRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")

  log.debug("Adding school. sub=\"{}\"".format(sub))

  if 'blink:admin' not in token['aud']:
    log.debug("User is not an admin. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=403, detail="Forbidden")

  add_school(body, db)

  return JSONResponse(
    status_code=201,
    content={
      'code': 201,
      'state': 'CREATED'
    }
  )


@router.get(
  path='',
  summary='Get a list of schools from the database that satisfy the given conditions'
)
def get_school_list_api(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  aud = token.get('aud')
  sub = token.get("sub")

  log.debug("Getting school list. sub=\"{}\"".format(sub))

  school_name = request.query_params.get('schoolName')

  if 'blink:admin' not in aud:
    log.debug("User is not an admin. user_uid=\"{}\"".format(sub))
    return JSONResponse(
      status_code=403,
      content={
        'code': 403,
        'state': 'Forbidden'
      }
    )

  if school_name is None:
    log.debug('School name was not given')
    raise HTTPException(status_code=400, detail='School name was not given')

  if school_name == '':
    school_name = None

  jsn = get_school_list(school_name, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': jsn
    }
  )


@router.delete(
  path='',
  summary="Delete a school from the database"
)
def deletes_school_api(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")
  aud = token.get("aud")

  log.debug("Deleting school. sub=\"{}\"".format(sub))

  school_uid = request.headers.get('School-Uid')

  if 'blink:admin' not in aud:
    log.debug("User is not an admin. user_uid=\"{}\"".format(sub))
    raise HTTPException(status_code=403, detail="Forbidden")

  if school_uid is None:
    log.debug('School uid was not given')
    raise HTTPException(status_code=400, detail='NEIS code was not given')

  delete_school(school_uid, db)

  return JSONResponse(
    status_code=200,
    content={
      'code': 200,
      'state': 'OK'
    }
  )
