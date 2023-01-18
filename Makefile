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


wazo-confgend.egg-info:
	python3 setup.py egg_info

.PHONY: egg-info
egg-info: wazo-confgend.egg-info



# creation of development virtual environment
VENV:=$(PWD)/.venv
# python version used for development
TOXENV:=py37

$(VENV):
	tox --recreate --devenv $(VENV) -e $(TOXENV)

.PHONY: devenv
devenv: $(VENV)



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
