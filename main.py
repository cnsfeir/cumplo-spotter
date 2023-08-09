from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from cumplo_common.dependencies.authentication import authenticate
from cumplo_common.dependencies.authorization import is_admin
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import funding_requests
from utils.constants import IS_TESTING, LOG_FORMAT

if not IS_TESTING:
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=DEBUG)

basicConfig(level=DEBUG, format=LOG_FORMAT)
logger = getLogger(__name__)

getLogger("google").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)
getLogger("asyncio").setLevel(CRITICAL)
getLogger("fsevents").setLevel(CRITICAL)
getLogger("werkzeug").setLevel(CRITICAL)
getLogger("charset_normalizer").setLevel(CRITICAL)

app = FastAPI(dependencies=[Depends(authenticate)])


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(funding_requests.router)
app.include_router(funding_requests.internal, dependencies=[Depends(is_admin)])
