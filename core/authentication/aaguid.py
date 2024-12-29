import json
import logging

from pydantic.dataclasses import dataclass

from database.database import redis_aaguid_db

log = logging.getLogger(__name__)


def load_aaguid():
  log.debug("Flushing aaguid list from redis")
  redis_aaguid_db.flushall()

  log.debug("Loading aaguid list to redis")
  with open("resources/combined_aaguid.json", "r") as f:
    aaguid_json: dict = json.load(f)

  keys = aaguid_json.keys()

  for key in keys:
    redis_aaguid_db.set(key, json.dumps(aaguid_json[key]))


@dataclass
class Authenticator:
  name: str
  icon_light: str
  icon_dark: str


def get_authenticator(aaguid: str) -> Authenticator:
  aaguid_json = redis_aaguid_db.get(aaguid)
  if aaguid_json is None:
    return None

  aaguid_dict = json.loads(aaguid_json)
  return Authenticator(
    name=aaguid_dict['name'],
    icon_light=aaguid_dict['icon_light'],
    icon_dark=aaguid_dict['icon_dark'],
  )
