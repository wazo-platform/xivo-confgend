import subprocess
import pytest
from wazo_test_helpers import asset_launching_test_case
import pathlib
import sys
from typing import List, Iterable


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


def run(cmd: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, timeout=timeout
    )
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
            completed = run(docker_command, timeout=1)
        except subprocess.CalledProcessError as ex:
            print(ex.stderr, file=sys.stderr)
            raise
        return completed

    @classmethod
    def setUpClass(cls):
        super().setUpClass()


@pytest.mark.usefixtures("pjsip_void_conf")
class TestConfgenDefaults(BaseTestCase):
    def test_uuid_yml(self):
        completed = self.docker_exec(["wazo-confgen", "wazo/uuid.yml"])
        assert completed.returncode == 0

    def test_provd_config_yml(self):
        completed = self.docker_exec(["wazo-confgen", "provd/config.yml"])
        assert completed.returncode == 0

    def test_pjsip_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/pjsip.conf"])
        expected_lines = list(normalize_lines(self.pjsip_void_conf))
        actual_lines = list(normalize_lines(lines(completed.stdout)))
        assert actual_lines == expected_lines

    def test_features_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/features.conf"])
        assert completed.returncode == 0

    def test_extensions_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/extensions.conf"])
        assert completed.returncode == 0

    def test_queuerules_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/queuerules.conf"])
        assert completed.returncode == 0

    def test_queueskills_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/queueskills.conf"])
        assert completed.returncode == 0

    def test_queueskillrules_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/queueskillrules.conf"])
        assert completed.returncode == 0

    def test_iax_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/iax.conf"])
        assert completed.returncode == 0

    def test_queues_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/queues.conf"])
        assert completed.returncode == 0

    def test_confbridge_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/confbridge.conf"])
        assert completed.returncode == 0

    def test_modules_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/modules.conf"])
        assert completed.returncode == 0

    def test_musiconhold_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/musiconhold.conf"])
        assert completed.returncode == 0

    def test_hep_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/hep.conf"])
        assert completed.returncode == 0

    def test_rtp_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/rtp.conf"])
        assert completed.returncode == 0

    def test_voicemail_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/voicemail.conf"])
        assert completed.returncode == 0

    def test_res_parking_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/res_parking.conf"])
        assert completed.returncode == 0

    def test_sccp_conf(self):
        completed = self.docker_exec(["wazo-confgen", "asterisk/sccp.conf"])
        assert completed.returncode == 0
