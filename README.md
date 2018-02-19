xivo-confgend
=============
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-confgend)](https://jenkins.wazo.community/job/xivo-confgend)

xivo-confgend is a service for generating IPBX configuration files.


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```


Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
