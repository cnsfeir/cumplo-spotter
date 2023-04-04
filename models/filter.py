from abc import ABCMeta, abstractmethod
from logging import getLogger

from dotenv import load_dotenv

from integrations.firestore import firestore_client
from models.configuration import Configuration
from models.funding_request import FundingRequest
from models.request_duration import DurationUnit
from models.user import User

load_dotenv()
logger = getLogger(__name__)


class Filter(metaclass=ABCMeta):
    @abstractmethod
    def apply(self, _funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that don't meet the criteria.
        """


class AvailableFilter(Filter):
    def __init__(self, user: User) -> None:
        self.user = user

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that are already completed.
        """
        if not funding_request.is_completed:
            return True

        if self.user.notifications.get(funding_request.id):
            firestore_client.delete_notification(funding_request.id)

        return False


class NotificationFilter(Filter):
    def __init__(self, configuration: Configuration, user: User) -> None:
        self.configuration = configuration
        self.user = user

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have already been notified
        """
        if not self.configuration.filter_notified:
            return True

        notification = self.user.notifications.get(funding_request.id)

        if not notification or notification.has_expired(self.configuration.notification_expiration):
            firestore_client.set_notification_date(self.user.id, funding_request.id)
            return True

        return False


class ScoreFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a score lower than the minimum.
        """
        if self.configuration.score is None:
            return True

        return funding_request.score >= self.configuration.score


class MonthlyProfitFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a monthly profit lower than the minimum.
        """
        if self.configuration.monthly_profit_rate is None:
            return True

        return funding_request.monthly_profit_rate >= self.configuration.monthly_profit_rate


class IRRFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have an IRR lower than the minimum.
        """
        if self.configuration.irr is None:
            return True

        return funding_request.irr >= self.configuration.irr


class DurationFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a duration lower than the minimum.
        """
        # TODO: Figure out how to compare montlhy profit rate of funding requests with single and monthly payments
        if funding_request.duration.unit != DurationUnit.DAY:
            return False

        if self.configuration.duration is None:
            return True

        return funding_request.duration.value >= self.configuration.duration


class DicomFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a Dicom
        """
        if not self.configuration.filter_dicom:
            return True

        return not funding_request.borrower.dicom


class CreditsRequestedFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower hasn't requested the minimum amount of credits.
        """
        if not self.configuration.credits_requested:
            return True

        return funding_request.borrower.funding_requests_count >= self.configuration.credits_requested


class AmountRequestedFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower hasn't received the minimum amount of money.
        """
        if not self.configuration.amount_requested:
            return True

        return funding_request.borrower.total_amount_requested >= self.configuration.amount_requested


class AverageDaysDelinquentFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower has an average delinquent days higher than the maximum.
        """
        if not self.configuration.average_days_delinquent:
            return True

        if average_days_delinquent := funding_request.borrower.average_days_delinquent:
            return average_days_delinquent <= self.configuration.average_days_delinquent

        return True


class PaidInTimeFilter(Filter):
    def __init__(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests whose borrower doesn't have the minimum percentage
        of funding requests paid in time.
        """
        if not self.configuration.paid_in_time_percentage:
            return True

        if not funding_request.borrower.funding_requests_count:
            return True

        if paid_in_time_percentage := funding_request.borrower.paid_in_time_percentage:
            return paid_in_time_percentage >= self.configuration.paid_in_time_percentage

        return True
