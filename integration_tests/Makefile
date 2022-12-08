.ONESHELL:

WAZO_ROOT=$(HOME)/wazo
DENV_PATH=$(WAZO_ROOT)/denv/denv
MANAGE_DB_DIR=$(WAZO_ROOT)/xivo-manage-db
DOCKER=$(shell which docker)

IMAGE_TAG=local
confgend: DOCKERFILE=./docker/Dockerfile-confgend
confgend: IMAGE_NAME=wazoplatform/wazo-confgend-test
confgend: $(DOCKERFILE) $(shell git ls-files)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) ..


db: DOCKERFILE=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile
db: IMAGE_NAME=wazoplatform/wazo-confd-db-test
db: $(DOCKERFILE)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) $(MANAGE_DB_DIR)


egg-info:
	$(MAKE) -C .. egg-info


test-setup: confgend db egg-info
	# generate default settings for compose stack
	$(MAKE) -C assets .env
	# check docker-compose
	which docker-compose && docker-compose --version && echo "docker-compose available!"


test: test-setup
	pytest -v suite/


VENV_DIR=.venv

PYTHON=$(shell which python3)
$(VENV_DIR):
	$(PYTHON) -m venv --clear $(VENV_DIR)

venv: $(VENV_DIR)
	. $(VENV_DIR)/bin/activate
	pip install -U -r test-requirements.txt


clean:
	rm -rf $(VENV_DIR)


.PHONY: test-setup test egg-info venv clean confgend db
