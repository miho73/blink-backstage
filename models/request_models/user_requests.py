import re

from pydantic import BaseModel, field_validator, EmailStr


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
