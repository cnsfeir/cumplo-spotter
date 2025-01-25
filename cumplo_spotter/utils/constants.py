import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Basics
LOCATION = os.getenv("LOCATION", "us-central1")
PROJECT_ID = os.getenv("PROJECT_ID")
LOG_FORMAT = "\n%(levelname)s: %(message)s"
IS_TESTING = bool(os.getenv("IS_TESTING"))

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
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

# Cumplo
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")
CUMPLO_BASE_URL = os.getenv("CUMPLO_BASE_URL")
CUMPLO_HTML_API = os.getenv("CUMPLO_HTML_API", "")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
CUMPLO_GRAPHQL_HEADERS = {"Accept-Language": "es-CL"}
CUMPLO_GLOBAL_API = os.getenv("CUMPLO_GLOBAL_API", "")
CUMPLO_GLOBAL_API_FUNDING_REQUESTS = os.getenv("CUMPLO_GLOBAL_API_FUNDING_REQUESTS", "")
CUMPLO_GLOBAL_API_SIMULATION = os.getenv("CUMPLO_GLOBAL_API_SIMULATION", "")
CUMPLO_GLOBAL_API_DETAILS = os.getenv("CUMPLO_GLOBAL_API_DETAILS", "")
UPFRONT_FEE_KEY = os.getenv("UPFRONT_FEE_KEY", "COMISION ENTRADA")
EXIT_FEE_KEY = os.getenv("EXIT_FEE_KEY", "COMISION SALIDA")
SIMULATION_AMOUNT = int(os.getenv("SIMULATION_AMOUNT", "1000000"))

# Defaults
DEFAULT_FILTER_NOTIFIED = bool(os.getenv("DEFAULT_FILTER_NOTIFIED"))
DEFAULT_EXPIRATION_MINUTES = int(os.getenv("DEFAULT_EXPIRATION_MINUTES", "30"))

# Cache
CACHE_MAXSIZE = int(os.getenv("CACHE_MAXSIZE", "1000"))
CUMPLO_CACHE_TTL = int(os.getenv("CUMPLO_CACHE_TTL", "120"))
