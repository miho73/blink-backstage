import re
from typing import Optional

from pydantic import BaseModel, field_validator, EmailStr


class User(BaseModel):
  user_id: Optional[int] = None
  username: str

  email: EmailStr
  email_verified: bool = False

  student_verified: bool = False
  role: Optional[list[str]] = None

  @field_validator("email", mode="before")
  @classmethod
  def validate(cls, value):
    if len(value) < 5 or len(value) > 255:
      raise ValueError("Email must be 5 to 255 characters long")
    if not re.match(r'^[-\w.]+@([-\w]+\.)+[-\w]{2,4}$', value):
      raise ValueError("Email regex check failed")
    return value

  @field_validator("username", mode="before")
  @classmethod
  def validate_name(cls, value):
    if len(value) < 1 or len(value) > 100:
      raise ValueError("Username must be 1 to 100 characters long")
    return value


class GoogleUser(User):
  google_id: str
  picture: str


class JwtUser(BaseModel):
  user_id: int
  username: str
  role: list[str]

  @field_validator("username", mode="before")
  @classmethod
  def validate_name(cls, value):
    if len(value) < 1 or len(value) > 100:
      raise ValueError("Name must be 1 to 100 characters long")
    return value
