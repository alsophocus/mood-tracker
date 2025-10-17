#!/usr/bin/env python3
import sqlite3
import random
from datetime import datetime, timedelta

def add_fake_data():
    try:
        conn = sqlite3.connect('mood.db')
        cursor = conn.cursor()
        
        # Add timestamp column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE moods ADD COLUMN timestamp TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
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
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO moods (date, mood, notes, timestamp) 
                    VALUES (?, ?, ?, ?)
                ''', (current_date.date().isoformat(), mood, note, timestamp.isoformat()))
                
                print(f"Added: {current_date.date()} {timestamp.strftime('%H:%M')} - {mood}")
            
            current_date += timedelta(days=1)
        
        conn.commit()
        conn.close()
        print(f"\n✅ Successfully added fake data for October 2025!")
        print(f"📊 Data includes multiple entries per day with varied times and moods")
        
    except Exception as e:
        print(f"❌ Error adding fake data: {e}")

if __name__ == "__main__":
    add_fake_data()
