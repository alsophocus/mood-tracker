#!/usr/bin/env python3
"""
Migrate test files to work with new modular structure
"""

import os
import shutil
from datetime import datetime

def migrate_test_files():
    """Replace old test files with updated ones"""
    migrations = [
        ('tests/conftest_new.py', 'tests/conftest.py'),
        ('tests/test_database_new.py', 'tests/test_database.py'),
        ('tests/test_analytics_new.py', 'tests/test_analytics.py'),
        ('tests/test_routes_new.py', 'tests/test_routes.py')
    ]
    
    # Backup existing test files
    backup_dir = f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for new_file, target_file in migrations:
        if os.path.exists(target_file):
            shutil.copy2(target_file, os.path.join(backup_dir, os.path.basename(target_file)))
            print(f"✅ Backed up {target_file}")
        
        if os.path.exists(new_file):
            shutil.move(new_file, target_file)
            print(f"✅ Migrated {new_file} -> {target_file}")
    
    print(f"\n✅ Test migration completed!")
    print(f"📦 Original tests backed up to: {backup_dir}")
    print("\nRun tests with: python -m pytest tests/ -v")

if __name__ == '__main__':
    migrate_test_files()
