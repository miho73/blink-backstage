import re
from uuid import UUID

from pydantic import BaseModel, field_validator


class UploadPostRequest(BaseModel):
  board_id: str

  title: str
  content: str
  image: list[UUID]

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

  @field_validator("title")
  @classmethod
  def validate_title(cls, v):
    if len(v) > 512 or len(v) < 1:
      raise ValueError("Title is too long or too short")
    return v

  @field_validator("content")
  @classmethod
  def validate_content(cls, v):
    if len(v) < 1:
      raise ValueError("Content is too short")
    if len(v) > 10000:
      raise ValueError("Content is too long")
    return v

  @field_validator("image")
  @classmethod
  def validate_image(cls, v):
    if len(v) > 10:
      raise ValueError("Too many images")
    for i in v:
      if len(i) != 36:
        raise ValueError("Invalid image id")
      if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', i):
        raise ValueError("Image id is invalid as of UUID")
    return v


class UpdatePostRequest(BaseModel):
  title: str
  content: str
  image: list[UUID]

  @field_validator("title")
  @classmethod
  def validate_title(cls, v):
    if len(v) > 512 or len(v) < 1:
      raise ValueError("Title is too long or too short")
    return v

  @field_validator("content")
  @classmethod
  def validate_content(cls, v):
    if len(v) < 1:
      raise ValueError("Content is too short")
    if len(v) > 10000:
      raise ValueError("Content is too long")
    return v

  @field_validator("image")
  @classmethod
  def validate_image(cls, v):
    if len(v) > 10:
      raise ValueError("Too many images")
    for i in v:
      if len(i) != 36:
        raise ValueError("Invalid image id")
      if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', i):
        raise ValueError("Image id is invalid as of UUID")
    return v


class VoteRequest(BaseModel):
  vote: bool
  post_id: str

  class Config:
    alias_generator = lambda field: ''.join(
      word.capitalize() if i > 0 else word for i, word in enumerate(field.split('_'))
    )
    allow_population_by_field_name = True

  @field_validator("post_id")
  @classmethod
  def validate_post_id(cls, v):
    if len(v) != 36:
      raise ValueError("Invalid post id")
    if not re.match('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v):
      raise ValueError("Post id is invalid as of UUID")
    return v
