import json
import requests

from bannedWordServer.config import DISCORD_BASE_URL

def getManageableDiscordServers(authToken):
	result = requests.get(DISCORD_BASE_URL + 'users/@me/guilds',
	headers = {'Authorization': authToken})
	if (not result.status_code == 200): return []
	return list(filter(lambda server: (server['permissions'] & 0x00000008) == 0x00000008, json.loads(result.content)))