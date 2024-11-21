import logging

from fastapi import FastAPI

from routers.authentication import google_auth_api, authorization_api, password_auth_api
from routers.error_handler import add_error_handler
from routers.school import school_access_api, neis_school_api
from routers.school_verification import sv_user_api, sv_request_api, sv_access_api, sv_evaluation_api, \
  sv_evaluation_service
from routers.user import user_info_api

app = FastAPI(
  docs_url="/api/docs",
  openapi_url="/api/openapi.json",
  redoc_url="/api/redoc",
)

log = logging.getLogger(__name__)

log.info("Starting server")

####################################################
app.include_router(authorization_api.router)
app.include_router(google_auth_api.router)
app.include_router(password_auth_api.router)
####################################################
app.include_router(user_info_api.router)
####################################################
app.include_router(sv_user_api.router)
app.include_router(sv_request_api.router)
app.include_router(sv_access_api.router)
app.include_router(sv_evaluation_api.router)
app.include_router(sv_evaluation_service.router)
####################################################
app.include_router(school_access_api.router)
app.include_router(neis_school_api.router)
####################################################
add_error_handler(app)

log.info("Server ready to go")
