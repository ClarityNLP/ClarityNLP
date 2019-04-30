FROM mongo

COPY setup.js /docker-entrypoint-initdb.d/setup.js
COPY users.sh /docker-entrypoint-initdb.d/users.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["mongod"]
