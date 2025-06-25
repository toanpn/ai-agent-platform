# Multi-stage build for Angular application
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the Angular application for production
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy the built Angular application from the build stage
COPY --from=build /app/dist/chatbot-ui/browser /usr/share/nginx/html

# Create nginx configuration for Angular SPA with API proxy
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Handle API calls - proxy to backend' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /api/ {' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_pass http://api:80/api/;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Forwarded-Proto $scheme;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header Origin $http_origin;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_redirect off;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_buffering off;' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '        # Handle preflight requests' >> /etc/nginx/conf.d/default.conf && \
    echo '        if ($request_method = OPTIONS) {' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Access-Control-Allow-Origin $http_origin always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin, X-Requested-With" always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Access-Control-Allow-Credentials true always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Access-Control-Max-Age 1728000 always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Content-Length 0 always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            add_header Content-Type text/plain always;' >> /etc/nginx/conf.d/default.conf && \
    echo '            return 204;' >> /etc/nginx/conf.d/default.conf && \
    echo '        }' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Handle Angular SPA routing' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]