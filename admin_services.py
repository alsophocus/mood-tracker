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
        """Delete mood data until specified date"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # DEBUG: Check what data exists in the database
            cursor.execute('SELECT COUNT(*) FROM moods')
            total_records = cursor.fetchone()[0]
            
            # DEBUG: Get all dates in database to see format
            cursor.execute('SELECT DISTINCT date FROM moods ORDER BY date LIMIT 10')
            sample_dates = [str(row[0]) for row in cursor.fetchall()]
            
            # DEBUG: Check records with different date comparisons
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            count_with_date = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date::text <= %s', (str(target_date),))
            count_with_string = cursor.fetchone()[0]
            
            # Get total records before
            cursor.execute('SELECT COUNT(*) FROM moods')
            total_before = cursor.fetchone()[0]
            
            debug_info = {
                'total_records_in_db': total_records,
                'sample_dates': sample_dates,
                'target_date': str(target_date),
                'target_date_type': str(type(target_date)),
                'count_with_date_comparison': count_with_date,
                'count_with_string_comparison': count_with_string,
            }
            
            if count_with_date == 0:
                return {
                    'deleted': 0, 
                    'message': f'No records found to delete until {target_date}',
                    'total_before': total_before,
                    'total_after': total_before,
                    'target_date': str(target_date),
                    'debug_info': debug_info
                }
            
            # Delete records using the method that found records
            if count_with_date > 0:
                cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
            else:
                cursor.execute('DELETE FROM moods WHERE date::text <= %s', (str(target_date),))
                
            deleted = cursor.rowcount
            conn.commit()
            
            # Verify deletion by counting remaining records
            cursor.execute('SELECT COUNT(*) FROM moods')
            total_after = cursor.fetchone()[0]
            
            # Double-check no records exist until target date
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            remaining_until_date = cursor.fetchone()[0]
            
            # Get date range of remaining data
            cursor.execute('SELECT MIN(date), MAX(date) FROM moods')
            date_range = cursor.fetchone()
            
            return {
                'deleted': deleted,
                'message': f'Successfully deleted {deleted} records until {target_date}',
                'total_before': total_before,
                'total_after': total_after,
                'remaining_until_date': remaining_until_date,
                'target_date': str(target_date),
                'date_range_after': {
                    'start': str(date_range[0]) if date_range[0] else None,
                    'end': str(date_range[1]) if date_range[1] else None
                },
                'verification': 'PASSED' if remaining_until_date == 0 else f'FAILED - {remaining_until_date} records still exist until {target_date}',
                'debug_info': debug_info
            }
    
    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all mood data"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count before deletion
            cursor.execute('SELECT COUNT(*) FROM moods')
            count_before = cursor.fetchone()[0]
            
            if count_before == 0:
                return {
                    'deleted': 0,
                    'message': 'Database was already empty',
                    'total_before': 0,
                    'total_after': 0,
                    'verification': 'PASSED'
                }
            
            # Delete all records
            cursor.execute('DELETE FROM moods')
            deleted = cursor.rowcount
            
            # Reset sequence
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            conn.commit()
            
            # Verify deletion
            cursor.execute('SELECT COUNT(*) FROM moods')
            count_after = cursor.fetchone()[0]
            
            return {
                'deleted': deleted,
                'message': f'Successfully cleared all {deleted} mood records',
                'total_before': count_before,
                'total_after': count_after,
                'verification': 'PASSED' if count_after == 0 else f'FAILED - {count_after} records still exist'
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

class DatabaseTestService:
    """Database testing operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def test_connection(self) -> Dict[str, Any]:
        """Test basic database connectivity"""
        import traceback
        from config import Config
        
        try:
            # Check database URL configuration
            db_url = Config.DATABASE_URL
            if not db_url:
                return {
                    'success': False,
                    'error': 'DATABASE_URL is not configured',
                    'config_check': 'DATABASE_URL is None or empty'
                }
            
            # Show partial URL for debugging (hide password)
            url_parts = db_url.split('@')
            if len(url_parts) > 1:
                safe_url = f"{url_parts[0].split(':')[0]}://***:***@{url_parts[1]}"
            else:
                safe_url = "Invalid URL format"
            
            # Test direct psycopg connection
            try:
                import psycopg
                from psycopg.rows import dict_row
                
                # Try direct connection
                with psycopg.connect(db_url, row_factory=dict_row) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT 1')
                        result = cursor.fetchone()
                        
                        return {
                            'success': True,
                            'message': 'Direct psycopg connection successful',
                            'database_url_format': safe_url,
                            'test_result': result[0] if result else 'No result',
                            'connection_method': 'Direct psycopg'
                        }
                        
            except Exception as direct_error:
                # Try using the Database class method
                try:
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT 1')
                        result = cursor.fetchone()
                        
                        return {
                            'success': True,
                            'message': 'Database class connection successful',
                            'database_url_format': safe_url,
                            'test_result': result[0] if result else 'No result',
                            'connection_method': 'Database class',
                            'direct_connection_error': str(direct_error)
                        }
                        
                except Exception as class_error:
                    return {
                        'success': False,
                        'error': 'Both connection methods failed',
                        'database_url_format': safe_url,
                        'direct_connection_error': str(direct_error),
                        'class_connection_error': str(class_error),
                        'direct_traceback': traceback.format_exc(),
                        'database_url_length': len(db_url),
                        'database_url_starts_with': db_url[:20] if len(db_url) > 20 else db_url
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Configuration error: {str(e)}',
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
