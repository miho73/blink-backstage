from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, BOOLEAN, SMALLINT, TIMESTAMP
from sqlalchemy.orm import relationship

from database.database import TableBase
from models.user import Role


class Identity(TableBase):
  __tablename__ = "identity"
  __table_args__ = {"schema": "users"}

  user_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  username: str = Column(VARCHAR, nullable=False)

  email: str = Column(VARCHAR, nullable=False, unique=True)
  email_verified: bool = Column(BOOLEAN, nullable=False, default=False)

  join_date: datetime = Column(TIMESTAMP, nullable=False, default="now()")
  last_login: datetime = Column(TIMESTAMP)

  student_verified: bool = Column(BOOLEAN, nullable=False, default=False)
  school_id: int = Column(INTEGER, ForeignKey("school.schools.school_id"))
  _role: Role = Column("role", SMALLINT, nullable=False, default=Role.USER.value)

  school = relationship("School", uselist=False)
  auth_lookup = relationship("AuthLookup", back_populates="identity", uselist=False)

  @property
  def role(self):
    return Role(self._role)

  @role.setter
  def role(self, value: Role):
    self._role = value.value
