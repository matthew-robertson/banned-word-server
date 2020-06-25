from datetime import datetime, timedelta

from bannedWordServer import db

def current_time():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Plan(db.Model):
	__tablename__ = 'plan'

	plan_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	bannings_allowed = db.Column(db.Integer, nullable=False)
	created_at = db.Column(db.String, 
		nullable=False,
		default=current_time())
	updated_at = db.Column(db.String,
		nullable=False,
		default=current_time(),
		onupdate=current_time)
	server_mapping = db.relationship("ServerPlan", cascade="delete", backref="plan")

	def to_dict(self):
		entry = {}
		entry['plan_id'] = self.plan_id
		entry['name'] = self.name
		entry['bannings_allowed'] = self.bannings_allowed

		return entry