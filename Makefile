# Builds the docker image
.PHONY: build
build:
	docker build -f Dockerfile.development -t cumplo-spotter .

# Starts the API server
.PHONY: start
start:
	docker run -d -p 8080:8080 -v ./:/app cumplo-spotter
