import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.school.school_service import get_school_from_neis_code
from core.social.board_service import check_acl_by_aud
from core.user.user_info_service import role_to_school
from models.database_models.relational.social.board_acl import BoardACLAction
from models.database_models.relational.social.comment import Comment
from models.request_models.social.comment_request import CommentAdditionRequest

log = logging.getLogger(__name__)


def get_organized_comments(
  post_id: UUID,
  db: Session
):
  comments = (
    db.query(Comment)
    .filter(Comment.post_id == post_id)
    .all()
  )

  ret = []
  peoples = []
  for comment in comments:
    user_id = comment.author_id
    if user_id not in peoples:
      peoples.append(user_id)

    ret.append({
      'author': peoples.index(user_id),
      'content': comment.content,
      'writeTime': comment.write_time.isoformat(),
      'edited': comment.edited,
      'upvote': comment.upvote,
      'downvote': comment.downvote,
      'school': comment.school.school_name,
    })

  return ret


def leave_comment(
  sub: UUID,
  aud: [str],
  post_id: UUID,
  content: str,
  db: Session
):
  (student_verified, neis_code) = role_to_school(aud)
  if not student_verified:
    log.debug('This user is not verified as student and cannot leave comment. user_uid=\"{}\"'.format(sub))
    raise HTTPException(status_code=403, detail='Forbidden')

  school = get_school_from_neis_code(neis_code, db)

  comment = Comment(
    post_id=post_id,
    content=content,
    author_id=sub,
    school_id=school.school_id,
  )

  db.add(comment)
  db.commit()


def delete_comment(
  sub: UUID,
  aud: [str],
  comment_id: UUID,
  db: Session
):
  comment = (
    db.query(Comment)
    .filter(Comment.comment_id == comment_id)
    .first()
  )

  if comment is None:
    log.debug('Comment was not found. comment_id=\"{}\"'.format(comment_id))
    raise HTTPException(status_code=404, detail='Comment not found')

  if not check_acl_by_aud(aud, comment.post.board_id, BoardACLAction.DELETE, db):
    log.debug(
      "This user is not permitted to delete comments. user_uid=\"{}\", comment_id=\"{}\", board_id=\"{}\"".format(sub,
                                                                                                                  comment_id,
                                                                                                                  comment.post.board_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  if comment.author_id != sub:
    log.debug('This user is not the author of the comment. user_uid=\"{}\", comment_id=\"{}\"'.format(sub, comment_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  log.debug('Deleting comment. user_id=\"{}\" comment_id=\"{}\"'.format(sub, comment_id))
  db.delete(comment)
  db.commit()


def edit_comment(
  sub: UUID,
  aud: [str],
  comment_id: UUID,
  content: str,
  db: Session
):
  comment = (
    db.query(Comment)
    .filter(Comment.comment_id == comment_id)
    .first()
  )

  if comment is None:
    log.debug('Comment was not found and cannot be edited. comment_id=\"{}\"'.format(comment_id))
    raise HTTPException(status_code=404, detail='Comment not found')

  board_id = comment.post.board_id

  if not check_acl_by_aud(aud, board_id, BoardACLAction.WRITE, db):
    log.debug(
      "This user is not permitted to edit comments. user_uid=\"{}\", post_id=\"{}\", board_id=\"{}\"".format(sub,
                                                                                                             comment.post_id,
                                                                                                             comment.post.board_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  if comment.author_id != sub:
    log.debug('This user is not the author of the comment. user_uid=\"{}\", comment_id=\"{}\"'.format(sub, comment_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  log.debug('Editing comment. user_id=\"{}\" comment_id=\"{}\"'.format(sub, comment_id))
  comment.content = content
  comment.edited = True
  db.commit()
