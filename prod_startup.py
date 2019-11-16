from waitress import serve
from bannedWordServer.router import app

serve(app)