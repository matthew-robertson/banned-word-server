
from sqlalchemy import Column, Boolean, Integer
from sqlalchemy.orm import relationship
from models import Base

class Server(Base):
	__tablename__ = 'server'

	server_id = Column(Integer, primary_key=True)
	awake = Column(Boolean)
	timeout_duration_seconds = Column(Integer, nullable=False)
	banned_words = relationship("Ban")
