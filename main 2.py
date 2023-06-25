import os
from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

if not (IS_TESTING := bool(os.getenv("IS_TESTING"))):
    client = google.cloud.logging.Client()
    client.setup_logging()

FORMAT = "\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s" if IS_TESTING else "\n [%(levelname)s] %(message)s"
basicConfig(level=DEBUG, format=FORMAT)
logger = getLogger(__name__)

getLogger("google").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)
getLogger("asyncio").setLevel(CRITICAL)
getLogger("fsevents").setLevel(CRITICAL)
getLogger("werkzeug").setLevel(CRITICAL)
getLogger("charset_normalizer").setLevel(CRITICAL)

app = FastAPI()


@app.exception_handler(HTTPException)
async def handler(_request: Request, exception: HTTPException) -> JSONResponse:
    """
    Manage HTTPExceptions
    """
    logger.warning(exception.detail)
    return JSONResponse(content={"error": exception.detail}, status_code=exception.status_code)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(a.router, dependencies=[Depends(check_auth_request)], responses=error_descriptions)
