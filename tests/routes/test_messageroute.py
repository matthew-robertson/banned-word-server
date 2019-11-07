from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase

from bannedWordServer.config import BOT_TOKEN
from bannedWordServer.constants.errors import NotFoundError, InvalidTypeError, ValidationError, AuthenticationError
from bannedWordServer.models import Base
from bannedWordServer.models.server import Server
from bannedWordServer.models.ban import Ban
from bannedWordServer.routes.messageroute import MessageRoute

Session = sessionmaker()
engine = create_engine('sqlite:///:memory:')

class TestBanRoutePostOne(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)
		serverid = 1234
		new_ban = Ban(server_id=serverid, banned_word="asdf",\
			infracted_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),\
			calledout_at=(datetime.now()-timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"))
		new_server = Server(server_id=serverid, banned_words=[new_ban])
		self.session.add(new_server)

	def test_messageroute_post__ban_not_found(self):
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 3, 'sent_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
		self.assertRaises(NotFoundError, MessageRoute().post, self.session, "Bot " + BOT_TOKEN, request)

	def test_messageroute_post__unauthorized(self):
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 3, 'sent_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
		self.assertRaises(AuthenticationError, MessageRoute().post, self.session, "Bot " + "asdffdsa", request)

	def test_messageroute_post__good_request(self):
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)

	def test_messageroute_post__good_request_callout(self):
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		request = {'ban_id': 1, 'sent_time': current_time, 'called_out': True}
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertNotEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)

		result = MessageRoute().post(self.session, "Bot " + BOT_TOKEN, request)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().infracted_at)
		self.assertEqual(current_time, self.session.query(Ban).filter_by(rowid=1).first().calledout_at)

	def test_messageroute_post__invalid_paras(self):
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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