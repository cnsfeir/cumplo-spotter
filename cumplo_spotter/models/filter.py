from abc import ABC, abstractmethod
from logging import getLogger
from typing import final

from cumplo_common.models.filter_configuration import FilterConfiguration
from cumplo_common.models.funding_request import FundingRequest

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
            logger.info(f"Funding request {funding_request.id} filtered out by {self.__class__.__name__}")
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


class DebtorDicomFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose debtor has DICOM."""
        if self.configuration.debtor and self.configuration.debtor.ignore_dicom:
            return True

        if not funding_request.debtors:
            return True

        return not any(debtor.dicom for debtor in funding_request.debtors)


class BorrowerDicomFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose borrower has DICOM."""
        if self.configuration.borrower and self.configuration.borrower.ignore_dicom:
            return True

        return not funding_request.borrower.dicom


class BorrowerMinimumRequestedCreditsFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose borrower hasn't requested the minimum amount of credits."""
        if not self.configuration.borrower or not self.configuration.borrower.minimum_requested_credits:
            return True

        total_requests = funding_request.borrower.portfolio.total_requests
        return total_requests >= self.configuration.borrower.minimum_requested_credits


class DebtorMinimumRequestedCreditsFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose at least one debtor hasn't requested the minimum amount of credits."""
        if not self.configuration.debtor or not self.configuration.debtor.minimum_requested_credits:
            return True

        if not funding_request.debtors:
            return True

        return any(
            debtor.portfolio.total_requests >= self.configuration.debtor.minimum_requested_credits
            for debtor in funding_request.debtors
        )


class BorrowerMinimumRequestedAmountFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose borrower hasn't received the minimum amount of money."""
        if not self.configuration.borrower or not self.configuration.borrower.minimum_requested_amount:
            return True

        total_amount = funding_request.borrower.portfolio.total_amount
        return total_amount >= self.configuration.borrower.minimum_requested_amount


class BorrowerMaximumAverageDaysDelinquentFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the funding requests whose borrower has an average delinquent days higher than the maximum."""
        if not self.configuration.borrower or not self.configuration.borrower.maximum_average_days_delinquent:
            return True

        if average_days_delinquent := funding_request.borrower.average_days_delinquent:
            return average_days_delinquent <= self.configuration.borrower.maximum_average_days_delinquent

        return True


class BorrowerMinimumPaidInTimeFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the requests whose borrower doesn't have the minimum percentage of requests paid in time."""
        if not self.configuration.borrower or not self.configuration.borrower.minimum_paid_in_time_percentage:
            return True

        if not funding_request.borrower.portfolio.total_requests:
            return True

        if paid_in_time_percentage := funding_request.borrower.portfolio.paid_in_time:
            return paid_in_time_percentage >= self.configuration.borrower.minimum_paid_in_time_percentage

        return True


class DebtorMinimumPaidInTimeFilter(Filter):
    def _apply(self, funding_request: FundingRequest) -> bool:
        """Filter out the requests whose debtor doesn't have the minimum percentage of funding requests paid in time."""
        if not self.configuration.debtor or not self.configuration.debtor.minimum_paid_in_time_percentage:
            return True

        if not funding_request.debtors:
            return True

        return any(
            debtor.portfolio.paid_in_time >= self.configuration.debtor.minimum_paid_in_time_percentage
            for debtor in funding_request.debtors
            if debtor.portfolio.paid_in_time is not None
        )
