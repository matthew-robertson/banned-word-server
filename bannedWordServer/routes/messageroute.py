from models.ban import Ban
from routes.resource import Resource
from flask import jsonify

class MessageRoute(Resource):
	def get_collection(self, session, id):
		pass

	def get_one(self, session, id):
		pass

	def post(self, session, requestJson):
		banid = requestJson['ban_id']
		ban_to_modify = session.query(Ban).filter(rowid=banid).first()
		ban_to_modify.infracted_at = requestJson['sent_time']
		if (requestJson['called_out']):
			ban_to_modify.calledout_at = requestJson['sent_time']

		return ban_to_modify.to_dict()
