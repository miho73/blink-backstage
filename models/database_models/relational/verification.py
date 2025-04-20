from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import TIMESTAMP, SMALLINT, BYTEA, VARCHAR
from sqlalchemy.orm import relationship, backref, Mapped

from database.database import TableBase
from models.database_models.relational.identity import Identity


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

  verification_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True,
                                           nullable=False, server_default='gen_random_uuid()')
  user_id: Mapped[PyUUID] = Column(UUID(as_uuid=True), ForeignKey('users.identity.user_id'), unique=True,
                                   nullable=False)

  request_time: Mapped[datetime] = Column(TIMESTAMP, nullable=False, default="now()")
  examine_time: Mapped[datetime] = Column(TIMESTAMP)

  _request_type: Mapped[int] = Column('request_type', SMALLINT, nullable=False)
  evidence: Mapped[bytes] = Column(BYTEA)
  _evidence_type: Mapped[int] = Column('evidence_type', SMALLINT)
  grade: Mapped[int] = Column(SMALLINT, nullable=False)
  name: Mapped[str] = Column(VARCHAR(20), nullable=False)
  school: Mapped[str] = Column(VARCHAR(50), nullable=False)
  _state: Mapped[int] = Column('state', SMALLINT, nullable=False, default=0)
  doc_code: Mapped[str] = Column(VARCHAR(19))

  identity: Mapped[Identity] = relationship("Identity", backref=backref("verification", uselist=True)) # TODO: choose the destiny when the user is deleted

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
