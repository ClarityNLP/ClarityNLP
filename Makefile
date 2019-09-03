-include env.mk

env.mk: env.sh
	sed 's/"//g ; s/=/:=/' < $< > $@

start-clarity:
		docker-compose -f docker-compose.yml up --build

stop-clarity:
		docker-compose -f docker-compose.yml down --remove-orphans

start-clarity-dev:
		docker-compose -f docker-compose.dev.yml up --build

stop-clarity-dev:
		docker-compose -f docker-compose.dev.yml down --remove-orphans

start-clarity-localhost:
		docker-compose -f docker-compose.localhost.yml up --build

stop-clarity-localhost:
		docker-compose -f docker-compose.localhost.yml down --remove-orphans

start-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml up --build

stop-clarity-insecure:
		docker-compose -f docker-compose.insecure.yml down --remove-orphans

start-clarity-prod:
		docker-compose -f docker-compose.prod.yml up --build

stop-clarity-prod:
		docker-compose -f docker-compose.prod.yml down --remove-orphans

start-clarity-prod-local:
		docker-compose -f docker-compose.prod.dnsmasq.yml up --build

stop-clarity-prod-local:
		docker-compose -f docker-compose.prod.dnsmasq.yml down --remove-orphans

restart-clarity:
		docker-compose restart

rm-clarity:
		docker-compose kill
		docker-compose rm -f

reset-clarity: rm-clarity start-clarity
