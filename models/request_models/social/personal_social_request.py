import re
from uuid import UUID

from pydantic import BaseModel, field_validator


class StarBoardRequest(BaseModel):
  board_id: str
  star: bool

  class Config:
    alias_generator = lambda field: ''.join(
      word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_'))
    )
    allow_population_by_field_name = True

  @field_validator("board_id")
  @classmethod
  def validate_board_id(cls, v):
    if len(v) != 36:
      raise ValueError("Invalid board_id")
    if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
      raise ValueError("Board id is invalid as of UUID")
    return v
