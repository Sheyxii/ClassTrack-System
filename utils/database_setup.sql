-- ClassTrack Database Setup
-- Run this in MySQL Workbench to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS classtrack_db;
USE classtrack_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Insert sample users (password is hashed, but for demo purposes using plain text)
-- In production, use proper password hashing
INSERT INTO users (username, password, email) VALUES
('admin', 'admin123', 'admin@classtrack.com'),
('teacher1', 'teacher123', 'john.doe@classtrack.com'),
('teacher2', 'teacher456', 'jane.smith@classtrack.com');

-- View all users
SELECT * FROM users;
