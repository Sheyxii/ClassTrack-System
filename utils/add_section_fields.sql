-- Add new fields to existing sections table
-- Run this to update your existing database

USE classtrack_db;

-- Add section column if it doesn't exist
ALTER TABLE sections 
ADD COLUMN IF NOT EXISTS section VARCHAR(50) AFTER section_name;

-- Add subject column if it doesn't exist
ALTER TABLE sections 
ADD COLUMN IF NOT EXISTS subject VARCHAR(100) AFTER section;

-- Add room column if it doesn't exist
ALTER TABLE sections 
ADD COLUMN IF NOT EXISTS room VARCHAR(50) AFTER subject;

-- Verify the changes
DESCRIBE sections;
