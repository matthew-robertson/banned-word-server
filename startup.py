from waitress import serve
import os

from bannedWordServer.router import app

if "DEVELOPMENT_MODE" in os.environ:
    app.run(host="0.0.0.0")
else:
    serve(app, threads=int(os.environ["WAITRESS_THREAD_COUNT"]))
