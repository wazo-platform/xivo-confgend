import subprocess
import pytest
from wazo_test_helpers import asset_launching_test_case
import pathlib
import sys
from typing import List, Iterable


INTERNAL_CONFGEND_PORT = 8669
DEFAULT_CONFGEND_CLIENT_TIMEOUT = 10
DEFAULT_TIMEOUT = 10

@pytest.fixture(scope="class")
def pjsip_void_conf(request):
    with open("suite/pjsip_void.conf") as file:
        conf = file.readlines()

    request.cls.pjsip_void_conf = conf


def normalize_lines(line_stream: Iterable[str]):
    for line in line_stream:
        line = line.strip()
        if line:
            yield line


def lines(text: str):
    return text.splitlines()


def run(cmd: List[str], timeout: int = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
    except subprocess.CalledProcessError as ex:
        print(ex.stderr)
        raise
    return result


class BaseTestCase(asset_launching_test_case.AssetLaunchingTestCase):
    service = "confgend"
    assets_root = pathlib.Path(__file__).parent.parent / "assets"
    asset = "base"

    def docker_exec(
        cls, cmd: List[str], service_name: str = None
    ) -> subprocess.CompletedProcess:
        service_name = service_name or cls.service
        docker_command = [
            "docker-compose",
            *cls._docker_compose_options(),
            "exec",
            service_name,
        ] + cmd
        try:
            completed = run(docker_command)
        except subprocess.CalledProcessError as ex:
            print(ex.stderr, file=sys.stderr)
            raise
        return completed

    @classmethod
    def client(cls, args):
        # going through host local port-map
        host = "127.0.0.1"
        timeout = DEFAULT_CONFGEND_CLIENT_TIMEOUT
        return run(
            [
                "wazo-confgen",
                "--port",
                str(cls.service_port(INTERNAL_CONFGEND_PORT)),
                "--host",
                host,
                "--timeout",
                str(timeout),
                *args,
            ],
            timeout,
        )


@pytest.mark.usefixtures("pjsip_void_conf")
class TestConfgenDefaults(BaseTestCase):
    def test_uuid_yml(self):
        completed = self.client(["wazo/uuid.yml"])
        assert completed.returncode == 0

    def test_provd_config_yml(self):
        completed = self.client(["provd/config.yml"])
        assert completed.returncode == 0

    def test_pjsip_conf(self):
        completed = self.client(["asterisk/pjsip.conf"])
        expected_lines = list(normalize_lines(self.pjsip_void_conf))
        actual_lines = list(normalize_lines(lines(completed.stdout)))
        assert actual_lines == expected_lines

    def test_features_conf(self):
        completed = self.client(["asterisk/features.conf"])
        assert completed.returncode == 0

    def test_extensions_conf(self):
        completed = self.client(["asterisk/extensions.conf"])
        assert completed.returncode == 0

    def test_queuerules_conf(self):
        completed = self.client(["asterisk/queuerules.conf"])
        assert completed.returncode == 0

    def test_queueskills_conf(self):
        completed = self.client(["asterisk/queueskills.conf"])
        assert completed.returncode == 0

    def test_queueskillrules_conf(self):
        completed = self.client(["asterisk/queueskillrules.conf"])
        assert completed.returncode == 0

    def test_iax_conf(self):
        completed = self.client(["asterisk/iax.conf"])
        assert completed.returncode == 0

    def test_queues_conf(self):
        completed = self.client(["asterisk/queues.conf"])
        assert completed.returncode == 0

    def test_confbridge_conf(self):
        completed = self.client(["asterisk/confbridge.conf"])
        assert completed.returncode == 0

    def test_modules_conf(self):
        completed = self.client(["asterisk/modules.conf"])
        assert completed.returncode == 0

    def test_musiconhold_conf(self):
        completed = self.client(["asterisk/musiconhold.conf"])
        assert completed.returncode == 0

    def test_hep_conf(self):
        completed = self.client(["asterisk/hep.conf"])
        assert completed.returncode == 0

    def test_rtp_conf(self):
        completed = self.client(["asterisk/rtp.conf"])
        assert completed.returncode == 0

    def test_voicemail_conf(self):
        completed = self.client(["asterisk/voicemail.conf"])
        assert completed.returncode == 0

    def test_res_parking_conf(self):
        completed = self.client(["asterisk/res_parking.conf"])
        assert completed.returncode == 0

    def test_sccp_conf(self):
        completed = self.client(["asterisk/sccp.conf"])
        assert completed.returncode == 0
