from models.server import Server
from models.ban import Ban
from routes.resource import Resource
from flask import jsonify

class ServerRoute(Resource):
	def get_all(self, session):
		result = session.query(Server).all()
		result = [row.to_dict() for row in result]

		return jsonify(result)

	def get_one(self, session, serverid):
		result = session.query(Server).filter_by(server_id=serverid).first()
		if result:
			result = result.to_dict()

		return result

	def post(self, session, serverid):
		default_ban = Ban(server_id=serverid)
		new_server = Server(server_id=serverid, banned_words=[default_ban])
		session.add(new_server)
		return new_server

	def put(self, session, serverid, modified_params):
		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()

		if modified_params['awake']:
			server_to_modify.awake = modified_params['awake']
		if modified_params['timeout_duration_seconds']:
			server_to_modify.timeout_duration_seconds = modified_params['timeout_duration_seconds']
		if modified_params['banned_word'] and
			modified_params['banned_word']['index'] and 
			modified_params['banned_word']['banned_word']:
			index = modified_params['banned_word']['index']
			new_word = modified_params['banned_word']['index']

			ban_to_modify = server_to_modify.banned_words[index]
			ban_to_modify.banned_word = new_word
			ban_to_modify.infracted_at = datetime.now()
			ban_to_modify.calledout_at = datetime.now() - timedelta(seconds=server_to_modify.timeout_duration_seconds)
			

		return server_to_modify

	def delete(self, session, serverid):
		pass