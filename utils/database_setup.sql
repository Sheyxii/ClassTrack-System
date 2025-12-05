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
    section VARCHAR(50),
    subject VARCHAR(100),
    room VARCHAR(50),
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



-- ============================================
-- VIEW TABLES
-- ============================================


-- SEE ALL USERS
SELECT * FROM users;

-- SEE SECTIONS FOR SPECIFIC USER (change 'admin' to any username)
SELECT s.*, u.username 
FROM sections s
JOIN users u ON s.user_id = u.user_id
WHERE u.username = 'admin'
AND s.is_archived = FALSE
ORDER BY s.created_at DESC;

-- SEE ALL SECTIONS (ALL USERS)
SELECT 
    s.section_id,
    s.section_name,
    u.username AS owner,
    s.is_archived,
    s.created_at
FROM sections s
JOIN users u ON s.user_id = u.user_id
ORDER BY u.username, s.section_name;

-- 4. SEE STUDENTS IN SPECIFIC SECTION (change 'BSCS 2B' to your section)
SELECT * FROM students
WHERE section_id = (SELECT section_id FROM sections WHERE section_name = 'BSCS 2B')
AND is_archived = FALSE
ORDER BY last_name, first_name;

-- SEE ALL STUDENTS FOR SPECIFIC USER (change 'admin' to username)
SELECT 
    st.student_id,
    st.first_name,
    st.last_name,
    st.grade,
    s.section_name,
    u.username AS teacher
FROM students st
JOIN sections s ON st.section_id = s.section_id
JOIN users u ON s.user_id = u.user_id
WHERE u.username = 'admin'
AND st.is_archived = FALSE
ORDER BY s.section_name, st.last_name;

-- COUNT STUDENTS PER SECTION PER USER
SELECT 
    u.username,
    s.section_name,
    COUNT(st.student_id) AS student_count
FROM sections s
JOIN users u ON s.user_id = u.user_id
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
WHERE s.is_archived = FALSE
GROUP BY u.username, s.section_name
ORDER BY u.username, s.section_name;

-- SEE EVERYTHING (COMPLETE OVERVIEW)
SELECT 
    u.username,
    s.section_name,
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    st.grade,
    st.email
FROM users u
LEFT JOIN sections s ON u.user_id = s.user_id AND s.is_archived = FALSE
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
ORDER BY u.username, s.section_name, st.last_name;

-- COMPARE DATA BETWEEN USERS
SELECT 
    u.username,
    COUNT(DISTINCT s.section_id) AS total_sections,
    COUNT(st.student_id) AS total_students
FROM users u
LEFT JOIN sections s ON u.user_id = s.user_id AND s.is_archived = FALSE
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
GROUP BY u.username
ORDER BY u.username;

-- SEE ARCHIVED DATA
SELECT * FROM sections WHERE is_archived = TRUE;
SELECT * FROM students WHERE is_archived = TRUE;

-- QUICK USER COUNT
SELECT 
    (SELECT COUNT(*) FROM sections WHERE user_id = 1 AND is_archived = FALSE) AS admin_sections,
    (SELECT COUNT(*) FROM sections WHERE user_id = 2 AND is_archived = FALSE) AS marsh_sections;

