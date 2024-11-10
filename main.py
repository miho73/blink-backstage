import logging

from fastapi import FastAPI

from routers.authentication import google_auth_router, authorization, password_auth_router
from routers.error_handler import add_error_handler
from routers.user import user

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

add_error_handler(app)

log.info("Server ready to go")
