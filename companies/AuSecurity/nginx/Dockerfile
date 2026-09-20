FROM nginx:1.25-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our nginx config
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy frontend static files
COPY frontend/ /usr/share/nginx/html/

EXPOSE 80
