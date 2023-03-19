from werkzeug.exceptions import HTTPException


class ForbiddenException(HTTPException):
    description = "Forbidden"
    code = 403
