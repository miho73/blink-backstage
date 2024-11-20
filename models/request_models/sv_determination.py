from pydantic import BaseModel, field_validator


class SvDetermination(BaseModel):
  verification_id: int
  state: int
  school_id: int

  @field_validator("state", mode="before")
  @classmethod
  def validate_state(cls, value):
    if value < 2 or value > 7:
      raise ValueError("State must be one of 2, 3, 4, 5, 6, 7")
    return value
