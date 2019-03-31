-include env.mk

env.mk: env.sh
	sed 's/"//g ; s/=/:=/' < $< > $@

DOCKER_VERSION := $(shell docker --version 2>/dev/null)
DOCKER_COMPOSE_VERSION := $(shell docker-compose --version 2>/dev/null)

all:
ifndef DOCKER_VERSION
    $(error "command docker is not available, please install Docker")
endif
ifndef DOCKER_COMPOSE_VERSION
    $(error "command docker-compose is not available, please install Docker")
endif

start-clarity:
		docker-compose up --build

stop-clarity:
		docker-compose down --remove-orphans

start-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml up --build

stop-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml down --remove-orphans

restart-clarity:
		docker-compose restart

rm-clarity:
		docker-compose kill
		docker-compose rm -f

reset-clarity: rm-clarity start-clarity
