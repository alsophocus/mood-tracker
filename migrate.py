#!/usr/bin/env python3
"""
Migration script to move from old app.py to new modular structure
"""

import os
import shutil
from datetime import datetime

def backup_old_files():
    """Backup original files"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = ['app.py', 'requirements.txt', '.env.example']
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backed up {file}")
    
    return backup_dir

def migrate_files():
    """Replace old files with new ones"""
    migrations = [
        ('app_new.py', 'app.py'),
        ('requirements_new.txt', 'requirements.txt'),
        ('.env_new.example', '.env.example')
    ]
    
    for new_file, target_file in migrations:
        if os.path.exists(new_file):
            shutil.move(new_file, target_file)
            print(f"✅ Migrated {new_file} -> {target_file}")

def main():
    print("🚀 Starting migration to modular structure...")
    
    # Backup original files
    backup_dir = backup_old_files()
    print(f"📦 Files backed up to: {backup_dir}")
    
    # Migrate files
    migrate_files()
    
    print("\n✅ Migration completed!")
    print("\nNext steps:")
    print("1. Update your environment variables in .env")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")
    print(f"4. Original files are backed up in: {backup_dir}")

if __name__ == '__main__':
    main()
