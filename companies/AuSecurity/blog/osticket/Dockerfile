FROM php:8.2-apache-bookworm

ARG OSTICKET_VERSION=1.18.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl unzip \
       libfreetype6-dev libjpeg62-turbo-dev libpng-dev \
       libicu-dev libonig-dev libzip-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" mysqli gd intl mbstring zip opcache \
    && a2enmod rewrite \
    && rm -rf /var/lib/apt/lists/*

RUN rm -rf /var/www/html/* \
    && curl -fsSL \
       "https://github.com/osTicket/osTicket/releases/download/v${OSTICKET_VERSION}/osTicket-v${OSTICKET_VERSION}.zip" \
       -o /tmp/osticket.zip \
    && unzip -q /tmp/osticket.zip -d /tmp/osticket \
    && cp -a /tmp/osticket/upload/. /var/www/html/ \
    && cp /var/www/html/include/ost-sampleconfig.php /var/www/html/include/ost-config.php \
    && rm -rf /tmp/osticket /tmp/osticket.zip \
    && chown -R www-data:www-data /var/www/html \
    && chmod 0666 /var/www/html/include/ost-config.php

# Intentionally insecure training artifact.
RUN mkdir -p /var/www/html/archives
COPY backup.zip /var/www/html/archives/backup.zip
COPY vulnerable-lab.conf /etc/apache2/conf-available/vulnerable-lab.conf
RUN a2enconf vulnerable-lab \
    && chown -R www-data:www-data /var/www/html/archives \
    && chmod 0644 /var/www/html/archives/backup.zip

EXPOSE 80
