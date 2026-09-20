FROM php:8.2-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libzip-dev \
    zip \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install \
    pdo \
    pdo_pgsql \
    zip \
    fileinfo

# Enable Apache modules
RUN a2enmod rewrite headers

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy composer files first for layer caching
COPY composer.json ./

# Install PHP dependencies
RUN composer install --no-dev --optimize-autoloader --no-interaction --no-progress

# Copy application source
COPY . .

# Set correct document root to public/
RUN sed -i 's|/var/www/html|/var/www/html/public|g' /etc/apache2/sites-available/000-default.conf

# Copy custom Apache vhost
COPY apache2/imager.conf /etc/apache2/sites-available/imager.conf
RUN a2dissite 000-default.conf && a2ensite imager.conf

# Create uploads directory for locally-stored profile pictures
RUN mkdir -p /var/www/html/public/uploads/avatars

# Fix permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/public \
    && chmod -R 775 /var/www/html/public/uploads

EXPOSE 80
