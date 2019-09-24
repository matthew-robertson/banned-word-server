from flask import jsonify

from models.server import Server
from models.ban import Ban
from routes.resource import Resource

class ServerRoute(Resource):
	def get_collection(self, session):
		result = session.query(Server).all()
		result = [row.to_dict() for row in result]

		return jsonify(result)

	def get_one(self, session, serverid):
		result = session.query(Server).filter_by(server_id=serverid).first()
		if result:
			result = result.to_dict()

		return result

	def post_collection(self, session, serverid):
		default_ban = Ban(server_id=serverid)
		new_server = Server(server_id=serverid, banned_words=[default_ban])
		session.add(new_server)
		return new_server.to_dict()

	def partial_update(self, session, serverid, modified_params):
		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()

		if 'awake' in modified_params.keys():
			server_to_modify.awake = modified_params['awake']
		if 'timeout_duration_seconds' in modified_params.keys():
			server_to_modify.timeout_duration_seconds = modified_params['timeout_duration_seconds']
		if 'banned_word' in modified_params.keys():
			index = modified_params['banned_word']['index']
			new_word = modified_params['banned_word']['word']

			ban_to_modify = server_to_modify.banned_words[index]
			ban_to_modify.banned_word = new_word
			ban_to_modify.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			ban_to_modify.calledout_at = (datetime.now() - timedelta(seconds=server_to_modify.timeout_duration_seconds)).strftime("%Y-%m-%d %H:%M:%S")
			

		return server_to_modify.to_dict()

	def delete(self, session, serverid):
		pass