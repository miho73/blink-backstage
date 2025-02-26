import redis.asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import config

SQL_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
  host=config["database"]['relational']["host"],
  port=config["database"]['relational']["port"],
  name=config["database"]['relational']["name"],
  user=config["database"]['relational']["user"],
  password=config["database"]['relational']["password"]
)

engine = create_engine(SQL_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
TableBase = declarative_base()


def create_connection():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


redis_db = redis.Redis(
  host=config['database']["redis"]["host"],
  port=config['database']["redis"]["port"],
  password=config['database']["redis"]["password"],
  db=0,
  decode_responses=True
)

redis_aaguid_db = redis.Redis(
  host=config['database']["redis"]["host"],
  port=config['database']["redis"]["port"],
  password=config['database']["redis"]["password"],
  db=1,
  decode_responses=True
)

meal_cache_db = redis.Redis(
  host=config['database']["redis"]["host"],
  port=config['database']["redis"]["port"],
  password=config['database']["redis"]["password"],
  db=2,
  decode_responses=True
)
