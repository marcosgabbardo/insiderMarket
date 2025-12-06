-- Database initialization script
-- This file is executed when MySQL container starts for the first time

USE polymarket_insider;

-- Set proper character encoding
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Enable binary logging for point-in-time recovery
SET GLOBAL binlog_format = 'ROW';

-- Optimize MySQL for the workload
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB

-- Create indexes will be handled by Alembic migrations
