.ONESHELL:

# all source files dependencies that should be considered for build
SRCFILES=$(shell fd -t f . .)


.PHONY: tests
tests: tests/default

.PHONY: tests/default
tests/default: tests/tox tests/integration

.PHONY: tests/tox
tests/tox:
	tox $(TOXARGS)

.PHONY: tests/bats
tests/bats:
	bats tests


.PHONY: egg-info
egg-info: wazo-confgend.egg-info

wazo-confgend.egg-info:
	python setup.py egg_info


# creation of development virtual environment
VENV:=$(PWD)/.venv
# python version used for development
TOXENV:=py37

$(VENV):
	tox --recreate --devenv $(VENV) -e $(TOXENV)

.PHONY: devenv
devenv: $(VENV)


## Generate installation files using setuptools
PYTHON=/usr/bin/env python3
INSTALL_PREFIX=/usr/local
INSTALL_ROOT=/
INSTALLOPTS+=-O

INSTALL_RECORD=.install
$(INSTALL_RECORD):
	$(PYTHON) setup.py install --record $(INSTALL_RECORD) \
	--prefix=$(INSTALL_PREFIX) --root=$(INSTALL_ROOT) \
	$(INSTALLOPTS)

.PHONY: install
install: $(INSTALL_RECORD)

.PHONY: uninstall
uninstall:
	cat $(INSTALL_RECORD) | xargs rm

# assumes a debian build environment
DEBIAN_BUILD_OUTPUT_DIR=.debian
$(DEBIAN_BUILD_OUTPUT_DIR)/%.deb: $(shell git ls-files)
	dpkg-buildpackage -us -uc
	mv ../$** $(DEBIAN_BUILD_OUTPUT_DIR)

build/debian:
	dpkg-buildpackage -us -uc


DOCKER=$(shell which docker)
IMAGE_NAME=wazoplatform/wazo-confgend
IMAGE_TAG=local
DOCKERFILE=./Dockerfile
IMAGE_ID_FILE=./.images/default.iid
.PHONY: build/docker
build/docker: $(DOCKERFILE) $(shell git ls-files)
	mkdir -p $$(dirname $(IMAGE_ID_FILE))
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) --iidfile $(IMAGE_ID_FILE) .


.PHONY: clean/tests
clean/tests:
	rm -rf .tests

# tox generate those files.
.PHONY: clean/tox
clean/tox:
	-rm -r .tox

.PHONY: clean/images
clean/images:
	-rm -r $$(dirname $(IMAGE_ID_FILE))

.PHONY: clean
clean: clean/tests clean/tox
