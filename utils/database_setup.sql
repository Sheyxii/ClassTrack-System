# ClassTrack Database Setup

# Create database
CREATE DATABASE IF NOT EXISTS classtrack_db; 
USE classtrack_db;

# Users table
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

# Sections table
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

# Students table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP NULL,
    PRIMARY KEY (student_id, section_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    INDEX idx_section_id (section_id),
    INDEX idx_archived (is_archived),
    INDEX idx_name (first_name, last_name)
);

# Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    INDEX idx_section_date (section_id, attendance_date),
    UNIQUE KEY unique_section_date (section_id, attendance_date)
);

# Attendance records table
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT NOT NULL,
    student_id VARCHAR(20) NOT NULL,
    section_id INT NOT NULL,
    status ENUM('present', 'absent') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attendance_id) REFERENCES attendance(attendance_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id, section_id) REFERENCES students(student_id, section_id) ON DELETE CASCADE,
    INDEX idx_attendance (attendance_id),
    INDEX idx_student (student_id, section_id),
    UNIQUE KEY unique_attendance_student (attendance_id, student_id)
);

# Grades table
CREATE TABLE IF NOT EXISTS grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    section_id INT NOT NULL,
    midterm DECIMAL(5,2) DEFAULT NULL,
    final DECIMAL(5,2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id, section_id) REFERENCES students(student_id, section_id) ON DELETE CASCADE,
    INDEX idx_student_section (student_id, section_id),
    UNIQUE KEY unique_student_section_grade (student_id, section_id)
);

# Resources table
CREATE TABLE IF NOT EXISTS resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_subject (subject)
);

# Schedules table
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    section VARCHAR(100),
    day VARCHAR(20) NOT NULL,
    time VARCHAR(50) NOT NULL,
    room VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_day (day)
);

# Insert default user
INSERT INTO users (username, password, email) VALUES
('roxanne', 'roxanne', 'roxanne@gmail.com')
ON DUPLICATE KEY UPDATE username=username;

# Update grades table to support 0-100 scores (run after table creation)
ALTER TABLE grades 
MODIFY COLUMN midterm DECIMAL(5,2) DEFAULT NULL,
MODIFY COLUMN final DECIMAL(5,2) DEFAULT NULL;

# Update existing 0 values to NULL for cleaner display
UPDATE grades SET midterm = NULL WHERE midterm = 0.00;
UPDATE grades SET final = NULL WHERE final = 0.00;

# ============================================
# VIEW TABLES QUERIES
# ============================================

# 1. All users
SELECT 
    user_id,
    username,
    email,
    created_at,
    last_login
FROM users
ORDER BY created_at DESC;

# 2. Sections for specific user
SELECT 
    s.section_id,
    s.section_name,
    s.section,
    s.subject,
    s.room,
    s.created_at,
    u.username
FROM sections s
JOIN users u ON s.user_id = u.user_id
WHERE u.username = 'roxanne'
AND s.is_archived = FALSE
ORDER BY s.created_at DESC;

# 3. All sections
SELECT 
    s.section_id,
    s.section_name,
    s.section,
    s.subject,
    s.room,
    u.username AS owner,
    s.is_archived,
    s.created_at
FROM sections s
JOIN users u ON s.user_id = u.user_id
ORDER BY u.username, s.section_name;

# 4. Students in specific section
SELECT 
    st.student_id,
    st.first_name,
    st.last_name,
    st.age,
    st.email,
    st.phone,
    st.birthday,
    s.section_name
FROM students st
JOIN sections s ON st.section_id = s.section_id
WHERE s.section_name = 'CMSC 203 - BSCS 2B'
AND st.is_archived = FALSE
ORDER BY st.last_name, st.first_name;

# 5. All students for specific user
SELECT 
    st.student_id,
    st.first_name,
    st.last_name,
    st.age,
    st.email,
    s.section_name,
    u.username AS teacher
FROM students st
JOIN sections s ON st.section_id = s.section_id
JOIN users u ON s.user_id = u.user_id
WHERE u.username = 'roxanne'
AND st.is_archived = FALSE
ORDER BY s.section_name, st.last_name;

# 6. Count students per section
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

# 7. Complete overview
SELECT 
    u.username,
    s.section_name,
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    st.age,
    st.email
FROM users u
LEFT JOIN sections s ON u.user_id = s.user_id AND s.is_archived = FALSE
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
ORDER BY u.username, s.section_name, st.last_name;

