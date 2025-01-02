import logging
import uuid
from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.school import neis_school_service
from core.social.board_service import check_acl, check_acl_by_aud
from core.user.user_info_service import role_to_school
from models.database_models.relational.identity import Identity
from models.database_models.relational.social.board import Board
from models.database_models.relational.social.board_acl import BoardACLAction
from models.database_models.relational.social.post import Post
from models.request_models.social.post_request import UploadPostRequest, UpdatePostRequest
from uuid import UUID as PyUUID

log = logging.getLogger(__name__)


def upload_post(
  sub: PyUUID,
  aud: list[str],
  body: UploadPostRequest,
  db: Session
):
  identity: Type[Identity] = db.query(Identity).filter(Identity.user_id == sub).first()

  if identity is None:
    raise HTTPException(404, "User not found")

  student_verified, neis_code = role_to_school(aud)
  board_id = uuid.UUID(body.board_id)

  if not student_verified:
    raise HTTPException(403, "User is not a student")

  if not check_acl(identity, board_id, BoardACLAction.WRITE, db):
    raise HTTPException(403, "User does not have permission to write to this board")

  school = neis_school_service.db_neis_to_school(neis_code, db)
  if school is None:
    raise HTTPException(404, "School not found")

  new_post: Post = Post(
    author_id=sub,
    school_id=school.school_id,
    board_id=board_id,

    title=body.title,
    content=body.content,
    images=body.image
  )

  db.add(new_post)
  db.commit()

  return new_post.post_id


def delete_post(sub, aud, post_id, db):
  post = db.query(Post).filter(Post.post_id == post_id).first()
  if post is None:
    raise HTTPException(404, "Post not found")

  # first check if user is an author
  if post.author_id == sub:
    log.debug("Deleted post as author. post_id=\"{post_id}\", deleted_by=\"{sub}\"".format(post_id=post_id, sub=sub))
    complete_delete(post, db)
    return

  # then check if user is a moderator
  if check_acl(sub, post.board_id, BoardACLAction.DELETE, db):
    log.debug("Deleted post as moderator. post_id=\"{post_id}\", deleted_by=\"{sub}\"".format(post_id=post_id, sub=sub))
    complete_delete(post, db)
    return

  raise HTTPException(403, "User does not have permission to delete this post")

def complete_delete(post, db):
  db.delete(post)
  db.commit()


def edit_post(sub, aud, post_id, body, db):
  post = db.query(Post).filter(Post.post_id == post_id).first()
  if post is None:
    raise HTTPException(404, "Post not found")

  if post.author_id == sub:
    log.debug("Edited post as author. post_id=\"{post_id}\", edited_by=\"{sub}\"".format(post_id=post_id, sub=sub))
    complete_edit(post, body, db)
    return
  if check_acl(sub, post.board_id, BoardACLAction.UPDATE, db):
    log.debug("Edited post as moderator. post_id=\"{post_id}\", edited_by=\"{sub}\"".format(post_id=post_id, sub=sub))
    complete_edit(post, body, db)
    return

  raise HTTPException(403, "User does not have permission to edit this post")


def complete_edit(
  post: Post,
  body: UpdatePostRequest,
  db: Session
):
  post.title = body.title
  post.content = body.content
  post.images = body.image
  post.edited = True
  db.commit()


def get_posts(aud, board_id, db):
  if check_acl_by_aud(aud, board_id, BoardACLAction.READ, db):
    return (
      db.query(Post).filter(Post.board_id == board_id)
        .order_by(Post.write_time.desc())
        .limit(10)
        .all()
    )

  raise HTTPException(403, "User does not have permission to list this board")


def get_post(
  aud: list[str],
  post_id: PyUUID,
  db: Session
):
  post = db.query(Post).filter(Post.post_id == post_id).first()

  if check_acl_by_aud(aud, post.board_id, BoardACLAction.READ, db):
    if post is None:
      raise HTTPException(404, "Post not found")

    post.views += 1
    db.commit()
    return post

  raise HTTPException(403, "User does not have permission to view this post")
