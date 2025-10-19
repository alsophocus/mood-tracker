#!/usr/bin/env python3
"""
Database reset script for Railway deployment
This script will clear all data from the moods table
"""

import subprocess
import sys

def run_railway_command(sql_command):
    """Execute SQL command via Railway CLI"""
    try:
        # Use Railway CLI to connect to database and execute SQL
        cmd = [
            'railway', 'run', 'python3', '-c',
            f"""
import os
import psycopg
from psycopg.rows import dict_row

# Get DATABASE_URL from Railway environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('ERROR: DATABASE_URL not found')
    exit(1)

try:
    with psycopg.connect(db_url, row_factory=dict_row) as conn:
        cursor = conn.cursor()
        cursor.execute('{sql_command}')
        conn.commit()
        print('✅ SQL executed successfully')
        
        # Show remaining data count
        cursor.execute('SELECT COUNT(*) as count FROM moods')
        result = cursor.fetchone()
        print(f'Moods remaining: {{result["count"]}}')
        
        cursor.execute('SELECT COUNT(*) as count FROM users')  
        result = cursor.fetchone()
        print(f'Users remaining: {{result["count"]}}')
        
except Exception as e:
    print(f'❌ Database error: {{e}}')
    exit(1)
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running Railway command: {e}")
        return False

def main():
    print("🗑️  Database Reset Script")
    print("This will delete ALL mood data from the database!")
    
    # Confirm deletion
    confirm = input("Are you sure you want to delete all mood data? (type 'YES' to confirm): ")
    if confirm != 'YES':
        print("❌ Operation cancelled")
        return
    
    print("\n1. Clearing all mood entries...")
    if not run_railway_command("DELETE FROM moods"):
        print("❌ Failed to clear moods table")
        return
    
    print("\n2. Resetting auto-increment sequences...")
    if not run_railway_command("ALTER SEQUENCE moods_id_seq RESTART WITH 1"):
        print("❌ Failed to reset moods sequence")
        return
    
    print("\n✅ Database reset completed successfully!")
    print("You can now start adding new mood data.")

if __name__ == "__main__":
    main()
