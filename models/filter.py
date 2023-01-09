from abc import ABCMeta, abstractmethod
from logging import getLogger

from dotenv import load_dotenv

from integrations.firestore import firestore_client
from models.funding_request import FundingRequest
from models.notification import Notification
from models.request_duration import DurationUnit

load_dotenv()
logger = getLogger(__name__)


class Filter(metaclass=ABCMeta):
    @abstractmethod
    def apply(self, _funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that don't meet the criteria.
        """


class AvailableFilter(Filter):
    def __init__(self, notifications: dict[int, Notification]) -> None:
        self.notifications = notifications

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that are already completed.
        """
        if is_completed := funding_request.is_completed:
            if self.notifications.get(funding_request.id):
                firestore_client.delete_notification(funding_request.id)

        return not is_completed


class ScoreFilter(Filter):
    def __init__(self, min_score: float) -> None:
        self.min_score = min_score

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a score lower than the minimum.
        """
        return funding_request.score >= self.min_score


class MonthlyProfitFilter(Filter):
    def __init__(self, min_profit_rate: float) -> None:
        self.min_profit_rate = min_profit_rate

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a monthly profit lower than the minimum.
        """
        return funding_request.monthly_profit_rate >= self.min_profit_rate


class DurationUnitFilter(Filter):
    def __init__(self, duration_unit: DurationUnit) -> None:
        self.duration_unit = duration_unit

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a duration unit different than month.
        """
        return funding_request.duration.unit != self.duration_unit


class DicomFilter(Filter):
    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a Dicom
        """
        if credit_history := funding_request.borrower.history:
            return not credit_history.dicom
        return True


class NotificationFilter(Filter):
    def __init__(self, notifications: dict[int, Notification]) -> None:
        self.notifications = notifications

    def apply(self, funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have already been notified
        """
        if notification := self.notifications.get(funding_request.id):
            if not notification.has_expired:
                return False

        firestore_client.set_notification_date(funding_request.id)
        return True
