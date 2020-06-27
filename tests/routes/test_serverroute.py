import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest import TestCase
from unittest.mock import patch

from bannedWordServer.constants.errors import (
    NotFoundError,
    InvalidTypeError,
    DuplicateResourceError,
    AuthenticationError,
    ValidationError,
)
from bannedWordServer import db
from bannedWordServer.models import Plan
from tests.utils.test_utils import create_server
from bannedWordServer.routes.serverroute import ServerRoute

Session = sessionmaker()
engine = create_engine("sqlite:///:memory:")
BOT_TOKEN = os.environ["BOT_TOKEN"]


class TestServerRouteGetCollection(TestCase):
    def setUp(self):
        db.Model.metadata.create_all(engine)
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)

    def test_serverroute_get_collection__no_elements(self):
        result = ServerRoute().get_collection(self.session, "Bot " + BOT_TOKEN)
        self.assertEqual(result, [])

    def test_serverroute_get_collection__one_element(self):
        create_server(self.session, server_id=1234)
        result = ServerRoute().get_collection(self.session, "Bot " + BOT_TOKEN)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["server_id"], 1234)

    def test_serverroute_get_collection__multiple_elements(self):
        create_server(self.session, server_id=1234)
        create_server(self.session, server_id=4321)
        result = ServerRoute().get_collection(self.session, "Bot " + BOT_TOKEN)
        self.assertEqual(len(result), 2)

    @patch("bannedWordServer.routes.serverroute.authenticateBotOrServerAdmin")
    def test_serverroute_get_collection__unauthorized(self, auth_mock):
        auth_mock.return_value = False
        create_server(self.session, server_id=1234)
        create_server(self.session, server_id=4321)
        self.assertRaises(
            AuthenticationError,
            ServerRoute().get_collection,
            self.session,
            "Bot " + "asdffdsa",
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()


class TestServerRouteGetOne(TestCase):
    def setUp(self):
        db.Model.metadata.create_all(engine)
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        server1, _ = create_server(self.session, server_id=1234)
        server2, _ = create_server(self.session, server_id=4321)
        self.expected_output = [server1.to_dict(), server2.to_dict()]

    def test_serverroute_get_one__good_request(self):
        result = ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, "1234")
        self.assertEqual(result, self.expected_output[0])

    @patch("bannedWordServer.routes.serverroute.authenticateBotOrServerAdmin")
    def test_serverroute_get_one__unauthorized(self, auth_mock):
        auth_mock.return_value = False
        self.assertRaises(
            AuthenticationError,
            ServerRoute().get_one,
            self.session,
            "Bot " + "asdffdsa",
            "1234",
        )

    def test_serverroute_get_one__not_found(self):
        self.assertRaises(
            NotFoundError,
            ServerRoute().get_one,
            self.session,
            "Bot " + BOT_TOKEN,
            "1111",
        )

    def test_serverroute_get_one__bad_input(self):
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().get_one,
            self.session,
            "Bot " + BOT_TOKEN,
            "asdf",
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()


class TestServerRoutePostCollection(TestCase):
    def setUp(self):
        db.Model.metadata.create_all(engine)
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)
        plan = Plan(plan_id=1, name="Test Plan", bannings_allowed=3)
        self.session.add(plan)

    def test_serverroute_post_collection__good_request(self):
        serverid = 1234
        result = ServerRoute().post_collection(
            self.session, "Bot " + BOT_TOKEN, str(serverid)
        )
        self.assertEqual(
            result,
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, str(serverid)),
        )

    def test_serverroute_post_collection__duplicate_request(self):
        serverid = 1234
        result = ServerRoute().post_collection(
            self.session, "Bot " + BOT_TOKEN, str(serverid)
        )
        self.assertEqual(
            result,
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, str(serverid)),
        )
        self.assertRaises(
            DuplicateResourceError,
            ServerRoute().post_collection,
            self.session,
            "Bot " + BOT_TOKEN,
            str(serverid),
        )

    @patch("bannedWordServer.routes.serverroute.authenticateBotOrServerAdmin")
    def test_serverroute_post_collection__unauthorized_request(self, auth_mock):
        auth_mock.return_value = False
        serverid = 1234
        self.assertRaises(
            AuthenticationError,
            ServerRoute().post_collection,
            self.session,
            "Bot " + "asdffdsa",
            str(serverid),
        )

    def test_serverroute_post_collection__bad_id_string_request(self):
        serverid = "asdf"
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().post_collection,
            self.session,
            "Bot " + BOT_TOKEN,
            str(serverid),
        )

    def test_serverroute_post_collection__bad_id_float_request(self):
        serverid = 1.23
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().post_collection,
            self.session,
            "Bot " + BOT_TOKEN,
            str(serverid),
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()


