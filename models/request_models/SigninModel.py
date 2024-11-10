from pydantic import BaseModel, field_validator


class PasswordSigninRequest(BaseModel):
  id: str
  password: str
  recaptcha: str

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
