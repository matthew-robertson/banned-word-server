from datetime import datetime

from bannedWordServer import db


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AuthorInfraction(db.Model):
    __tablename__ = "author_infraction"

    rowid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("author.user_id", onupdate="cascade"),
        nullable=False,
    )
    ban_id = db.Column(
        db.Integer,
        db.ForeignKey("server_banned_word.rowid", onupdate="cascade"),
        nullable=False,
    )
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

    def to_dict(self):
        entry = {}
        entry["user_id"] = self.user_id
        entry["ban_id"] = self.ban_id
        entry["infraction_count"] = self.infraction_count
        entry["updated_at"] = self.updated_at

        return entry
