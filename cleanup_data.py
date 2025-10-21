#!/usr/bin/env python3
"""
Simple cleanup script for Railway deployment
Deletes mood data until October 19, 2025
"""
import psycopg
import os
from datetime import date

def main():
    """Delete mood data until October 19, 2025"""
    target_date = date(2025, 10, 19)
    
    print(f"🧹 Deleting mood data until {target_date.isoformat()}...")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    try:
        # Connect to database
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cursor:
                # Count records first
                cursor.execute("SELECT COUNT(*) FROM moods WHERE date <= %s", (target_date,))
                count = cursor.fetchone()[0]
                
                print(f"📊 Found {count} records to delete")
                
                if count == 0:
                    print("✅ No records to delete")
                    return
                
                # Delete records
                cursor.execute("DELETE FROM moods WHERE date <= %s", (target_date,))
                deleted = cursor.rowcount
                
                print(f"✅ Deleted {deleted} mood records until {target_date}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
