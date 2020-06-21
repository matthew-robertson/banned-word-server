import re
from math import floor
from datetime import datetime

from bannedWordServer.auth import authenticateBotOnly
from bannedWordServer.models import Ban, BanRecord
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
		record_to_modify = session.query(BanRecord).filter_by(ban_id=banid).first()
		if not ban_to_modify or not record_to_modify: raise NotFoundError

		if not isinstance(requestJson['sent_time'], str): raise InvalidTypeError
		if not self.pattern.match(requestJson['sent_time']): raise ValidationError

		diff_in_seconds = (
			datetime.strptime(requestJson['sent_time'], "%Y-%m-%d %H:%M:%S") - 
			datetime.strptime(ban_to_modify.infracted_at, "%Y-%m-%d %H:%M:%S")).total_seconds()
		if diff_in_seconds > record_to_modify.record_seconds:
			record_to_modify.record_seconds = diff_in_seconds

		record_to_modify.infraction_count += 1

		ban_to_modify.infracted_at = requestJson['sent_time']
		if ('called_out' in requestJson.keys()):
			ban_to_modify.calledout_at = requestJson['sent_time']

		return session.query(Ban).filter_by(rowid=banid).first().to_dict()
