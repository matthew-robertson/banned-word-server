from datetime import datetime, timedelta

from bannedWordServer import db

class Ban(db.Model):
	__tablename__ = 'server_banned_word'

	rowid = db.Column(db.Integer, primary_key=True)
	banned_word = db.Column(db.String, nullable=False, default='defaultbannedword')
	server_id = db.Column(db.Integer, db.ForeignKey('server.server_id'), nullable=False)
	infracted_at = db.Column(db.String, nullable=False, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	calledout_at = db.Column(db.String, nullable=False, default=(datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d %H:%M:%S"))
	record = db.relationship("BanRecord", uselist=False, cascade="delete", backref="server_banned_word")

	def to_dict(self):
		entries = {}
		entries['server_id'] = self.server_id
		entries['rowid'] = self.rowid
		entries['banned_word'] = self.banned_word
		entries['infracted_at'] = self.infracted_at
		entries['calledout_at'] = self.calledout_at
		entries['record'] = self.record.to_dict()

		return entries
