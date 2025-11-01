# --- Stage 1: Build the React Application ---
# _MODIFIED_: Upgrade from node:18 to node:20 for Vite compatibility
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

# Add a "cache buster" argument to force this layer to re-run
ARG CACHE_BUSTER=1
RUN npm install

COPY . .

RUN npm run build


# --- Stage 2: Serve the Application with Nginx ---
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]