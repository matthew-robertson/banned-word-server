import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase

from bannedWordServer.models import Base
from bannedWordServer.models.server import Server
from bannedWordServer.routes.serverroute import ServerRoute

Session = sessionmaker()
engine = create_engine('sqlite:///:memory:')

class TestServerRoute(TestCase):
	def setUp(self):
		Base.metadata.create_all(engine)
		self.connection = engine.connect()
		self.trans = self.connection.begin()
		self.session = Session(bind=self.connection)

	def test_get_collection__no_elements(self):
		result = ServerRoute().get_collection(self.session)
		self.assertEqual(result, [])

	def test_get_collection__one_element(self):
		server = Server(server_id=1234)
		self.session.add(server)
		result = ServerRoute().get_collection(self.session)
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0]['server_id'], server.server_id)		


	def test_get_collection__multiple_elements(self):
		server1 = Server(server_id=1234)
		server2 = Server(server_id=4321)
		self.session.add(server1)
		self.session.add(server2)
		result = ServerRoute().get_collection(self.session)
		self.assertEqual(len(result), 2)


	def tearDown(self):
		self.session.close()
		self.trans.rollback()
		self.connection.close()
