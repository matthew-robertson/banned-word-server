from confusables import is_confusable
from datetime import datetime, timedelta

from bannedWordServer.constants.errors import ValidationError, DuplicateResourceError, NotFoundError, InvalidTypeError, AuthenticationError
from bannedWordServer.models.ban import Ban
from bannedWordServer.models.server import Server
from bannedWordServer.routes.resource import Resource
from bannedWordServer.auth import authenticateBotOnly

class BanRoute(Resource):
	def get_collection(self, session, authToken, serverid: int) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
		except:
			raise InvalidTypeError
		relevant_server = session.query(Server).filter_by(server_id=serverid).first()
		if not relevant_server: raise NotFoundError

		result = session.query(Ban).filter_by(server_id=serverid).all()
		result = [row.to_dict() for row in result]
		return result

	def get_one(self, session, authToken, banid: int) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			banid = int(banid)
		except:
			raise InvalidTypeError
		result = session.query(Ban).filter_by(rowid=banid).first()
		if not result:
			raise NotFoundError
		return result.to_dict()

	def post_collection(self, session, authToken, serverid: int, banned_word: str) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
		except:
			raise InvalidTypeError
		if not isinstance(banned_word, str): raise InvalidTypeError
		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
		if not server_to_modify: raise NotFoundError
		if len(server_to_modify.banned_words) == 3:
			raise ValidationError

		already_exists = any([is_confusable(banned_word, ban.banned_word) for ban in server_to_modify.banned_words])
		if already_exists: raise DuplicateResourceError

		new_ban = Ban(server_id=serverid,
			banned_word=banned_word,
			infracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			calledout_at=(datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d %H:%M:%S"))
		session.add(new_ban)

		return session.query(Ban).filter_by(server_id=serverid, banned_word=banned_word).first().to_dict()

	def post_one(self, session, authToken, serverid: str, banid: str, banned_word: str) -> dict:
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			serverid = int(serverid)
			banid = int(banid)
		except:
			raise InvalidTypeError
		if not isinstance(banned_word, str): raise InvalidTypeError
		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
		if not server_to_modify: raise NotFoundError
		ban = session.query(Ban).filter_by(server_id=serverid, rowid=banid).first()
		if not ban:	raise NotFoundError

		already_exists = any([is_confusable(banned_word, ban.banned_word) for ban in server_to_modify.banned_words])
		if already_exists: raise DuplicateResourceError

		ban.banned_word = banned_word
		ban.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		ban.calledout_at = (datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d %H:%M:%S")
		return self.get_one(session, authToken, banid)

	def delete(self, session, authToken, serverid: str, banid: str):
		if not authenticateBotOnly(authToken): raise AuthenticationError
		try:
			banid = int(banid)
			serverid = int(serverid)
		except:
			raise InvalidTypeError

		server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
		if not server_to_modify: raise NotFoundError
		if len(server_to_modify.banned_words) == 1:
			raise ValidationError

		ban = session.query(Ban).filter_by(server_id=serverid, rowid=banid).first()

		if not ban:	raise NotFoundError
		session.delete(ban)
		