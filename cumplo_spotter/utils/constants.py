import os

from dotenv import load_dotenv

load_dotenv()

AVERAGE_DAYS_DELINQUENT_SELECTOR = "div.loan-view-item span:nth-of-type(3)"
CONFIGURATIONS_COLLECTION = os.getenv("CONFIGURATIONS_COLLECTION", "configurations")
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")
CUMPLO_BASE_URL = os.getenv("CUMPLO_BASE_URL", "https://secure.cumplo.cl")
CUMPLO_HERALD_QUEUE = os.getenv("CUMPLO_HERALD_QUEUE", "")
CUMPLO_HERALD_URL = os.getenv("CUMPLO_HERALD_URL", "")
CUMPLO_REST_API = os.getenv("CUMPLO_REST_API", "")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
CUMPLO_SPOTTER_URL = os.getenv("CUMPLO_SPOTTER_URL", "")
CUMPLO_SPOTTER_QUEUE = os.getenv("CUMPLO_SPOTTER_QUEUE", "")
DEFAULT_FILTER_NOTIFIED = bool(os.getenv("DEFAULT_FILTER_NOTIFIED"))
DEFAULT_EXPIRATION_MINUTES = int(os.getenv("DEFAULT_EXPIRATION_MINUTES", "30"))
DICOM_STRINGS = ["CON DICOM", "CONDICOM", "PRESENTA DICOM"]
IRS_SECTOR_SELECTOR = "strong.loan-view-primary-color + span"
IS_TESTING = bool(os.getenv("IS_TESTING"))
LOCATION = os.getenv("LOCATION", "us-central1")
LOG_FORMAT = "\n [%(levelname)s] %(message)s"
NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
PAID_FUNDING_REQUESTS_COUNT_SELECTOR = "div.loan-view-item span:nth-of-type(1)"
PAID_IN_TIME_PERCENTAGE_SELECTOR = "div.loan-view-item span:nth-of-type(5)"
PROJECT_ID = os.getenv("PROJECT_ID")
SUPPORTING_DOCUMENTS_XPATH = "//div[@class='loan-view-documents-section']//img/parent::span/following-sibling::span"
TOTAL_AMOUNT_REQUESTED_SELECTOR = "div.loan-view-page-subtitle + p"
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
