from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify

import config
from models.server import Server
from models.ban import Ban
from routes.serverroute import ServerRoute

_engine = create_engine('sqlite:///'+config.DB_LOCATION, echo=False)
_Session = sessionmaker(bind=_engine)

def start_session():
	return _Session()

app = Flask(__name__)

def request_wrapper(session, request_func):


@app.route('/v1/server')
def servers():
	session = start_session()
	result = ServerRoute().get_all(session)

	return result

@app.route('/v1/server/<serverid>', methods=['GET', 'POST'])
def server(serverid):
	session = start_session()
	
	if request.method == 'POST':
		try:
		    result = ServerRoute().post(session, serverid)
		    session.commit()
		    return result
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()
	if request.method == 'PUT':
		try:
		    result = ServerRoute().put(session, serverid, request.json)
		    session.commit()
		    return result
		except:
		    session.rollback()
		    raise
		finally:
		    session.close()

	
	result = ServerRoute().get_one(session, serverid)
	return result

#app.run()