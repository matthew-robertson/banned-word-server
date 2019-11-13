from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase

from bannedWordServer.config import BOT_TOKEN
from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError, DuplicateResourceError, AuthenticationError
from bannedWordServer.models import Base
from bannedWordServer.models.server import Server
from bannedWordServer.models.ban import Ban
from bannedWordServer.routes.banroute import BanRoute

Session = sessionmaker()
engine = create_engine('sqlite:///:memory:')

class TestBanRouteGetCollection(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)

		self.serverid = "1234"
		new_server = Server(server_id=int(self.serverid))
		self.session.add(new_server)

	def test_banroute_get_collection__bad_serverid(self):
		self.assertRaises(InvalidTypeError, BanRoute().get_collection, self.session, "Bot " + BOT_TOKEN, "asdf")

	def test_banroute_get_collection__server_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().get_collection, self.session, "Bot " + BOT_TOKEN, 12345)

	def test_banroute_get_collection__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().get_collection, self.session, "Bot " + "asdffdsa", 12345)

	def test_banroute_get_collection__no_elements(self):
		result = BanRoute().get_collection(self.session, "Bot " + BOT_TOKEN, self.serverid)
		self.assertEqual(result, [])

	def test_banroute_get_collection__one_element(self):
		banned_word = "asdf"
		ban = Ban(server_id=int(self.serverid), banned_word=banned_word)
		self.session.add(ban)

		result = BanRoute().get_collection(self.session, "Bot " + BOT_TOKEN, self.serverid)
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]['banned_word'], banned_word)

	def test_banroute_get_collection__multiple_elements(self):
		b1w = "asdf"
		b2w = "qwerty"
		ban1 = Ban(server_id=int(self.serverid), banned_word=b1w)
		ban2 = Ban(server_id=int(self.serverid), banned_word=b2w)
		self.session.add(ban1)
		self.session.add(ban2)

		result = BanRoute().get_collection(self.session, "Bot " + BOT_TOKEN, self.serverid)
		self.assertEqual(len(result), 2)
		self.assertEqual(result[0]['banned_word'], b1w)
		self.assertEqual(result[1]['banned_word'], b2w)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRouteGetCollection(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)

	def test_banroute_get_one__bad_serverid(self):
		self.assertRaises(InvalidTypeError, BanRoute().get_one, self.session, "Bot " + BOT_TOKEN, "asdf")

	def test_banroute_get_one__not_found(self):
		self.assertRaises(NotFoundError, BanRoute().get_one, self.session, "Bot " + BOT_TOKEN, "0")

	def test_banroute_get_one__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().get_one, self.session, "Bot " + "asdffdsa", "0")

	def test_banroute_get_one__good_request(self):
		b1 = Ban(server_id=1, banned_word="asdf")
		b2 = Ban(server_id=1, banned_word="qwerty")
		self.session.add(b1)
		self.session.add(b2)

		result = BanRoute().get_one(self.session, "Bot " + BOT_TOKEN, "2")
		self.assertEqual(b2.banned_word, result['banned_word'])

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRoutePostCollection(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		self.serverid = "1234"
		new_server = Server(server_id=int(self.serverid))
		self.session.add(new_server)

	def test_banroute_post_collection__good_request(self):
		banned_word = "asdf"
		result = BanRoute().post_collection(self.session, "Bot " + BOT_TOKEN, self.serverid, banned_word)
		db_result = self.session.query(Ban).filter_by(server_id=self.serverid, banned_word=banned_word).first()
		self.assertEqual(result,db_result.to_dict())

	def test_banroute_post_collection__server_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().post_collection, self.session, "Bot " + BOT_TOKEN, "4321", "asdf")

	def test_banroute_post_collection__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().post_collection, self.session, "Bot " + "asdffdsa", self.serverid, "asdf")

	def test_banroute_post_collection__duplicate_word(self):
		banned_word = "asdf"
		BanRoute().post_collection(self.session, "Bot " + BOT_TOKEN, self.serverid, banned_word)
		self.assertRaises(DuplicateResourceError, BanRoute().post_collection, self.session, "Bot " + BOT_TOKEN, self.serverid, banned_word)

	def test_banroute_post_collection__invalid_word(self):
		banned_word = 1234
		self.assertRaises(InvalidTypeError, BanRoute().post_collection, self.session, "Bot " + BOT_TOKEN, self.serverid, banned_word)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRoutePostOne(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		serverid = 1234
		new_ban = Ban(server_id=serverid, banned_word="asdf", infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		new_server = Server(server_id=serverid, banned_words=[new_ban])
		self.session.add(new_server)

	def test_banroute_post_one__good_request(self):
		new_word = "qwerty"
		banid = 1

		ban = self.session.query(Ban).filter_by(rowid=banid).first()
		old_time = ban.infracted_at
		self.assertNotEqual(new_word, ban.banned_word)

		BanRoute().post_one(self.session, "Bot " + BOT_TOKEN, banid, new_word)
		self.assertEqual(new_word, BanRoute().get_one(self.session, "Bot " + BOT_TOKEN, banid)['banned_word'])
		self.assertEqual(True,\
			datetime.strptime(ban.infracted_at, "%Y-%m-%d %H:%M:%S") >\
			datetime.strptime(old_time, "%Y-%m-%d %H:%M:%S"))

	def test_banroute_post_one__ban_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().post_one, self.session, "Bot " + BOT_TOKEN, 5, "asdf")

	def test_banroute_post_one__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().post_one, self.session, "Bot " + "asdffdsa", 5, "asdf")

	def test_banroute_post_one__word_invalid(self):
		self.assertRaises(InvalidTypeError, BanRoute().post_one, self.session, "Bot " + BOT_TOKEN, 1, 1234)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()