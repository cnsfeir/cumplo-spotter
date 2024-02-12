# pylint: disable=no-member

from logging import getLogger

from cumplo_common.models.filter_configuration import FilterConfiguration
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.models.user import User

from cumplo_spotter.integrations import cumplo
from cumplo_spotter.models.filter import (
    DicomFilter,
    MaximumAverageDaysDelinquentFilter,
    MaximumDurationFilter,
    MinimumAmountRequestedFilter,
    MinimumCreditsRequestedFilter,
    MinimumDurationFilter,
    MinimumIRRFilter,
    MinimumMonthlyProfitFilter,
    MinimumPaidInTimeFilter,
    MinimumScoreFilter,
)

logger = getLogger(__name__)


def get_available() -> list[FundingRequest]:
    """
    Gets a list of available funding requests sorted by monthly profit rate

    Returns:
        list[dict]: List of available funding requests
    """
    funding_requests = cumplo.get_available_funding_requests()
    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    return funding_requests


def get_promising(user: User) -> list[FundingRequest]:
    """
    Gets a list of promising funding requests based on the user's configuration sorted by monthly profit rate

    Args:
        user (User): User to get the configuration from

    Returns:
        list[FundingRequest]: List of promising funding requests
    """
    funding_requests = cumplo.get_available_funding_requests()

    promising_requests = set()
    for configuration in user.filters.values():
        promising_requests.update(filter_(funding_requests, configuration))

    return sorted(list(promising_requests), key=lambda x: x.monthly_profit_rate, reverse=True)


def filter_(funding_requests: list[FundingRequest], configuration: FilterConfiguration) -> list[FundingRequest]:
    """
    Filters a list of funding requests based on the user's filter

    Args:
        funding_requests (list[FundingRequest]): List of funding requests
        configuration (FilterConfiguration): User's filter

    Returns:
        list[FundingRequest]: Filtered funding requests
    """
    filters = [
        MinimumScoreFilter(configuration),
        MinimumIRRFilter(configuration),
        MinimumMonthlyProfitFilter(configuration),
        DicomFilter(configuration),
        MinimumDurationFilter(configuration),
        MaximumDurationFilter(configuration),
        MinimumPaidInTimeFilter(configuration),
        MinimumAmountRequestedFilter(configuration),
        MinimumCreditsRequestedFilter(configuration),
        MaximumAverageDaysDelinquentFilter(configuration),
    ]

    logger.info(f"Applying {len(filters)} filters to {len(funding_requests)} funding requests")
    funding_requests = list(filter(lambda x: all(f.apply(x) for f in filters), funding_requests))

    logger.info(f"Got {len(funding_requests)} funding requests after applying filters")
    return funding_requests
