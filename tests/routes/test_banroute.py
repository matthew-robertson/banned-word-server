import os

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase

from bannedWordServer.constants.errors import ValidationError, NotFoundError, InvalidTypeError, DuplicateResourceError, AuthenticationError
from bannedWordServer import db
from bannedWordServer.models import Ban, BanRecord, Server
from bannedWordServer.routes.banroute import BanRoute

Session = sessionmaker()
engine = create_engine('sqlite:///:memory:')
BOT_TOKEN = os.environ['BOT_TOKEN']

class TestBanRouteGetCollection(TestCase):
	def setUp(self):
		db.Model.metadata.create_all(engine)
		self.authtoken = "Bot " + BOT_TOKEN
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)

		self.serverid = "1234"
		new_server = Server(server_id=int(self.serverid))
		self.session.add(new_server)

	def test_banroute_get_collection__bad_serverid(self):
		self.assertRaises(InvalidTypeError, BanRoute().get_collection, self.session, self.authtoken, "asdf")

	def test_banroute_get_collection__server_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().get_collection, self.session, self.authtoken, 12345)

	def test_banroute_get_collection__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().get_collection, self.session, "Bot " + "asdffdsa", 12345)

	def test_banroute_get_collection__no_elements(self):
		result = BanRoute().get_collection(self.session, self.authtoken, self.serverid)
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
		db.Model.metadata.create_all(engine)
		self.authtoken = "Bot " + BOT_TOKEN
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)

	def test_banroute_get_one__bad_serverid(self):
		self.assertRaises(InvalidTypeError, BanRoute().get_one, self.session, self.authtoken, "asdf")

	def test_banroute_get_one__not_found(self):
		self.assertRaises(NotFoundError, BanRoute().get_one, self.session, self.authtoken, "0")

	def test_banroute_get_one__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().get_one, self.session, "Bot " + "asdffdsa", "0")

	def test_banroute_get_one__good_request(self):
		b1 = Ban(server_id=1, banned_word="asdf")
		r1 = BanRecord(server_banned_word=b1)
		b2 = Ban(server_id=1, banned_word="qwerty")
		r2 = BanRecord(server_banned_word=b2)
		self.session.add(b1)
		self.session.add(r1)
		self.session.add(b2)
		self.session.add(r2)

		result = BanRoute().get_one(self.session, "Bot " + BOT_TOKEN, "2")
		self.assertEqual(b2.banned_word, result['banned_word'])

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRoutePostCollection(TestCase):
	def setUp(self):
		db.Model.metadata.create_all(engine)
		self.connection = engine.connect()
		self.authtoken = "Bot " + BOT_TOKEN
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		self.serverid = "1234"
		new_server = Server(server_id=int(self.serverid))
		self.session.add(new_server)

	def test_banroute_post_collection__good_request(self):
		banned_word = "asdf"
		result = BanRoute().post_collection(self.session, self.authtoken, self.serverid, banned_word)
		db_result = self.session.query(Ban).filter_by(server_id=self.serverid, banned_word=banned_word).first()
		self.assertEqual(result,db_result.to_dict())
		self.assertTrue('record' in result)


	def test_banroute_post_collection__too_many_words(self):
		BanRoute().post_collection(self.session, self.authtoken, self.serverid, "asdf")
		BanRoute().post_collection(self.session, self.authtoken, self.serverid, "sdfa")
		BanRoute().post_collection(self.session, self.authtoken, self.serverid, "dfas")
		self.assertRaises(ValidationError, BanRoute().post_collection, self.session, self.authtoken, self.serverid, "fasd")

	def test_banroute_post_collection__server_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().post_collection, self.session, self.authtoken, "4321", "asdf")

	def test_banroute_post_collection__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().post_collection, self.session, "Bot " + "asdffdsa", self.serverid, "asdf")

	def test_banroute_post_collection__duplicate_word(self):
		banned_word = "asdf"
		BanRoute().post_collection(self.session, "Bot " + BOT_TOKEN, self.serverid, banned_word)
		self.assertRaises(DuplicateResourceError, BanRoute().post_collection, self.session, self.authtoken, self.serverid, banned_word)

	def test_banroute_post_collection__confusable_word(self):
		BanRoute().post_collection(self.session, "Bot " + BOT_TOKEN, self.serverid, 'lest')
		self.assertRaises(DuplicateResourceError, BanRoute().post_collection, self.session, self.authtoken, self.serverid, 'iest')

	def test_banroute_post_collection__invalid_word(self):
		banned_word = 1234
		self.assertRaises(InvalidTypeError, BanRoute().post_collection, self.session, self.authtoken, self.serverid, banned_word)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRoutePostOne(TestCase):
	def setUp(self):
		db.Model.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		self.serverid = 1234
		new_ban = Ban(server_id=self.serverid, banned_word="asdf", infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		self.record = BanRecord(server_banned_word=new_ban, record_seconds=60)
		new_server = Server(server_id=self.serverid, banned_words=[new_ban])
		self.session.add(new_server)
		self.session.add(new_ban)
		self.session.add(self.record)

	def test_banroute_post_one__good_request(self):
		new_word = "qwerty"
		banid = 1

		ban = self.session.query(Ban).filter_by(rowid=banid).first()
		old_time = ban.infracted_at
		self.assertNotEqual(new_word, ban.banned_word)

		BanRoute().post_one(self.session, "Bot " + BOT_TOKEN, self.serverid, banid, new_word)
		self.assertEqual(new_word, BanRoute().get_one(self.session, "Bot " + BOT_TOKEN, banid)['banned_word'])
		self.assertEqual(True,\
			datetime.strptime(ban.infracted_at, "%Y-%m-%d %H:%M:%S") >\
			datetime.strptime(old_time, "%Y-%m-%d %H:%M:%S"))

	def test_banroute_post_one__resets_record(self):
		new_word = "qwerty"
		banid = 1

		ban = self.session.query(Ban).filter_by(rowid=banid).first()
		old_time = ban.infracted_at
		self.assertNotEqual(0, self.record.record_seconds)

		BanRoute().post_one(self.session, "Bot " + BOT_TOKEN, self.serverid, banid, new_word)
		self.assertEqual(0, self.record.record_seconds)

	def test_banroute_post_one__ban_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().post_one, self.session, "Bot " + BOT_TOKEN, self.serverid, 5, "asdf")

	def test_banroute_post_one__confusable_word(self):
		BanRoute().post_collection(self.session, "Bot " + BOT_TOKEN, self.serverid, 'lest')
		self.assertRaises(DuplicateResourceError, BanRoute().post_one, self.session, "Bot " + BOT_TOKEN, self.serverid, 1, "iest")

	def test_banroute_post_one__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().post_one, self.session, "Bot " + "asdffdsa", self.serverid, 5, "asdf")

	def test_banroute_post_one__word_invalid(self):
		self.assertRaises(InvalidTypeError, BanRoute().post_one, self.session, "Bot " + BOT_TOKEN, self.serverid, 1, 1234)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()

