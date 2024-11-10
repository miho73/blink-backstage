from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, BOOLEAN
from sqlalchemy.orm import relationship

from database.database import TableBase


class AuthLookup(TableBase):
  __tablename__ = "auth_lookup"
  __table_args__ = {"schema": "authentication"}

  lookup_id: int = Column(INTEGER, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
  user_id: int = Column(INTEGER, ForeignKey("users.identity.user_id"), unique=True, nullable=False)

  google = Column(BOOLEAN, nullable=False, default=False)
  password = Column(BOOLEAN, nullable=False, default=False)
  passkey = Column(BOOLEAN, nullable=False, default=False)

  identity = relationship("Identity", back_populates="auth_lookup")

  google_method = relationship("GoogleMethod", back_populates="auth_lookup", uselist=False)
  password_method = relationship("PasswordMethod", back_populates="auth_lookup", uselist=False)
