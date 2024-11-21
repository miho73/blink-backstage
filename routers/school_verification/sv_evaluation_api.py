import logging

from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.sv.sv import get_request_detail, get_evidence, determine_sv
from database.database import create_connection
from models.database_models.verification import SvEvidenceType
from models.request_models.school_verification_requests import SvEvaluation

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv/approve',
  tags=['sv']
)


@router.get(
  path=''
)
def get_request_info(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug('Getting SV request info upon JWT. jwt=\"{}\"'.format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get("sub")
  aud = token.get("aud")

  if 'blink:admin' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  vid = request.query_params.get('vid')

  if vid is None:
    log.debug('Verification id was not given.')
    raise HTTPException(status_code=400, detail='vid was not given')

  detail = get_request_detail(int(vid), db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': detail
    }
  )


@router.get(
  path='/evidence'
)
def view_evidence(
  request: Request,
  db: Session = Depends(create_connection)
):
  jwt = request.query_params.get("jwt")

  if jwt is None:
    log.debug('JWT was not given')
    raise HTTPException(status_code=403, detail='Forbidden')

  log.debug('Get SV request evidence by JWT. jwt=\"{}\"'.format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get("sub")
  aud = token.get("aud")

  if 'blink:admin' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  vid = request.query_params.get('vid')

  if vid is None:
    log.debug('Verification id was not given.')
    raise HTTPException(status_code=400, detail='vid was not given')

  (e_type, e) = get_evidence(int(vid), db)

  if e_type is SvEvidenceType.PDF:
    c_type = 'application/pdf'
  elif e_type is SvEvidenceType.PNG:
    c_type = 'image/png'
  elif e_type is SvEvidenceType.JPEG:
    c_type = 'image/jpeg'
  else:
    raise HTTPException(status_code=500, detail='Database integrity')

  return Response(
    content=e,
    headers={
      'Content-Type': c_type
    }
  )


@router.post(
  path=''
)
def determine(
  body: SvEvaluation,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug('Judge SV request using JWT. jwt=\"{}\"'.format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get('sub')
  aud = token.get('aud')

  if 'blink:admin' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  determine_sv(body, db)
  db.commit()

  log.debug(
    'Determination of SV was made. verification_id=\"{}\", judge_uid=\"{}\", state=\"{}\"'.format(body.verification_id,
                                                                                                  sub, body.state))
