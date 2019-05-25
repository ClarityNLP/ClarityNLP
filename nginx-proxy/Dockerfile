FROM jwilder/nginx-proxy:alpine

RUN apk add --no-cache \
  apache2-utils

COPY htpasswd.sh /app/htpasswd.sh
RUN chmod +x /app/htpasswd.sh

COPY custom.conf /etc/nginx/conf.d/custom.conf

CMD ["/app/htpasswd.sh", "forego", "start", "-r"]
