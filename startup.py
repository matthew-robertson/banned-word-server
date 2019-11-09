from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request
from flask_cors import CORS

from bannedWordServer.config import DB_LOCATION, SECRET_KEY
from bannedWordServer.models.ban import Ban
from bannedWordServer.models.server import Server
from bannedWordServer.routes.banroute import BanRoute
from bannedWordServer.routes.messageroute import MessageRoute
from bannedWordServer.routes.serverroute import ServerRoute

_engine = create_engine('sqlite:///'+DB_LOCATION, echo=False)
_Session = sessionmaker(bind=_engine)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)
def start_session():
	return _Session()


@app.route('/v1/servers', methods=['GET', 'POST'])
def servers():
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
		    result = ServerRoute().post_collection(session, request.headers['Authorization'], int(request.json['server_id']))
		    session.commit()
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()
	elif request.method == 'GET':
		result = jsonify(ServerRoute().get_collection(session, request.headers['Authorization']))

	return result

@app.route('/v1/servers/<serverid>', methods=['GET', 'POST'])
def server(serverid):
	serverid = int(serverid)
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
		    result = ServerRoute().partial_update(session, request.headers['Authorization'], serverid, request.json)
		    session.commit()
		    return result
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()
	elif request.method == 'GET':
		result = ServerRoute().get_one(session, request.headers['Authorization'], serverid)
	return result

@app.route('/v1/servers/<serverid>/bans', methods=['GET', 'POST'])
def bans(serverid):
	serverid = int(serverid)
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
			result = BanRoute().post_collection(session, request.headers['Authorization'], serverid, request.json['banned_word'])
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
	elif request.method == 'GET':
		result = jsonify(BanRoute().get_collection(session, request.headers['Authorization'], serverid))
	return result

@app.route('/v1/servers/<serverid>/bans/<banid>', methods=['GET', 'POST'])
def ban(serverid, banid):
	serverid = int(serverid)
	banid = int(banid)
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
			result = BanRoute().post_one(session, request.headers['Authorization'], banid, request.json['banned_word'])
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
	elif request.method == 'GET':
		result = BanRoute().get_one(session, request.headers['Authorization'], banid)
	return result

@app.route('/v1/messages', methods=['POST'])
def message():
	session = start_session()
	result = None
	try:
		result = MessageRoute().post(session, request.headers['Authorization'], request.json)
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()
	return result

#app.run()