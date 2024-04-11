# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from xivo_dao.alchemy.groupfeatures import GroupFeatures
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.resources.group import dao as group_dao

# from .helpers.utils import read_conf_file, run, normalize_lines
from .helpers.base import BaseTestCase, db, db_session  # noqa: F401

INTERNAL_CONFGEND_PORT = 8669
DEFAULT_CONFGEND_CLIENT_TIMEOUT = 10
DEFAULT_TIMEOUT = 10
TENANT_UUID = '00000000-0000-0000-0000-000000000000'


@pytest.fixture()
def tenant(db_session):  # noqa: F811
    tenant = Tenant(
        uuid=TENANT_UUID,
        slug='test',
    )
    db_session.add(tenant)
    db_session.flush()
    return tenant


@pytest.fixture()
def group(tenant):
    group = GroupFeatures(
        name='groupname',
        label='grouplabel',
        tenant_uuid=tenant.uuid,
        ring_strategy='linear',
        user_timeout=24,
        retry_delay=5,
        timeout=42,
        preprocess_subroutine='subroutine',
        mark_answered_elsewhere=0,
        ring_in_use=False,
        music_on_hold='default',
        caller_id_name='GROUP-',
        caller_id_mode='prepend',
    )

    group = group_dao.create(group)
    yield group
    group_dao.delete(group)


@pytest.mark.usefixtures('group')
class TestLinearGroupExtensionsConf(BaseTestCase):
    def test_simple_users_group(self):
        completed = self.confgen(["asterisk/extensions_group_linear.conf"])
        assert completed.stdout != ''
