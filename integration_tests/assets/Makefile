.ONESHELL:

# Generate a .env file for docker-compose variables
INTEGRATION_TEST_TIMEOUT?=10
WAZO_ROOT?=$(HOME)/wazo
CONFGEND_SRC?=$(shell realpath ../..)
.env: $(MAKEFILE)
	cat >$@ <<- EOF
	CONFGEND_SRC=$(CONFGEND_SRC)
	INTEGRATION_TEST_TIMEOUT=$(INTEGRATION_TEST_TIMEOUT)
	EOF
