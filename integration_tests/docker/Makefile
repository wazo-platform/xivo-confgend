.ONESHELL:

IMAGE_DIR=./.images
MANAGE_DB_DIR=$(WAZO_ROOT)/xivo-manage-db
$(IMAGE_DIR):
	mkdir -p $(IMAGE_DIR)

DOCKER=$(shell which docker)
IMAGE_TAG=local
.PHONY: confgend
confgend: DOCKERFILE=./confgend.Dockerfile
confgend: IMAGE_NAME=wazoplatform/wazo-confgend-test
confgend: IMAGE_ID_FILE=$(IMAGE_DIR)/confgend.iid
confgend: $(DOCKERFILE) $(shell git ls-files) $(IMAGE_DIR)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) --iidfile $(IMAGE_ID_FILE) ../..


.PHONY: db
db: DOCKERFILE=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile
db: IMAGE_NAME=wazoplatform/wazo-confd-db-test
db: IMAGE_ID_FILE=$(IMAGE_DIR)/db.iid
db: $(DOCKERFILE) $(shell git ls-files) $(IMAGE_DIR)
	$(DOCKER) build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(DOCKERFILE) --iidfile $(IMAGE_ID_FILE) $(MANAGE_DB_DIR)


.PHONY: clean/images
clean/images:
	-rm -r $$(dirname $(IMAGE_ID_FILE))

.PHONY: clean
clean: clean/images
