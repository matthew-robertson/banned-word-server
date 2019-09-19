from sqlalchemy import Column, Integer, String, ForeignKey
from datetime import datetime, timedelta

from models import Base

class Ban(Base):
	__tablename__ = 'server_banned_word'

	rowid = Column(Integer, primary_key=True)
	banned_word = Column(String, nullable=False, default='defaultbannedword')
	server_id = Column(Integer, ForeignKey('server.server_id'), nullable=False)
	infracted_at = Column(String, nullable=False, default=datetime.now())
	calledout_at = Column(String, nullable=False, default=datetime.now() - timedelta(seconds=1800))

	def to_dict(self):
		entries = {}
		entries['server_id'] = self.server_id
		entries['rowid'] = self.rowid
		entries['banned_word'] = self.banned_word
		entries['infracted_at'] = self.infracted_at
		entries['calledout_at'] = self.calledout_at

		return entries
