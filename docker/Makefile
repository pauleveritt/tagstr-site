DOCKER_COMMAND=docker
BASE_IMAGE=alpine3.20
LABEL_PREFIX=koxudaxi/
OPTIONS=--load
BUILD_ARGS=
.PHONY: build dry-run update-submodule docker-python generate-dockerfile


build-all:
	ls docker | while read BASE_IMAGE;\
      do make build ;done

build-push-all:
	ls docker | while read BASE_IMAGE;\
      do make build-push ;done

build:
	@echo "Building with BASE_IMAGE=$(BASE_IMAGE)"
	if [ -z "$(BASE_IMAGE)" ]; then \
		echo "BASE_IMAGE is not set"; \
		exit 1; \
	fi
	if [ ! -d "docker/$(BASE_IMAGE)" ]; then \
		echo "docker/$(BASE_IMAGE) does not exist"; \
		exit 1; \
	fi
	cd docker && ${DOCKER_COMMAND} buildx build ${BUILD_ARGS}  -t ${LABEL_PREFIX}python:3.14.0a0-tag-strings-rebased-${BASE_IMAGE}  -t  ${LABEL_PREFIX}python:3.14.0a0-${BASE_IMAGE} ${BASE_IMAGE} ${OPTIONS}

build-push:
	make build OPTIONS="--push" BUILD_ARGS="--platform linux/amd64,linux/arm64"

dry-run:
	make build DOCKER_COMMAND="echo docker"

ls-base-image:
	ls docker

update-submodule:
	git submodule update --init --recursive
	git submodule foreach git pull origin support_tag_strings_rebased

docker-python:
	 make update-submodule

generate-dockerfile: docker-python
	cd docker-python && ./apply-templates.sh
	test ! -d "docker" && mkdir docker
	cp -frpv docker-python/3.14.0a0/* docker/
