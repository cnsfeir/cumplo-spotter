from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from cumplo_common.dependencies import authenticate, is_admin
from cumplo_common.middlewares import PubSubMiddleware
from fastapi import Depends, FastAPI

from cumplo_spotter.routers import funding_requests
from cumplo_spotter.utils.constants import IS_TESTING, LOG_FORMAT

# NOTE: Mute noisy third-party loggers
for module in ("google", "urllib3", "werkzeug"):
    getLogger(module).setLevel(CRITICAL)

if IS_TESTING:
    basicConfig(level=DEBUG, format=LOG_FORMAT)
else:
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=DEBUG)


app = FastAPI(dependencies=[Depends(authenticate)])
app.add_middleware(PubSubMiddleware)

app.include_router(funding_requests.public.router)
app.include_router(funding_requests.private.router, dependencies=[Depends(is_admin)])