class TestBanRouteDelete(TestCase):
	def setUp(self):
		db.Model.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		self.serverid = 1234
		new_ban1 = Ban(server_id=self.serverid, banned_word="asdf", infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		new_record1 = BanRecord(server_banned_word=new_ban1)
		new_ban2 = Ban(server_id=self.serverid, banned_word="fdsa", infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		new_record2 = BanRecord(server_banned_word=new_ban2)
		new_ban3 = Ban(server_id=self.serverid, banned_word="test", infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		new_record3 = BanRecord(server_banned_word=new_ban3)
		new_server = Server(server_id=self.serverid, banned_words=[new_ban1, new_ban2, new_ban3])
		self.session.add(new_server)
		self.session.add(new_ban1)
		self.session.add(new_ban2)
		self.session.add(new_ban3)
		self.session.add(new_record1)
		self.session.add(new_record2)
		self.session.add(new_record3)
		

	def test_banroute_delete__good_request(self):
		banid = 1

		self.assertEqual(3, len(self.session.query(BanRecord).all()))
		BanRoute().delete(self.session, "Bot " + BOT_TOKEN, self.serverid, banid)
		self.assertRaises(NotFoundError, BanRoute().get_one, self.session, "Bot " + BOT_TOKEN, banid)
		server_words = self.session.query(Server).filter_by(server_id=self.serverid).first().banned_words
		self.assertEqual(len(server_words), 2)
		self.assertEqual(2, len(self.session.query(BanRecord).all()))

	def test_banroute_delete__ban_not_found(self):
		self.assertRaises(NotFoundError, BanRoute().delete, self.session, "Bot " + BOT_TOKEN, self.serverid, 5)

	def test_banroute_delete__unauthorized(self):
		self.assertRaises(AuthenticationError, BanRoute().delete, self.session, "Bot " + "asdffdsa", self.serverid, 1)

	def test_banroute_delete__twice(self):
		banid = 1
		BanRoute().delete(self.session, "Bot " + BOT_TOKEN, self.serverid, banid)
		self.assertRaises(NotFoundError, BanRoute().delete, self.session, "Bot " + BOT_TOKEN, self.serverid, banid)

	def test_banroute_delete__delete_last_word(self):
		BanRoute().delete(self.session, "Bot " + BOT_TOKEN, self.serverid, 1)
		BanRoute().delete(self.session, "Bot " + BOT_TOKEN, self.serverid, 3)
		self.assertRaises(ValidationError, BanRoute().delete, self.session, "Bot " + BOT_TOKEN, self.serverid, 2)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()