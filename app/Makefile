SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:

deps:
	go mod tidy
	go mod vendor

build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

blockchain:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
.PHONY: blockchain

docker-image:
	docker build -f ./blockchain/Dockerfile -t "blockchain:latest" .
	docker build -f ./mining/Dockerfile -t "mining:latest" .
.PHONY: docker-image

docker-compose-up: docker-image
	docker-compose -f docker-compose.yml up --build
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose -f docker-compose.yml stop -t 1
	docker-compose -f docker-compose.yml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose -f docker-compose.yml logs -f
.PHONY: docker-compose-logs

test:
	pytest -s
.PHONY: test

demo:
	python3 client.py
.PHONY: demo

restart:
	make docker-compose-down
	make docker-compose-up
.PHONY: restart
