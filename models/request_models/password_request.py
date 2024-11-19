from pydantic import BaseModel, field_validator


class UpdatePasswordRequest(BaseModel):
  current_password: str
  new_password: str
  recaptcha: str

  @field_validator("current_password", mode="before")
  @classmethod
  def validate_current_password(cls, value):
    if len(value) < 6:
      raise ValueError("Current password must be longer than 6 characters long")
    return value

  @field_validator("new_password", mode="before")
  @classmethod
  def validate_new_password(cls, value):
    if len(value) < 6:
      raise ValueError("New password must be longer than 6 characters long")
    return value

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value
