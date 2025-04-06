import logging
from datetime import datetime
from typing import Type
from urllib import parse
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.user.user_info_service import get_identity_by_userid, role_to_school
from models.database_models.relational.identity import Identity
from models.database_models.relational.schools import School
from models.database_models.relational.verification import SvRequest, SvState
from models.request_models.school_verification_requests import SvEvaluation

log = logging.getLogger(__name__)


def get_sv_request_detail(vid_str: str, db: Session) -> dict:
  vid = UUID(vid_str)

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
    'verificationId': str(r.verification_id),
    'userId': str(r.user_id),
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
      'vid': str(r.verification_id),
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


def get_evidence(vid_str: str, db: Session):
  vid = UUID(vid_str)

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
  vid = UUID(judge.verification_id)

  sv = (
    db.query(SvRequest)
    .filter_by(verification_id=vid)
    .first()
  )

  if sv.state is not SvState.REQUESTED and sv.state is not SvState.HOLDING:
    log.debug('State for request sv is not REQUESTED. verification_id=\"{}\"'.format(judge.verification_id))
    raise HTTPException(status_code=400, detail="Not requested")

  sv._state = judge.state
  sv.examine_time = datetime.now()
  if judge.state is SvState.ACCEPTED.value:
    school = (
      db.query(School)
      .filter_by(school_id=judge.school_id)
      .first()
    )

    sv.identity.grade = judge.grade
    sv.identity.role += ['core:student', 'sv:' + school.neis_code]

    school.user_count = school.user_count + 1


def withdraw_verification(sub: UUID, db: Session):
  identity: Type[Identity] = get_identity_by_userid(sub, db)

  student_verified, neis_code = role_to_school(identity.role)

  if not student_verified:
    log.debug('User is not verified. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=400, detail="User not verified")

  school = (
    db.query(School)
    .filter_by(neis_code=neis_code)
    .first()
  )

  school.user_count = school.user_count - 1
  identity.role.remove('core:student')
  identity.role.remove('sv:' + school.neis_code)
  identity.grade = None
