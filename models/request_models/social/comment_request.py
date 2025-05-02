import re

from pydantic import BaseModel, field_validator


class CommentAdditionRequest(BaseModel):
  post_id: str
  content: str

  class Config:
    alias_generator = lambda field: ''.join(
      word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_'))
    )
    allow_population_by_field_name = True

  @field_validator('content')
  @classmethod
  def validate_content(cls, v):
    if len(v) < 1 or len(v) > 2000:
      raise ValueError("Content length must be between 1 and 2000")
    return v

  @field_validator("post_id")
  @classmethod
  def validate_post_id(cls, v):
    if len(v) != 36:
      raise ValueError("Invalid post id")
    if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
      raise ValueError("Post id is invalid as of UUID")
    return v


class CommentEditRequest(BaseModel):
  comment_id: str
  content: str

  class Config:
    alias_generator = lambda field: ''.join(
      word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_'))
    )
    allow_population_by_field_name = True

  @field_validator('content')
  @classmethod
  def validate_content(cls, v):
    if len(v) < 1 or len(v) > 2000:
      raise ValueError("Content length must be between 1 and 2000")
    return v

  @field_validator("comment_id")
  @classmethod
  def validate_comment_id(cls, v):
    if len(v) != 36:
      raise ValueError("Invalid comment id")
    if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
      raise ValueError("Comment id is invalid as of UUID")
    return v
