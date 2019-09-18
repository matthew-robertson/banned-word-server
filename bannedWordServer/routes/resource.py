from abc import ABC, abstractmethod

class Resource(ABC):
	@abstractmethod
	def get_all(session, id):
		pass

	@abstractmethod
	def get_one(session, id):
		pass

	def post(session):
		pass

	def put(session):
		pass

	def patch(session):
		pass

	def delete(session, id):
		pass