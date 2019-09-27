from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.orm import relationship

from bannedWordServer.models import Base

class Server(Base):
	__tablename__ = 'server'

	server_id = Column(Integer, primary_key=True)
	awake = Column(Boolean, default=True)
	timeout_duration_seconds = Column(Integer, nullable=False, default=1800)
	infracted_at = Column(String, nullable=False, default="-1")
	calledout_at = Column(String, nullable=False, default="-1")
	banned_words = relationship("Ban")

	def to_dict(self):
		entries = {}
		entries['server_id'] = self.server_id
		entries['timeout_duration_seconds'] = self.timeout_duration_seconds
		entries['banned_words'] = [word.to_dict() for word in self.banned_words]
		entries['awake'] = self.awake

		return entries