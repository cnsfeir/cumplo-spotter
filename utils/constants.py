import os

AVERAGE_DAYS_DELINQUENT_SELECTOR = "div.loan-view-item span:nth-of-type(3)"
CONFIGURATIONS_COLLECTION = os.getenv("CONFIGURATIONS_COLLECTION", "configurations")
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")
CUMPLO_BASE_URL = os.getenv("CUMPLO_BASE_URL", "https://secure.cumplo.cl")
CUMPLO_FUNDING_REQUESTS_API = os.getenv("CUMPLO_FUNDING_REQUESTS_API", "")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
DEFAULT_FILTER_NOTIFIED = bool(os.getenv("DEFAULT_FILTER_NOTIFIED"))
DEFAULT_NOTIFICATION_EXPIRATION = int(os.getenv("DEFAULT_NOTIFICATION_EXPIRATION", "2"))
DICOM_STRINGS = ["CON DICOM", "CONDICOM", "PRESENTA DICOM"]
IS_TESTING = bool(os.getenv("IS_TESTING"))
LOG_FORMAT = "\n [%(levelname)s] %(message)s"
MAX_CONFIGURATIONS = int(os.getenv("MAX_CONFIGURATIONS", "3"))
NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
PAID_FUNDING_REQUESTS_COUNT_SELECTOR = "div.loan-view-item span:nth-of-type(1)"
PAID_IN_TIME_PERCENTAGE_SELECTOR = "div.loan-view-item span:nth-of-type(5)"
PROJECT_ID = os.getenv("PROJECT_ID", "")
SANTIAGO_TIMEZONE = "America/Santiago"
SUPPORTING_DOCUMENTS_XPATH = "//div[@class='loan-view-documents-section']//img/parent::span/following-sibling::span"
TOTAL_AMOUNT_REQUESTED_SELECTOR = "div.loan-view-page-subtitle + p"
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
