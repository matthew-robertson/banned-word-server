import json
import os
import requests

def getManageableDiscordServers(auth_token):
	result = requests.get(
		os.environ['DISCORD_BASE_URL'] + 'users/@me/guilds',
		headers = {'Authorization': auth_token}
	)

	if (not result.status_code == 200): return [], result.status_code
	return list(filter(lambda server: (server['permissions'] & 0x00000008) == 0x00000008, json.loads(result.content))), result.status_code

def getDiscordUser(auth_token):
	result = requests.get(
		os.environ['DISCORD_BASE_URL'] + 'users/@me',
		headers = {'Authorization': auth_token}
	)

	return json.loads(result.content), result.status_code