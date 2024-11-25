import logging

from fastapi import APIRouter, Request, HTTPException, UploadFile
from fastapi.params import Depends, Security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.google.recaptcha_service import verify_recaptcha
from core.school_verification.sv_request_service import add_request, add_evidence
from core.user import user_info_service
from database.database import create_connection
from models.database_models import Identity
from models.request_models.school_verification_requests import NewVerificationRequest, WithdrawVerificationRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv',
  tags=['sv']
)


@router.post(
  path='/draft',
  summary='Submit a new SV draft'
)
def submit_sv_draft_api(
  body: NewVerificationRequest,
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Added new verification request upon JWT. jwt=\"{}\"".format(jwt))

  if verify_recaptcha(body.recaptcha, request.client.host, 'sv/new') is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  token = authorize_jwt(jwt)
  sub = token.get("sub")

  add_request(sub, body, db)
  db.commit()
  log.debug("New verification request draft was saved. user_uid=\"{}\"".format(sub))
  return JSONResponse(
    content={
      'code': 201,
      'status': 'CREATED'
    },
    status_code=201
  )


@router.post(
  path='/evidence',
  summary='Upload evidence for an SV request'
)
async def upload_sv_evidence_api(
  evidence: UploadFile,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Upload evidence upon JWT. jwt=\"{}\"".format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get("sub")

  identity: Identity = user_info_service.get_identity_by_userid(sub, db)
  if identity is None:
    log.debug('Identity specified by JWT was not found and evidence was not uploaded. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail='Identity not found')

  await add_evidence(evidence, identity, db)

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK"
    }
  )
