import logging

from fastapi import APIRouter
from fastapi.params import Security, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub
from core.social import post_service
from database.database import create_connection
from models.request_models.social.post_request import UploadPostRequest

log = logging.getLogger(__name__)

router = APIRouter(
  prefix='/api/social',
  tags=['school']
)


@router.post('/post')
async def post(
  body: UploadPostRequest,
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection),
):
  log.info("Posting new post. title=\"{title}\", content=\"{content}\"".format(title=body.title, content=body.content))

  token = authorize_jwt(jwt)
  sub = get_sub(token)

  post_uuid = post_service.upload_post(sub, body, db)
  db.commit()

  return JSONResponse(
    content={
      "code": 201,
      "state": "CREATED",
      "message": str(post_uuid)
    }
  )
