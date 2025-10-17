#!/usr/bin/env python3
import os
import psycopg
from psycopg.rows import dict_row

# Set the DATABASE_URL to use Railway's public URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@turntable.proxy.rlwy.net:41615/railway'

def check_constraints():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        print(f"🔗 Connecting to PostgreSQL...")
        
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        cursor = conn.cursor()
        
        # Check for unique constraints on moods table
        cursor.execute("""
            SELECT 
                tc.constraint_name, 
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'moods' 
                AND tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
            ORDER BY tc.constraint_name;
        """)
        
        constraints = cursor.fetchall()
        print("\n🔒 Constraints on moods table:")
        for constraint in constraints:
            print(f"  - {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")
        
        # Check for any composite unique constraints
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'moods' 
                AND tc.constraint_type = 'UNIQUE'
            GROUP BY tc.constraint_name;
        """)
        
        unique_constraints = cursor.fetchall()
        if unique_constraints:
            print("\n⚠️ UNIQUE constraints found:")
            for constraint in unique_constraints:
                print(f"  - {constraint['constraint_name']}: ({constraint['columns']})")
                
                # Drop the problematic constraint
                print(f"  🔧 Dropping constraint: {constraint['constraint_name']}")
                cursor.execute(f'ALTER TABLE moods DROP CONSTRAINT IF EXISTS {constraint["constraint_name"]}')
        
        conn.commit()
        conn.close()
        
        print("\n✅ Constraint check completed")
        
    except Exception as e:
        print(f"❌ Error checking constraints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_constraints()
