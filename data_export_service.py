"""
SOLID-compliant data export/import service
Single Responsibility Principle - handles only data export/import operations
"""

from insights_interfaces import DataExportInterface
from database import Database
from typing import Dict, List, Any
from datetime import datetime
import json
import csv
import io


class DataExportService(DataExportInterface):
    """Single Responsibility - manages data export and import"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def export_user_data(self, user_id: int, format: str = 'json') -> Dict[str, Any]:
        """Export all user data"""
        try:
            data = {
                'export_info': {
                    'user_id': user_id,
                    'export_date': datetime.now().isoformat(),
                    'format': format,
                    'version': '1.0'
                },
                'moods': self._export_moods(user_id),
                'tags': self._export_tags(user_id),
                'goals': self._export_goals(user_id),
                'reminders': self._export_reminders(user_id)
            }
            
            if format == 'json':
                return {
                    'success': True,
                    'data': data,
                    'filename': f'mood_data_{user_id}_{datetime.now().strftime("%Y%m%d")}.json'
                }
            elif format == 'csv':
                csv_data = self._convert_to_csv(data)
                return {
                    'success': True,
                    'data': csv_data,
                    'filename': f'mood_data_{user_id}_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            else:
                return {'success': False, 'error': 'Unsupported format'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_user_data(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Import user data"""
        try:
            imported_counts = {
                'moods': 0,
                'tags': 0,
                'goals': 0,
                'reminders': 0
            }
            
            # Import moods
            if 'moods' in data:
                imported_counts['moods'] = self._import_moods(user_id, data['moods'])
            
            # Import tags
            if 'tags' in data:
                imported_counts['tags'] = self._import_tags(user_id, data['tags'])
            
            # Import goals
            if 'goals' in data:
                imported_counts['goals'] = self._import_goals(user_id, data['goals'])
            
            # Import reminders
            if 'reminders' in data:
                imported_counts['reminders'] = self._import_reminders(user_id, data['reminders'])
            
            return {
                'success': True,
                'imported_counts': imported_counts,
                'message': 'Data imported successfully!'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _export_moods(self, user_id: int) -> List[Dict[str, Any]]:
        """Export mood data"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT m.*, 
                           ARRAY_AGG(t.name) as tags
                    FROM moods m
                    LEFT JOIN mood_tags mt ON m.id = mt.mood_id
                    LEFT JOIN tags t ON mt.tag_id = t.id
                    WHERE m.user_id = %s
                    GROUP BY m.id
                    ORDER BY m.date DESC
                """, (user_id,))
                
                return cursor.fetchall()
        except Exception:
            return []
    
    def _export_tags(self, user_id: int) -> List[Dict[str, Any]]:
        """Export tags used by user"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DISTINCT t.*
                    FROM tags t
                    JOIN mood_tags mt ON t.id = mt.tag_id
                    JOIN moods m ON mt.mood_id = m.id
                    WHERE m.user_id = %s
                """, (user_id,))
                
                return cursor.fetchall()
        except Exception:
            return []
    
    def _export_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """Export user goals"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM mood_goals 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                return cursor.fetchall()
        except Exception:
            return []
    
    def _export_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Export user reminders"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM mood_reminders 
                    WHERE user_id = %s
                    ORDER BY reminder_time
                """, (user_id,))
                
                return cursor.fetchall()
        except Exception:
            return []
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert data to CSV format"""
        output = io.StringIO()
        
        # Export moods as main CSV
        if data['moods']:
            writer = csv.DictWriter(output, fieldnames=data['moods'][0].keys())
            writer.writeheader()
            writer.writerows(data['moods'])
        
        return output.getvalue()
    
    def _import_moods(self, user_id: int, moods: List[Dict[str, Any]]) -> int:
        """Import mood data"""
        count = 0
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for mood in moods:
                    cursor.execute("""
                        INSERT INTO moods (user_id, mood, date, notes, timestamp,
                                         context_location, context_activity, context_weather, context_notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, date) DO NOTHING
                    """, (
                        user_id, mood.get('mood'), mood.get('date'), mood.get('notes'),
                        mood.get('timestamp'), mood.get('context_location'),
                        mood.get('context_activity'), mood.get('context_weather'),
                        mood.get('context_notes')
                    ))
                    count += 1
                
                conn.commit()
        except Exception as e:
            print(f"Import moods error: {e}")
        
        return count
    
    def _import_goals(self, user_id: int, goals: List[Dict[str, Any]]) -> int:
        """Import goals data"""
        count = 0
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for goal in goals:
                    cursor.execute("""
                        INSERT INTO mood_goals (user_id, title, description, goal_type,
                                              target_value, current_value, target_date, status, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id, goal.get('title'), goal.get('description'),
                        goal.get('goal_type'), goal.get('target_value'),
                        goal.get('current_value'), goal.get('target_date'),
                        goal.get('status'), goal.get('metadata')
                    ))
                    count += 1
                
                conn.commit()
        except Exception as e:
            print(f"Import goals error: {e}")
        
        return count
    
    def _import_reminders(self, user_id: int, reminders: List[Dict[str, Any]]) -> int:
        """Import reminders data"""
        count = 0
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for reminder in reminders:
                    cursor.execute("""
                        INSERT INTO mood_reminders (user_id, title, message, reminder_time,
                                                   days_of_week, is_active, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id, reminder.get('title'), reminder.get('message'),
                        reminder.get('reminder_time'), reminder.get('days_of_week'),
                        reminder.get('is_active'), reminder.get('metadata')
                    ))
                    count += 1
                
                conn.commit()
        except Exception as e:
            print(f"Import reminders error: {e}")
        
        return count
