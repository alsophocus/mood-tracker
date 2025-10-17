import pytest
import sqlite3
from app import get_db_connection, init_db
from datetime import datetime

class TestDatabase:
    
    def test_database_initialization(self, client):
        """Test database tables are created correctly"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        
        # Check moods table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moods'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_user_creation(self, client):
        """Test user creation in database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                      ('test@example.com', 'Test User', 'google'))
        conn.commit()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', ('test@example.com',))
        user = cursor.fetchone()
        
        assert user is not None
        assert user[1] == 'test@example.com'  # email
        assert user[2] == 'Test User'  # name
        assert user[3] == 'google'  # provider
        
        conn.close()
    
    def test_mood_creation(self, client):
        """Test mood entry creation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create user first
        cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                      ('test@example.com', 'Test User', 'google'))
        user_id = cursor.lastrowid
        
        # Create mood entry
        date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (user_id, date, 'good', 'Test note'))
        conn.commit()
        
        cursor.execute('SELECT * FROM moods WHERE user_id = ?', (user_id,))
        mood = cursor.fetchone()
        
        assert mood is not None
        assert mood[1] == user_id  # user_id
        assert mood[3] == 'good'  # mood
        assert mood[4] == 'Test note'  # notes
        
        conn.close()
    
    def test_user_mood_isolation(self, client):
        """Test users can only access their own moods"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create two users
        cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                      ('user1@example.com', 'User 1', 'google'))
        user1_id = cursor.lastrowid
        
        cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                      ('user2@example.com', 'User 2', 'github'))
        user2_id = cursor.lastrowid
        
        # Create moods for each user
        date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (user1_id, date, 'good', 'User 1 mood'))
        cursor.execute('INSERT INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (user2_id, date, 'sad', 'User 2 mood'))
        conn.commit()
        
        # Test user 1 can only see their mood
        cursor.execute('SELECT * FROM moods WHERE user_id = ?', (user1_id,))
        user1_moods = cursor.fetchall()
        assert len(user1_moods) == 1
        assert user1_moods[0][4] == 'User 1 mood'
        
        # Test user 2 can only see their mood
        cursor.execute('SELECT * FROM moods WHERE user_id = ?', (user2_id,))
        user2_moods = cursor.fetchall()
        assert len(user2_moods) == 1
        assert user2_moods[0][4] == 'User 2 mood'
        
        conn.close()
    
    def test_duplicate_date_handling(self, client):
        """Test updating mood for same date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create user
        cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                      ('test@example.com', 'Test User', 'google'))
        user_id = cursor.lastrowid
        
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Insert first mood
        cursor.execute('INSERT OR REPLACE INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (user_id, date, 'good', 'First note'))
        conn.commit()
        
        # Update with new mood for same date
        cursor.execute('INSERT OR REPLACE INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (user_id, date, 'super good', 'Updated note'))
        conn.commit()
        
        # Should only have one entry
        cursor.execute('SELECT * FROM moods WHERE user_id = ? AND date = ?', (user_id, date))
        moods = cursor.fetchall()
        
        assert len(moods) == 1
        assert moods[0][3] == 'super good'  # Updated mood
        assert moods[0][4] == 'Updated note'  # Updated note
        
        conn.close()
