VERSION=$(shell cat VERSION)
PYTHON_CLIENT_VERSION=$(VERSION)

# Default target
all: build

build: build-backend
	@echo "Build version: $(VERSION)"

push: version push-backend
	@echo "Push version: $(VERSION)"

version:
	@echo "Incrementing version number..."
	echo $(shell awk -F. \
        '/^[0-9]+\.[0-9]+\.[0-9]+$$/ {print $$1 "." $$2 "." ($$3+1)}' \
        VERSION) > VERSION

# Target to build the backend Docker image
build-backend:
	$(MAKE) -C backend build

# Target to push the backend Docker image
push-backend:
	$(MAKE) -C backend push

# Target to remove built Docker image from local machine
clean:
	$(MAKE) -C backend clean

kubernetes:
	source .env; helm upgrade --install ${RELEASE_NAME} kubernetes/arena \
	--set docker.password=${DOCKER_PASSWORD} \
	--set postgresql.user=${POSTGRES_USER} \
	--set postgresql.password=${POSTGRES_PASSWORD} \
	--set redis.password=${REDIS_PASSWORD} \
	--set backend.firstSuperUser.user=${FIRST_SUPERUSER} \
	--set backend.firstSuperUser.password=${FIRST_SUPERUSER_PASSWORD}


.PHONY: all build push version build-backend push-backend clean kubernetes