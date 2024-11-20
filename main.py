import logging

from fastapi import FastAPI

from core.school_verification import process_request
from routers.authentication import google_auth_router, authorization, password_auth_router
from routers.error_handler import add_error_handler
from routers.school import school_access, neis_school
from routers.school_verification import user_verification_info, get_verified, sv_access, sv_approve
from routers.user import user, user_auth

app = FastAPI(
  docs_url="/api/docs",
  openapi_url="/api/openapi.json",
  redoc_url="/api/redoc",
)

log = logging.getLogger(__name__)

log.info("Starting server")

app.include_router(authorization.router)
app.include_router(google_auth_router.router)
app.include_router(password_auth_router.router)
app.include_router(user.router)
app.include_router(user_auth.router)
app.include_router(user_verification_info.router)
app.include_router(get_verified.router)
app.include_router(school_access.router)
app.include_router(process_request.router)
app.include_router(neis_school.router)
app.include_router(sv_access.router)
app.include_router(sv_approve.router)

add_error_handler(app)

log.info("Server ready to go")
