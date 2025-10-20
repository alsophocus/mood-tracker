"""
Database implementation following SOLID principles
"""
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from typing import List, Dict, Optional, Any
from datetime import date, datetime

from config import Config
from interfaces import MoodReader, MoodWriter, UserReader, UserWriter, DatabaseConnection
from models import MoodEntry, User, MoodType

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL connection management - Single Responsibility Principle"""
    
    def __init__(self, database_url: str):
        self.url = database_url
        self._initialized = False
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg.connect(self.url, row_factory=dict_row)
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()
    
    def initialize(self) -> None:
        """Initialize database schema"""
        if self._initialized:
            return
        
        if not self.url:
            raise ValueError("DATABASE_URL is required but not set")
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        name TEXT,
                        provider TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Moods table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS moods (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        date DATE NOT NULL,
                        mood TEXT NOT NULL,
                        notes TEXT DEFAULT '',
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Indexes for performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_user_date ON moods(user_id, date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_timestamp ON moods(timestamp)')
                
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {e}")

class MoodRepository(MoodReader, MoodWriter):
    """Mood data access implementation - Single Responsibility Principle"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection  # Dependency Inversion Principle
    
    def get_user_moods(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get user's moods ordered by most recent timestamp"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM moods WHERE user_id = %s ORDER BY timestamp DESC'
            if limit:
                query += f' LIMIT {limit}'
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
    
    def get_moods_by_date(self, user_id: int, target_date: date) -> List[Dict[str, Any]]:
        """Get moods for specific date"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM moods 
                WHERE user_id = %s AND date = %s 
                ORDER BY timestamp ASC
            ''', (user_id, target_date))
            return cursor.fetchall()
    
    def save_mood(self, user_id: int, mood_date: date, mood: str, notes: str = '') -> Dict[str, Any]:
        """Save mood entry with current timestamp"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO moods (user_id, date, mood, notes, timestamp)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING *
            ''', (user_id, mood_date, mood, notes))
            return cursor.fetchone()

class UserRepository(UserReader, UserWriter):
    """User data access implementation - Single Responsibility Principle"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection  # Dependency Inversion Principle
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
    
    def create_or_update_user(self, email: str, name: str, provider: str) -> Dict[str, Any]:
        """Create or update user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, name, provider)
                VALUES (%s, %s, %s)
                ON CONFLICT (email)
                DO UPDATE SET name = EXCLUDED.name, provider = EXCLUDED.provider
                RETURNING *
            ''', (email, name, provider))
            return cursor.fetchone()

# Factory function following Dependency Inversion Principle
def create_repositories(database_url: str = None):
    """Factory to create repositories with proper dependencies"""
    if not database_url:
        database_url = Config.DATABASE_URL
    
    db_connection = PostgreSQLConnection(database_url)
    db_connection.initialize()
    
    mood_repo = MoodRepository(db_connection)
    user_repo = UserRepository(db_connection)
    
    return mood_repo, user_repo, db_connection
