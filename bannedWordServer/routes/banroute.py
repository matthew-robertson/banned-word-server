from confusables import is_confusable
from datetime import datetime, timedelta

from bannedWordServer.constants.errors import (
    PlanError,
    ValidationError,
    DuplicateResourceError,
    NotFoundError,
    InvalidTypeError,
    AuthenticationError,
)
from bannedWordServer.models import Ban, Server, BanRecord
from bannedWordServer.routes.resource import Resource
from bannedWordServer.auth import authenticateBotOnly, authenticateBotOrServerAdmin


class BanRoute(Resource):
    def get_collection(self, session, authToken, serverid: int) -> dict:
        if not authenticateBotOnly(authToken):
            raise AuthenticationError
        try:
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError
        relevant_server = session.query(Server).filter_by(server_id=serverid).first()
        if not relevant_server:
            raise NotFoundError

        result = session.query(Ban).filter_by(server_id=serverid).all()
        result = [row.to_dict() for row in result]
        return result

    def get_one(self, session, authToken, banid: int) -> dict:
        if not authenticateBotOnly(authToken):
            raise AuthenticationError
        try:
            banid = int(banid)
        except ValueError:
            raise InvalidTypeError
        result = session.query(Ban).filter_by(rowid=banid).first()
        if not result:
            raise NotFoundError
        return result.to_dict()

    def post_collection(
        self, session, authToken, serverid: int, banned_word: str
    ) -> dict:
        try:
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError

        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError
        if not isinstance(banned_word, str):
            raise InvalidTypeError

        server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
        if not server_to_modify:
            raise NotFoundError

        if (
            len(server_to_modify.banned_words)
            >= server_to_modify.get_plan().bannings_allowed
        ):
            raise PlanError

        already_exists = any(
            [
                is_confusable(banned_word, ban.banned_word)
                for ban in server_to_modify.banned_words
            ]
        )
        if already_exists:
            raise DuplicateResourceError

        new_ban = Ban(
            server_id=serverid,
            banned_word=banned_word,
            infracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            calledout_at=(datetime.now() - timedelta(weeks=52)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        new_record = BanRecord(server_banned_word=new_ban)

        session.add(new_ban)
        session.add(new_record)
        return (
            session.query(Ban)
            .filter_by(server_id=serverid, banned_word=banned_word)
            .first()
            .to_dict()
        )

    def post_one(
        self, session, authToken, serverid: str, banid: str, banned_word: str
    ) -> dict:
        try:
            serverid = int(serverid)
            banid = int(banid)
        except ValueError:
            raise InvalidTypeError

        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError
        if not isinstance(banned_word, str):
            raise InvalidTypeError
        server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
        if not server_to_modify:
            raise NotFoundError

        if (
            len(server_to_modify.banned_words)
            > server_to_modify.get_plan().bannings_allowed
        ):
            raise PlanError

        ban_to_modify = (
            session.query(Ban).filter_by(server_id=serverid, rowid=banid).first()
        )
        record_to_modify = session.query(BanRecord).filter_by(ban_id=banid).first()
        if not ban_to_modify or not record_to_modify:
            raise NotFoundError

        already_exists = any(
            [
                is_confusable(banned_word, ban.banned_word)
                for ban in server_to_modify.banned_words
            ]
        )
        if already_exists:
            raise DuplicateResourceError

        ban_to_modify.banned_word = banned_word
        ban_to_modify.infracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ban_to_modify.calledout_at = (datetime.now() - timedelta(weeks=52)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        record_to_modify.reinitialize()

        return self.get_one(session, authToken, banid)

    def delete(self, session, authToken, serverid: str, banid: str):
        try:
            banid = int(banid)
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError
        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError

        server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
        if not server_to_modify:
            raise NotFoundError
        if len(server_to_modify.banned_words) == 1:
            raise ValidationError

        ban = session.query(Ban).filter_by(server_id=serverid, rowid=banid).first()

        if not ban:
            raise NotFoundError
        session.delete(ban)
