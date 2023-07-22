import string
import unicodedata

SEPARATORS = ["_", "-"]


def clean_text(error: str) -> str:
    """
    Cleans a text by removing punctuation and normalizing unicode characters
    """
    for separator in SEPARATORS:
        error = " ".join(error.split(separator))

    return " ".join(
        unicodedata.normalize("NFD", error)
        .encode("ASCII", "ignore")
        .decode("UTF-8")
        .replace("\n", " ")
        .replace("\r", " ")
        .translate(str.maketrans("", "", string.punctuation))
        .upper()
        .split()
    )


def secure_key(key: str) -> str:
    """
    Returns a secure version of a key
    """
    return f"{key[:5]}{'*' * (len(key) - 15)}{key[-10:]}"
