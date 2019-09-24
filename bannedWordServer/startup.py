from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request

import config
from models.ban import Ban
from models.server import Server
from routes.banroute import BanRoute
from routes.messageroute import MessageRoute
from routes.serverroute import ServerRoute

_engine = create_engine('sqlite:///'+config.DB_LOCATION, echo=False)
_Session = sessionmaker(bind=_engine)

def start_session():
	return _Session()

app = Flask(__name__)

@app.route('/v1/servers', methods=['GET', 'POST'])
def servers():
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
		    result = ServerRoute().post_collection(session, request.json['server_id'])
		    session.commit()
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()
	elif request.method == 'GET':
		result = ServerRoute().get_collection(session)

	return result

@app.route('/v1/servers/<serverid>', methods=['GET', 'POST'])
def server(serverid):
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
		    result = ServerRoute().partial_update(session, serverid, request.json)
		    session.commit()
		    return result
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()
	elif request.method == 'GET':
		result = ServerRoute().get_one(session, serverid)
	return result

@app.route('/v1/servers/<serverid>/bans', methods=['GET', 'POST'])
def bans(serverid):
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
			result = BanRoute().post_collection(session, serverid, request.json['banned_word'])
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
	elif request.method == 'GET':
		result = BanRoute().get_collection(session, serverid)
	return result

@app.route('/v1/servers/<serverid>/bans/<banid>', methods=['GET', 'POST'])
def ban(serverid, banid):
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
			result = BanRoute().post_one(session, banid, request.json['banned_word'])
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
	elif request.method == 'GET':
		result = BanRoute().get_one(session, banid)
	return result

@app.route('/v1/messages', methods=['POST'])
def message():
	session = start_session()
	result = None
	try:
		result = MessageRoute().post(session, request.json)
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()
	return result

app.run()