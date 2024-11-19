from sqlalchemy.orm import Session

from models.database_models.verification import SvRequest


def get_request_list(user_id: int, db: Session) -> list[dict]:
  q = (
    db.query(SvRequest)
    .filter_by(user_id=user_id)
    .all()
  )

  ret = []

  for r in q:
    ret.append({
      'vid': r.verification_id,
      'state': r.state.value,
      'evidence_type': r.evidence_type is not None and r.evidence_type.value or None,
      'doc_code': r.doc_code,
      'name': r.name,
      'school': r.school,
      'grade': r.grade,
      'requested_at': r.request_time.isoformat(),
      'examined_at': r.examine_time is not None and r.examine_time.isoformat() or None,
    })

  return ret
