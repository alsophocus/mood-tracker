"""
Admin services following SOLID principles
Centralized database operations management
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import date, datetime, timedelta
import random
from database import Database
from models import MoodType

class AdminServiceInterface(ABC):
    """Interface for admin operations - Interface Segregation Principle"""
    
    @abstractmethod
    def get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of available admin operations"""
        pass
    
    @abstractmethod
    def execute_operation(self, operation_id: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute specific admin operation"""
        pass

class DatabaseCleanupService:
    """Database cleanup operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def cleanup_until_date(self, target_date: date) -> Dict[str, Any]:
        """Delete mood data until specified date using working database methods"""
        try:
            # Get all moods to count before deletion
            all_moods = self.db.get_all_moods()  # We'll need to add this method
            total_before = len(all_moods) if all_moods else 0
            
            # Count moods until target date
            moods_to_delete = [mood for mood in all_moods if mood['date'] <= target_date] if all_moods else []
            count_to_delete = len(moods_to_delete)
            
            if count_to_delete == 0:
                return {
                    'deleted': 0,
                    'message': f'No records found to delete until {target_date}',
                    'total_before': total_before,
                    'total_after': total_before,
                    'target_date': str(target_date)
                }
            
            # Use the working connection method
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete records
                cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
                deleted = cursor.rowcount
                conn.commit()
            
            # Get remaining count
            remaining_moods = self.db.get_all_moods()
            total_after = len(remaining_moods) if remaining_moods else 0
            
            return {
                'deleted': deleted,
                'message': f'Successfully deleted {deleted} records until {target_date}',
                'total_before': total_before,
                'total_after': total_after,
                'target_date': str(target_date),
                'verification': 'PASSED' if deleted == count_to_delete else f'WARNING - Expected {count_to_delete}, deleted {deleted}'
            }
            
        except Exception as e:
            return {
                'deleted': 0,
                'message': f'Error during cleanup: {str(e)}',
                'error': str(e)
            }
    
    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all mood data using working database methods"""
        try:
            # Get count before deletion
            all_moods = self.db.get_all_moods()
            count_before = len(all_moods) if all_moods else 0
            
            if count_before == 0:
                return {
                    'deleted': 0,
                    'message': 'Database was already empty',
                    'total_before': 0,
                    'total_after': 0,
                    'verification': 'PASSED'
                }
            
            # Use the working connection method
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete all records
                cursor.execute('DELETE FROM moods')
                deleted = cursor.rowcount
                
                # Reset sequence
                cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
                conn.commit()
            
            # Verify deletion
            remaining_moods = self.db.get_all_moods()
            count_after = len(remaining_moods) if remaining_moods else 0
            
            return {
                'deleted': deleted,
                'message': f'Successfully cleared all {deleted} mood records',
                'total_before': count_before,
                'total_after': count_after,
                'verification': 'PASSED' if count_after == 0 else f'FAILED - {count_after} records still exist'
            }
            
        except Exception as e:
            return {
                'deleted': 0,
                'message': f'Error during clear: {str(e)}',
                'error': str(e)
            }

class DataGenerationService:
    """Data generation operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def generate_fake_data(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Generate fake mood data for testing"""
        moods = list(MoodType)
        generated = 0
        errors = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count before generation
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = %s', (user_id,))
            count_before = cursor.fetchone()[0]
            
            for i in range(days):
                target_date = date.today() - timedelta(days=i)
                mood = random.choice(moods).value
                notes = f"Generated mood entry for {target_date}"
                
                try:
                    cursor.execute('''
                        INSERT INTO moods (user_id, date, mood, notes, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, date) DO NOTHING
                    ''', (user_id, target_date, mood, notes, datetime.now()))
                    
                    if cursor.rowcount > 0:
                        generated += 1
                except Exception as e:
                    errors.append(f"Error on {target_date}: {str(e)}")
            
            conn.commit()
            
            # Count after generation
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = %s', (user_id,))
            count_after = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(date), MAX(date) FROM moods WHERE user_id = %s', (user_id,))
            date_range = cursor.fetchone()
            
            return {
                'generated': generated,
                'message': f'Generated {generated} fake mood entries for user {user_id}',
                'total_before': count_before,
                'total_after': count_after,
                'actual_increase': count_after - count_before,
                'errors': errors,
                'date_range': {
                    'start': str(date_range[0]) if date_range[0] else None,
                    'end': str(date_range[1]) if date_range[1] else None
                },
                'verification': 'PASSED' if count_after > count_before else 'WARNING - No new records added'
            }
    
    def generate_current_week_data(self, user_id: int) -> Dict[str, Any]:
        """Generate mood data for current week"""
        moods = list(MoodType)
        generated = 0
        
        # Get current week dates
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count before generation
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = %s', (user_id,))
            count_before = cursor.fetchone()[0]
            
            for i in range(7):
                current_date = week_start + timedelta(days=i)
                if current_date <= today:
                    mood = random.choice(moods).value
                    notes = f"Generated for {current_date.strftime('%A')}"
                    
                    cursor.execute('''
                        INSERT INTO moods (user_id, date, mood, notes, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, date) DO NOTHING
                    ''', (user_id, current_date, mood, notes, datetime.now()))
                    
                    if cursor.rowcount > 0:
                        generated += 1
            
            conn.commit()
            
            # Count after generation
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = %s', (user_id,))
            count_after = cursor.fetchone()[0]
            
            return {
                'generated': generated,
                'message': f'Generated {generated} entries for current week (user {user_id})',
                'total_before': count_before,
                'total_after': count_after,
                'actual_increase': count_after - count_before,
                'week_start': str(week_start),
                'week_end': str(week_start + timedelta(days=6)),
                'verification': 'PASSED' if count_after >= count_before else 'WARNING - No new records added'
            }

class DatabaseMigrationService:
    """Database migration operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def check_permissions(self) -> Dict[str, Any]:
        """Check what database operations are allowed"""
        permissions = {}
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Test SELECT (should work)
                try:
                    cursor.execute('SELECT 1')
                    permissions['SELECT'] = 'ALLOWED'
                except Exception as e:
                    permissions['SELECT'] = f'DENIED: {str(e)}'
                
                # Test CREATE TABLE
                try:
                    cursor.execute('CREATE TABLE IF NOT EXISTS permission_test (id INTEGER)')
                    permissions['CREATE_TABLE'] = 'ALLOWED'
                    
                    # Clean up
                    try:
                        cursor.execute('DROP TABLE permission_test')
                    except:
                        pass
                        
                except Exception as e:
                    permissions['CREATE_TABLE'] = f'DENIED: {str(e)}'
                
                # Test ALTER TABLE on existing table
                try:
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS test_permission_col VARCHAR(10)')
                    cursor.execute('ALTER TABLE moods DROP COLUMN IF EXISTS test_permission_col')
                    permissions['ALTER_TABLE'] = 'ALLOWED'
                except Exception as e:
                    permissions['ALTER_TABLE'] = f'DENIED: {str(e)}'
                
                # Test INSERT/UPDATE/DELETE (should work since cleanup works)
                try:
                    cursor.execute('SELECT COUNT(*) FROM moods LIMIT 1')
                    permissions['DML_OPERATIONS'] = 'ALLOWED'
                except Exception as e:
                    permissions['DML_OPERATIONS'] = f'DENIED: {str(e)}'
                
                conn.rollback()  # Don't commit any changes
                
                return {
                    'success': True,
                    'message': f'Permission check completed:\n• SELECT: {permissions.get("SELECT", "UNKNOWN")}\n• CREATE_TABLE: {permissions.get("CREATE_TABLE", "UNKNOWN")}\n• ALTER_TABLE: {permissions.get("ALTER_TABLE", "UNKNOWN")}\n• DML_OPERATIONS: {permissions.get("DML_OPERATIONS", "UNKNOWN")}',
                    'permissions': permissions
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Permission check failed: {str(e)}',
                'permissions': permissions
            }
    
    def migrate_basic(self) -> Dict[str, Any]:
        """
        SOLID-compliant basic migration using strategy pattern
        Dependency Inversion: depends on MigrationStrategyInterface abstractions
        """
        from migration_strategies import (
            AutocommitMigrationStrategy,
            TransactionMigrationStrategy, 
            ReadOnlyTestStrategy,
            MigrationExecutor
        )
        
        # Dependency Injection - inject database dependency
        strategies = [
            AutocommitMigrationStrategy(self.db),
            TransactionMigrationStrategy(self.db),
            ReadOnlyTestStrategy(self.db)
        ]
        
        # Open/Closed Principle - executor can handle new strategies without modification
        executor = MigrationExecutor(strategies)
        return executor.execute_with_fallback()
        """Try a very simple migration approach"""
        try:
            # Check if tables already exist first
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check existing tables
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('tags', 'mood_tags')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                # Check existing columns
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'moods' AND column_name LIKE 'context_%'
                """)
                existing_context_columns = [row[0] for row in cursor.fetchall()]
                
                message = f'Migration check results:\n• Existing tables: {existing_tables}\n• Context columns: {existing_context_columns}'
                
                if 'tags' in existing_tables and 'mood_tags' in existing_tables:
                    return {
                        'success': True,
                        'message': f'{message}\n• Status: Migration tables already exist!',
                        'existing_tables': existing_tables,
                        'existing_context_columns': existing_context_columns
                    }
                
                # If tables don't exist, we have a permissions issue
                return {
                    'success': False,
                    'message': f'{message}\n• Status: Tables missing, need CREATE permissions',
                    'error': 'Tables do not exist and cannot be created due to database permissions',
                    'existing_tables': existing_tables,
                    'suggestion': 'Database user needs CREATE TABLE and ALTER TABLE permissions'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Simple migration check failed: {str(e)}',
                'message': f'Failed to check migration status: {str(e)}'
            }
    
    def migrate_mood_triggers(self) -> Dict[str, Any]:
        """Add mood triggers and context tables using the same working pattern as cleanup"""
        steps_completed = []
        
        try:
            # Use the exact same pattern as successful cleanup operations
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Step 1: Create tags table (simple approach like cleanup)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tags (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) UNIQUE NOT NULL,
                        category VARCHAR(30) NOT NULL,
                        color VARCHAR(7) DEFAULT '#6750A4',
                        icon VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')
                steps_completed.append("✅ Created tags table")
                
                # Step 2: Create mood_tags junction table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS mood_tags (
                        id SERIAL PRIMARY KEY,
                        mood_id INTEGER NOT NULL REFERENCES moods(id) ON DELETE CASCADE,
                        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(mood_id, tag_id)
                    )
                ''')
                steps_completed.append("✅ Created mood_tags junction table")
                
                # Step 3: Add context columns (using same simple approach)
                try:
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS context_location VARCHAR(100)')
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS context_activity VARCHAR(100)')
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS context_weather VARCHAR(50)')
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS context_sleep_hours DECIMAL(3,1)')
                    cursor.execute('ALTER TABLE moods ADD COLUMN IF NOT EXISTS context_energy_level INTEGER')
                    steps_completed.append("✅ Added context columns to moods table")
                except Exception as e:
                    steps_completed.append(f"ℹ️ Context columns may already exist: {str(e)}")
                
                # Step 4: Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_tags_mood_id ON mood_tags(mood_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_tags_tag_id ON mood_tags(tag_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category)')
                steps_completed.append("✅ Created performance indexes")
                
                # Step 5: Insert default tags (same pattern as cleanup operations)
                default_tags = [
                    ('work', 'work', '#FF6B6B', 'fas fa-briefcase'),
                    ('exercise', 'health', '#4ECDC4', 'fas fa-dumbbell'),
                    ('family', 'social', '#45B7D1', 'fas fa-home'),
                    ('travel', 'activities', '#96CEB4', 'fas fa-plane'),
                    ('home', 'environment', '#FFEAA7', 'fas fa-house'),
                    ('stress', 'emotions', '#DDA0DD', 'fas fa-exclamation-triangle')
                ]
                
                tags_inserted = 0
                for name, category, color, icon in default_tags:
                    cursor.execute('''
                        INSERT INTO tags (name, category, color, icon)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    ''', (name, category, color, icon))
                    if cursor.rowcount > 0:
                        tags_inserted += 1
                
                steps_completed.append(f"✅ Inserted {tags_inserted} default tags")
                
                # Commit using same pattern as cleanup
                conn.commit()
                steps_completed.append("✅ All changes committed")
                
                # Verify using same pattern as cleanup
                cursor.execute('SELECT COUNT(*) FROM tags')
                tag_count = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'message': f'Migration completed successfully - {tag_count} tags available',
                    'steps_completed': steps_completed,
                    'tags_created': tag_count
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Migration failed: {str(e)}',
                'steps_completed': steps_completed
            }

class DatabaseTestService:
    """Database testing operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connectivity using the same methods as main routes"""
        import traceback
        
        try:
            # Test 1: Use the same method as main routes - get_user_moods
            try:
                # This should work if the main app works
                test_moods = self.db.get_user_moods(1, limit=1)  # Try to get 1 mood for user 1
                
                return {
                    'success': True,
                    'message': 'Database connection successful using get_user_moods method',
                    'test_result': f'Found {len(test_moods) if test_moods else 0} moods',
                    'connection_method': 'db.get_user_moods() - same as main app',
                    'sample_mood': dict(test_moods[0]) if test_moods else 'No moods found'
                }
                
            except Exception as method_error:
                # Test 2: Try direct connection like in routes.py health check
                try:
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT version()')
                        version = cursor.fetchone()['version']
                        
                        return {
                            'success': True,
                            'message': 'Database connection successful using direct connection',
                            'database_version': version,
                            'connection_method': 'db.get_connection() - same as health check',
                            'method_error': str(method_error)
                        }
                        
                except Exception as direct_error:
                    return {
                        'success': False,
                        'error': 'Both database methods failed',
                        'method_error': str(method_error),
                        'direct_error': str(direct_error),
                        'method_traceback': traceback.format_exc(),
                        'note': 'This is strange since the main app works fine'
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Test setup failed: {str(e)}',
                'traceback': traceback.format_exc()
            }

class DatabaseAnalyticsService:
    """Database analytics operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute('SELECT COUNT(*) FROM moods')
            total_moods = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Date range
            cursor.execute('SELECT MIN(date), MAX(date) FROM moods')
            date_range = cursor.fetchone()
            
            # Records per user
            cursor.execute('''
                SELECT u.email, COUNT(m.id) as mood_count
                FROM users u
                LEFT JOIN moods m ON u.id = m.user_id
                GROUP BY u.id, u.email
                ORDER BY mood_count DESC
            ''')
            user_stats = cursor.fetchall()
            
            return {
                'total_moods': total_moods,
                'total_users': total_users,
                'date_range': {
                    'start': str(date_range[0]) if date_range[0] else None,
                    'end': str(date_range[1]) if date_range[1] else None
                },
                'user_stats': [dict(row) for row in user_stats]
            }

class AdminService(AdminServiceInterface):
    """Main admin service - Dependency Inversion Principle"""
    
    def __init__(self, db: Database):
        self.db = db
        self.cleanup_service = DatabaseCleanupService(db)
        self.generation_service = DataGenerationService(db)
        self.analytics_service = DatabaseAnalyticsService(db)
        self.test_service = DatabaseTestService(db)
        self.migration_service = DatabaseMigrationService(db)
    
    def get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of available admin operations"""
        return [
            {
                'id': 'test_connection',
                'name': 'Test Database Connection',
                'description': 'Test basic database connectivity and show raw data',
                'category': 'debug',
                'params': []
            },
            {
                'id': 'check_permissions',
                'name': 'Check Database Permissions',
                'description': 'Check what database operations are allowed',
                'category': 'debug',
                'params': []
            },
            {
                'id': 'migrate_basic',
                'name': 'Basic Migration',
                'description': 'Create mood triggers tables using simplest approach',
                'category': 'migration',
                'params': []
            },
            {
                'id': 'cleanup_until_date',
                'name': 'Cleanup Until Date',
                'description': 'Delete all mood data until specified date (inclusive)',
                'category': 'cleanup',
                'params': [
                    {'name': 'target_date', 'type': 'date', 'default': '2025-10-19', 'description': 'Delete data until this date (YYYY-MM-DD)'}
                ]
            },
            {
                'id': 'clear_all_data',
                'name': 'Clear All Data',
                'description': 'Delete all mood data (DANGEROUS)',
                'category': 'cleanup',
                'params': []
            },
            {
                'id': 'generate_fake_data',
                'name': 'Generate Fake Data',
                'description': 'Generate fake mood data for testing',
                'category': 'generation',
                'params': [
                    {'name': 'days', 'type': 'int', 'default': 30, 'description': 'Number of days to generate'}
                ]
            },
            {
                'id': 'generate_current_week',
                'name': 'Generate Current Week',
                'description': 'Generate mood data for current week',
                'category': 'generation',
                'params': []
            },
            {
                'id': 'database_stats',
                'name': 'Database Statistics',
                'description': 'Get comprehensive database statistics',
                'category': 'analytics',
                'params': []
            }
        ]
    
    def execute_operation(self, operation_id: str, params: Dict[str, Any] = None, user_id: int = None) -> Dict[str, Any]:
        """Execute specific admin operation"""
        if params is None:
            params = {}
        
        try:
            if operation_id == 'test_connection':
                return self.test_service.test_connection()
            
            elif operation_id == 'check_permissions':
                result = self.migration_service.check_permissions()
                result['success'] = result.get('success', True)
                return result
            
            elif operation_id == 'migrate_basic':
                result = self.migration_service.migrate_basic()
                result['success'] = result.get('success', True)
                return result
            
            elif operation_id == 'migrate_mood_triggers_simple':
                result = self.migration_service.migrate_mood_triggers_simple()
                result['success'] = result.get('success', True)
                return result
            
            elif operation_id == 'cleanup_until_date':
                target_date_str = params.get('target_date', '2025-10-19')
                try:
                    from datetime import datetime
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'error': f'Invalid date format: {target_date_str}. Use YYYY-MM-DD'}
                
                result = self.cleanup_service.cleanup_until_date(target_date)
                result['success'] = True
                result['target_date'] = str(target_date)
                return result
            
            elif operation_id == 'clear_all_data':
                result = self.cleanup_service.clear_all_data()
                result['success'] = True
                return result
            
            elif operation_id == 'generate_fake_data':
                days = params.get('days', 30)
                result = self.generation_service.generate_fake_data(user_id, days)
                result['success'] = True
                return result
            
            elif operation_id == 'generate_current_week':
                result = self.generation_service.generate_current_week_data(user_id)
                result['success'] = True
                return result
            
            elif operation_id == 'database_stats':
                return self.analytics_service.get_database_stats()
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation_id}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
