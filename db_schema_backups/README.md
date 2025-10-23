# Database Schema Backups

This directory contains database schema backups created before making structural changes to the database.

## Purpose
- **Safety**: Backup schema before making changes
- **Recovery**: Restore previous schema if needed
- **History**: Track schema evolution over time

## File Naming Convention
- Format: `schema_backup_YYYYMMDD_HHMMSS.sql`
- Example: `schema_backup_20251022_095950.sql`

## Usage

### Create Backup
```python
from db_backup_util import backup_schema_before_changes

# Before making schema changes
backup_path = backup_schema_before_changes("Adding new analytics table")
```

### List Backups
```python
from db_backup_util import DatabaseBackupService

backup_service = DatabaseBackupService()
backups = backup_service.list_backups()
```

### Restore Schema (if needed)
```python
backup_service.restore_schema("db_schema_backups/schema_backup_20251022_095950.sql")
```

## Important Notes
- ⚠️ **This folder is in .gitignore** - backups are not committed to version control
- 🧹 **Clean this folder** before production deployment
- 📅 **Backups include timestamp** for easy identification
- 🔄 **Schema only** - no data is backed up, only table structures

## Current Schema Baseline
- Initial backup: `schema_backup_20251022_095950.sql`
- Contains: Users table, MoodEntry table, and all indexes
