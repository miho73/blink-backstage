import logging

from fastapi import HTTPException, UploadFile
from pyasn1_modules.rfc2985 import contentType
from sqlalchemy import and_
from sqlalchemy.orm import Session

from core.user import user_info
from models.database_models import Identity
from models.database_models.verification import SvRequest, SvRequestType, SvState, SvEvidenceType
from models.request_models.school_verification_request import NewVerificationRequest

log = logging.getLogger(__name__)


def add_new_request(sub: int, req: NewVerificationRequest, db: Session):
  identity: Identity = user_info.get_identity_by_userid(sub, db)

  if identity is None:
    log.debug('Identity specified by JWT was not found and request was not made. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail='Identity not found')

  prev_request = (
    db.query(SvRequest)
    .filter(
      and_(
        SvRequest.user_id == sub,
        SvRequest._state != SvState.DENIED.value,
        SvRequest._state != SvState.IDENTITY_MISMATCH.value,
        SvRequest._state != SvState.INVALID_DOCUMENT.value,
        SvRequest._state != SvState.INVALID_EVIDENCE.value,
        SvRequest._state != SvState.ACCEPTED.value
      )
    )
    .first()
  )
  if prev_request is not None:
    exists_query = (
      db.query(SvRequest)
      .filter_by(user_id=sub)
      .filter_by(_state=SvState.DRAFT.value)
      .exists()
    )
    exists = db.query(exists_query).scalar()
    if exists:
      log.debug('User has draft user_uid=\"{}\"'.format(sub))
      raise HTTPException(status_code=400, detail="Upload evidence")
    else:
      log.debug('User already has a request in progress. user_uid=\"{}\"'.format(sub))
      raise HTTPException(status_code=400, detail="Already requested")

  draft: SvRequest = SvRequest(
    user_id=sub,
    _request_type=SvRequestType.CERTIFICATE_OF_ENROLLMENT.value,
    grade=req.grade,
    name=req.name,
    school=req.school_name,
    doc_code=req.doc_code
  )
  db.add(draft)
  db.commit()


async def insert_evidence(file: UploadFile, identity: Identity, db: Session):
  log.debug(
    "Evidence was uploaded. user_uid=\"{}\" size=\"{}\" content_type\"{}\" filename=\"{}\""
    .format(identity.user_id, file.size, file.content_type, file.filename)
  )

  content_type = file.content_type
  if content_type == 'application/pdf':
    file_type = SvEvidenceType.PDF
  elif contentType == 'image/png':
    file_type = SvEvidenceType.PNG
  elif content_type == 'image/jpeg':
    file_type = SvEvidenceType.JPEG
  else:
    log.debug(
      'Invalid file type was uploaded. user_uid=\"{}\" content_type=\"{}\"'.format(identity.user_id, file.content_type))
    raise HTTPException(status_code=400, detail='Invalid file type')

  if file.size > 1048576:
    log.debug('File size is too large. user_uid=\"{}\" size=\"{}\"'.format(identity.user_id, file.size))
    raise HTTPException(status_code=400, detail='File too large')

  evidence = (
    db.query(SvRequest)
    .filter_by(user_id=identity.user_id)
    .filter_by(_state=SvState.DRAFT.value)
    .order_by(SvRequest.verification_id.desc())
    .first()
  )

  if evidence is None:
    log.debug('Draft to upload was not found. user_uid=\"{}\"'.format(identity.user_id))
    raise HTTPException(status_code=400, detail='No draft found')

  content = await file.read()

  evidence.evidence = content
  evidence.state = SvState.REQUESTED
  evidence.evidence_type = file_type

  db.commit()

  log.debug('Evidence was saved. user_uid=\"{}\"'.format(identity.user_id))
