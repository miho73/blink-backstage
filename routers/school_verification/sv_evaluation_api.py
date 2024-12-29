import logging
import re

from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.params import Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.school_verification.sv import get_sv_request_detail, get_evidence, evaluate_sv
from database.database import create_connection
from models.database_models.relational.verification import SvEvidenceType
from models.request_models.school_verification_requests import SvEvaluation

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv/evaluation',
  tags=['sv']
)


@router.get(
  path='/request',
  summary="Get SV request info for evaluation purpose"
)
def get_sv_request_api(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get("sub")
  aud = token.get("aud")

  log.debug('Getting SV request info. sub=\"{}\"'.format(sub))

  if 'root:access' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  vid = request.query_params.get('vid')

  if vid is None:
    log.debug('Verification id was not given.')
    raise HTTPException(status_code=400, detail='vid was not given')

  if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', vid):
    log.debug('Verification id is not a valid UUID. vid=\"{}\"'.format(vid))
    raise HTTPException(status_code=400, detail='Invalid vid')

  detail = get_sv_request_detail(vid, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'data': detail
    }
  )


@router.get(
  path='/evidence',
  summary="Get SV request evidence for evaluation purpose"
)
def get_evidence_api(
  request: Request,
  db: Session = Depends(create_connection)
):
  jwt = request.query_params.get("jwt")

  if jwt is None:
    log.debug('JWT was not given')
    raise HTTPException(status_code=403, detail='Forbidden')

  token = authorize_jwt(jwt)
  sub = token.get("sub")
  aud = token.get("aud")

  log.debug('Get SV request evidence. sub=\"{}\"'.format(sub))

  if 'root:access' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  vid = request.query_params.get('vid')

  if vid is None:
    log.debug('Verification id was not given.')
    raise HTTPException(status_code=400, detail='vid was not given')

  if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', vid):
    log.debug('Verification id is not a valid UUID. vid=\"{}\"'.format(vid))
    raise HTTPException(status_code=400, detail='Invalid vid')

  (e_type, e) = get_evidence(vid, db)

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


@router.patch(
  path='',
  summary="Evaluate SV request"
)
def evaluate_sv_api(
  body: SvEvaluation,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = token.get('sub')
  aud = token.get('aud')

  log.debug('Evaluate SV request. sub=\"{}\"'.format(sub))

  if 'root:access' not in aud:
    log.debug('User is not an admin. user_id=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  evaluate_sv(body, db)
  db.commit()

  log.debug(
    'Evaluation of SV was made. verification_id=\"{}\", judge_uid=\"{}\", state=\"{}\"'.format(body.verification_id,
                                                                                                  sub, body.state))
