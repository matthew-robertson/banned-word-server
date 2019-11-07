from bannedWordServer.config import BOT_TOKEN

def authenticateBotOnly(authToken):
	return authToken == 'Bot ' + BOT_TOKEN
