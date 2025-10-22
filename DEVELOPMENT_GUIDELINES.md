# 🔧 DEVELOPMENT GUIDELINES

## 📋 **CRITICAL RULES - READ FIRST**

### **🏷️ Git Tagging Policy**
- **DO NOT** tag every commit
- **DO NOT** use tags to explain what you did - that's the commit message's job
- Tags are for **major releases** and **stable versions** only
- Use semantic versioning: `v1.0.0`, `v1.1.0`, `v1.1.1`
- Maximum 1-2 tags per development session

### **🗄️ Database Management Policy**
- **NEVER** modify database schema without explicit permission
- **NEVER** modify database logic without asking first
- **ALWAYS** explain what database changes you plan to make
- **ALWAYS** create schema backup before any database work
- **ALWAYS** provide rollback plan for database changes

### **☁️ Railway Database Setup**
- **Database**: PostgreSQL hosted on Railway (cloud)
- **CLI**: Railway CLI is installed and project selected
- **Access**: Use Railway CLI for database operations
- **Backup**: Always backup schema before modifications

## 🛠️ **Development Environment**

### **Database Connection**
```bash
# Railway database (production/staging)
railway connect postgres  # Connect to Railway PostgreSQL
railway run python app.py  # Run app with Railway environment
```

### **Local Development**
```bash
# Local development with Railway database
source venv/bin/activate
railway run python app.py  # Uses Railway DATABASE_URL
```

## 📝 **Database Change Protocol**

### **Before ANY Database Changes:**
1. **ASK PERMISSION** - Explain what you want to change
2. **CREATE BACKUP** - Export current schema
3. **PROVIDE ROLLBACK PLAN** - How to undo changes
4. **GET APPROVAL** - Wait for explicit approval

### **Schema Backup Commands**
```bash
# Backup current schema
railway connect postgres -- pg_dump --schema-only > schema_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup data (if needed)
railway connect postgres -- pg_dump > full_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Rollback Commands**
```bash
# Restore schema from backup
railway connect postgres < schema_backup_YYYYMMDD_HHMMSS.sql
```

## 🚫 **FORBIDDEN ACTIONS**

### **Database**
- ❌ DROP TABLE without permission
- ❌ ALTER TABLE without permission  
- ❌ CREATE TABLE without permission
- ❌ DELETE data without permission
- ❌ UPDATE schema without backup

### **Git**
- ❌ Tag every commit
- ❌ Use tags for commit explanations
- ❌ Create unnecessary tags
- ❌ Force push without discussion

## ✅ **REQUIRED ACTIONS**

### **Database Work**
- ✅ Ask before any schema changes
- ✅ Create backup before changes
- ✅ Explain the change purpose
- ✅ Provide rollback plan
- ✅ Test changes thoroughly

### **Git Work**
- ✅ Write clear commit messages
- ✅ Use tags only for releases
- ✅ Keep commit history clean
- ✅ Push regularly to backup work

## 🎯 **Communication Protocol**

### **Database Changes Request Format**
```
I need to modify the database:

WHAT: [Describe the change]
WHY: [Explain the reason]
IMPACT: [What tables/data affected]
BACKUP: [Backup plan]
ROLLBACK: [How to undo]

Please approve before proceeding.
```

### **Example Request**
```
I need to modify the database:

WHAT: Add 'priority' column to moods table
WHY: To support mood priority levels feature
IMPACT: moods table only, no data loss
BACKUP: pg_dump schema before changes
ROLLBACK: ALTER TABLE moods DROP COLUMN priority;

Please approve before proceeding.
```

## 📊 **Current Project Status**

- **Version**: v0.4.1-stable
- **Database**: Railway PostgreSQL (cloud)
- **Environment**: Railway CLI configured
- **Status**: Stable, working application

---

**⚠️ IMPORTANT**: These guidelines must be followed in ALL future development sessions. Any AI assistant working on this project must read and follow these rules.

**Last Updated**: 2025-10-22  
**Next Session**: Must read this document first
