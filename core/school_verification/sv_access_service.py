import logging

from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy.orm import Session

from models.database_models.relational.verification import SvRequest, SvState

log = logging.getLogger(__name__)


def access_get_sv(db: Session, **kwargs):
  data = (
    db.query(SvRequest)
    .filter(
      SvRequest.name.like(
        kwargs.get('name') is not None and
        '%' + kwargs.get('name') + '%'
        or '%'
      )
    )
    .filter(
      SvRequest.school.like(
        kwargs.get('school_name') is not None and
        '%' + kwargs.get('school_name') + '%'
        or '%'
      )
    )
    .order_by(asc(SvRequest.request_time))
    .limit(50)
    .all()
  )

  res = []

  for sv in data:
    if sv.state is SvState.DRAFT:
      state = 'DRAFT'
    elif sv.state is SvState.REQUESTED:
      state = 'REQUESTED'
    elif sv.state is SvState.HOLDING:
      state = 'HOLDING'
    elif sv.state is SvState.ACCEPTED:
      state = 'ACCEPTED'
    elif sv.state is SvState.INVALID_EVIDENCE:
      state = 'INVALID DOCUMENT'
    elif sv.state is SvState.IDENTITY_MISMATCH:
      state = 'IDENTITY_MISMATCH'
    elif sv.state is SvState.INVALID_DOCUMENT:
      state = 'INVALID DOCUMENT'
    elif sv.state is SvState.DENIED:
      state = 'DENIED'
    else:
      log.debug('Unknown sv state stored in db. state=\"{}\", verification_uid=\"{}\"'.format(sv.state,
                                                                                              sv.verification_id))
      raise HTTPException(status_code=500, detail='Database integrity')

    res.append({
      'verificationId': sv.verification_id,
      'userId': sv.user_id,
      'requestTime': sv.request_time.isoformat(),
      'evidence': sv.evidence is not None,
      'grade': sv.grade,
      'schoolName': sv.school,
      'name': sv.name,
      'state': state
    })

  return res
