#!/usr/bin/env python3
"""
Populate Railway database with fake mood data for 2024-2025
"""

import os
import random
from datetime import datetime, date, timedelta
import psycopg
from psycopg.rows import dict_row

# Mood options
MOODS = ['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well']

# Sample notes for variety
SAMPLE_NOTES = [
    '', '', '',  # Many entries have no notes
    'Good day at work',
    'Feeling stressed',
    'Great workout today',
    'Had coffee with friends',
    'Busy day',
    'Relaxing evening',
    'Productive morning',
    'Feeling grateful',
    'Long day',
    'Nice weather',
    'Family time',
    'Challenging project',
    'Weekend vibes',
    'Early morning',
    'Late night',
    'Feeling motivated'
]

def get_database_url():
    """Get database URL from environment or Railway"""
    # Try different environment variable names that Railway might use
    db_url = (
        os.environ.get('DATABASE_URL') or
        os.environ.get('POSTGRES_URL') or 
        os.environ.get('DB_URL') or
        os.environ.get('DATABASE_PRIVATE_URL') or
        os.environ.get('POSTGRES_PRIVATE_URL')
    )
    
    if not db_url:
        print("❌ No database URL found in environment variables")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            if any(term in key.upper() for term in ['DATABASE', 'POSTGRES', 'DB']):
                print(f"  {key}: {os.environ[key][:50]}...")
        return None
    
    return db_url

def create_fake_data():
    """Generate fake mood data for 2024-2025"""
    
    # Connect to database
    db_url = get_database_url()
    if not db_url:
        return
        
    print(f"Connecting to database...")
    print(f"Database URL: {db_url[:30]}...")
    
    try:
        conn = psycopg.connect(db_url, row_factory=dict_row)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Get user ID (assuming user exists)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users LIMIT 1")
        user = cur.fetchone()
        
        if not user:
            print("❌ No users found in database. Please create a user first.")
            return
        
        user_id = user['id']
        print(f"✅ Using user ID: {user_id}")
    
    # Generate data for 2024-2025
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)
    current_date = start_date
    
    total_entries = 0
    
    print(f"🚀 Generating fake data from {start_date} to {end_date}")
    
    with conn.cursor() as cur:
        while current_date <= end_date:
            # Random number of entries per day (3-6)
            entries_today = random.randint(3, 6)
            
            # Generate random times throughout the day
            times_today = []
            for _ in range(entries_today):
                hour = random.randint(6, 23)  # Active hours 6 AM to 11 PM
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                timestamp = datetime.combine(current_date, datetime.min.time().replace(
                    hour=hour, minute=minute, second=second
                ))
                times_today.append(timestamp)
            
            # Sort times chronologically
            times_today.sort()
            
            # Insert mood entries for this day
            for timestamp in times_today:
                mood = random.choice(MOODS)
                notes = random.choice(SAMPLE_NOTES)
                
                cur.execute("""
                    INSERT INTO moods (user_id, date, mood, notes, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, current_date, mood, notes, timestamp))
                
                total_entries += 1
            
            # Progress indicator
            if current_date.day == 1:
                print(f"📅 Processing {current_date.strftime('%B %Y')}...")
            
            current_date += timedelta(days=1)
        
        # Commit all changes
        conn.commit()
        print(f"✅ Successfully inserted {total_entries} mood entries")
        
        # Show some statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_entries,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                COUNT(DISTINCT date) as days_with_data
            FROM moods 
            WHERE user_id = %s
        """, (user_id,))
        
        stats = cur.fetchone()
        print(f"\n📊 Database Statistics:")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Date range: {stats['earliest_date']} to {stats['latest_date']}")
        print(f"   Days with data: {stats['days_with_data']}")
        
        # Show mood distribution
        cur.execute("""
            SELECT mood, COUNT(*) as count
            FROM moods 
            WHERE user_id = %s
            GROUP BY mood
            ORDER BY count DESC
        """, (user_id,))
        
        mood_stats = cur.fetchall()
        print(f"\n🎭 Mood Distribution:")
        for mood_stat in mood_stats:
            print(f"   {mood_stat['mood']}: {mood_stat['count']} entries")
    
    conn.close()
    print(f"\n🎉 Fake data generation completed!")

if __name__ == "__main__":
    create_fake_data()
