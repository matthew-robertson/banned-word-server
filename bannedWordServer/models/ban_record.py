from datetime import datetime, timedelta

from bannedWordServer import db

def current_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class BanRecord(db.Model):
	__tablename__ = 'ban_record'

	rowid = db.Column(db.Integer, primary_key=True)
	ban_id = db.Column(db.Integer, db.ForeignKey('server_banned_word.rowid', onupdate="cascade"), nullable=False)
	record_seconds = db.Column(db.Integer, nullable=False, default=0)
	created_at = db.Column(db.String, 
		nullable=False,
		default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	updated_at = db.Column(db.String,
		nullable=False,
		default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
		onupdate=current_time)

	def to_dict(self):
		entry = {}
		entry['record_seconds'] = self.record_seconds
		entry['updated_at'] = self.updated_at

		return entry