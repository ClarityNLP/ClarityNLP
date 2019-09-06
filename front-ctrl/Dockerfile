FROM nginx:1.15.2-alpine

# Nginx config
RUN rm -rf /etc/nginx/conf.d
COPY conf /etc/nginx

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
