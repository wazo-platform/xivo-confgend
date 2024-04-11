# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from .helpers.base import BaseTestCase
from .helpers.utils import normalize_lines, read_conf_file


class TestConfgenDefaults(BaseTestCase):
    def test_uuid_yml(self):
        completed = self.confgen(["wazo/uuid.yml"])
        assert completed.returncode == 0

    def test_provd_config_yml(self):
        completed = self.confgen(["provd/config.yml"])
        assert completed.returncode == 0

    def test_pjsip_conf(self):
        completed = self.confgen(["asterisk/pjsip.conf"])
        expected_lines = read_conf_file("suite/pjsip_void.conf")
        actual_lines = list(normalize_lines(completed.stdout.splitlines()))
        assert actual_lines == expected_lines

    def test_features_conf(self):
        completed = self.confgen(["asterisk/features.conf"])
        assert completed.returncode == 0

    def test_extensions_conf(self):
        completed = self.confgen(["asterisk/extensions.conf"])
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
