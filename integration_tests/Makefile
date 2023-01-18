.ONESHELL:


test-setup: image/confgend-test image/db egg-info
	# generate default settings for compose stack
	$(MAKE) -C assets .env
	# check docker-compose
	which docker-compose && docker-compose --version && echo "docker-compose available!"


define activate_venv =
	. $(VENV_DIR)/bin/activate
endef


test: test-setup venv
	$(activate_venv)
	pytest -v suite/


WAZO_ROOT=$(HOME)/wazo
DENV_PATH=$(WAZO_ROOT)/denv/denv

DOCKER=$(shell which docker)

IMAGE_TAG=local

image/confgend-base: IMAGE_NAME=wazoplatform/wazo-confgend
image/confgend-base: DOCKERFILE=../Dockerfile
image/confgend-base: $(DOCKERFILE) $(shell git ls-files)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) ..


image/confgend-test: DOCKERFILE=./docker/Dockerfile-confgend
image/confgend-test: IMAGE_NAME=wazoplatform/wazo-confgend-test
image/confgend-test: $(DOCKERFILE) $(shell git ls-files) image/confgend-base	
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) ..


ifdef MANAGE_DB_DIR
MANAGE_DB_TARGET=local
else
MANAGE_DB_TARGET=docker.io
endif


image/db/local: DOCKERFILE=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile
image/db/local: IMAGE_NAME=wazoplatform/wazo-confgend-db-test
image/db/local: $(DOCKERFILE)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) $(MANAGE_DB_DIR)


image/db/docker.io: PULL_SRC=docker.io/wazoplatform/wazo-confd-db-test:latest
image/db/docker.io: IMAGE_NAME=wazoplatform/wazo-confgend-db-test
image/db/docker.io:
	$(DOCKER) pull $(PULL_SRC)
	$(DOCKER) tag $(PULL_SRC) $(IMAGE_NAME):$(IMAGE_TAG)

image/db: image/db/$(MANAGE_DB_TARGET)

egg-info:
	cd .. && python3 setup.py egg_info


VENV_DIR=.venv

PYTHON=$(shell which python3)
$(VENV_DIR):
	$(PYTHON) -m venv --clear $(VENV_DIR)

venv: $(VENV_DIR) test-requirements.txt
	. $(VENV_DIR)/bin/activate
	pip install -U --force-reinstall -r test-requirements.txt


clean:
	rm -rf $(VENV_DIR)


.PHONY: test-setup test egg-info venv clean image/confgend-test image/confgend-base image/db image/db/local image/db/docker.io
