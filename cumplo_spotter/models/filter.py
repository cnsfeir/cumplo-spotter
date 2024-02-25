from abc import ABCMeta, abstractmethod

from cumplo_common.models.filter_configuration import FilterConfiguration
from cumplo_common.models.funding_request import FundingRequest

from cumplo_spotter.models.cumplo.request_duration import DurationUnit


class Filter(metaclass=ABCMeta):
    def __init__(self, configuration: FilterConfiguration) -> None:
        self.configuration = configuration

    @abstractmethod
    def apply(self, funding_request: FundingRequest) -> bool:  # pylint: disable=missing-function-docstring
        ...


class CreditTypeFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that don't have the target credit types.
        """
        if self.configuration.target_credit_types is None:
            return True

        return funding_request.credit_type in self.configuration.target_credit_types


class MinimumInvestmentFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a available investment lower than the minimum.
        """
        if self.configuration.minimum_investment_amount is None:
            return True

        return funding_request.maximum_investment >= self.configuration.minimum_investment_amount


class MinimumScoreFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a score lower than the minimum.
        """
        if self.configuration.minimum_score is None:
            return True

        return funding_request.score >= self.configuration.minimum_score


class MinimumMonthlyProfitFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a monthly profit lower than the minimum.
        """
        if self.configuration.minimum_monthly_profit_rate is None:
            return True

        return funding_request.monthly_profit_rate >= self.configuration.minimum_monthly_profit_rate


class MinimumIRRFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have an IRR lower than the minimum.
        """
        if self.configuration.minimum_irr is None:
            return True

        return funding_request.irr >= self.configuration.minimum_irr


class MinimumDurationFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a duration lower than the minimum.
        """
        if self.configuration.minimum_duration is None:
            return True

        duration = (
            funding_request.duration.value
            if funding_request.duration.unit == DurationUnit.DAY
            else funding_request.duration.value * 30
        )
        return duration >= self.configuration.minimum_duration


class MaximumDurationFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a duration greater than the maximum.
        """
        if self.configuration.maximum_duration is None:
            return True

        duration = (
            funding_request.duration.value
            if funding_request.duration.unit == DurationUnit.DAY
            else funding_request.duration.value * 30
        )
        return duration <= self.configuration.maximum_duration


class DicomFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a Dicom
        """
        if self.configuration.ignore_dicom:
            return True

        return not funding_request.borrower.dicom


class MinimumCreditsRequestedFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower hasn't requested the minimum amount of credits.
        """
        if not self.configuration.minimum_requested_credits:
            return True

        return funding_request.borrower.portfolio.total_requests >= self.configuration.minimum_requested_credits


class MinimumAmountRequestedFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower hasn't received the minimum amount of money.
        """
        if not self.configuration.minimum_requested_amount:
            return True

        return funding_request.borrower.portfolio.total_amount >= self.configuration.minimum_requested_amount


class MaximumAverageDaysDelinquentFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower has an average delinquent days higher than the maximum.
        """
        if not self.configuration.maximum_average_days_delinquent:
            return True

        if average_days_delinquent := funding_request.borrower.average_days_delinquent:
            return average_days_delinquent <= self.configuration.maximum_average_days_delinquent

        return True


class MinimumPaidInTimeFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower doesn't have the minimum percentage
        of funding requests paid in time.
        """
        if not self.configuration.minimum_paid_in_time_percentage:
            return True

        if not funding_request.borrower.portfolio.total_requests:
            return True

        if paid_in_time_percentage := funding_request.borrower.portfolio.paid_in_time:
            return paid_in_time_percentage >= self.configuration.minimum_paid_in_time_percentage

        return True
