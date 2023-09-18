# pylint: disable=no-member


from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from cumplo_common.dependencies.authentication import authenticate
from cumplo_common.dependencies.authorization import is_admin
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cumplo_spotter.utils.constants import IS_TESTING, LOG_FORMAT
from routers import funding_requests

basicConfig(level=DEBUG, format=LOG_FORMAT)
logger = getLogger(__name__)

# NOTE: Mute noisy third-party loggers
for module in ("google", "urllib3", "asyncio", "werkzeug"):
    getLogger(module).setLevel(CRITICAL)

if not IS_TESTING:
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=DEBUG)


app = FastAPI(dependencies=[Depends(authenticate)])

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(funding_requests.public.router)
app.include_router(funding_requests.private.router, dependencies=[Depends(is_admin)])
