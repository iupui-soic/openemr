# syntax=docker/dockerfile:1
# ============================================================================
# OpenEMR Dockerfile for seiri22 branch
# Based on upstream openemr-devops 8.0.1 pattern
# ============================================================================
# ============================================================================
# BASE IMAGE CONFIGURATION
# ============================================================================
ARG ALPINE_VERSION=3.22
FROM alpine:${ALPINE_VERSION} AS base
# PHP version configuration
ARG PHP_VERSION=8.4
ENV PHP_VERSION=${PHP_VERSION}
ARG PHP_VERSION_ABBR=${PHP_VERSION//./}
ENV PHP_VERSION_ABBR=${PHP_VERSION_ABBR}
# ============================================================================
# SYSTEM PACKAGE INSTALLATION
# ============================================================================
RUN apk --no-cache upgrade
RUN apk add --no-cache \
    apache2 \
    apache2-proxy \
    apache2-ssl \
    apache2-utils \
    bash \
    certbot \
    curl \
    dcron \
    git \
    imagemagick \
    mariadb-client \
    mariadb-connector-c \
    ncurses \
    nodejs \
    npm \
    openssl \
    openssl-dev \
    perl \
    rsync \
    shadow \
    tar
# Install PHP and all required extensions
RUN apk add --no-cache \
    php${PHP_VERSION_ABBR} \
    php${PHP_VERSION_ABBR}-apache2 \
    php${PHP_VERSION_ABBR}-bcmath \
    php${PHP_VERSION_ABBR}-calendar \
    php${PHP_VERSION_ABBR}-ctype \
    php${PHP_VERSION_ABBR}-curl \
    php${PHP_VERSION_ABBR}-dom \
    php${PHP_VERSION_ABBR}-fileinfo \
    php${PHP_VERSION_ABBR}-fpm \
    php${PHP_VERSION_ABBR}-gd \
    php${PHP_VERSION_ABBR}-iconv \
    php${PHP_VERSION_ABBR}-intl \
    php${PHP_VERSION_ABBR}-json \
    php${PHP_VERSION_ABBR}-ldap \
    php${PHP_VERSION_ABBR}-mbstring \
    php${PHP_VERSION_ABBR}-mysqli \
    php${PHP_VERSION_ABBR}-opcache \
    php${PHP_VERSION_ABBR}-openssl \
    php${PHP_VERSION_ABBR}-pdo \
    php${PHP_VERSION_ABBR}-pdo_mysql \
    php${PHP_VERSION_ABBR}-pecl-apcu \
    php${PHP_VERSION_ABBR}-pecl-imagick \
    php${PHP_VERSION_ABBR}-phar \
    php${PHP_VERSION_ABBR}-redis \
    php${PHP_VERSION_ABBR}-session \
    php${PHP_VERSION_ABBR}-simplexml \
    php${PHP_VERSION_ABBR}-soap \
    php${PHP_VERSION_ABBR}-sockets \
    php${PHP_VERSION_ABBR}-sodium \
    php${PHP_VERSION_ABBR}-tokenizer \
    php${PHP_VERSION_ABBR}-xml \
    php${PHP_VERSION_ABBR}-xmlreader \
    php${PHP_VERSION_ABBR}-xmlwriter \
    php${PHP_VERSION_ABBR}-xsl \
    php${PHP_VERSION_ABBR}-zip \
    php${PHP_VERSION_ABBR}-zlib
# ============================================================================
# APACHE CONFIGURATION
# ============================================================================
RUN sed -i 's/^Listen 80$/Listen 0.0.0.0:80/' /etc/apache2/httpd.conf
# ============================================================================
# USER AND PERMISSIONS CONFIGURATION
# ============================================================================
RUN usermod -u 1000 apache
# ============================================================================
# PHP CONFIGURATION
# ============================================================================
RUN ln -sf /usr/bin/php${PHP_VERSION_ABBR} /usr/bin/php
# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer
# ============================================================================
# MULTI-STAGE BUILD: OpenEMR Source and Dependencies
# ============================================================================
# Stage 1: Fetch OpenEMR source code from seiri22 branch
ARG OPENEMR_REPO=https://github.com/iupui-soic/openemr.git
ARG OPENEMR_BRANCH=seiri22
FROM base AS openemr-source
ARG OPENEMR_REPO
ARG OPENEMR_BRANCH
# Cache buster - pass a changing value (e.g., commit SHA) to invalidate cache
ARG CACHEBUST=unknown
RUN echo "Cache bust: ${CACHEBUST}" \
    && apk add --no-cache git \
    && git clone --single-branch --branch ${OPENEMR_BRANCH} ${OPENEMR_REPO} --depth 1 openemr \
    && rm -rf openemr/.git
# Stage 2: Install PHP dependencies (Composer)
FROM base AS openemr-composer
COPY --from=openemr-source /openemr /openemr
WORKDIR /openemr
RUN --mount=type=cache,target=/root/.composer/cache \
    composer install --no-dev --optimize-autoloader \
    && composer dump-autoload --optimize --apcu
# Stage 3: Build frontend assets (npm)
FROM base AS openemr-assets
COPY --from=openemr-source /openemr /openemr
WORKDIR /openemr
RUN apk add --no-cache build-base
RUN --mount=type=cache,target=/root/.npm \
    npm install --unsafe-perm \
    && npm run build \
    && cd ccdaservice \
    && npm install --unsafe-perm \
    && cd .. \
    && rm -fr node_modules \
    && apk del --no-cache build-base
# Stage 4: Final assembly - combine everything in base image
FROM base AS production
# Copy OpenEMR source
COPY --from=openemr-source /openemr /tmp/openemr
# Copy Composer dependencies
COPY --from=openemr-composer /openemr/vendor /tmp/openemr/vendor
COPY --from=openemr-composer /openemr/composer.json /tmp/openemr/composer.json
COPY --from=openemr-composer /openemr/composer.lock /tmp/openemr/composer.lock
# Copy built assets
COPY --from=openemr-assets /openemr/public /tmp/openemr/public
COPY --from=openemr-assets /openemr/ccdaservice /tmp/openemr/ccdaservice
RUN cd /tmp \
    # Set secure permissions
    && find openemr -type d -exec chmod 500 {} + \
    && find openemr -type f -exec chmod 400 {} + \
    # Exceptions that need to be writable during setup
    && chmod 666 openemr/sites/default/sqlconf.php \
    && chmod 700 openemr/sites/default \
    && find openemr/sites/default/documents -type d -exec chmod 700 {} + \
    && find openemr/sites/default/documents -type f -exec chmod 600 {} + \
    # Set ownership to apache user
    && chown -R apache:apache openemr/ \
    # Move OpenEMR to web root directory
    && mv openemr /var/www/localhost/htdocs/ \
    # Create SSL certificate directories
    && mkdir -p /etc/ssl/certs /etc/ssl/private \
    # Disable Apache logging (logs handled by Docker)
    && sed -i 's/^ *CustomLog/#CustomLog/' /etc/apache2/httpd.conf \
    && sed -i 's/^ *ErrorLog/#ErrorLog/' /etc/apache2/httpd.conf \
    && sed -i 's/^ *CustomLog/#CustomLog/' /etc/apache2/conf.d/ssl.conf \
    && sed -i 's/^ *TransferLog/#TransferLog/' /etc/apache2/conf.d/ssl.conf
# ============================================================================
# WORKING DIRECTORY AND VOLUMES
# ============================================================================
WORKDIR /var/www/localhost/htdocs/openemr
VOLUME [ "/etc/letsencrypt/", "/etc/ssl" ]
# ============================================================================
# APACHE AND PHP CONFIGURATION FILES
# ============================================================================
ENV APACHE_LOG_DIR=/var/log/apache2
COPY php.ini /etc/php${PHP_VERSION_ABBR}/php.ini
COPY openemr.conf /etc/apache2/conf.d/
# ============================================================================
# OPENEMR SCRIPTS AND UTILITIES
# ============================================================================
COPY openemr.sh ssl.sh xdebug.sh auto_configure.php /var/www/localhost/htdocs/openemr/
COPY utilities/unlock_admin.php utilities/unlock_admin.sh /root/
RUN chmod 500 openemr.sh ssl.sh xdebug.sh /root/unlock_admin.sh \
    && chmod 000 auto_configure.php /root/unlock_admin.php
# ============================================================================
# UPGRADE SYSTEM
# ============================================================================
COPY upgrade/docker-version \
     upgrade/fsupgrade-1.sh \
     upgrade/fsupgrade-2.sh \
     upgrade/fsupgrade-3.sh \
     upgrade/fsupgrade-4.sh \
     upgrade/fsupgrade-5.sh \
     upgrade/fsupgrade-6.sh \
     upgrade/fsupgrade-7.sh \
     upgrade/fsupgrade-8.sh \
     upgrade/fsupgrade-9.sh \
     /root/
RUN chmod 500 \
    /root/fsupgrade-1.sh \
    /root/fsupgrade-2.sh \
    /root/fsupgrade-3.sh \
    /root/fsupgrade-4.sh \
    /root/fsupgrade-5.sh \
    /root/fsupgrade-6.sh \
    /root/fsupgrade-7.sh \
    /root/fsupgrade-8.sh \
    /root/fsupgrade-9.sh
# ============================================================================
# APACHE RUNTIME DIRECTORY
# ============================================================================
RUN mkdir -p /run/apache2
# ============================================================================
# DEVELOPMENT TOOLS LIBRARY
# ============================================================================
COPY utilities/devtoolsLibrary.source /root/
# ============================================================================
# SWARM MODE SUPPORT
# ============================================================================
RUN mkdir /swarm-pieces \
    && rsync --owner --group --perms --delete --recursive --links /etc/ssl /swarm-pieces/ \
    && rsync --owner --group --perms --delete --recursive --links /var/www/localhost/htdocs/openemr/sites /swarm-pieces/
# ============================================================================
# CONTAINER STARTUP
# ============================================================================
CMD [ "./openemr.sh" ]
EXPOSE 80 443
# ============================================================================
# FINAL BUILD TARGET (ALIAS)
# ============================================================================
FROM production AS final
