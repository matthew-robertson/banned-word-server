from datetime import datetime, timedelta

from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError
from bannedWordServer.models.ban import Ban
from bannedWordServer.routes.resource import Resource

class BanRoute(Resource):
	def get_collection(self, session, serverid: int) -> dict:
		result = session.query(Ban).filter_by(server_id=serverid).all()
		result = [row.to_dict() for row in result]

		return result

	def get_one(self, session, banid: int) -> dict:
		result = session.query(Ban).filter_by(rowid=banid).first()
		if not result:
			raise NotFoundError
		result = result.to_dict()

	def post_collection(self, session, serverid: int, banned_word: str) -> dict:
		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
		if not server_to_modify: raise NotFoundError

		default_ban = Ban(server_id=serverid)
		new_ban = Ban(server_id=serverid, banned_word=banned_word)
		session.add(new_ban)
		return new_ban.to_dict()

	def post_one(self, session, banid: int, banned_word: str) -> dict:
		if not isinstance(banned_word, str) or not isinstance(banid, int): raise InvalidTypeError
		ban = session.query(Ban).filter_by(rowid=banid).first()
		if not ban:	raise NotFoundError

		ban.banned_word = banned_word
		ban.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		ban.calledout_at = (datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d %H:%M:%S")
		return ban.to_dict()

	def delete(self, session, serverid):
		pass