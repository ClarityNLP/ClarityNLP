FROM mongo:3.4.2

COPY users.sh /docker-entrypoint-initdb.d/users.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["mongod"]
