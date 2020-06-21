import os

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase

from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError, ValidationError, AuthenticationError
from bannedWordServer import db
from bannedWordServer.models import Ban, BanRecord, Server
from bannedWordServer.routes.messageroute import MessageRoute

Session = sessionmaker()
engine = create_engine('sqlite:///:memory:')
BOT_TOKEN = os.environ['BOT_TOKEN']

class TestBanRoutePostOne(TestCase):
	def setUp(self):
		db.Model.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		self.current_time = datetime.now()

		serverid = 1234
		new_ban = Ban(server_id=serverid, banned_word="asdf",\
			infracted_at=(self.current_time-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),\
			calledout_at=(self.current_time-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		self.record = BanRecord(server_banned_word=new_ban)
		new_server = Server(server_id=serverid, banned_words=[new_ban])
		self.session.add(new_server)
		self.session.add(new_ban)
		self.session.add(self.record)

	def test_messageroute_post__ban_not_found(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 3, 'sent_time': self.current_time.strftime("%Y-%m-%d %H:%M:%S")}
		self.assertRaises(NotFoundError, MessageRoute().post, self.session, "Bot " + BOT_TOKEN, request)

	def test_messageroute_post__unauthorized(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 3, 'sent_time': self.current_time.strftime("%Y-%m-%d %H:%M:%S")}
		self.assertRaises(AuthenticationError, MessageRoute().post, self.session, "Bot " + "asdffdsa", request)

	def test_messageroute_post__good_request(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': self.current_time.strftime("%Y-%m-%d %H:%M:%S")}
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)
		self.assertEqual(
			1,
			self.session.query(BanRecord).filter_by(rowid=1).first().infraction_count)

	def test_messageroute_post__record_setting(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': self.current_time.strftime("%Y-%m-%d %H:%M:%S")}
		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertEqual(
			timedelta(days=6).total_seconds(),
			self.session.query(BanRecord).filter_by(rowid=1).first().record_seconds)

	def test_messageroute_post__non_record_setting(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': self.current_time.strftime("%Y-%m-%d %H:%M:%S")}
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.record.record_seconds = 999999999999
		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertNotEqual(
			timedelta(days=6).total_seconds(),
			self.session.query(BanRecord).filter_by(rowid=1).first().record_seconds)

	def test_messageroute_post__good_request_callout(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': current_time, 'called_out': True}
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)

		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)

	def test_messageroute_post__invalid_paras(self):
		current_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': "asdf", 'sent_time': current_time, 'called_out': True}
		self.assertRaises(InvalidTypeError, MessageRoute().post, self.session, "Bot " + BOT_TOKEN, request)

		request = {'ban_id': 1, 'sent_time': 1234, 'called_out': True}
		self.assertRaises(InvalidTypeError, MessageRoute().post, self.session, "Bot " + BOT_TOKEN, request)

		request = {'ban_id': 1, 'sent_time': 'asdf', 'called_out': True}
		self.assertRaises(ValidationError, MessageRoute().post, self.session, "Bot " + BOT_TOKEN, request)

	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()