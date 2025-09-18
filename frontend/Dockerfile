FROM node:18-alpine

WORKDIR /app

# Install dependencies for node-gyp and other native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Copy package files
COPY package.json ./
COPY yarn.lock* ./

# Install dependencies
RUN yarn install --network-timeout 100000

# Copy application code
COPY . .

# Set permissions
RUN chmod -R 755 /app

EXPOSE 3000

# Environment variables for React
ENV REACT_APP_BACKEND_URL=http://localhost:8001
ENV WDS_SOCKET_HOST=localhost
ENV WDS_SOCKET_PORT=3000
ENV CHOKIDAR_USEPOLLING=true
ENV GENERATE_SOURCEMAP=false

CMD ["yarn", "start"]