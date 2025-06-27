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

# Path to the certificate for the first domain
first_domain=$(echo $DOMAIN | cut -d ',' -f 1)
live_path="/etc/letsencrypt/live/$first_domain"

# If certificate does not exist, obtain it
if [ ! -d "$live_path" ]; then
  echo "Certificate not found for $first_domain. Obtaining a new one..."
  # Convert comma-separated domains to -d arguments
  domain_args=$(echo $DOMAIN | sed 's/,/ -d /g')
  certbot certonly --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    -d $domain_args \
    --text --agree-tos --no-eff-email
else
  echo "Certificate for $first_domain already exists."
fi

# Start a loop to periodically renew the certificate
echo "Starting renewal process..."
trap exit TERM
while :; do
  certbot renew
  sleep 12h & wait $!
done