import os
from abc import ABCMeta, abstractmethod
from logging import getLogger

from dotenv import load_dotenv

from integrations.firestore import firestore_client
from models.funding_request import FundingRequest
from models.request_duration import DurationUnit

load_dotenv()
logger = getLogger(__name__)

MIN_SCORE = float(os.getenv("MIN_SCORE", "3.5"))
MIN_MONTHLY_PROFIT = float(os.getenv("MIN_MONTHLY_PROFIT", "1.5"))


class Filter(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def apply(_funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that don't meet the criteria.
        """


class AvailableFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that are already completed.
        """
        if is_completed := funding_request.is_completed:
            notifications = firestore_client.get_notifications()
            if notifications.get(funding_request.id):
                firestore_client.delete_notification(funding_request.id)

        return not is_completed


class ScoreFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a score lower than the minimum.
        """
        return funding_request.score >= MIN_SCORE


class MonthlyProfitFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a monthly profit lower than the minimum.
        """
        return funding_request.monthly_profit_rate >= MIN_MONTHLY_PROFIT


class DurationUnitFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a duration unit different than month.
        """
        return funding_request.duration.unit != DurationUnit.MONTH


class DicomFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have a Dicom
        """
        if credit_history := funding_request.borrower.history:
            return not credit_history.dicom
        return True


class NotificationFilter(Filter):
    @staticmethod
    def apply(funding_request: FundingRequest) -> bool:
        """
        Filters out the funding requests that have already been notified
        """
        notifications = firestore_client.get_notifications()
        if notification := notifications.get(funding_request.id):
            if not notification.has_expired:
                return False

        firestore_client.set_notification_date(funding_request.id)
        return True
