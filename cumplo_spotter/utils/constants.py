import os
from dataclasses import dataclass

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

# Markers
GOVERNMENT_TREASURY_DEBT_MARKER = [
    "NO TIENE DEUDAS CON LA TGR",
    "NO PRESENTA DEUDAS CON LA TGR",
    "NO PRESENTA DEUDA CON LA TESORERIA",
    "NO PRESENTA DEUDAS CON LA TESORERIA",
]


@dataclass
class DicomMarker:
    BOTH_TRUE = "DEUDOR Y CLIENTE CON DICOM"
    BOTH_FALSE = "DEUDOR Y CLIENTE SIN DICOM"
    DEBTOR_TRUE = "DEUDOR CON DICOM"
    BORROWER_TRUE = ("CLIENTE CON DICOM", "CIENTE CON DICOM", "SOLICITANTE CON DICOM")
    BORROWER_FALSE = "SOLICITANTE SIN DICOM"
    SINGLE_FALSE = ("SIN DICOM", "TAMPOCO PRESENTA DICOM", "NO TIENE DICOM", "DICOM NO")
    SINGLE_TRUE = ("CON DICOM", "CONDICOM", "PRESENTA DICOM")


# Firestore Collections
CONFIGURATIONS_COLLECTION = os.getenv("CONFIGURATIONS_COLLECTION", "configurations")
NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

# Cumplo
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")
CUMPLO_BASE_URL = os.getenv("CUMPLO_BASE_URL")
CUMPLO_HTML_API = os.getenv("CUMPLO_HTML_API", "")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
CUMPLO_GRAPHQL_HEADERS = {"Accept-Language": "es-CL"}
CUMPLO_GLOBAL_API = os.getenv("CUMPLO_GLOBAL_API", "")
CUMPLO_POINTS_KEY = os.getenv("CUMPLO_POINTS_KEY", "COMISION CUMPLO")
PLATFORM_FEE_KEY = os.getenv("PLATFORM_FEE_KEY", "USO DE LA PLATAFORMA")
SIMULATION_AMOUNT = int(os.getenv("SIMULATION_AMOUNT", "1000000"))

# Defaults
DEFAULT_FILTER_NOTIFIED = bool(os.getenv("DEFAULT_FILTER_NOTIFIED"))
DEFAULT_EXPIRATION_MINUTES = int(os.getenv("DEFAULT_EXPIRATION_MINUTES", "30"))

# Cache
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "1000"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "180"))
