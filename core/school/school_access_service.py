import logging

from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy.orm import Session

from models.database_models.relational.schools import School, SchoolType, Sex
from models.request_models.school_requests import AddSchoolRequest

log = logging.getLogger(__name__)


def get_school_list(school_name: str, db: Session) -> list[dict]:
  schools = (
    db.query(School)
    .filter(
      School.school_name.like(
        school_name is not None and
        '%' + school_name + '%'
        or '%'
      )
    )
    .order_by(asc(School.school_id))
    .all()
  )

  ret = []

  for school in schools:
    if school.school_type is SchoolType.GENERAL_HIGH_SCHOOL:
      stype = '일반고'
    elif school.school_type is SchoolType.AUTONOMOUS_HIGH_SCHOOL:
      stype = '자율고'
    elif school.school_type is SchoolType.SPECIAL_HIGH_SCHOOL:
      stype = '특목고'
    elif school.school_type is SchoolType.SPECIALIZED_HIGH_SCHOOL:
      stype = '특성화고'
    elif school.school_type is SchoolType.MIDDLE_SCHOOL:
      stype = '중학교'
    else:
      log.debug('Unknown school type stored in db. school_type=\"{}\", school_uid=\"{}\"'.format(school.school_type,
                                                                                                 school.school_id))
      raise HTTPException(status_code=500, detail='Database integrity')

    if school.sex is Sex.BOYS:
      sex = '남'
    elif school.sex is Sex.GIRLS:
      sex = '여'
    elif school.sex is Sex.MIXED:
      sex = '남여공학'
    else:
      log.debug('Unknown school type stored in db. school_sex=\"{}\", school_uid=\"{}\"'.format(school.sex,
                                                                                                school.school_id))
      raise HTTPException(status_code=500, detail='Database integrity')

    ret.append({
      "schoolId": school.school_id,
      "schoolName": school.school_name,
      "schoolType": stype,
      "neisCode": school.neis_code,
      "address": school.address,
      "sex": sex,
      "userCount": school.user_count,
    })

  return ret


def add_school(school: AddSchoolRequest, db: Session):
  exists_query = (
    db.query(School)
    .filter_by(school_name=school.school_name)
    .filter_by(neis_code=school.neis_code)
    .exists()
  )
  exists = db.query(exists_query).scalar()

  if exists:
    log.debug('School already exists. school_name=\"{}\"'.format(school.school_name))
    raise HTTPException(status_code=409, detail='School already exists')

  if school.school_type == '일반고':
    school_type = SchoolType.GENERAL_HIGH_SCHOOL
  elif school.school_type == '자율고':
    school_type = SchoolType.AUTONOMOUS_HIGH_SCHOOL
  elif school.school_type == '특목고':
    school_type = SchoolType.SPECIAL_HIGH_SCHOOL
  elif school.school_type == '특성화고':
    school_type = SchoolType.SPECIALIZED_HIGH_SCHOOL
  elif school.school_type == '중학교':
    school_type = SchoolType.MIDDLE_SCHOOL
  else:
    log.debug('Unknown school type. school_type=\"{}\"'.format(school.school_type))
    raise ValueError("Invalid school type")

  if school.sex == '남':
    sex = Sex.BOYS
  elif school.sex == '여':
    sex = Sex.GIRLS
  elif school.sex == '남여공학':
    sex = Sex.MIXED
  else:
    log.debug('Unknown school sex type. school_sex=\"{}\"'.format(school.sex))
    raise ValueError('Invalid school sex type')

  ns = School(
    school_name=school.school_name,
    _school_type=school_type.value,
    neis_code=school.neis_code,
    address=school.address,
    _sex=sex.value
  )

  db.add(ns)
  db.commit()
  log.debug('New school added. school_name=\"{}\"'.format(school.school_name))


def delete_school(school_id: str, db: Session):
  school = db.query(School).filter_by(neis_code=school_id).first()
  if school is None:
    log.debug('School not found. school_id=\"{}\"'.format(school_id))
    raise HTTPException(status_code=404, detail='School not found')

  db.delete(school)
  db.commit()
  log.debug('School deleted. school_id=\"{}\"'.format(school_id))
