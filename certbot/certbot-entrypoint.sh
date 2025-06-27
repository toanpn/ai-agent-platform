#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if a domain is provided
if [ -z "$DOMAIN" ]; then
  echo "Error: DOMAIN environment variable not set."
  exit 1
fi

# Function to check if an email is provided
if [ -z "$EMAIL" ]; then
  echo "Error: EMAIL environment variable not set."
  exit 1
fi

# Path to the certificate
live_path="/etc/letsencrypt/live/$DOMAIN"

# If certificate does not exist, obtain it
if [ ! -d "$live_path" ]; then
  echo "Certificate not found for $DOMAIN. Obtaining a new one..."
  certbot certonly --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    --text --agree-tos --no-eff-email
else
  echo "Certificate for $DOMAIN already exists."
fi

# Start a loop to periodically renew the certificate
echo "Starting renewal process..."
trap exit TERM
while :; do
  certbot renew
  sleep 12h & wait $!
done