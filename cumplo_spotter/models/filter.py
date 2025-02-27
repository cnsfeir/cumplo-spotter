from abc import ABC, abstractmethod
from logging import getLogger
from typing import final

from cumplo_common.models import FilterConfiguration, FundingRequest

from cumplo_spotter.models.cumplo.request_duration import DurationUnit

logger = getLogger(__name__)


class Filter(ABC):
    def __init__(self, configuration: FilterConfiguration) -> None:
        self.configuration = configuration

    @abstractmethod
    def _apply(self, funding_request: FundingRequest) -> bool: ...

    @final
    def apply(self, funding_request: FundingRequest) -> bool:
        """Apply the filter to the funding request."""
        if not (result := self._apply(funding_request)):
            filter_name = f"'{self.configuration.name}' {self.__class__.__name__}"
            logger.info(f"Funding request {funding_request.id} filtered out by {filter_name}")
        return result


class CreditTypeFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that don't have the target credit types."""
        if self.configuration.target_credit_types is None:
            return True

        return funding_request.credit_type in self.configuration.target_credit_types


class MinimumInvestmentFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a available investment lower than the minimum."""
        if self.configuration.minimum_investment_amount is None:
            return True

        return funding_request.maximum_investment >= self.configuration.minimum_investment_amount


class MinimumAmountFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a available investment lower than the minimum."""
        if self.configuration.minimum_amount is None:
            return True

        return funding_request.amount >= self.configuration.minimum_amount


class MinimumScoreFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a score lower than the minimum."""
        if self.configuration.minimum_score is None:
            return True

        return funding_request.score >= self.configuration.minimum_score


class MinimumMonthlyProfitFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a monthly profit lower than the minimum."""
        if self.configuration.minimum_monthly_profit_rate is None:
            return True

        return funding_request.monthly_profit_rate >= self.configuration.minimum_monthly_profit_rate


class MinimumIRRFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have an IRR lower than the minimum."""
        if self.configuration.minimum_irr is None:
            return True

        return funding_request.irr >= self.configuration.minimum_irr


class MinimumDurationFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a duration lower than the minimum."""
        if self.configuration.minimum_duration is None:
            return True

        duration = (
            funding_request.duration.value
            if funding_request.duration.unit == DurationUnit.DAY
            else funding_request.duration.value * 30
        )
        return duration >= self.configuration.minimum_duration


class MaximumDurationFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests that have a duration greater than the maximum."""
        if self.configuration.maximum_duration is None:
            return True

        duration = (
            funding_request.duration.value
            if funding_request.duration.unit == DurationUnit.DAY
            else funding_request.duration.value * 30
        )
        return duration <= self.configuration.maximum_duration


class DicomFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose debtor has DICOM."""
        if self.configuration.ignore_dicom:
            return True

        dicoms = [debtor.dicom for debtor in funding_request.debtors] or [funding_request.borrower.dicom]
        return not any(dicoms)


class PortfolioFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        if not self.configuration.portfolio:
            return True

        portfolios = [debtor.portfolio for debtor in funding_request.debtors] + [funding_request.borrower.portfolio]

        for portfolio in portfolios:
            for filter_ in self.configuration.portfolio:
                value = portfolio.get(
                    unit=filter_.unit,
                    category=filter_.category,
                    percentage_unit=filter_.percentage_unit,
                    percentage_base=filter_.percentage_base,
                )

                if filter_.minimum is not None and value < filter_.minimum:
                    logger.info(f"Funding request {funding_request.id} filtered out by {filter_}")
                    return False

                if filter_.maximum is not None and value > filter_.maximum:
                    logger.info(f"Funding request {funding_request.id} filtered out by {filter_}")
                    return False

        return True
