from pydantic import BaseModel, field_validator


class AddSchoolRequest(BaseModel):
  school_name: str
  school_type: str
  address: str
  neis_code: str
  sex: str

  @field_validator('school_name', mode='before')
  @classmethod
  def check_school_name(cls, value):
    if len(value) > 50 or len(value) < 1:
      raise ValueError('School name must be between 1 and 50 characters')
    return value

  @field_validator('school_type', mode='before')
  @classmethod
  def check_school_type(cls, value):
    if value not in ['일반고', '자율고', '특목고', '특성화고', '중학교']:
      raise ValueError('School type must be one of 일반고, 자율고, 특목고, 특성화고, 중학교')
    return value

  @field_validator('address', mode='before')
  @classmethod
  def check_address(cls, value):
    if len(value) > 255 or len(value) < 1:
      raise ValueError('Address must be between 1 and 255 characters')
    return value

  @field_validator('neis_code', mode='before')
  @classmethod
  def check_neis_code(cls, value):
    if not len(value) == 10:
      raise ValueError('NEIS code must be 10 characters')
    return value

  @field_validator("sex", mode="before")
  @classmethod
  def check_sex(cls, value):
    if value not in ['남', '여', '남여공학']:
      raise ValueError('NEIS code must be 10 characters')
    return value
