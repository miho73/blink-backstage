import logging
import uuid
from http.client import HTTPException
from typing import Type

from sqlalchemy.orm import Session

from core.social.board_service import check_privilege
from models.database_models.relational.identity import Identity
from models.database_models.relational.social.board_acl import BoardACLAction
from models.database_models.relational.social.post import Post
from models.request_models.social.post_request import UploadPostRequest

log = logging.getLogger(__name__)


def upload_post(
  sub: int,
  body: UploadPostRequest,
  db: Session
):
  identity: Type[Identity] = db.query(Identity).filter(Identity.user_id == sub).first()

  if identity is None:
    raise HTTPException("User not found", 404)

  board_id = uuid.UUID(body.board_id)

  if not check_privilege(identity, board_id, BoardACLAction.WRITE, db):
    raise HTTPException("User does not have permission to write to this board", 403)

  new_post: Post = Post(
    author_id=sub,
    school_id=identity.school_id,
    board_id=board_id,

    title=body.title,
    content=body.content,
    images=body.images
  )

  db.add(new_post)
  return new_post.post_id
