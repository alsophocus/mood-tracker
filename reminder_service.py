"""
SOLID-compliant reminder service
Single Responsibility Principle - handles only reminder operations
"""

from insights_interfaces import ReminderServiceInterface
from database import Database
from typing import Dict, List, Any
from datetime import datetime, time, timedelta
import json


class ReminderService(ReminderServiceInterface):
    """Single Responsibility - manages mood entry reminders"""
    
    def __init__(self, db: Database):
        self.db = db
        self._ensure_reminders_table()
    
    def _ensure_reminders_table(self):
        """Ensure reminders table exists"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mood_reminders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        message TEXT,
                        reminder_time TIME NOT NULL,
                        days_of_week VARCHAR(20) DEFAULT '1,2,3,4,5,6,7',
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_sent TIMESTAMP,
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Reminders table creation error: {e}")
    
    def create_reminder(self, user_id: int, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new reminder"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO mood_reminders (
                        user_id, title, message, reminder_time, 
                        days_of_week, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (
                    user_id,
                    reminder_data.get('title', 'Mood Check-in'),
                    reminder_data.get('message', 'How are you feeling today?'),
                    reminder_data.get('reminder_time'),
                    reminder_data.get('days_of_week', '1,2,3,4,5,6,7'),
                    json.dumps(reminder_data.get('metadata', {}))
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                return {
                    'success': True,
                    'reminder_id': result['id'],
                    'created_at': result['created_at'],
                    'message': 'Reminder created successfully!'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all reminders for user"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, message, reminder_time, days_of_week,
                           is_active, created_at, last_sent, metadata
                    FROM mood_reminders 
                    WHERE user_id = %s 
                    ORDER BY reminder_time
                """, (user_id,))
                
                reminders = cursor.fetchall()
                
                for reminder in reminders:
                    reminder['metadata'] = json.loads(reminder['metadata']) if reminder['metadata'] else {}
                    reminder['next_reminder'] = self._calculate_next_reminder(reminder)
                
                return reminders
                
        except Exception as e:
            print(f"Get reminders error: {e}")
            return []
    
    def should_send_reminder(self, user_id: int) -> bool:
        """Check if reminder should be sent"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user has logged mood today
                cursor.execute("""
                    SELECT COUNT(*) FROM moods 
                    WHERE user_id = %s AND date = CURRENT_DATE
                """, (user_id,))
                
                mood_count = cursor.fetchone()[0]
                
                # If already logged mood today, no reminder needed
                if mood_count > 0:
                    return False
                
                # Check active reminders for current time
                current_time = datetime.now().time()
                current_day = datetime.now().isoweekday()  # 1=Monday, 7=Sunday
                
                cursor.execute("""
                    SELECT COUNT(*) FROM mood_reminders 
                    WHERE user_id = %s 
                    AND is_active = true
                    AND reminder_time <= %s
                    AND days_of_week LIKE %s
                    AND (last_sent IS NULL OR last_sent::date < CURRENT_DATE)
                """, (user_id, current_time, f'%{current_day}%'))
                
                reminder_count = cursor.fetchone()[0]
                return reminder_count > 0
                
        except Exception as e:
            print(f"Should send reminder error: {e}")
            return False
    
    def mark_reminder_sent(self, reminder_id: int) -> Dict[str, Any]:
        """Mark reminder as sent"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE mood_reminders 
                    SET last_sent = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (reminder_id,))
                
                conn.commit()
                return {'success': True}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_next_reminder(self, reminder: Dict[str, Any]) -> str:
        """Calculate next reminder time"""
        try:
            reminder_time = reminder['reminder_time']
            days_of_week = [int(d) for d in reminder['days_of_week'].split(',')]
            
            now = datetime.now()
            current_day = now.isoweekday()
            
            # Find next occurrence
            for i in range(8):  # Check next 7 days
                check_date = now + timedelta(days=i)
                check_day = check_date.isoweekday()
                
                if check_day in days_of_week:
                    next_time = datetime.combine(check_date.date(), reminder_time)
                    if next_time > now:
                        return next_time.strftime('%Y-%m-%d %H:%M')
            
            return 'No upcoming reminder'
            
        except Exception:
            return 'Unknown'
