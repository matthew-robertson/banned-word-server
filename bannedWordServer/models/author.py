from datetime import datetime

from bannedWordServer import db


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Author(db.Model):
    __tablename__ = "author"

    user_id = db.Column(db.Integer, primary_key=True)
    infraction_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.String, nullable=False, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    updated_at = db.Column(
        db.String,
        nullable=False,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        onupdate=current_time,
    )
    infractions = db.relationship("AuthorInfraction")

    def to_dict(self):
        entry = {}
        entry["user_id"] = self.user_id
        entry["incraction_count"] = self.infraction_count
        entry["updated_at"] = self.updated_at
        entry["infractions"] = [infraction.to_dict() for infraction in self.infractions]

        return entry
