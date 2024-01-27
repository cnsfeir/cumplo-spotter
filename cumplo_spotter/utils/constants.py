import os

from dotenv import load_dotenv

load_dotenv()

# Basics
LOCATION = os.getenv("LOCATION", "us-central1")
PROJECT_ID = os.getenv("PROJECT_ID")
LOG_FORMAT = "\n%(levelname)s: %(message)s"
IS_TESTING = bool(os.getenv("IS_TESTING"))

# Topics
AVAILABLE_FUNDING_REQUESTS_TOPIC = os.getenv("AVAILABLE_FUNDING_REQUESTS_TOPIC", "available-funding-requests")
PROMISING_FUNDING_REQUESTS_TOPIC = os.getenv("PROMISING_FUNDING_REQUESTS_TOPIC", "promising-funding-requests")

# Selectors
SUPPORTING_DOCUMENTS_XPATH = "//div[@class='loan-view-documents-section']//img/parent::span/following-sibling::span"
AVERAGE_DAYS_DELINQUENT_SELECTOR = "div.loan-view-item span:nth-of-type(3)"
IRS_SECTOR_SELECTOR = "strong.loan-view-primary-color + span"
PAID_FUNDING_REQUESTS_COUNT_SELECTOR = "div.loan-view-item span:nth-of-type(1)"
PAID_IN_TIME_PERCENTAGE_SELECTOR = "div.loan-view-item span:nth-of-type(5)"
TOTAL_AMOUNT_REQUESTED_SELECTOR = "div.loan-view-page-subtitle + p"
DICOM_STRINGS = ["CON DICOM", "CONDICOM", "PRESENTA DICOM"]

# Firestore Collections
CONFIGURATIONS_COLLECTION = os.getenv("CONFIGURATIONS_COLLECTION", "configurations")
NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")
CUMPLO_BASE_URL = os.getenv("CUMPLO_BASE_URL", "https://secure.cumplo.cl")
CUMPLO_REST_API = os.getenv("CUMPLO_REST_API", "")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")

# Defaults
DEFAULT_FILTER_NOTIFIED = bool(os.getenv("DEFAULT_FILTER_NOTIFIED"))
DEFAULT_EXPIRATION_MINUTES = int(os.getenv("DEFAULT_EXPIRATION_MINUTES", "30"))
