#!/usr/bin/env python3
"""
Script to add fake data to PostgreSQL database.
This should be run on Railway or with proper DATABASE_URL access.
"""
import os
import sys

# Add current directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import get_db_connection, init_db, ACTUAL_USE_POSTGRES
    print("✅ Successfully imported app modules")
except ImportError as e:
    print(f"❌ Failed to import app modules: {e}")
    sys.exit(1)

def add_fake_data():
    try:
        # Initialize database first
        init_db()
        
        if not ACTUAL_USE_POSTGRES:
            print("❌ This script requires PostgreSQL")
            return
        
        # Read and execute SQL file
        with open('fake_data.sql', 'r') as f:
            sql_content = f.read()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the SQL (split by semicolons for multiple statements)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                print(f"✅ Executed: {statement[:50]}...")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Successfully added fake data to PostgreSQL!")
        print("📊 Added complete October 2025 data with multiple entries per day")
        
    except Exception as e:
        print(f"❌ Error adding fake data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_fake_data()
