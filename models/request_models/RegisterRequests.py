from pydantic import BaseModel, field_validator


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
