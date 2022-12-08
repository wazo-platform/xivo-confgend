DOCKER_COMPOSE=docker-compose
WAZO_ROOT=$(HOME)/wazo
DENV_PATH=$(WAZO_ROOT)/denv/denv

image/confgend:
	# build confgend
	$(MAKE) -C docker confgend IMAGE_TAG=local

image/db:
	# build db
	$(MAKE) -C docker db IMAGE_TAG=local

egg-info:
	$(MAKE) -C .. egg-info


test-setup: image/confgend image/db egg-info
	# check docker-compose
	which docker-compose && docker-compose --version
	# check denv
	test -e $(DENV_PATH) && source $(DENV_PATH) && type denv

VENV_DIR=.venv

PYTHON=$(shell which python3)
$(VENV_DIR):
	$(PYTHON) -m venv --clear $(VENV_DIR)

venv: $(VENV_DIR)
	. $(VENV_DIR)/bin/activate
	pip install -U -r test-requirements.txt


clean:
	rm -rf $(VENV_DIR)

.PHONY: test-setup test egg-info image/confgend image/db venv