# 8. Summary statistics per user
SELECT 
    u.username,
    COUNT(DISTINCT s.section_id) AS total_sections,
    COUNT(st.student_id) AS total_students
FROM users u
LEFT JOIN sections s ON u.user_id = s.user_id AND s.is_archived = FALSE
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
GROUP BY u.username
ORDER BY u.username;

# 9. Student grades with semestral average
SELECT 
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    s.section_name,
    g.midterm,
    g.final,
    ROUND((g.midterm + g.final) / 2, 2) AS semestral_grade
FROM students st
JOIN sections s ON st.section_id = s.section_id
LEFT JOIN grades g ON st.student_id = g.student_id AND st.section_id = g.section_id
WHERE st.is_archived = FALSE
ORDER BY s.section_name, semestral_grade ASC;

# 10. Attendance summary per student
SELECT 
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    s.section_name,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) AS present_count,
    COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) AS absent_count,
    COUNT(ar.record_id) AS total_sessions,
    ROUND((COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(ar.record_id)), 2) AS attendance_percentage
FROM students st
JOIN sections s ON st.section_id = s.section_id
LEFT JOIN attendance_records ar ON st.student_id = ar.student_id AND st.section_id = ar.section_id
WHERE st.is_archived = FALSE
GROUP BY st.student_id, st.first_name, st.last_name, s.section_name
ORDER BY s.section_name, attendance_percentage DESC;

# 11. Resources per user
SELECT 
    u.username,
    r.file_name,
    r.subject,
    r.file_size,
    r.uploaded_at
FROM resources r
JOIN users u ON r.user_id = u.user_id
ORDER BY u.username, r.uploaded_at DESC;

# 12. Schedules for specific user
SELECT 
    u.username,
    sc.subject,
    sc.section,
    sc.day,
    sc.time,
    sc.room,
    sc.created_at
FROM schedules sc
JOIN users u ON sc.user_id = u.user_id
WHERE u.username = 'roxanne'
ORDER BY 
    CASE sc.day
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END,
    sc.time;

# 13. Archived data
SELECT 
    section_id,
    section_name,
    section,
    subject,
    room,
    archived_at
FROM sections 
WHERE is_archived = TRUE
ORDER BY archived_at DESC;

SELECT 
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    s.section_name,
    st.archived_at
FROM students st
JOIN sections s ON st.section_id = s.section_id
WHERE st.is_archived = TRUE
ORDER BY st.archived_at DESC;

# 14. Top 10 performing students
SELECT 
    st.student_id,
    CONCAT(st.first_name, ' ', st.last_name) AS student_name,
    s.section_name,
    g.midterm,
    g.final,
    ROUND((g.midterm + g.final) / 2, 2) AS semestral_grade
FROM students st
JOIN sections s ON st.section_id = s.section_id
JOIN grades g ON st.student_id = g.student_id AND st.section_id = g.section_id
WHERE st.is_archived = FALSE
AND g.midterm > 0 AND g.final > 0
ORDER BY semestral_grade ASC
LIMIT 10;

# 15. Section statistics
SELECT 
    s.section_name,
    s.subject,
    s.room,
    COUNT(DISTINCT st.student_id) AS total_students,
    COUNT(DISTINCT g.grade_id) AS students_with_grades,
    ROUND(AVG((g.midterm + g.final) / 2), 2) AS average_grade,
    MIN((g.midterm + g.final) / 2) AS lowest_grade,
    MAX((g.midterm + g.final) / 2) AS highest_grade
FROM sections s
LEFT JOIN students st ON s.section_id = st.section_id AND st.is_archived = FALSE
LEFT JOIN grades g ON st.student_id = g.student_id AND st.section_id = g.section_id
WHERE s.is_archived = FALSE
GROUP BY s.section_id, s.section_name, s.subject, s.room
ORDER BY s.section_name;




-- SEE STUDENT GRADES WITH SECTIONS
SELECT 
    st.student_id, 
    CONCAT(st.first_name, ' ', st.last_name) AS student_name, 
    s.section_name, 
    g.midterm, 
    g.final, 
    CAST(AVG(g.midterm + g.final) / 2 AS DECIMAL(10,2)) AS semestral_grade
FROM students st
JOIN sections s ON st.section_id = s.section_id
LEFT JOIN grades g ON st.student_id = g.student_id 
    AND st.section_id = g.section_id
WHERE st.is_archived = FALSE
GROUP BY st.student_id, st.first_name, st.last_name, s.section_name, g.midterm, g.final
ORDER BY s.section_name, semestral_grade ASC;