import logging

from fastapi import FastAPI

from core.authentication.aaguid import load_aaguid
from routers.authentication import google_auth_api, authorization_api, password_auth_api, passkey_auth_api
from routers.error_handler import add_error_handler
from routers.school import school_access_api, neis_school_api, neis_cache_api, common_school_api
from routers.school_verification import sv_request_api, sv_access_api, sv_evaluation_api, \
  sv_user_request_api
from routers.social import post_request_api, board_request_api, comment_request_api
from routers.user import user_info_api, user_preference_api, personal_social_api, user_access_api

app = FastAPI(
  docs_url="/api/docs",
  openapi_url="/api/openapi.json",
  redoc_url="/api/redoc",
)

log = logging.getLogger(__name__)

log.info("Starting server")

load_aaguid()

####################################################
app.include_router(authorization_api.router)
app.include_router(google_auth_api.router)
app.include_router(password_auth_api.router)
app.include_router(passkey_auth_api.router)
####################################################
app.include_router(user_info_api.router)
app.include_router(user_preference_api.router)
app.include_router(personal_social_api.router)
app.include_router(user_access_api.router)
####################################################
app.include_router(sv_request_api.router)
app.include_router(sv_access_api.router)
app.include_router(sv_evaluation_api.router)
app.include_router(sv_user_request_api.router)
####################################################
app.include_router(school_access_api.router)
app.include_router(neis_school_api.router)
app.include_router(neis_cache_api.router)
app.include_router(common_school_api.router)
####################################################
app.include_router(post_request_api.router)
app.include_router(board_request_api.router)
app.include_router(comment_request_api.router)
####################################################
add_error_handler(app)

log.info("Server ready to go")
