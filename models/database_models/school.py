from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, SMALLINT

from database.database import TableBase


class SchoolType(Enum):
  GENERAL_HIGH_SCHOOL = 0
  AUTONOMOUS_HIGH_SCHOOL = 1
  SPECIAL_HIGH_SCHOOL = 2
  SPECIALIZED_HIGH_SCHOOL = 3
  MIDDLE_SCHOOL = 4
  ETC = 5


class Sex(Enum):
  BOYS = 0
  GIRLS = 1
  MIXED = 2


class School(TableBase):
  __tablename__ = "schools"
  __table_args__ = {"schema": "school"}

  school_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  school_name: str = Column(VARCHAR, nullable=False)
  _school_type: int = Column("school_type", SMALLINT, nullable=False)
  neis_code: str = Column(VARCHAR, nullable=False)
  address: str = Column(VARCHAR, nullable=False)
  _sex: int = Column("sex", SMALLINT, nullable=False)
  user_count: int = Column(INTEGER, nullable=False, default=0)

  @property
  def school_type(self):
    return SchoolType(self._school_type)

  @school_type.setter
  def school_type(self, value: SchoolType):
    self._school_type = value.value

  @property
  def sex(self):
    return Sex(self._sex)

  @sex.setter
  def sex(self, value: Sex):
    self._sex = value.value
