from waitress import serve
import os

from bannedWordServer.router import app

if os.environ['DEVELOPMENT_MODE']:
	app.run()
else:
	serve(app)