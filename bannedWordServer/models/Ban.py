from sqlalchemy import Column, Integer, String, ForeignKey

from models import Base

class Ban(Base):
	__tablename__ = 'server_banned_word'

	rowid = Column(Integer, primary_key=True)
	banned_word = Column(String, nullable=False)
	server_id = Column(Integer, ForeignKey('server.server_id'), nullable=False)
	infracted_at = Column(String, nullable=False)
	calledout_at = Column(String, nullable=False)
