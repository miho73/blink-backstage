from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, BOOLEAN, SMALLINT, TIMESTAMP
from sqlalchemy.orm import relationship, backref

from database.database import TableBase
from models.user import Role


class Identity(TableBase):
  __tablename__ = "identity"
  __table_args__ = {"schema": "users"}

  user_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  username: str = Column(VARCHAR(100), nullable=False)

  email: EmailStr = Column(VARCHAR(255), nullable=False, unique=True)
  email_verified: bool = Column(BOOLEAN, nullable=False, default=False)

  join_date: datetime = Column(TIMESTAMP, nullable=False, default="now()")
  last_login: datetime = Column(TIMESTAMP)

  student_verified: bool = Column(BOOLEAN, nullable=False, default=False)
  school_id: int = Column(INTEGER, ForeignKey("school.schools.school_id"))
  grade: int = Column(SMALLINT)
  _role: Role = Column("role", SMALLINT, nullable=False, default=Role.USER.value)

  school = relationship("School", uselist=False, backref=backref("students", uselist=True))

  @property
  def role(self):
    return Role(self._role)

  @role.setter
  def role(self, value: Role):
    self._role = value.value
