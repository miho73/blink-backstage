from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, SMALLINT, BYTEA, VARCHAR
from sqlalchemy.orm import relationship, backref

from database.database import TableBase


class SvRequestType(Enum):
  CERTIFICATE_OF_ENROLLMENT = 0


class SvEvidenceType(Enum):
  PDF = 0
  PNG = 1
  JPEG = 2


class SvState(Enum):
  DRAFT = 0
  REQUESTED = 1
  HOLDING = 2
  ACCEPTED = 3
  INVALID_EVIDENCE = 4
  IDENTITY_MISMATCH = 5
  INVALID_DOCUMENT = 6
  DENIED = 7


class SvRequest(TableBase):
  __tablename__ = 'verification'
  __table_args__ = {'schema': "users"}

  verification_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  user_id: int = Column(INTEGER, ForeignKey('users.identity.user_id'), unique=True, nullable=False)

  request_time: datetime = Column(TIMESTAMP, nullable=False, default="now()")
  examine_time: datetime = Column(TIMESTAMP)

  _request_type: int = Column('request_type', SMALLINT, nullable=False)
  evidence: bytes = Column(BYTEA)
  _evidence_type: int = Column('evidence_type', SMALLINT)
  grade: int = Column(SMALLINT, nullable=False)
  name: str = Column(VARCHAR(20), nullable=False)
  school: str = Column(VARCHAR(50), nullable=False)
  _state: int = Column('state', SMALLINT, nullable=False, default=0)
  doc_code: str = Column(VARCHAR(19))

  identity = relationship("Identity", backref=backref("verification", uselist=True))

  @property
  def request_type(self):
    return SvRequestType(self._request_type)

  @request_type.setter
  def request_type(self, value: SvRequestType):
    self._request_type = value.value

  @property
  def evidence_type(self) -> Optional[SvEvidenceType]:
    return self._evidence_type is not None and SvEvidenceType(self._evidence_type) or None

  @evidence_type.setter
  def evidence_type(self, value: SvEvidenceType):
    self._evidence_type = value.value

  @property
  def state(self):
    return SvState(self._state)

  @state.setter
  def state(self, value: SvState):
    self._state = value.value
