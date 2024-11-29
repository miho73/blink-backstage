import logging

from fastapi import APIRouter, Depends, Security, Request, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.google.recaptcha_service import verify_recaptcha
from core.school_verification.sv import get_request_list, withdraw_verification
from database.database import create_connection
from models.database_models.relational.verification import SvRequest
from models.request_models.school_verification_requests import WithdrawVerificationRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/sv/user',
  tags=['sv']
)


@router.get(
  path='/requests',
  summary="Get school verification requests of user"
)
def get_sv_requests_api(
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug("Getting school school verification data upon JWT. jwt=\"{}\"".format(jwt))

  token = authorize_jwt(jwt)
  sub = token.get("sub")

  request_list = get_request_list(sub, db)

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK',
      'requests': request_list
    }
  )


@router.delete(
  path='/requests',
    summary="Delete SV request"
)
def delete_sv_request_api(
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  vid = request.headers.get('Resource-Id')
  token = request.headers.get("Recaptcha")

  if vid is None or token is None:
    log.debug("Request ID or reCAPTCHA token was not found in headers. jwt=\"{}\"".format(jwt))
    raise HTTPException(status_code=400, detail="Invalid Request")

  # google recaptcha
  if verify_recaptcha(token, request.client.host, "sv/delete") is False:
    log.debug("Recaptcha delete school verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  vd = int(vid)

  log.debug("Deleting school verification request upon JWT. jwt=\"{}\". request_id=\"{}\"".format(jwt, vd))

  token = authorize_jwt(jwt)
  sub = token.get("sub")

  result = db.execute(
    delete(SvRequest)
    .where(SvRequest.verification_id == vd)
    .where(SvRequest.user_id == sub)
  )

  affected = result.rowcount

  if affected != 1:
    log.debug(
      "Delete request was not normally performed. sub=\"{}\". request_id=\"{}\". affected=\"{}\"".format(sub, vd,
                                                                                                         affected))
    raise HTTPException(status_code=400, detail="Abnormal")

  else:
    db.commit()
    log.debug("Delete request was succeed. sub=\"{}\". request_id=\"{}\"".format(sub, vd))

    return JSONResponse(
      content={
        "code": 200,
        "state": "OK"
      }
    )

@router.post(
  path='/withdraw',
    summary="Withdraw SV request of previously been verified user"
)
def withdraw_verification_api(
  body: WithdrawVerificationRequest,
  request: Request,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.debug('Withdraw verification upon JWT. jwt=\"{}\"'.format(jwt))

  if verify_recaptcha(body.recaptcha, request.client.host, 'sv/withdraw') is False:
    log.debug("Recaptcha school_verification failed")
    raise HTTPException(status_code=400, detail="Recaptcha failed")

  token = authorize_jwt(jwt)
  sub = token.get('sub')

  withdraw_verification(sub, db)
  db.commit()

  log.debug('Verification was withdrawn. user_uid=\"{}\"'.format(sub))

  return JSONResponse(
    content={
      'code': 200,
      'state': 'OK'
    }
  )
