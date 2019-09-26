class ValidationError(Exception):
	pass

class NotFoundError(ValidationError):
	pass

class InvalidTypeError(ValidationError):
	pass

class DuplicateResourceError(Exception):
	pass