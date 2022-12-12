.ONESHELL:

WAZO_ROOT=$(HOME)/wazo
DENV_PATH=$(WAZO_ROOT)/denv/denv
MANAGE_DB_DIR=$(WAZO_ROOT)/xivo-manage-db
DOCKER=$(shell which docker)

IMAGE_TAG=local

image/confgend-base:
	$(MAKE) -C .. build/docker


image/confgend-test: DOCKERFILE=./docker/Dockerfile-confgend
image/confgend-test: IMAGE_NAME=wazoplatform/wazo-confgend-test
image/confgend-test: $(DOCKERFILE) $(shell git ls-files) image/confgend-base
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) ..

DB_RECIPE=build
DB_PULL_SRC=docker.io/wazoplatform/wazo-confd-db-test:latest
image/db: DOCKERFILE=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile
image/db: IMAGE_NAME=wazoplatform/wazo-confgend-db-test
image/db: $(DOCKERFILE)
ifeq ($(DB_RECIPE),build)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) $(MANAGE_DB_DIR)
else ifeq ($(DB_RECIPE),pull)
	$(DOCKER) pull $(DB_PULL_SRC)
	$(DOCKER) tag $(DB_PULL_SRC) $(IMAGE_NAME):$(IMAGE_TAG)
endif

egg-info:
	$(MAKE) -C .. egg-info


test-setup: image/confgend-test image/db egg-info
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


.PHONY: test-setup test egg-info venv clean image/confgend-test image/confgend-base image/db
