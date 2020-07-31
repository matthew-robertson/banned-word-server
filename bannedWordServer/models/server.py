from bannedWordServer import db


class Server(db.Model):
    __tablename__ = "server"

    server_id = db.Column(db.Integer, primary_key=True)
    awake = db.Column(db.Boolean, default=True)
    prefix = db.Column(db.String, nullable=False, default="!vt")
    timeout_duration_seconds = db.Column(db.Integer, nullable=False, default=1800)
    infracted_at = db.Column(db.String, nullable=False, default="-1")
    calledout_at = db.Column(db.String, nullable=False, default="-1")
    banned_words = db.relationship("Ban")
    plan_mapping = db.relationship(
        "ServerPlan", uselist=False, cascade="delete", backref="server"
    )

    def to_dict(self):
        entries = {}
        entries["server_id"] = self.server_id
        entries["timeout_duration_seconds"] = self.timeout_duration_seconds
        entries["banned_words"] = [word.to_dict() for word in self.banned_words]
        entries["awake"] = self.awake
        entries["plan"] = self.plan_mapping.plan.to_dict()
        entries["prefix"] = self.prefix

        return entries

    def get_plan(self):
        return self.plan_mapping.plan
