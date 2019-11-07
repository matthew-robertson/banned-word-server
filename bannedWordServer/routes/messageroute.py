import re

from bannedWordServer.auth import authenticateBotOnly
from bannedWordServer.models.ban import Ban
from bannedWordServer.routes.resource import Resource
from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError, ValidationError, AuthenticationError

class MessageRoute(Resource):
	def __init__(self):
		self.pattern = re.compile(r"[0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*:[0-9]*")

	def get_collection(self, session, id):
		pass

	def get_one(self, session, id):
		pass

	def post(self, session, authToken, requestJson) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			banid = int(requestJson['ban_id'])
		except:
			raise InvalidTypeError

		ban_to_modify = session.query(Ban).filter_by(rowid=banid).first()
		if not ban_to_modify: raise NotFoundError

		if not isinstance(requestJson['sent_time'], str): raise InvalidTypeError
		if not self.pattern.match(requestJson['sent_time']): raise ValidationError

		ban_to_modify.infracted_at = requestJson['sent_time']
		if ('called_out' in requestJson.keys()):
			ban_to_modify.calledout_at = requestJson['sent_time']

		return session.query(Ban).filter_by(rowid=banid).first().to_dict()
