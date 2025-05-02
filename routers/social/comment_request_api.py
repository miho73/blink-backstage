import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Security, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.social import check_acl
from core.social.board_service import check_acl_by_aud
from core.social.comment_service import get_organized_comments, leave_comment, delete_comment, edit_comment
from core.social.post_service import get_post, get_board_by_post
from database.database import create_connection
from models.database_models.relational.social.board_acl import BoardACLAction
from models.request_models.social.comment_request import CommentAdditionRequest, CommentEditRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/social/comment',
  tags=['social', 'comment']
)


@router.get(
  path='/{post_id}',
  summary="Get comments for post"
)
def get_comments(
  jwt: str = Security(authorization_header),
  post_id: UUID = None,
  db: Session = Depends(create_connection)
):
  log.debug("Get comments of post. post_id=\"{}\"".format(post_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  board = get_board_by_post(post_id, db)

  if not check_acl_by_aud(aud, board.board_id, BoardACLAction.READ, db):
    log.debug(
      "This user is not permitted to read comments. user_uid=\"{}\", post_id=\"{}\", board_id=\"{}\"".format(sub,
                                                                                                             post_id,
                                                                                                             board.board_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  comments = get_organized_comments(post_id, db)

  return JSONResponse(
    status_code=200,
    content={
      'code': 200,
      'state': 'OK',
      'comments': comments
    }
  )


@router.post(
  path='',
  summary="Post comment for post"
)
def post_comment(
  body: CommentAdditionRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.debug("Post comment for post. post_id=\"{}\"".format(body.post_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  post_id = UUID(body.post_id)

  board = get_board_by_post(post_id, db)

  if not check_acl_by_aud(aud, board.board_id, BoardACLAction.WRITE, db):
    log.debug(
      "This user is not permitted to write comments. user_uid=\"{}\", post_id=\"{}\", board_id=\"{}\"".format(sub,
                                                                                                              post_id,
                                                                                                              board.board_id))
    raise HTTPException(status_code=403, detail='Forbidden')

  leave_comment(sub, aud, post_id, body.content, db)

  return JSONResponse(
    status_code=201,
    content={
      'code': 201,
      'state': 'CREATED'
    }
  )


@router.delete(
  path='/{comment_id}',
  summary="Delete comment for post"
)
def delete_comment_api(
  jwt: str = Security(authorization_header),
  comment_id: UUID = None,
  db: Session = Depends(create_connection)
):
  log.debug("Delete comment. comment_id=\"{}\"".format(comment_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  # This function includes ACL check
  delete_comment(sub, aud, comment_id, db)

  return JSONResponse(
    status_code=200,
    content={
      'code': 200,
      'state': 'OK'
    }
  )


@router.patch(
  path='',
  summary="Edit comment for post"
)
def edit_comment_api(
  body: CommentEditRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.debug("Edit comment. comment_id=\"{}\"".format(body.comment_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  comment_id = UUID(body.comment_id)

  # This function includes ACL check
  edit_comment(sub, aud, comment_id, body.content, db)

  return JSONResponse(
    status_code=200,
    content={
      'code': 200,
      'state': 'OK'
    }
  )
