from bannedWordServer.config import BOT_TOKEN

def authenticateBotOnly(authToken):
	return authToken == BOT_TOKEN
