from abc import ABC, abstractmethod

class Resource(ABC):
	@abstractmethod
	def get_collection(self, session, id):
		pass

	@abstractmethod
	def get_one(self, session, id):
		pass