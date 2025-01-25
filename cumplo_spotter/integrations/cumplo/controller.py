from concurrent.futures import ThreadPoolExecutor, as_completed
from logging import getLogger

from cachetools import TTLCache, cached
from cumplo_common.models import FundingRequest

from cumplo_spotter.integrations.cumplo.api_global import CumploGlobalAPI, GlobalFundingRequest
from cumplo_spotter.models.cumplo import CumploFundingRequest
from cumplo_spotter.utils.constants import CACHE_MAXSIZE, CUMPLO_CACHE_TTL

logger = getLogger(__name__)
cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CUMPLO_CACHE_TTL)


@cached(cache=cache)
def get_available_funding_requests() -> list[FundingRequest]:
    """
    Query the Cumplo's GraphQL API and returns a list of available funding requests.

    Returns:
        list[FundingRequest]: List of available funding requests

    """
    logger.info("Getting funding requests from Cumplo API")

    funding_requests = []
    global_funding_requests = CumploGlobalAPI.get_funding_requests(ignore_completed=True)
    logger.info(f"Found {len(global_funding_requests)} existing funding requests")

    with ThreadPoolExecutor(max_workers=25) as executor:
        funding_request_by_future = {
            executor.submit(_get_funding_request_details, global_funding_request): global_funding_request
            for global_funding_request in global_funding_requests
        }
        for future in as_completed(funding_request_by_future):
            global_funding_request = funding_request_by_future[future]
            details, simulation = future.result()

            data = {**details, **global_funding_request.model_dump(), "simulation": simulation}
            funding_request = CumploFundingRequest.model_validate(data)
            funding_request.borrower.id = global_funding_request.id_borrower

            if not funding_request.is_completed and funding_request.maximum_investment:
                funding_requests.append(funding_request.export())

    logger.info(f"Got {len(funding_requests)} funding requests")
    return funding_requests


def _get_funding_request_details(funding_request: GlobalFundingRequest) -> tuple[dict, dict]:
    """Request the details of a given funding request."""
    details = CumploGlobalAPI.get_funding_request(funding_request.id)
    simulation = CumploGlobalAPI.simulate_funding_request(funding_request, details["fecha_vencimiento"])
    return details, simulation
