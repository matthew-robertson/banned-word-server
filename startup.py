from waitress import serve
import os

from bannedWordServer.router import app

if os.environ['DEVELOPMENT_MODE']:
	app.run(host='0.0.0.0')
else:
	serve(app)
