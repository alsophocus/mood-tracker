#!/usr/bin/env python3
"""
Non-interactive database reset script for Railway
"""

import os
import psycopg
from psycopg.rows import dict_row

def main():
    # Get DATABASE_URL from Railway environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not found')
        exit(1)

    try:
        with psycopg.connect(db_url, row_factory=dict_row) as conn:
            cursor = conn.cursor()
            
            print("🗑️  Clearing all mood data...")
            
            # Delete all mood entries
            cursor.execute('DELETE FROM moods')
            deleted_count = cursor.rowcount
            print(f"✅ Deleted {deleted_count} mood entries")
            
            # Reset the auto-increment sequence
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            print("✅ Reset mood ID sequence")
            
            conn.commit()
            
            # Show remaining data count
            cursor.execute('SELECT COUNT(*) as count FROM moods')
            result = cursor.fetchone()
            print(f"Moods remaining: {result['count']}")
            
            cursor.execute('SELECT COUNT(*) as count FROM users')  
            result = cursor.fetchone()
            print(f"Users remaining: {result['count']}")
            
            print("\n✅ Database reset completed successfully!")
            
    except Exception as e:
        print(f'❌ Database error: {e}')
        exit(1)

if __name__ == "__main__":
    main()
