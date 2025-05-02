import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.database_models.relational.schools import School

log = logging.getLogger(__name__)


def get_school_from_neis_code(
  neis_code: str,
  db: Session
):
  school = (
    db.query(School)
    .filter_by(neis_code=neis_code)
    .first()
  )

  if school is None:
    log.debug('School was not found. neis_code=\"{}\"'.format(neis_code))
    raise HTTPException(status_code=404, detail='School not found')

  return school
