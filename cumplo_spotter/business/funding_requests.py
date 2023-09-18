# pylint: disable=no-member

from logging import getLogger

from cumplo_common.models.configuration import Configuration
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.models.user import User

from cumplo_spotter.integrations import cumplo
from cumplo_spotter.models.filter import (
    AmountRequestedFilter,
    AverageDaysDelinquentFilter,
    CreditsRequestedFilter,
    DicomFilter,
    DurationFilter,
    IRRFilter,
    MonthlyProfitFilter,
    PaidInTimeFilter,
    ScoreFilter,
)

logger = getLogger(__name__)


async def get_available() -> list[FundingRequest]:
    """
    Gets a list of available funding requests sorted by monthly profit rate

    Returns:
        list[dict]: List of available funding requests
    """
    funding_requests = await cumplo.get_available_funding_requests()
    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    return funding_requests


async def get_promising(user: User) -> list[FundingRequest]:
    """
    Gets a list of promising funding requests based on the user's configuration sorted by monthly profit rate

    Args:
        user (User): User to get the configuration from

    Returns:
        list[FundingRequest]: List of promising funding requests
    """
    funding_requests = await cumplo.get_available_funding_requests()

    promising_requests = set()
    for configuration in user.configurations.values():
        promising_requests.update(filter_(funding_requests, configuration))

    return sorted(list(promising_requests), key=lambda x: x.monthly_profit_rate, reverse=True)


def filter_(funding_requests: list[FundingRequest], configuration: Configuration) -> list[FundingRequest]:
    """
    Filters a list of funding requests based on the user's configuration

    Args:
        funding_requests (list[FundingRequest]): List of funding requests
        configuration (Configuration): User's configuration

    Returns:
        list[FundingRequest]: Filtered funding requests
    """
    filters = [
        ScoreFilter(configuration),
        IRRFilter(configuration),
        MonthlyProfitFilter(configuration),
        DurationFilter(configuration),
        DicomFilter(configuration),
        PaidInTimeFilter(configuration),
        AmountRequestedFilter(configuration),
        CreditsRequestedFilter(configuration),
        AverageDaysDelinquentFilter(configuration),
    ]

    logger.info(f"Applying {len(filters)} filters to {len(funding_requests)} funding requests")
    funding_requests = list(filter(lambda x: all(filter_.apply(x) for filter_ in filters), funding_requests))

    logger.info(f"Got {len(funding_requests)} funding requests after applying filters")
    return funding_requests
