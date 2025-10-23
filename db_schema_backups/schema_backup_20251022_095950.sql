-- Database Schema Backup
-- Created: 2025-10-22T09:59:50.126850
-- Description: Manual backup test
-- Original DB: mood.db

-- Drop existing tables (uncomment if needed)
-- DROP TABLE IF EXISTS mood_entries;
-- DROP TABLE IF EXISTS users;

-- Table Definitions
CREATE TABLE moods 
                    (id INTEGER PRIMARY KEY, date TEXT, mood TEXT, notes TEXT, timestamp TEXT);

CREATE TABLE users 
                         (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT);

-- Index Definitions
