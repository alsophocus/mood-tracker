#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def clear_database():
    """Clear all mood data from the database"""
    try:
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print("🗑️  Clearing all mood data...")
            
            # Delete all mood entries
            cursor.execute('DELETE FROM moods')
            deleted_moods = cursor.rowcount
            print(f"✅ Deleted {deleted_moods} mood entries")
            
            # Reset the auto-increment sequence
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            print("✅ Reset mood ID sequence")
            
            conn.commit()
            
            # Show remaining counts
            cursor.execute('SELECT COUNT(*) FROM moods')
            mood_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            
            print(f"Moods remaining: {mood_count}")
            print(f"Users remaining: {user_count}")
            print("\n✅ Database cleared successfully!")
        
    except Exception as e:
        print(f'❌ Error clearing database: {e}')
        sys.exit(1)

if __name__ == "__main__":
    clear_database()
