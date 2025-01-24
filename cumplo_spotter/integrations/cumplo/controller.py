from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, as_completed, wait
from logging import getLogger

from cachetools import TTLCache, cached
from cumplo_common.models.funding_request import FundingRequest

from cumplo_spotter.integrations.cumplo.api_global import CumploGlobalAPI, GlobalFundingRequest
from cumplo_spotter.integrations.cumplo.api_html import CumploHTMLAPI
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

    with ThreadPoolExecutor(max_workers=20) as executor:
        funding_request_by_future = {
            executor.submit(_get_funding_request_details, global_funding_request): global_funding_request
            for global_funding_request in global_funding_requests
        }
        for future in as_completed(funding_request_by_future):
            global_funding_request = funding_request_by_future[future]
            average_days_delinquent, simulation, details = future.result()

            data = {**details, **global_funding_request.model_dump(), "simulation": simulation}
            funding_request = CumploFundingRequest.model_validate(data)
            funding_request.borrower.average_days_delinquent = average_days_delinquent
            funding_request.borrower.id = global_funding_request.id_borrower

            if not funding_request.is_completed and funding_request.maximum_investment:
                funding_requests.append(funding_request.export())

    logger.info(f"Got {len(funding_requests)} funding requests")
    return funding_requests


def _get_funding_request_details(funding_request: GlobalFundingRequest) -> tuple[int | None, dict, dict]:
    """Request the details of a given funding request."""
    with ThreadPoolExecutor(max_workers=2) as executor:
        attribute_by_future = {
            executor.submit(CumploHTMLAPI.get_average_days_delinquent, funding_request.id): "average_days_delinquent",
            executor.submit(CumploGlobalAPI.get_funding_request, funding_request.id): "details",
        }
        requests, _ = wait(attribute_by_future, return_when=ALL_COMPLETED)
        results = {attribute_by_future[future]: future.result() for future in requests}

    details = results["details"]
    simulation = CumploGlobalAPI.simulate_funding_request(funding_request, details["fecha_vencimiento"])
    return results["average_days_delinquent"], simulation, details
