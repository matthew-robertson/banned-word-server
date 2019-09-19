from abc import ABC, abstractmethod

class Resource(ABC):
	@abstractmethod
	def get_all(self, session, id):
		pass

	@abstractmethod
	def get_one(self, session, id):
		pass

	def post(self, session, id):
		pass

	def put(session):
		pass

	def patch(session):
		pass

	def delete(session, id):
		pass