#!/usr/bin/env python3
"""
Database migration for mood triggers and context system
Following SOLID principles with proper separation of concerns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from datetime import datetime

class MoodTriggersMigration:
    """Migration class following Single Responsibility Principle"""
    
    def __init__(self, database):
        self.db = database
        self.migration_name = "add_mood_triggers"
        self.version = "0.1.7"
    
    def up(self):
        """Apply migration - add mood triggers tables"""
        print(f"🔄 Applying migration: {self.migration_name}")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    category VARCHAR(30) NOT NULL,
                    color VARCHAR(7) DEFAULT '#6750A4',
                    icon VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create mood_tags junction table (many-to-many)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_tags (
                    id SERIAL PRIMARY KEY,
                    mood_id INTEGER NOT NULL REFERENCES moods(id) ON DELETE CASCADE,
                    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(mood_id, tag_id)
                )
            ''')
            
            # Add context fields to moods table
            cursor.execute('''
                ALTER TABLE moods 
                ADD COLUMN IF NOT EXISTS context_location VARCHAR(100),
                ADD COLUMN IF NOT EXISTS context_activity VARCHAR(100),
                ADD COLUMN IF NOT EXISTS context_weather VARCHAR(50),
                ADD COLUMN IF NOT EXISTS context_sleep_hours DECIMAL(3,1),
                ADD COLUMN IF NOT EXISTS context_energy_level INTEGER CHECK (context_energy_level >= 1 AND context_energy_level <= 5)
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_tags_mood_id ON mood_tags(mood_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_tags_tag_id ON mood_tags(tag_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_context_activity ON moods(context_activity)')
            
            conn.commit()
            
        self._insert_default_tags()
        print(f"✅ Migration {self.migration_name} applied successfully")
    
    def down(self):
        """Rollback migration - remove mood triggers tables"""
        print(f"🔄 Rolling back migration: {self.migration_name}")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Remove added columns from moods table
            cursor.execute('''
                ALTER TABLE moods 
                DROP COLUMN IF EXISTS context_location,
                DROP COLUMN IF EXISTS context_activity,
                DROP COLUMN IF EXISTS context_weather,
                DROP COLUMN IF EXISTS context_sleep_hours,
                DROP COLUMN IF EXISTS context_energy_level
            ''')
            
            # Drop tables in correct order (foreign keys first)
            cursor.execute('DROP TABLE IF EXISTS mood_tags')
            cursor.execute('DROP TABLE IF EXISTS tags')
            
            conn.commit()
            
        print(f"✅ Migration {self.migration_name} rolled back successfully")
    
    def _insert_default_tags(self):
        """Insert default tag categories and common tags"""
        default_tags = [
            # Work category
            ('work', 'work', '#FF6B6B', 'fas fa-briefcase'),
            ('meeting', 'work', '#FF6B6B', 'fas fa-users'),
            ('deadline', 'work', '#FF6B6B', 'fas fa-clock'),
            ('presentation', 'work', '#FF6B6B', 'fas fa-presentation'),
            
            # Health category
            ('exercise', 'health', '#4ECDC4', 'fas fa-dumbbell'),
            ('sleep', 'health', '#4ECDC4', 'fas fa-bed'),
            ('medication', 'health', '#4ECDC4', 'fas fa-pills'),
            ('doctor', 'health', '#4ECDC4', 'fas fa-user-md'),
            
            # Social category
            ('family', 'social', '#45B7D1', 'fas fa-home'),
            ('friends', 'social', '#45B7D1', 'fas fa-user-friends'),
            ('date', 'social', '#45B7D1', 'fas fa-heart'),
            ('party', 'social', '#45B7D1', 'fas fa-glass-cheers'),
            
            # Activities category
            ('travel', 'activities', '#96CEB4', 'fas fa-plane'),
            ('hobby', 'activities', '#96CEB4', 'fas fa-palette'),
            ('reading', 'activities', '#96CEB4', 'fas fa-book'),
            ('music', 'activities', '#96CEB4', 'fas fa-music'),
            
            # Environment category
            ('home', 'environment', '#FFEAA7', 'fas fa-house'),
            ('outdoors', 'environment', '#FFEAA7', 'fas fa-tree'),
            ('city', 'environment', '#FFEAA7', 'fas fa-city'),
            ('nature', 'environment', '#FFEAA7', 'fas fa-leaf'),
            
            # Emotions category
            ('stress', 'emotions', '#DDA0DD', 'fas fa-exclamation-triangle'),
            ('anxiety', 'emotions', '#DDA0DD', 'fas fa-heart-pulse'),
            ('joy', 'emotions', '#DDA0DD', 'fas fa-smile'),
            ('calm', 'emotions', '#DDA0DD', 'fas fa-peace')
        ]
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for name, category, color, icon in default_tags:
                cursor.execute('''
                    INSERT INTO tags (name, category, color, icon)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                ''', (name, category, color, icon))
            
            conn.commit()
        
        print(f"✅ Inserted {len(default_tags)} default tags")

def main():
    """Run migration"""
    migration = MoodTriggersMigration(db)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        migration.down()
    else:
        migration.up()

if __name__ == "__main__":
    main()
