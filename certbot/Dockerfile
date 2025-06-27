# Use the official Certbot image as a base
FROM certbot/certbot

# Copy the custom entrypoint script into the image
COPY certbot-entrypoint.sh /usr/local/bin/

# Make the script executable
RUN chmod +x /usr/local/bin/certbot-entrypoint.sh

# Set the entrypoint for the container to our script
ENTRYPOINT ["certbot-entrypoint.sh"]