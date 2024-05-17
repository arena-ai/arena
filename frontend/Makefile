include ../.env
IMAGE_NAME=${DOCKER_IMAGE_FRONTEND}
TAG=latest
REGISTRY=sarus.azurecr.io

# Default target
all: build

# Target to build Docker image
build: Dockerfile package.json
	docker build -t $(IMAGE_NAME):$(TAG) .

# Target to push Docker image
push: build
	docker tag $(IMAGE_NAME):$(TAG) $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	docker image push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

# Target to remove built Docker image from local machine
clean:
	docker rmi $(IMAGE_NAME):$(TAG)
	docker rmi $(REGISTRY)/$(IMAGE_NAME):$(TAG)

.PHONY: build push all clean