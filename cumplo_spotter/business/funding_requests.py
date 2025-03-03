from logging import getLogger

from cumplo_common.models import FilterConfiguration, FundingRequest, User

from cumplo_spotter.integrations import cumplo
from cumplo_spotter.models.filter import (
    CreditTypeFilter,
    DicomFilter,
    MaximumDurationFilter,
    MinimumAmountFilter,
    MinimumDurationFilter,
    MinimumInvestmentFilter,
    MinimumIRRFilter,
    MinimumMonthlyProfitFilter,
    MinimumScoreFilter,
    PortfolioFilter,
)

logger = getLogger(__name__)


def get_available() -> list[FundingRequest]:
    """
    Get a list of available funding requests sorted by monthly profit rate.

    Returns:
        list[dict]: List of available funding requests

    """
    funding_requests = cumplo.get_available_funding_requests()
    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    return funding_requests


def get_promising(user: User) -> list[FundingRequest]:
    """
    Get a list of promising funding requests based on the user's configuration sorted by monthly profit rate.

    Args:
        user (User): User to get the configuration from

    Returns:
        list[FundingRequest]: List of promising funding requests

    """
    funding_requests = cumplo.get_available_funding_requests()

    promising_requests = set()
    for configuration in user.filters.values():
        promising_requests.update(filter_(funding_requests, configuration))

    return sorted(promising_requests, key=lambda x: x.monthly_profit_rate, reverse=True)


def filter_(funding_requests: list[FundingRequest], configuration: FilterConfiguration) -> list[FundingRequest]:
    """
    Filter a list of funding requests based on the user's filter.

    Args:
        funding_requests (list[FundingRequest]): List of funding requests
        configuration (FilterConfiguration): User's filter

    Returns:
        list[FundingRequest]: Filtered funding requests

    """
    filters = [
        MinimumAmountFilter(configuration),
        CreditTypeFilter(configuration),
        MinimumInvestmentFilter(configuration),
        MinimumScoreFilter(configuration),
        MinimumIRRFilter(configuration),
        MinimumMonthlyProfitFilter(configuration),
        DicomFilter(configuration),
        MinimumDurationFilter(configuration),
        MaximumDurationFilter(configuration),
        PortfolioFilter(configuration),
    ]

    logger.info(f"Applying {len(filters)} filters to {len(funding_requests)} funding requests")
    funding_requests = list(filter(lambda x: all(f.apply(x) for f in filters), funding_requests))

    logger.info(f"Got {len(funding_requests)} funding requests after applying filter {configuration.name}")
    return funding_requests
