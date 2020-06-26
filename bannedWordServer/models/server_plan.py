from datetime import datetime, timedelta

from bannedWordServer import db

def current_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ServerPlan(db.Model):
	__tablename__ = 'server_plan'

	rowid = db.Column(db.Integer, primary_key=True)
	server_id = db.Column(db.Integer, db.ForeignKey('server.server_id', onupdate="cascade"), nullable=False)
	plan_id = db.Column(db.Integer, db.ForeignKey('plan.plan_id'), nullable=False)
	created_at = db.Column(db.String, 
		nullable=False,
		default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	updated_at = db.Column(db.String,
		nullable=False,
		default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
		onupdate=current_time)

	def to_dict(self):
		entry = {}
		entry['plan_id'] = self.plan_id
		entry['server_id'] = self.server_id

		return entry

	def reinitialize(self):
		self.record_seconds = 0
		self.infraction_count = 0