from bannedWordServer import db

class Server(db.Model):
	__tablename__ = 'server'

	server_id = db.Column(db.Integer, primary_key=True)
	awake = db.Column(db.Boolean, default=True)
	timeout_duration_seconds = db.Column(db.Integer, nullable=False, default=1800)
	infracted_at = db.Column(db.String, nullable=False, default="-1")
	calledout_at = db.Column(db.String, nullable=False, default="-1")
	banned_words = db.relationship("Ban")

	def to_dict(self):
		entries = {}
		entries['server_id'] = self.server_id
		entries['timeout_duration_seconds'] = self.timeout_duration_seconds
		entries['banned_words'] = [word.to_dict() for word in self.banned_words]
		entries['awake'] = self.awake

		return entries