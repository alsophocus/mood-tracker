#!/usr/bin/env python3
import os
import sys
from datetime import date
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def clear_data_until_date(target_date):
    """Clear mood data until the specified date (inclusive)"""
    try:
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            print(f"🗑️  Clearing mood data until {target_date}...")
            
            # Count records first
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            count = cursor.fetchone()[0]
            print(f"📊 Found {count} mood records to delete")
            
            if count == 0:
                print("✅ No records to delete")
                return
            
            # Delete mood entries until target date
            cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
            deleted_moods = cursor.rowcount
            print(f"✅ Deleted {deleted_moods} mood entries until {target_date}")
            
            conn.commit()
            
            # Show remaining counts
            cursor.execute('SELECT COUNT(*) FROM moods')
            remaining = cursor.fetchone()[0]
            print(f"📈 Remaining mood entries: {remaining}")
            
            # Show date range of remaining data
            cursor.execute('SELECT MIN(date), MAX(date) FROM moods')
            date_range = cursor.fetchone()
            if date_range[0]:
                print(f"📅 Remaining data range: {date_range[0]} to {date_range[1]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    target_date = date(2025, 10, 19)
    print(f"🧹 Mood Data Cleanup - Deleting until {target_date}")
    print("=" * 50)
    
    clear_data_until_date(target_date)
    print("\n🎉 Cleanup completed!")
