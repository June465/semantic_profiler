# Use an official Nginx image as the base
FROM nginx:alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy a custom Nginx configuration (we will create this next)
COPY nginx.conf /etc/nginx/conf.d

# Copy the static assets from the React build output
# We assume the build output is in a 'dist' directory
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# The default command for Nginx is to start the server
CMD ["nginx", "-g", "daemon off;"]