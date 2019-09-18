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