from flask import jsonify
from datetime import datetime, timedelta

from models.ban import Ban
from routes.resource import Resource

class BanRoute(Resource):
	def get_collection(self, session, server_id):
		result = session.query(Ban).filter_by(server_id=server_id).all()
		result = [row.to_dict() for row in result]

		return jsonify(result)

	def get_one(self, session, banid):
		result = session.query(Ban).filter_by(rowid=banid).first()
		if result:
			result = result.to_dict()

		return result

	def post_collection(self, session, serverid, banned_word):
		default_ban = Ban(server_id=serverid)
		new_ban = Ban(server_id=serverid, banned_word=banned_word)
		session.add(new_ban)
		return new_ban.to_dict()

	def post_one(self, session, banid, banned_word):
		ban = session.query(Ban).filter_by(rowid=banid).first()
		ban.banned_word = banned_word
		ban.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		ban.calledout_at = (datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d %H:%M:%S")
		return ban.to_dict()

	def delete(self, session, serverid):
		pass