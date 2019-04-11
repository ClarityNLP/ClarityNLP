-include env.mk

env.mk: env.sh
	sed 's/"//g ; s/=/:=/' < $< > $@

DOCKER_VERSION := $(shell docker --version 2>/dev/null)
DOCKER_COMPOSE_VERSION := $(shell docker-compose --version 2>/dev/null)

all:
ifndef DOCKER_VERSION
    $(error Makefile -- command docker is not available, please install Docker)
endif
ifndef DOCKER_COMPOSE_VERSION
    $(error Makefile -- command docker-compose is not available, please install Docker)
endif
ifeq ($(OS),Windows_NT)
    $(error Makefile -- local dns solution not ready for windows)
else
    UNAME_S := $(shell uname -s)
    $(info Makefile -- non windows distro detected)
ifeq ($(UNAME_S),Darwin)
    $(info Makefile -- OSX detected)
ifneq ("$(wildcard /etc/resolver/dev)","")
    $(info Makefile -- dev resolver already exists at /etc/resolver/dev)
else
    $(info Makefile -- dev resolver not found. Creating /etc/resolver/dev)
    $(shell sudo mkdir -p /etc/resolver/ && echo "nameserver 127.0.0.1" | sudo tee -a /etc/resolver/dev > /dev/null)
endif
endif
ifeq ($(UNAME_S),Linux)
    $(error local dns solution not ready for linux)
endif
endif

start-clarity:
		docker-compose up --build

stop-clarity:
		docker-compose down --remove-orphans

start-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml up --build

stop-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml down --remove-orphans

start-clarity-prod:
		docker-compose -f docker-compose.prod.yml up --build

stop-clarity-prod:
		docker-compose -f docker-compose.prod.yml down --remove-orphans

restart-clarity:
		docker-compose restart

rm-clarity:
		docker-compose kill
		docker-compose rm -f

reset-clarity: rm-clarity start-clarity
