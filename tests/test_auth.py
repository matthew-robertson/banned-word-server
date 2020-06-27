import os

from unittest import TestCase
from unittest.mock import patch

from bannedWordServer.auth import authenticateBotOnly, authenticateServerAdminOnly, authenticateBotOrServerAdmin

def fake_serverlist(authToken):
	s1 = {"features": [], "id": "347174618706083848", "name": "Earth Wind and Shire", "owner": True, "permissions": 2147483647 }
	s2 = {"features": [], "id": "1234", "name": "Testbed", "owner": False, "permissions": 0 }
	return [s1, s2], 200

class TestAuthenticateBotOnly(TestCase):
	def test_authenticateBotOnly_successful(self):
		result = authenticateBotOnly("Bot " + os.environ["BOT_TOKEN"])
		self.assertTrue(result)

	def test_authenticateBotOnly_unsuccessful(self):
		result = authenticateBotOnly("Bot " + os.environ["BOT_TOKEN"] + "asdf")
		self.assertFalse(result)

@patch('bannedWordServer.auth.getManageableDiscordServers', side_effect=fake_serverlist)
class TestAuthenticateServerAdminOnly(TestCase):
	def test_authenticateServerAdminOnly_successful(self, apistub):
		result = authenticateServerAdminOnly(347174618706083848, "asdf")
		self.assertTrue(result)

	def test_authenticateServerAdminOnly_not_admin(self, apistub):
		result = authenticateServerAdminOnly(4321, "asdf")
		self.assertFalse(result)

@patch('bannedWordServer.auth.getManageableDiscordServers', side_effect=fake_serverlist)
class TestAuthenticateBotOrServerAdmin(TestCase):
	def test_authenticatBotOrAdmin_bot(self, apiStub):
		result = authenticateBotOrServerAdmin(4321, "Bot " + os.environ["BOT_TOKEN"])
		self.assertTrue(result)

	def test_authenticatBotOrAdmin_admin(self, apiStub):
		result = authenticateBotOrServerAdmin(347174618706083848, "asdf")
		self.assertTrue(result)

	def test_authenticatBotOrAdmin_neither(self, apiStub):
		result = authenticateBotOrServerAdmin(4321, "asdf")
		self.assertFalse(result)