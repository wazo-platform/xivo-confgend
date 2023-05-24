# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import re
import pathlib
import subprocess
from collections.abc import Iterable

from wazo_test_helpers import asset_launching_test_case

from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.helpers.db_utils import session_scope
from sqlalchemy.orm import Session
from xivo_dao.helpers.db_manager import init_db_from_config


INTERNAL_CONFGEND_PORT = 8669
DEFAULT_CONFGEND_CLIENT_TIMEOUT = 10
DEFAULT_TIMEOUT = 10


def normalize_lines(line_stream: Iterable[str]):
    for line in line_stream:
        line = line.strip()
        if line:
            yield line


def normalize_block(text: str) -> str:
    lines = [l for l in text.split("\n") if l]
    lead_ws = re.compile(r"^[ \t]+")
    leads = [lead_ws.match(l) for l in lines]
    if not all(leads):
        return text
    else:
        common_end_pos = min(m.end() for m in leads)
        print("common_end_pos", common_end_pos)
        return "\n".join(l[common_end_pos:] for l in lines)


def run(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, timeout=timeout
    )
    return result


def read_conf_file(path):
    with open(path) as file:
        conf = file.readlines()
        return list(normalize_lines(conf))


class BaseTestCase(asset_launching_test_case.AssetLaunchingTestCase):
    service = "confgend"
    assets_root = pathlib.Path(__file__).parent.parent / "assets"
    asset = "base"

    @classmethod
    def confgen(cls, args):
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
    def setUpClass(cls):
        super().setUpClass()
        host = "127.0.0.1"
        port = cls.service_port(5432, 'postgres')
        init_db_from_config({
            "db_uri": f"postgresql://asterisk:proformatique@{host}:{port}/asterisk"
        })

    def load_provisioning(self, data: dict):
        session: Session
        with session_scope() as session:
            provisioning_conf = session.query(Provisioning).first()
            for key, value in data.items():
                setattr(provisioning_conf, key, value)



class TestConfgenDefaults(BaseTestCase):
    def test_uuid_yml(self):
        completed = self.confgen(["wazo/uuid.yml"])
        assert completed.returncode == 0

    def test_provd_config_yml(self):
        completed = self.confgen(["provd/config.yml"])
        assert completed.returncode == 0

    def test_provd_network_yml(self):
        expected = list(normalize_lines(normalize_block('''
        general:
          http_port: 8667
        ''').splitlines()))
        completed = self.confgen(["provd/network.yml"])
        assert completed.returncode == 0
        actual_lines = list(normalize_lines(completed.stdout.splitlines()))
        assert actual_lines == expected

    def test_pjsip_conf(self):
        completed = self.confgen(["asterisk/pjsip.conf"])
        expected_lines = normalize_block("""
        [global]
        user_agent = Wazo PBX
        endpoint_identifier_order = auth_username,username,ip

        [system]

        [transport-udp]
        type = transport
        protocol = udp
        bind = 0.0.0.0:5060

        [transport-wss]
        type = transport
        protocol = wss
        bind = 0.0.0.0:5060
        """).splitlines()
        actual_lines = list(normalize_lines(completed.stdout.splitlines()))
        assert actual_lines == expected_lines

    def test_features_conf(self):
        completed = self.confgen(["asterisk/features.conf"])
        assert completed.returncode == 0

    def test_extensions_conf(self):
        completed = self.confgen(["asterisk/extensions.conf"])
        assert completed.returncode == 0

    def test_queuerules_conf(self):
        completed = self.confgen(["asterisk/queuerules.conf"])
        assert completed.returncode == 0

    def test_queueskills_conf(self):
        completed = self.confgen(["asterisk/queueskills.conf"])
        assert completed.returncode == 0

    def test_queueskillrules_conf(self):
        completed = self.confgen(["asterisk/queueskillrules.conf"])
        assert completed.returncode == 0

    def test_iax_conf(self):
        completed = self.confgen(["asterisk/iax.conf"])
        assert completed.returncode == 0

    def test_queues_conf(self):
        completed = self.confgen(["asterisk/queues.conf"])
        assert completed.returncode == 0

    def test_confbridge_conf(self):
        completed = self.confgen(["asterisk/confbridge.conf"])
        assert completed.returncode == 0

    def test_modules_conf(self):
        completed = self.confgen(["asterisk/modules.conf"])
        assert completed.returncode == 0

    def test_musiconhold_conf(self):
        completed = self.confgen(["asterisk/musiconhold.conf"])
        assert completed.returncode == 0

    def test_hep_conf(self):
        completed = self.confgen(["asterisk/hep.conf"])
        assert completed.returncode == 0

    def test_rtp_conf(self):
        completed = self.confgen(["asterisk/rtp.conf"])
        assert completed.returncode == 0

    def test_voicemail_conf(self):
        completed = self.confgen(["asterisk/voicemail.conf"])
        assert completed.returncode == 0

    def test_res_parking_conf(self):
        completed = self.confgen(["asterisk/res_parking.conf"])
        assert completed.returncode == 0

    def test_sccp_conf(self):
        completed = self.confgen(["asterisk/sccp.conf"])
        assert completed.returncode == 0



class TestConfgenCustom(BaseTestCase):
    def test_provd_network_yml_custom_ip_and_port(self):
        output = normalize_block('''
        general:
          external_ip: 10.40.10.1
          http_port: 8665
        ''')
        data = dict(net4_ip="10.40.10.1", http_port=8665)
        self.load_provisioning(data)
        completed = self.confgen(["provd/network.yml"])
        assert completed.returncode == 0
        ref_lines = list(normalize_lines(output.splitlines()))
        actual_lines = list(normalize_lines(completed.stdout.splitlines()))
        assert actual_lines == ref_lines
