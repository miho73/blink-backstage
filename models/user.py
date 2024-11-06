import re
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, field_validator


class Role(Enum):
  USER = "USER"
  ADMIN = "ADMIN"


class UserSchema(BaseModel):
    user_id: Optional[int] = None
    username: str

    email: str
    email_verified: bool = False

    student_verified: bool = False
    role: List[Role] = []

    def set_role(self, role: int):
      role_arr = []

      if role % 2 == 1:
        role_arr.append(Role.USER)
        role -= 1
      role /= 2

      if role % 2 == 1:
        role_arr.append(Role.ADMIN)
        role -= 1
      self.role = role_arr


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


class GoogleUser(UserSchema):
    google_id: str
    picture: str


class JwtUser(BaseModel):
    user_id: int
    username: str
    role: Role

    @field_validator("username", mode="before")
    @classmethod
    def validate_name(cls, value):
        if len(value) < 1 or len(value) > 100:
            raise ValueError("Name must be 1 to 100 characters long")
        return value
