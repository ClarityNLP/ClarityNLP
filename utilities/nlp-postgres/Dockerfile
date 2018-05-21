FROM postgres

RUN apt-get update && apt-get -y install wget && apt-get -y install zip unzip

# COPY . .

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
