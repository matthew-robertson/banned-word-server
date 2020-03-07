from bannedWordServer.config import BOT_TOKEN
from bannedWordServer.externalapi import getManageableDiscordServers

def authenticateBotOrServerAdmin(serverid, authToken):
	return (authenticateBotOnly(authToken) or authenticateServerAdminOnly(serverid, authToken))

def authenticateBotOnly(authToken):
	return authToken == BOT_TOKEN

def authenticateServerAdminOnly(serverid, authToken):
	servers = getManageableDiscordServers(authToken)	
	return any(int(server['id']) == int(serverid) for server in servers)