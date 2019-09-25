from flask import jsonify

from models.server import Server
from models.ban import Ban
from routes.resource import Resource
from constants.errors import NotFoundError, InvalidTypeError

class ServerRoute(Resource):
	def get_collection(self, session):
		result = session.query(Server).all()
		result = [row.to_dict() for row in result]

		return jsonify(result)

	def get_one(self, session, serverid: int) -> dict:
		if not isinstance(serverid, int): raise InvalidTypeError

		result = session.query(Server).filter_by(server_id=serverid).first()
		if not result:
			raise NotFoundError
		return result.to_dict()

	def post_collection(self, session, serverid: int) -> dict:
		if not isinstance(serverid, int): raise InvalidTypeError

		default_ban = Ban(server_id=serverid)
		new_server = Server(server_id=serverid, banned_words=[default_ban])
		session.add(new_server)
		return new_server.to_dict()

	def partial_update(self, session, serverid: int, modified_params: dict) -> dict:
		if not isinstance(serverid, int): raise InvalidTypeError
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

		if 'banned_word' in modified_params.keys():
			index: int = modified_params['banned_word']['index']
			new_word: str = modified_params['banned_word']['word']

			if not isinstance(index, int): raise InvalidTypeError
			if not isinstance(new_word, str): raise InvalidTypeError

			ban_to_modify = server_to_modify.banned_words[index]
			ban_to_modify.banned_word = new_word
			ban_to_modify.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			ban_to_modify.calledout_at = (datetime.now() - timedelta(seconds=server_to_modify.timeout_duration_seconds)).strftime("%Y-%m-%d %H:%M:%S")

		return server_to_modify.to_dict()

	def delete(self, session, serverid):
		pass