#!/usr/bin/env python3
import os
import random
from datetime import datetime, timedelta

# Set environment variables for PostgreSQL connection
os.environ['DATABASE_URL'] = 'postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@postgres-thp7.railway.internal:5432/railway'

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print("❌ psycopg not available. Install with: pip install psycopg[binary]")
    exit(1)

def add_fake_data():
    try:
        # Connect to PostgreSQL
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        cursor = conn.cursor()
        
        # Ensure user exists (user_id = 1)
        cursor.execute('SELECT id FROM users WHERE id = %s', (1,))
        user = cursor.fetchone()
        
        if not user:
            # Create test user
            cursor.execute('''
                INSERT INTO users (id, email, name, provider) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            ''', (1, 'test@example.com', 'Test User', 'local'))
            print("✅ Created test user")
        
        # Mood options and their values
        moods = ['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well']
        notes_options = [
            'Feeling great today!',
            'Had a productive morning',
            'Feeling a bit tired',
            'Good day overall',
            'Stressed about work',
            'Relaxing weekend',
            'Excited about new project',
            'Feeling grateful',
            'Need more sleep',
            'Beautiful weather today'
        ]
        
        # Generate data for October 2025 (complete month)
        start_date = datetime(2025, 10, 1)
        end_date = datetime(2025, 10, 31)
        
        user_id = 1
        
        current_date = start_date
        while current_date <= end_date:
            # Add 1-3 mood entries per day at different times
            entries_per_day = random.randint(1, 3)
            
            for i in range(entries_per_day):
                # Random time during the day
                hour = random.randint(7, 22)  # Between 7 AM and 10 PM
                minute = random.randint(0, 59)
                
                # Create timestamp
                timestamp = current_date.replace(hour=hour, minute=minute)
                
                # Random mood (weighted towards neutral/positive)
                mood_weights = [5, 10, 15, 25, 25, 15, 5]  # Favor middle moods
                mood = random.choices(moods, weights=mood_weights)[0]
                
                # Random note (sometimes empty)
                note = random.choice(notes_options) if random.random() > 0.3 else ''
                
                # Insert into PostgreSQL database
                cursor.execute('''
                    INSERT INTO moods (user_id, date, mood, notes, timestamp) 
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, date, timestamp) DO UPDATE SET 
                    mood = EXCLUDED.mood, notes = EXCLUDED.notes
                ''', (user_id, current_date.date(), mood, note, timestamp))
                
                print(f"Added: {current_date.date()} {timestamp.strftime('%H:%M')} - {mood}")
            
            current_date += timedelta(days=1)
        
        conn.commit()
        conn.close()
        print(f"\n✅ Successfully added fake data to PostgreSQL for October 2025!")
        print(f"📊 Data includes multiple entries per day with varied times and moods")
        
    except Exception as e:
        print(f"❌ Error adding fake data to PostgreSQL: {e}")
        print("💡 Make sure you're connected to the Railway network or use Railway CLI")

if __name__ == "__main__":
    add_fake_data()
