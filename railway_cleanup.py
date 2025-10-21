#!/usr/bin/env python3
"""
Railway-deployable script to delete mood data until October 19, 2025
Following SOLID principles using existing database interfaces
"""
import os
import sys
from datetime import date
from database import Database

def main():
    """Delete mood data until October 19, 2025"""
    target_date = date(2025, 10, 19)
    
    print(f"🧹 Railway Cleanup - Deleting mood data until {target_date}")
    print("=" * 60)
    
    try:
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records first
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            count = cursor.fetchone()[0]
            print(f"📊 Found {count} mood records to delete until {target_date}")
            
            if count == 0:
                print("✅ No records to delete")
                return
            
            # Delete mood entries until target date
            cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
            deleted_moods = cursor.rowcount
            print(f"✅ Deleted {deleted_moods} mood entries until {target_date}")
            
            conn.commit()
            
            # Show remaining data info
            cursor.execute('SELECT COUNT(*) FROM moods')
            remaining = cursor.fetchone()[0]
            print(f"📈 Remaining mood entries: {remaining}")
            
            if remaining > 0:
                cursor.execute('SELECT MIN(date), MAX(date) FROM moods')
                date_range = cursor.fetchone()
                print(f"📅 Remaining data range: {date_range[0]} to {date_range[1]}")
            
            print("\n🎉 Cleanup completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
