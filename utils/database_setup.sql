-- ClassTrack Database Setup


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

-- Create sections table
CREATE TABLE IF NOT EXISTS sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_section_name (section_name),
    INDEX idx_user_id (user_id),
    INDEX idx_archived (is_archived)
);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) NOT NULL,
    section_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INT,
    email VARCHAR(100),
    phone VARCHAR(20),
    birthday VARCHAR(20),
    address TEXT,
    grade DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP NULL,
    PRIMARY KEY (student_id, section_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    INDEX idx_section_id (section_id),
    INDEX idx_archived (is_archived),
    INDEX idx_name (first_name, last_name)
);

-- Insert users (Note: the password is not yet hashed)
INSERT INTO users (username, password, email) VALUES
('admin', 'admin123', 'admin@classtrack.com')
ON DUPLICATE KEY UPDATE username=username;

-- View all users
SELECT * FROM users;
