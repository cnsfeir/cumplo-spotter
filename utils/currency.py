import babel.numbers


def format_currency(amount: int) -> str:
    """Formats an amount of money in CLP"""
    return babel.numbers.format_currency(amount, currency="CLP", locale="es_CL")
