-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS semantic_profiler_db;

-- Create the user and grant privileges.
-- IMPORTANT: Replace 'password' with your desired password!
-- The '%' means the user can connect from any host (important for Docker containers)
CREATE USER IF NOT EXISTS 'user'@'%' IDENTIFIED BY 'ouWEe91';
GRANT ALL PRIVILEGES ON semantic_profiler_db.* TO 'user'@'%';
FLUSH PRIVILEGES;

-- You can add initial tables/data here if needed for migrations (optional)
-- e.g.,
-- USE semantic_profiler_db;
-- CREATE TABLE IF NOT EXISTS some_table (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(255)
-- );