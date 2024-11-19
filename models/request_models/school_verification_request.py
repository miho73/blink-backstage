import re

from pydantic import BaseModel, field_validator


class NewVerificationRequest(BaseModel):
  name: str
  school_name: str
  grade: int
  doc_code: str
  recaptcha: str

  @field_validator("name", mode="before")
  @classmethod
  def validate_name(cls, value):
    if len(value) < 1 or len(value) > 20:
      raise ValueError("Name must be 1 to 20 characters long")
    return value

  @field_validator("school_name", mode="before")
  @classmethod
  def validate_school_name(cls, value):
    if len(value) < 1 or len(value) > 50:
      raise ValueError("School name must be 1 to 50 characters long")
    return value

  @field_validator("grade", mode="before")
  @classmethod
  def validate_grade(cls, value):
    if value < 1 or value > 3:
      raise ValueError("Grade must be one of 1, 2, 3")
    return value

  @field_validator("doc_code", mode="before")
  @classmethod
  def validate_doc_code(cls, value):
    if not re.match(r'^\d{4}-\d{4}-\d{4}-\d{4}$', value):
      raise ValueError("Doc code is invalid")
    return value

  @field_validator("recaptcha", mode="before")
  @classmethod
  def validate_recaptcha(cls, value):
    if value is None:
      raise ValueError("reCAPTCHA token was not passed")
    return value
