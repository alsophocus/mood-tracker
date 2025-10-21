#!/usr/bin/env python3
"""
Script to delete all mood data until October 19, 2025
Following SOLID principles using existing database interfaces
"""
import os
import sys
from datetime import date, datetime
from config import Config
from database_new import create_repositories

def delete_mood_data_until_date(target_date: date):
    """
    Delete all mood entries until the specified date (inclusive)
    
    Args:
        target_date: Delete all data up to and including this date
    """
    print(f"🗑️  Deleting mood data until {target_date.isoformat()}...")
    
    try:
        # Create database connection using existing SOLID architecture
        mood_repo, user_repo, db_connection = create_repositories(Config.DATABASE_URL)
        
        # Initialize database connection
        db_connection.initialize()
        
        # Get connection and execute deletion
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records to be deleted first
            cursor.execute(
                "SELECT COUNT(*) as count FROM moods WHERE date <= %s",
                (target_date,)
            )
            count_result = cursor.fetchone()
            records_to_delete = count_result['count'] if count_result else 0
            
            if records_to_delete == 0:
                print("✅ No records found to delete.")
                return
            
            print(f"📊 Found {records_to_delete} mood records to delete.")
            
            # Confirm deletion
            confirm = input(f"⚠️  Are you sure you want to delete {records_to_delete} mood records until {target_date}? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Deletion cancelled.")
                return
            
            # Execute deletion
            cursor.execute(
                "DELETE FROM moods WHERE date <= %s",
                (target_date,)
            )
            
            deleted_count = cursor.rowcount
            print(f"✅ Successfully deleted {deleted_count} mood records until {target_date.isoformat()}")
            
    except Exception as e:
        print(f"❌ Error deleting mood data: {str(e)}")
        sys.exit(1)

def main():
    """Main execution function"""
    print("🧹 Mood Data Cleanup Script")
    print("=" * 40)
    
    # Target date: October 19, 2025
    target_date = date(2025, 10, 19)
    
    print(f"Target date: {target_date.isoformat()}")
    print(f"Database URL: {Config.DATABASE_URL[:50]}..." if Config.DATABASE_URL else "Not configured")
    
    if not Config.DATABASE_URL:
        print("❌ DATABASE_URL not configured. Please check your .env file.")
        sys.exit(1)
    
    delete_mood_data_until_date(target_date)
    print("\n🎉 Cleanup completed!")

if __name__ == "__main__":
    main()
