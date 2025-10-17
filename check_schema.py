#!/usr/bin/env python3
import os
import psycopg
from psycopg.rows import dict_row

# Set the DATABASE_URL to use Railway's public URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@turntable.proxy.rlwy.net:41615/railway'

def check_schema():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        print(f"🔗 Connecting to PostgreSQL...")
        
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        cursor = conn.cursor()
        
        # Check moods table schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'moods' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Moods table schema:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check if timestamp column exists
        has_timestamp = any(col['column_name'] == 'timestamp' for col in columns)
        
        if not has_timestamp:
            print("\n⚠️ TIMESTAMP column is missing! Adding it...")
            cursor.execute('ALTER TABLE moods ADD COLUMN timestamp TIMESTAMP')
            conn.commit()
            print("✅ Added timestamp column")
        else:
            print("\n✅ Timestamp column exists")
        
        # Check recent moods
        cursor.execute('SELECT COUNT(*) as count FROM moods')
        count = cursor.fetchone()['count']
        print(f"\n📊 Total moods in database: {count}")
        
        cursor.execute('SELECT * FROM moods ORDER BY id DESC LIMIT 3')
        recent = cursor.fetchall()
        print("\n🔍 Recent moods:")
        for mood in recent:
            print(f"  - ID: {mood['id']}, User: {mood['user_id']}, Date: {mood['date']}, Mood: {mood['mood']}, Timestamp: {mood.get('timestamp', 'N/A')}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_schema()
