from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from middlewares.authentication import authenticate
from routers import configurations, funding_requests
from utils.constants import IS_TESTING, LOG_FORMAT

if not IS_TESTING:
    client = google.cloud.logging.Client()
    client.setup_logging()

basicConfig(level=DEBUG, format=LOG_FORMAT)
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


app.include_router(funding_requests.router, dependencies=[Depends(authenticate)])
app.include_router(funding_requests.internal, dependencies=[Depends(authenticate)])

app.include_router(configurations.router, dependencies=[Depends(authenticate)])
