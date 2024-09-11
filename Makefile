# Makefile

# Shell configuration
SHELL := /bin/bash

# Define variables
PYTHON_VERSION := 3.10
ALPINE_VERSION := 3.16
APP_NAME       := qa-app
VERSION        := 0.1.0
BASE_IMAGE_NAME := localhost
BACKEND_IMAGE  := $(BASE_IMAGE_NAME)/$(APP_NAME)-backend:$(VERSION)
FRONTEND_IMAGE := $(BASE_IMAGE_NAME)/$(APP_NAME)-frontend:$(VERSION)

# Docker Compose settings
DOCKER_COMPOSE := docker compose
DC_FILE        := deployments/docker-compose.yml
ENV_FILE       := .env

# Build information
BUILD_DATE     := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_REF      := $(VERSION)

# Determine the environment
ENV ?= development
ifeq ($(ENV),production)
    ENV_FILE := .env.production
else ifeq ($(ENV),ci)
    ENV_FILE := .env.ci
endif

# Load environment variables from .env file
include $(ENV_FILE)
export

# ==============================================================================
# Building containers

.PHONY: build
build: backend frontend

.PHONY: backend
backend:
	docker build \
		-f deployments/docker/Dockerfile.backend \
		-t $(BACKEND_IMAGE) \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg ENV=$(ENV) \
		.

.PHONY: frontend
frontend:
	docker build \
		-f deployments/docker/Dockerfile.frontend \
		-t $(FRONTEND_IMAGE) \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg BUILD_REF=$(VERSION) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg ENV=$(ENV) \
		.

# ==============================================================================
# Running the application

.PHONY: run
run:
	$(DOCKER_COMPOSE) -f $(DC_FILE) --env-file $(ENV_FILE) up -d

.PHONY: run-services
up:
	@if [ -z "$(SERVICE1)" ] || [ -z "$(SERVICE2)" ]; then \
		echo "Usage: make run-services SERVICE1=<service1> SERVICE2=<service2>"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) -f $(DC_FILE) --env-file $(ENV_FILE) up -d $(SERVICE1) $(SERVICE2)

.PHONY: stop
stop:
	$(DOCKER_COMPOSE) -f $(DC_FILE) down

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) -f $(DC_FILE) logs -f

# ==============================================================================
# Development helpers

.PHONY: shell-backend
shell-backend:
	$(DOCKER_COMPOSE) -f $(DC_FILE) exec backend /bin/sh

.PHONY: shell-frontend
shell-frontend:
	$(DOCKER_COMPOSE) -f $(DC_FILE) exec frontend /bin/sh

.PHONY: clean
clean:
	docker system prune -f

# ==============================================================================
# Help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build            : Build all Docker images"
	@echo "  backend          : Build backend Docker image"
	@echo "  frontend         : Build frontend Docker image"
	@echo "  run              : Run the application using Docker Compose"
	@echo "  run-services     : Run two specific services (Usage: make run-services SERVICE1=<service1> SERVICE2=<service2>)"
	@echo "  stop             : Stop the application"
	@echo "  logs             : View application logs"
	@echo "  shell-backend    : Open a shell in the backend container"
	@echo "  shell-frontend   : Open a shell in the frontend container"
	@echo "  clean            : Clean up Docker system"
	@echo "  help             : Show this help message"
