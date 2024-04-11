import pathlib
import subprocess

import pytest
from wazo_test_helpers import asset_launching_test_case
from xivo_dao import init_db
from xivo_dao.helpers.db_manager import Session

from .utils import run

INTERNAL_CONFGEND_PORT = 8669
DEFAULT_CONFGEND_CLIENT_TIMEOUT = 10
INTERNAL_POSTGRES_PORT = 5432


@pytest.fixture
def db():
    return Session


@pytest.fixture
def db_session(db):
    try:
        session = db()
        yield session
        session.flush()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        db.remove()


class BaseTestCase(asset_launching_test_case.AssetLaunchingTestCase):
    service = "confgend"
    assets_root = pathlib.Path(__file__).parent.parent.parent / "assets"
    asset = "base"

    @classmethod
    def confgen(cls, args) -> subprocess.CompletedProcess:
        host = "127.0.0.1"
        port = cls.service_port(INTERNAL_CONFGEND_PORT, 'confgend')
        timeout = DEFAULT_CONFGEND_CLIENT_TIMEOUT
        return run(
            [
                "wazo-confgen",
                "--port",
                str(port),
                "--host",
                host,
                "--timeout",
                str(timeout),
                *args,
            ],
            timeout,
        )

    @classmethod
    def init_db(cls) -> None:
        db_port = cls.service_port(INTERNAL_POSTGRES_PORT, 'postgres')
        init_db(f'postgresql://asterisk:proformatique@localhost:{db_port}/asterisk')

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.init_db()
