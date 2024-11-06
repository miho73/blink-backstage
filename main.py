import logging

from fastapi import FastAPI

from routers.authentication import google_auth_router

app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

log = logging.getLogger(__name__)

log.info("Starting server")

app.include_router(google_auth_router.router)

log.info("Server ready to go")
