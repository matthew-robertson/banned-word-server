class ValidationError(Exception):
	pass

class NotFoundError(ValidationError):
	pass

class InvalidTypeError(ValidationError):
	pass
