import logging
from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Security, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.social import post_service
from core.validation import regex_check
from database.database import create_connection
from models.request_models.social.post_request import UploadPostRequest, UpdatePostRequest, VoteRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/social/post',
  tags=['school']
)


@router.post(
  path='',
  description='Upload a new post',
)
async def post(
  body: UploadPostRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.info("Posting new post. title=\"{title}\", content=\"{content}\"".format(title=body.title, content=body.content))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  post_uuid = post_service.upload_post(sub, aud, body, db)

  return JSONResponse(
    content={
      "code": 201,
      "state": "CREATED",
      "postId": str(post_uuid)
    }
  )

@router.delete(
  path='/{post_id}',
  description='Delete a post',
)
async def delete(
  post_id: str,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.info("Deleting post. post_id=\"{post_id}\"".format(post_id=post_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  post_service.delete_post(sub, aud, post_id, db)

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK"
    }
  )

@router.patch(
  path='/{post_id}',
  description='Edit a post',
)
async def edit(
  post_id: str,
  body: UpdatePostRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.info("Editing post. post_id=\"{post_id}\", title=\"{title}\", content=\"{content}\"".format(post_id=post_id, title=body.title, content=body.content))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  post_service.edit_post(sub, aud, post_id, body, db)

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK"
    }
  )

@router.get(
  path='/list/{board_id}',
  description='Get a post',
)
async def get(
  board_id: str,
  head: str | None = '',
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.info("Listing posts. board_id=\"{board_id}\"".format(board_id=board_id))

  token = authorize_jwt(jwt)
  aud = get_aud(token)

  if regex_check(board_id, r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'):
    board_uuid = UUID(board_id)
  else:
    raise ValueError("Invalid board_id")

  begin_uuid = None
  if regex_check(head, r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'):
    log.debug("Query posts from board. board_id=\"{board_id}\", head=\"{head}\"".format(board_id=board_id, head=head))
    begin_uuid = UUID(head)

  posts = post_service.get_posts(aud, board_uuid, begin_uuid, db)
  response = []
  for post in posts:
    response.append({
      "postId": str(post.post_id),
      "title": post.title,
      "content": post.content,
      "edited": post.edited,
      "writeTime": post.write_time.isoformat(),
      "schoolName": post.school.school_name,
      "views": post.views,
      "upvote": post.upvote,
      "downvote": post.downvote,
    })

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK",
      "posts": response
    }
  )

@router.get(
  path='/{post_id}',
  description='Get a post',
)
async def get_post(
  post_id: str,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.info("Getting post. post_id=\"{post_id}\"".format(post_id=post_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  (post, vote) = post_service.get_post(sub, aud, UUID(post_id), db)

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK",
      "post": {
        "postId": str(post.post_id),
        "title": post.title,
        "content": post.content,
        "images": post.images,
        "author": post.author_id == sub,
        "edited": post.edited,
        "writeTime": post.write_time.isoformat(),
        "schoolName": post.school.school_name,
        "views": post.views,
        "upvote": post.upvote,
        "downvote": post.downvote,
        "vote": vote.vote if vote else None,
      }
    }
  )

@router.post(
  path='/vote',
  description='Upvote a post',
)
def upvote(
  vote_request: VoteRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  log.info("Upvoting post. post_id=\"{post_id}\"".format(post_id=vote_request.post_id))

  token = authorize_jwt(jwt)
  sub = get_sub(token)
  aud = get_aud(token)

  (up, down, vote) = post_service.vote_post(sub, aud, UUID(vote_request.post_id), vote_request.vote, db)

  return JSONResponse(
    content={
      "code": 200,
      "state": "OK",
      "votes": {
        "vote": vote,
        "upvote": up,
        "downvote": down
      }
    }
  )
