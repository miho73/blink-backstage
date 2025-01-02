import logging
from typing import Type

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import config
from models.database_models.relational.schools import School

log = logging.getLogger(__name__)

SCHOOL_INFO_URL = config['api']['neis']['school_info']
API_KEY = config['api']['neis']['key']


def query_school_info(school_name: str) -> list[dict]:
  response = requests.get(
    url='https://open.neis.go.kr/hub/schoolInfo',
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
