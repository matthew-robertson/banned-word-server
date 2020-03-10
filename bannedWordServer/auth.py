from bannedWordServer.config import BOT_TOKEN
from bannedWordServer.externalapi import getManageableDiscordServers

def authenticateBotOrServerAdmin(serverid, auth_token):
	return (authenticateBotOnly(auth_token) or authenticateServerAdminOnly(serverid, auth_token))

def authenticateBotOnly(auth_token):
	return auth_token == BOT_TOKEN

def authenticateServerAdminOnly(serverid, auth_token):
	servers, status_code = getManageableDiscordServers(auth_token)	
	return any(int(server['id']) == int(serverid) for server in servers)