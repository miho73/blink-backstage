import logging
from datetime import datetime
from urllib import parse

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.user.user_info_service import get_identity_by_userid
from models.database_models.relational.identity import Identity
from models.database_models.relational.schools import School
from models.database_models.relational.verification import SvRequest, SvState
from models.request_models.school_verification_requests import SvEvaluation

log = logging.getLogger(__name__)


def get_sv_request_detail(vid: int, db: Session) -> dict:
  r = (
    db.query(SvRequest)
    .filter_by(verification_id=vid)
    .first()
  )

  if r is None:
    log.debug('SV request was not found. vid=\"{}\"'.format(vid))
    raise HTTPException(status_code=404, detail='Request not found')

  if r.state is SvState.DRAFT:
    state = 'DRAFT'
  elif r.state is SvState.REQUESTED:
    state = 'REQUESTED'
  elif r.state is SvState.HOLDING:
    state = 'HOLDING'
  elif r.state is SvState.ACCEPTED:
    state = 'ACCEPTED'
  elif r.state is SvState.INVALID_EVIDENCE:
    state = 'INVALID DOCUMENT'
  elif r.state is SvState.IDENTITY_MISMATCH:
    state = 'IDENTITY_MISMATCH'
  elif r.state is SvState.INVALID_DOCUMENT:
    state = 'INVALID DOCUMENT'
  elif r.state is SvState.DENIED:
    state = 'DENIED'
  else:
    log.debug('Unknown sv state stored in db. state=\"{}\", verification_uid=\"{}\"'.format(r.state,
                                                                                            r.verification_id))
    raise HTTPException(status_code=500, detail='Database integrity')

  return {
    'verificationId': r.verification_id,
    'userId': r.user_id,
    'requestTime': r.request_time.isoformat(),
    'state': state,
    'evidenceType': r.evidence_type is not None and r.evidence_type.value or None,
    'docCode': r.doc_code,
    'name': r.name,
    'schoolName': r.school,
    'grade': r.grade,
    'nameEucKr': parse.quote(r.name.encode("euc-kr"))
  }


def get_request_list(user_id: int, db: Session) -> list[dict]:
  q = (
    db.query(SvRequest)
    .filter_by(user_id=user_id)
    .order_by(desc(SvRequest.verification_id))
    .all()
  )

  ret = []

  for r in q:
    ret.append({
      'vid': r.verification_id,
      'state': r.state.value,
      'evidenceType': r.evidence_type is not None and r.evidence_type.value or None,
      'docCode': r.doc_code,
      'name': r.name,
      'school': r.school,
      'grade': r.grade,
      'requestedAt': r.request_time.isoformat(),
      'examinedAt': r.examine_time is not None and r.examine_time.isoformat() or None,
    })

  return ret


def get_evidence(vid: int, db: Session):
  request = (
    db.query(SvRequest)
    .filter_by(verification_id=vid)
    .first()
  )

  if request is None:
    log.debug('SV request was not found. vid=\"{}\"'.format(vid))
    raise HTTPException(status_code=404, detail='Request not found')

  return request.evidence_type, request.evidence


def evaluate_sv(judge: SvEvaluation, db: Session):
  sv = (
    db.query(SvRequest)
    .filter_by(verification_id=judge.verification_id)
    .first()
  )

  if sv.state is not SvState.REQUESTED:
    log.debug('State for request sv is not REQUESTED. verification_id=\"{}\"'.format(judge.verification_id))
    raise HTTPException(status_code=400, detail="Not requested")

  sv._state = judge.state
  sv.examine_time = datetime.now()
  if judge.state is SvState.ACCEPTED.value:
    sv.identity.school_id = judge.school_id
    sv.identity.grade = judge.grade
    sv.identity.student_verified = True

    school = (
      db.query(School)
      .filter_by(school_id=judge.school_id)
      .first()
    )

    school.user_count = school.user_count + 1


def withdraw_verification(sub: int, db: Session):
  identity: Identity = get_identity_by_userid(sub, db)

  if identity.school is None:
    log.debug('User is not verified. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail="User not verified")

  identity.school.user_count = identity.school.user_count - 1
  identity.school_id = None
  identity.grade = None
  identity.student_verified = False
