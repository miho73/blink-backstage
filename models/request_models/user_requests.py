import re
from typing import Optional

from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from pydantic.alias_generators import to_camel


class UpdateUserProfileRequest(BaseModel):
  username: str
  email: EmailStr
  recaptcha: str

  @field_validator("username", mode="before")
  @classmethod
  def validate_username(cls, value):
    if len(value) < 1 or len(value) > 100:
      raise ValueError("Name must be 1 to 100 characters long")
    return value

  @field_validator("email", mode="before")
  @classmethod
  def validate_email(cls, value):
    if len(value) < 5 or len(value) > 255:
      raise ValueError("Email must be 5 to 255 characters long")
    if not re.match(r'^[-\w.]+@([-\w]+\.)+[-\w]{2,4}$', value):
      raise ValueError("Email regex check failed")
    return value

class UpdateUserAllergyInformationRequest(BaseModel):
  allergy: int

  @field_validator("allergy", mode="before")
  @classmethod
  def validate_allergy(cls, value):
    if value != 0 and (value < 2 or value > 524287):
      raise ValueError("Allergy code out of range")
    return value

class UpdateClassroomSNumberRequest(BaseModel):
  classroom: Optional[int]
  student_number: Optional[int]

  model_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
  )

  @field_validator("classroom", mode="before")
  @classmethod
  def validate_classroom_s_number(cls, value):
    if value is None:
      return None
    if value < 1 or value > 30:
      raise ValueError("Classroom out of range")
    return value

  @field_validator("student_number", mode="before")
  @classmethod
  def validate_student_number(cls, value):
    if value is None:
      return None
    if value < 1 or value > 50:
      raise ValueError("Student number out of range")
    return value