class TestServerRoutePartialUpdate(TestCase):
    def setUp(self):
        db.Model.metadata.create_all(engine)
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)

        self.serverid = "1234"
        create_server(self.session, server_id=self.serverid)

    def test_serverroute_partial_update__update_awake(self):
        update_params = {"awake": False}

        self.assertNotEqual(
            update_params["awake"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "awake"
            ],
        )

        ServerRoute().partial_update(
            self.session, "Bot " + BOT_TOKEN, self.serverid, update_params
        )
        self.assertEqual(
            update_params["awake"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "awake"
            ],
        )

    def test_serverroute_partial_update__update_timeout_duration(self):
        update_params = {"timeout_duration_seconds": 9001}

        self.assertNotEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

        ServerRoute().partial_update(
            self.session, "Bot " + BOT_TOKEN, self.serverid, update_params
        )
        self.assertEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

    def test_serverroute_partial_update__update_timeout_duration_too_long(self):
        update_params = {"timeout_duration_seconds": 777777777777777}

        self.assertNotEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

        self.assertRaises(
            ValidationError,
            ServerRoute().partial_update,
            self.session,
            "Bot " + BOT_TOKEN,
            self.serverid,
            update_params,
        )
        self.assertNotEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

    def test_serverroute_partial_update__update_all(self):
        update_params = {"awake": False}
        update_params["timeout_duration_seconds"] = 9001

        self.assertNotEqual(
            update_params["awake"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "awake"
            ],
        )
        self.assertNotEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

        ServerRoute().partial_update(
            self.session, "Bot " + BOT_TOKEN, self.serverid, update_params
        )
        self.assertEqual(
            update_params["awake"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "awake"
            ],
        )
        self.assertEqual(
            update_params["timeout_duration_seconds"],
            ServerRoute().get_one(self.session, "Bot " + BOT_TOKEN, self.serverid)[
                "timeout_duration_seconds"
            ],
        )

    def test_serverroute_partial_update__bad_server_id(self):
        update_params = {"awake": False}
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().partial_update,
            self.session,
            "Bot " + BOT_TOKEN,
            "asdf",
            update_params,
        )

    @patch("bannedWordServer.routes.serverroute.authenticateBotOrServerAdmin")
    def test_serverroute_partial_update__unauthorized(self, auth_mock):
        auth_mock.return_value = False

        update_params = {"awake": False}
        self.assertRaises(
            AuthenticationError,
            ServerRoute().partial_update,
            self.session,
            "",
            "1",
            update_params,
        )

    def test_serverroute_partial_update__nonexistant_server(self):
        update_params = {"awake": False}
        self.assertRaises(
            NotFoundError,
            ServerRoute().partial_update,
            self.session,
            "Bot " + BOT_TOKEN,
            9001,
            update_params,
        )

    def test_serverroute_partial_update__update_awake_invalid(self):
        update_params = {"awake": "asdf"}
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().partial_update,
            self.session,
            "Bot " + BOT_TOKEN,
            self.serverid,
            update_params,
        )

    def test_serverroute_partial_update__update_timeout_duration_invalid(self):
        update_params = {"timeout_duration_seconds": "asdf"}
        self.assertRaises(
            InvalidTypeError,
            ServerRoute().partial_update,
            self.session,
            "Bot " + BOT_TOKEN,
            self.serverid,
            update_params,
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()
        self.connection.close()
