import re

from pydantic import BaseModel, field_validator, EmailStr


class PasswordRegisterRequest(BaseModel):
  username: str
  email: EmailStr
  id: str
  password: str
  recaptcha: str

  @field_validator("email", mode="before")
  @classmethod
  def validate_email(cls, value):
    if len(value) < 5 or len(value) > 255:
      raise ValueError("Email must be 5 to 255 characters long")
    if not re.match(r'^[-\w.]+@([-\w]+\.)+[-\w]{2,4}$', value):
      raise ValueError("Email regex check failed")
    return value

  @field_validator("id", mode="before")
  @classmethod
  def validate_id(cls, value):
    if len(value) < 1 or len(value) > 255:
      raise ValueError("ID must be 1 to 255 characters long")
    return value

  @field_validator("password", mode="before")
  @classmethod
  def validate_password(cls, value):
    if len(value) < 6:
      raise ValueError("Password must longer than 6 characters")
    return value

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value

  @field_validator("username", mode="before")
  @classmethod
  def validate_name(cls, value):
    if len(value) < 1 or len(value) > 100:
      raise ValueError("Name must be 1 to 100 characters long")
    return value


class GoogleRegisterRequest(BaseModel):
  code: str
  recaptcha: str
  username: str

  @field_validator("username", mode="before")
  @classmethod
  def validate_name(cls, value):
    if len(value) < 1 or len(value) > 100:
      raise ValueError("Name must be 1 to 100 characters long")
    return value

  @field_validator("code", mode="before")
  @classmethod
  def validate_access_code(cls, value):
    if value is None:
      raise ValueError("Google OAuth2 access code was not passed")
    return value

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value
