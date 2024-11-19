import logging

import requests
from fastapi import HTTPException

from core.config import config

log = logging.getLogger(__name__)

SCHOOL_INFO_URL = config['api']['neis']['school_info']
API_KEY = config['api']['neis']['key']


def query_school_info(school_name: str):
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
      'school_name': school['SCHUL_NM'],
      'school_class': school['SCHUL_KND_SC_NM'],
      'neis_code': school['ATPT_OFCDC_SC_CODE'] + school['SD_SCHUL_CODE'],
      'address': school['ORG_RDNMA'],
      'sex': school['COEDU_SC_NM'],
      'school_type': school_type
    })

  return ret
