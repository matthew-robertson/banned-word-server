from datetime import datetime, timedelta

from bannedWordServer.auth import authenticateBotOnly
from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError, DuplicateResourceError, AuthenticationError
from bannedWordServer.models.server import Server
from bannedWordServer.models.ban import Ban
from bannedWordServer.routes.resource import Resource

class ServerRoute(Resource):
	def get_collection(self, session, authToken):
		if not authenticateBotOnly(authToken): raise AuthenticationError
		result = session.query(Server).all()
		result = [row.to_dict() for row in result]

		return result

	def get_one(self, session, authToken, serverid: str) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
		except:
			raise InvalidTypeError

		result = session.query(Server).filter_by(server_id=serverid).first()
		if not result:
			raise NotFoundError
		return result.to_dict()

	def post_collection(self, session, authToken, serverid: str) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
		except:
			raise InvalidTypeError
		already_exists = session.query(Server).filter_by(server_id=serverid).first()
		if already_exists:
			raise DuplicateResourceError

		default_ban = Ban(server_id=serverid)
		new_server = Server(server_id=serverid, banned_words=[default_ban])
		session.add(new_server)
		return self.get_one(session, authToken, serverid)

	def partial_update(self, session, authToken, serverid: str, modified_params: dict) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
		except:
			raise InvalidTypeError

		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
		if not server_to_modify: raise NotFoundError

		if 'awake' in modified_params.keys():
			awake: bool = modified_params['awake']
			if not isinstance(awake, bool): raise InvalidTypeError
			server_to_modify.awake = awake

		if 'timeout_duration_seconds' in modified_params.keys():
			timeout_duration_seconds: int = modified_params['timeout_duration_seconds']
			if not isinstance(timeout_duration_seconds, int): raise InvalidTypeError
			server_to_modify.timeout_duration_seconds = timeout_duration_seconds

		return self.get_one(session, authToken, serverid)

	def delete(self, session, serverid):
		pass