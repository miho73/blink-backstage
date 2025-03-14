import json
import logging
from datetime import datetime, time, timedelta
from typing import Type
from uuid import UUID

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import config
from core.user.user_info_service import get_identity_by_userid, role_to_school
from database.database import meal_cache_db
from models.database_models.relational.schools import School

log = logging.getLogger(__name__)

SCHOOL_INFO_URL = config['api']['neis']['school_info']
MEAL_INFO_URL = config['api']['neis']['meal_info']
SCHOOL_TIMETABLE_URL = config['api']['neis']['high_school_timetable_info']
API_KEY = config['api']['neis']['key']

today = datetime.today()
FIRST_DATE_OF_WEEK = today - timedelta(days=today.weekday())
LAST_DATE_OF_WEEK = FIRST_DATE_OF_WEEK + timedelta(days=4) # TODO: CHANGE CACHED DATE EVERYDAY


def query_school_info(school_name: str) -> list[dict]:
  response = requests.get(
    url=SCHOOL_INFO_URL,
    params={
      'KEY': API_KEY,
      'Type': 'json',
      'SCHUL_NM': school_name
    }
  )

  if response.status_code != 200:
    log.debug("NEIS API error. status_code={}".format(response.status_code))
    raise HTTPException(status_code=500, detail="NEIS API error")

  if 'schoolInfo' not in response.json():
    return []

  jsn = response.json()['schoolInfo'][1]['row']
  ret = []

  for school in jsn:
    if school['SCHUL_KND_SC_NM'] == '초등학교':
      continue

    school_type = school['HS_SC_NM']
    if school['HS_SC_NM'] is None or len(school['HS_SC_NM']) <= 2:
      school_type = school['SCHUL_KND_SC_NM']

    ret.append({
      'schoolName': school['SCHUL_NM'],
      'schoolClass': school['SCHUL_KND_SC_NM'],
      'neisCode': school['ATPT_OFCDC_SC_CODE'] + school['SD_SCHUL_CODE'],
      'address': school['ORG_RDNMA'],
      'sex': school['COEDU_SC_NM'],
      'schoolType': school_type
    })

  return ret

def db_neis_to_school(neis_code: str, db: Session) -> Type[School] | None:
  school = db.query(School).filter(School.neis_code == neis_code).first()

  if school is None:
    return None

  return school


def get_meal_data(neis_code: str) -> dict:
  log.debug('requesting NEIS meal API. neis_code={}'.format(neis_code))
  today = datetime.today().strftime('%Y%m%d')

  cnt = meal_cache_db.exists(neis_code+today)
  if cnt > 0:
    log.debug('meal cache hit. neis_code={}, day={}'.format(neis_code, today))
    return json.loads(meal_cache_db.get(neis_code+today))
  log.debug('meal cache miss. neis_code={}, day={}'.format(neis_code, today))

  response = requests.get(
    url=MEAL_INFO_URL,
    params={
      'KEY': API_KEY,
      'Type': 'json',
      'ATPT_OFCDC_SC_CODE': neis_code[:3],
      'SD_SCHUL_CODE': neis_code[3:],
      'MLSV_YMD': today
    }
  )

  if response.status_code != 200:
    log.debug("NEIS meal API error. status_code={}".format(response.status_code))
    raise HTTPException(status_code=500, detail="NEIS API error")

  if 'mealServiceDietInfo' not in response.json():
    log.debug('NEIS API returned empty meal data. result won\'t be cached. neis_code={}'.format(neis_code))
    return {}

  jsn = response.json()['mealServiceDietInfo'][1]['row']
  ret = {}

  for serve in jsn:
    if neis_code != serve['ATPT_OFCDC_SC_CODE'] + serve['SD_SCHUL_CODE']:
      log.debug('NEIS API returned wrong school code. ignore request. request={}, response={}'.format(neis_code, serve['ATPT_OFCDC_SC_CODE'] + serve['SD_SCHUL_CODE']))
      continue

    key = serve['MMEAL_SC_CODE']
    diet: str = serve['DDISH_NM']
    nutrient: str = serve['NTR_INFO']
    diet_list: [str] = diet.split('<br/>')
    nutrient_list: [str] = nutrient.split('<br/>')
    ret[key] = {
      'diet': diet_list,
      'nutrients': nutrient_list,
      'calories': serve['CAL_INFO'][0:-5],
    }

  now = datetime.now()
  end_of_day = datetime.combine(now.date(), time(23, 59, 59))
  remaining_time = end_of_day - now
  meal_cache_db.set(
    name=neis_code+today,
    value=json.dumps(ret),
    ex=remaining_time
  )
  log.debug('meal cache set. neis_code={}, ttl={}'.format(neis_code, remaining_time))

  return ret

def get_timetable_data(
  uid: UUID,
  db: Session
) -> dict:
  # TODO: split logic when the school is middle school
  log.debug('requesting timetable API. uid={}'.format(uid))

  identity = get_identity_by_userid(uid, db)
  if identity is None:
    raise HTTPException(status_code=404, detail='User not found')

  student_verified, neis_code = role_to_school(identity.role)

  if not student_verified:
    raise HTTPException(status_code=403, detail='User is not a student')

  school = db_neis_to_school(neis_code, db)
  if school is None:
    raise HTTPException(status_code=404, detail='School not found')

  grade = identity.grade
  classroom = identity.classroom
  if classroom is None:
    raise HTTPException(status_code=400, detail='Classroom not set')

  log.debug("requesting NEIS timetable API. neis_code={}, grade={}, classroom={}".format(neis_code, grade, classroom))
  response = requests.get(
    url=SCHOOL_TIMETABLE_URL,
    params={
      'KEY': API_KEY,
      'Type': 'json',
      'ATPT_OFCDC_SC_CODE': neis_code[:3],
      'SD_SCHUL_CODE': neis_code[3:],
      'GRADE': grade,
      'CLASS_NM': classroom,
      'TI_FROM_YMD': FIRST_DATE_OF_WEEK.strftime('%Y%m%d'),
      'TI_TO_YMD': LAST_DATE_OF_WEEK.strftime('%Y%m%d'),
    }
  )

  if response.status_code != 200:
    log.debug("NEIS timetable API error. status_code={}".format(response.status_code))
    raise HTTPException(status_code=500, detail="NEIS API error")

  log.debug(response.json())
  if 'hisTimetable' not in response.json():
    log.debug("request field \'hisTimetable\' does not exists in API response")
    raise HTTPException(status_code=404, detail='No schedule was found')

  lectures = response.json()['hisTimetable'][1]['row']
  ret = []
  log.debug(response.json())

  for lecture in lectures:
    ret.append({
      'subject': lecture['ITRT_CNTNT'],
      'class': {
        'grade': int(lecture['GRADE']),
        'class': int(lecture['CLASS_NM']),
      },
      'time': {
        'date': int(lecture['ALL_TI_YMD']) - int(FIRST_DATE_OF_WEEK.strftime('%Y%m%d')),
        'period': int(lecture['PERIO']),
      },
      'classroom': lecture['CLRM_NM'],
    })

  return {
    'academicYear': lectures[0]['AY'],
    'semester': lectures[0]['SEM'],
    'period': {
      'begin': FIRST_DATE_OF_WEEK.isoformat(),
      'end': LAST_DATE_OF_WEEK.isoformat(),
    },
    'schedules': ret
  }
