#!/usr/bin/env python3
"""
Script to add fake data to PostgreSQL database.
This should be run on Railway or with proper DATABASE_URL access.
"""
import os
import sys

# Set the DATABASE_URL to use Railway's public URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@turntable.proxy.rlwy.net:41615/railway'

# Add current directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import psycopg
    from psycopg.rows import dict_row
    print("✅ Successfully imported psycopg")
except ImportError as e:
    print(f"❌ Failed to import psycopg: {e}")
    sys.exit(1)

def add_fake_data():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        print(f"🔗 Connecting to: {DATABASE_URL[:50]}...")
        
        # Connect directly to PostgreSQL
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        cursor = conn.cursor()
        
        # Read and execute SQL file
        with open('fake_data.sql', 'r') as f:
            sql_content = f.read()
        
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
