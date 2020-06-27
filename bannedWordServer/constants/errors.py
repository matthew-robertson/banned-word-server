class ValidationError(Exception):
    status_code = 400


class AuthenticationError(Exception):
    status_code = 401


class PlanError(Exception):
    status_code = 402


class NotFoundError(ValidationError):
    status_code = 404


class InvalidTypeError(ValidationError):
    status_code = 400


class DuplicateResourceError(Exception):
    status_code = 403
