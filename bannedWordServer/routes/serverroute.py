from bannedWordServer.auth import authenticateBotOnly, authenticateBotOrServerAdmin
from bannedWordServer.constants.errors import (
    NotFoundError,
    InvalidTypeError,
    DuplicateResourceError,
    AuthenticationError,
    ValidationError,
)
from bannedWordServer.models import Ban, BanRecord, Server, ServerPlan
from bannedWordServer.routes.resource import Resource


class ServerRoute(Resource):
    def get_collection(self, session, authToken):
        if not authenticateBotOnly(authToken):
            raise AuthenticationError
        result = session.query(Server).all()
        result = [row.to_dict() for row in result]

        return result

    def get_one(self, session, authToken, serverid: str) -> dict:
        try:
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError
        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError

        result = session.query(Server).filter_by(server_id=serverid).first()
        if not result:
            raise NotFoundError
        return result.to_dict()

    def post_collection(self, session, authToken, serverid: str) -> dict:
        try:
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError
        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError

        already_exists = session.query(Server).filter_by(server_id=serverid).first()
        if already_exists:
            raise DuplicateResourceError

        default_ban = Ban(server_id=serverid)
        default_record = BanRecord(server_banned_word=default_ban)
        new_server = Server(server_id=serverid, banned_words=[default_ban])
        default_plan = ServerPlan(server_id=serverid, plan_id=1)
        session.add(new_server)
        session.add(default_ban)
        session.add(default_record)
        session.add(default_plan)
        return self.get_one(session, authToken, serverid)

    def partial_update(
        self, session, authToken, serverid: str, modified_params: dict
    ) -> dict:
        try:
            serverid = int(serverid)
        except ValueError:
            raise InvalidTypeError
        if not authenticateBotOrServerAdmin(serverid, authToken):
            raise AuthenticationError

        server_to_modify = session.query(Server).filter_by(server_id=serverid).first()
        if not server_to_modify:
            raise NotFoundError

        if "awake" in modified_params.keys():
            awake: bool = modified_params["awake"]
            if not isinstance(awake, bool):
                raise InvalidTypeError
            server_to_modify.awake = awake

        if "timeout_duration_seconds" in modified_params.keys():
            timeout_duration_seconds: int = modified_params["timeout_duration_seconds"]
            if not isinstance(timeout_duration_seconds, int):
                raise InvalidTypeError
            if timeout_duration_seconds >= 100000000:
                raise ValidationError
            server_to_modify.timeout_duration_seconds = timeout_duration_seconds

        if "prefix" in modified_params.keys():
            prefix: str = modified_params["prefix"]
            if not isinstance(prefix, str):
                raise InvalidTypeError
            if len(prefix) > 11:
                raise ValidationError
            server_to_modify.prefix = prefix
        return self.get_one(session, authToken, serverid)

    def delete(self, session, serverid):
        pass
