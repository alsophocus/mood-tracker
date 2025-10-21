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
            
            # Count records first
            cursor.execute('SELECT COUNT(*) FROM moods WHERE date <= %s', (target_date,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                return {'deleted': 0, 'message': 'No records to delete'}
            
            # Delete records
            cursor.execute('DELETE FROM moods WHERE date <= %s', (target_date,))
            deleted = cursor.rowcount
            conn.commit()
            
            return {'deleted': deleted, 'message': f'Deleted {deleted} records until {target_date}'}
    
    def clear_all_data(self) -> Dict[str, Any]:
        """Clear all mood data"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM moods')
            count = cursor.fetchone()[0]
            
            cursor.execute('DELETE FROM moods')
            deleted = cursor.rowcount
            
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            conn.commit()
            
            return {'deleted': deleted, 'message': f'Cleared all {deleted} mood records'}

class DataGenerationService:
    """Data generation operations - Single Responsibility Principle"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def generate_fake_data(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Generate fake mood data for testing"""
        moods = list(MoodType)
        generated = 0
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for i in range(days):
                target_date = date.today() - timedelta(days=i)
                mood = random.choice(moods).value
                notes = f"Generated mood entry for {target_date}"
                
                cursor.execute('''
                    INSERT INTO moods (user_id, date, mood, notes, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, target_date, mood, notes, datetime.now()))
                
                generated += 1
            
            conn.commit()
            
        return {'generated': generated, 'message': f'Generated {generated} fake mood entries'}
    
    def generate_current_week_data(self, user_id: int) -> Dict[str, Any]:
        """Generate mood data for current week"""
        moods = list(MoodType)
        generated = 0
        
        # Get current week dates
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
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
            
        return {'generated': generated, 'message': f'Generated {generated} entries for current week'}

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
    
    def get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of available admin operations"""
        return [
            {
                'id': 'cleanup_until_oct19',
                'name': 'Cleanup Until Oct 19',
                'description': 'Delete all mood data until October 19, 2025',
                'category': 'cleanup',
                'params': []
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
            if operation_id == 'cleanup_until_oct19':
                return self.cleanup_service.cleanup_until_date(date(2025, 10, 19))
            
            elif operation_id == 'clear_all_data':
                return self.cleanup_service.clear_all_data()
            
            elif operation_id == 'generate_fake_data':
                days = params.get('days', 30)
                return self.generation_service.generate_fake_data(user_id, days)
            
            elif operation_id == 'generate_current_week':
                return self.generation_service.generate_current_week_data(user_id)
            
            elif operation_id == 'database_stats':
                return self.analytics_service.get_database_stats()
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation_id}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
