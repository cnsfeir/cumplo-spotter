from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, as_completed, wait
from logging import getLogger

from cachetools import TTLCache, cached
from cumplo_common.models.funding_request import FundingRequest

from cumplo_spotter.integrations.cumplo.api_global import CumploGlobalAPI
from cumplo_spotter.integrations.cumplo.api_graphql import CumploGraphQLAPI
from cumplo_spotter.integrations.cumplo.api_html import CumploHTMLAPI
from cumplo_spotter.models.cumplo import CumploFundingRequest
from cumplo_spotter.utils.constants import CACHE_MAXSIZE, CACHE_TTL

logger = getLogger(__name__)
cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)


@cached(cache=cache)
def get_available_funding_requests() -> list[FundingRequest]:
    """
    Query the Cumplo's GraphQL API and returns a list of available funding requests.

    Returns:
        list[FundingRequest]: List of available funding requests

    """
    logger.info("Getting funding requests from Cumplo API")

    funding_requests = []
    raw_funding_requests = CumploGraphQLAPI.get_funding_requests()
    logger.info(f"Found {len(raw_funding_requests)} existing funding requests")

    with ThreadPoolExecutor(max_workers=20) as executor:
        funding_request_by_future = {
            executor.submit(_get_funding_request_details, raw_funding_request["operacion"]["id"]): raw_funding_request
            for raw_funding_request in raw_funding_requests
        }
        for future in as_completed(funding_request_by_future):
            raw_funding_request = funding_request_by_future[future]
            average_days_delinquent, simulation, details = future.result()

            data = {**details, **raw_funding_request["operacion"], "simulation": simulation}
            funding_request = CumploFundingRequest.model_validate(data)
            funding_request.borrower.average_days_delinquent = average_days_delinquent
            funding_request.borrower.id = raw_funding_request["empresa"]["id"]

            if not funding_request.is_completed and funding_request.maximum_investment:
                funding_requests.append(funding_request.export())

    logger.info(f"Got {len(funding_requests)} funding requests")
    return funding_requests


def _get_funding_request_details(id_funding_request: int) -> tuple[int | None, dict, dict]:
    """Request the details of a given funding request."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        attribute_by_future = {
            executor.submit(CumploHTMLAPI.get_average_days_delinquent, id_funding_request): "average_days_delinquent",
            executor.submit(CumploGlobalAPI.simulate_funding_request, id_funding_request): "simulation",
            executor.submit(CumploGlobalAPI.get_funding_request, id_funding_request): "details",
        }
        requests, _ = wait(attribute_by_future, return_when=ALL_COMPLETED)
        results = {attribute_by_future[future]: future.result() for future in requests}
        return results["average_days_delinquent"], results["simulation"], results["details"]
