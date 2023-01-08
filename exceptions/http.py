from werkzeug.exceptions import HTTPException


class ForbiddenException(HTTPException):
    code = 403
    description = "Forbidden"
