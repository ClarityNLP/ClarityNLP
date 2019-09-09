-include env.mk

env.mk: env.sh
	sed 's/"//g ; s/=/:=/' < $< > $@

start-clarity:
		docker-compose -f docker-compose.yml pull && docker-compose -f docker-compose.yml up -d --build

stop-clarity:
		docker-compose -f docker-compose.yml down --remove-orphans

start-clarity-vhost:
		docker-compose -f docker-compose.vhost.yml pull && docker-compose -f docker-compose.vhost.yml up -d --build

stop-clarity-vhost:
		docker-compose -f docker-compose.vhost.yml down --remove-orphans

start-clarity-dev:
		docker-compose -f docker-compose.dev.yml up --build

stop-clarity-dev:
		docker-compose -f docker-compose.dev.yml down --remove-orphans

start-clarity-localhost:
		docker-compose -f docker-compose.localhost.yml pull && docker-compose -f docker-compose.localhost.yml up -d --build

stop-clarity-localhost:
		docker-compose -f docker-compose.localhost.yml down --remove-orphans

start-clarity-localhost-tls:
		docker-compose -f docker-compose.localhost.tls.yml pull && docker-compose -f docker-compose.localhost.tls.yml up -d --build

stop-clarity-localhost-tls:
		docker-compose -f docker-compose.localhost.tls.yml down --remove-orphans

restart-clarity:
		docker-compose restart

rm-clarity:
		docker-compose kill
		docker-compose rm -f

reset-clarity: rm-clarity start-clarity
