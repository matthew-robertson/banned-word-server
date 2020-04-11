import os

def authenticateBotOnly(authToken):
	return authToken == 'Bot ' + os.environ['BOT_TOKEN']
