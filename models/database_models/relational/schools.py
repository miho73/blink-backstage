from enum import Enum
from uuid import UUID as PyUUID

from sqlalchemy import Column, UUID
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, SMALLINT
from sqlalchemy.orm import Mapped

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

  school_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False,
                                     server_default='gen_random_uuid()')
  school_name: Mapped[str] = Column(VARCHAR(50), nullable=False, index=True)
  _school_type: Mapped[int] = Column("school_type", SMALLINT, nullable=False)
  neis_code: Mapped[str] = Column(VARCHAR(10), nullable=False)
  address: Mapped[str] = Column(VARCHAR, nullable=False)
  _sex: Mapped[int] = Column("sex", SMALLINT, nullable=False)
  user_count: Mapped[int] = Column(INTEGER, nullable=False, default=0)

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
