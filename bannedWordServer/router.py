from flask import jsonify, request

from bannedWordServer import app, db
from bannedWordServer.constants.errors import NotFoundError, DuplicateResourceError, InvalidTypeError, ValidationError, AuthenticationError
from bannedWordServer.models import Ban, Server
from bannedWordServer.routes import BanRoute, MessageRoute, ServerRoute

def start_session():
	return db.session

@app.errorhandler(AuthenticationError)
@app.errorhandler(ValidationError)
@app.errorhandler(InvalidTypeError)
@app.errorhandler(DuplicateResourceError)
@app.errorhandler(NotFoundError)
def handle_error(error):
	response = jsonify()
	response.status_code = error.status_code
	return response

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

@app.route('/v1/servers/<serverid>/bans/<banid>', methods=['GET', 'POST', 'DELETE'])
def ban(serverid, banid):
	session = start_session()
	result = None
	if request.method == 'POST':
		try:
			result = BanRoute().post_one(session, request.headers['Authorization'], serverid, banid, request.json['banned_word'])
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
	elif request.method == 'GET':
		result = BanRoute().get_one(session, request.headers['Authorization'], banid)
	elif request.method == 'DELETE':
		try:
			BanRoute().delete(session, request.headers['Authorization'], serverid, banid)
			result = jsonify()
			result.status_code = 204
			session.commit()
		except:
			session.rollback()
			raise
		finally:
			session.close()
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