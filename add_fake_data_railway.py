#!/usr/bin/env python3
"""
Add fake mood data using the app's database connection
"""

import random
from datetime import datetime, date, timedelta
from database import db

# Mood options
MOODS = ['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well']

# Sample notes
SAMPLE_NOTES = [
    '', '', '',  # Many entries have no notes
    'Good day at work', 'Feeling stressed', 'Great workout today',
    'Had coffee with friends', 'Busy day', 'Relaxing evening',
    'Productive morning', 'Feeling grateful', 'Long day',
    'Nice weather', 'Family time', 'Weekend vibes'
]

def add_fake_data():
    """Add fake mood data for 2024-2025"""
    
    print("🚀 Adding fake mood data for 2024-2025...")
    
    # Initialize database
    try:
        db.initialize()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Get first user (assuming one exists)
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users LIMIT 1")
            user = cur.fetchone()
            
            if not user:
                print("❌ No users found. Please create a user first.")
                return
            
            user_id = user['id']
            print(f"✅ Using user ID: {user_id}")
    
    # Generate data
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)
    current_date = start_date
    total_entries = 0
    
    print(f"📅 Generating data from {start_date} to {end_date}")
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            while current_date <= end_date:
                # 3-6 entries per day
                entries_today = random.randint(3, 6)
                
                # Generate random times
                times_today = []
                for _ in range(entries_today):
                    hour = random.randint(6, 23)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    timestamp = datetime.combine(current_date, datetime.min.time().replace(
                        hour=hour, minute=minute, second=second
                    ))
                    times_today.append(timestamp)
                
                times_today.sort()
                
                # Insert entries
                for timestamp in times_today:
                    mood = random.choice(MOODS)
                    notes = random.choice(SAMPLE_NOTES)
                    
                    cur.execute("""
                        INSERT INTO moods (user_id, date, mood, notes, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, current_date, mood, notes, timestamp))
                    
                    total_entries += 1
                
                # Progress
                if current_date.day == 1:
                    print(f"📅 {current_date.strftime('%B %Y')}...")
                
                current_date += timedelta(days=1)
            
            conn.commit()
    
    print(f"✅ Added {total_entries} mood entries!")
    
    # Show stats
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM moods WHERE user_id = %s", (user_id,))
            total = cur.fetchone()['count']
            print(f"📊 Total mood entries in database: {total}")

if __name__ == "__main__":
    add_fake_data()
