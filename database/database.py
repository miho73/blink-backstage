from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import config

SQL_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
  host=config["database"]["host"],
  port=config["database"]["port"],
  name=config["database"]["name"],
  user=config["database"]["user"],
  password=config["database"]["password"]
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
