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
