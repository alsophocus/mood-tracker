#!/usr/bin/env python3
"""
Reset database using the app's database connection
"""

from database import db

def main():
    print("🗑️  Resetting database...")
    
    try:
        # Initialize database connection
        if not db._initialized:
            db.initialize()
            
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count existing moods
            cursor.execute('SELECT COUNT(*) FROM moods')
            existing_count = cursor.fetchone()[0]
            print(f"Found {existing_count} existing mood entries")
            
            # Delete all mood entries
            cursor.execute('DELETE FROM moods')
            print(f"✅ Deleted all mood entries")
            
            # Reset the auto-increment sequence
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            print("✅ Reset mood ID sequence")
            
            # Verify deletion
            cursor.execute('SELECT COUNT(*) FROM moods')
            remaining_count = cursor.fetchone()[0]
            print(f"Moods remaining: {remaining_count}")
            
            cursor.execute('SELECT COUNT(*) FROM users')
            users_count = cursor.fetchone()[0]
            print(f"Users remaining: {users_count}")
            
            print("\n✅ Database reset completed successfully!")
            print("You can now start adding new mood data.")
            
    except Exception as e:
        print(f'❌ Database error: {e}')
        exit(1)

if __name__ == "__main__":
    main()
