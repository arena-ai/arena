include .env
VERSION=$(shell cat VERSION)
PYTHON_CLIENT_VERSION=$(VERSION)

# Default target
all: build

build: build-backend build-frontend
	@echo "Build version: $(VERSION)"

push: version push-backend push-frontend
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

# Target to build the backend Docker image
build-frontend:
	$(MAKE) -C frontend build

# Target to push the backend Docker image
push-frontend:
	$(MAKE) -C frontend push

# Target to remove built Docker image from local machine
clean:
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean

# Dev environment
dev:
	docker compose up -d

# Deploy the helm app
kubernetes:
	helm upgrade --install ${RELEASE_NAME} kubernetes/arena \
	--set ingress-nginx.controller.service.loadBalancerIP=${PUBLIC_IP} \
	--set cluster.host=${CLUSTER_HOST} \
	--set docker.registry=${DOCKER_REGISTRY} \
	--set docker.password=${DOCKER_PASSWORD} \
	--set postgresql.user=${POSTGRES_USER} \
	--set postgresql.password=${POSTGRES_PASSWORD} \
	--set redis.password=${REDIS_PASSWORD} \
	--set backend.firstSuperUser.user=${FIRST_SUPERUSER} \
	--set backend.firstSuperUser.password=${FIRST_SUPERUSER_PASSWORD} \
	--set backend.usersOpenRegistration=${USERS_OPEN_REGISTRATION}

# Deploy the k8s dashboard
kubernetes-dashboard:
	helm upgrade --install kubernetes-dashboard kubernetes-dashboard \
	--repo https://kubernetes.github.io/dashboard/ \
	--create-namespace --namespace kubernetes-dashboard


.PHONY: all build push version build-backend push-backend build-frontend push-frontend clean dev kubernetes kubernetes-dashboard