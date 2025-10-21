"""
SOLID-compliant goal tracking service
Single Responsibility Principle - handles only goal tracking operations
"""

from insights_interfaces import GoalTrackerInterface
from database import Database
from typing import Dict, List, Any
from datetime import date, datetime, timedelta
import json


class GoalTracker(GoalTrackerInterface):
    """Single Responsibility - manages mood goals and progress tracking"""
    
    def __init__(self, db: Database):
        self.db = db
        self._ensure_goals_table()
    
    def _ensure_goals_table(self):
        """Ensure goals table exists"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mood_goals (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        goal_type VARCHAR(50) NOT NULL,
                        target_value DECIMAL(5,2),
                        current_value DECIMAL(5,2) DEFAULT 0,
                        target_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'active',
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Goals table creation error: {e}")
    
    def create_goal(self, user_id: int, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mood goal"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO mood_goals (
                        user_id, title, description, goal_type, 
                        target_value, target_date, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (
                    user_id,
                    goal_data.get('title'),
                    goal_data.get('description', ''),
                    goal_data.get('goal_type'),
                    goal_data.get('target_value'),
                    goal_data.get('target_date'),
                    json.dumps(goal_data.get('metadata', {}))
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                return {
                    'success': True,
                    'goal_id': result['id'],
                    'created_at': result['created_at'],
                    'message': 'Goal created successfully!'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all goals for user"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, description, goal_type, target_value, 
                           current_value, target_date, created_at, status, metadata
                    FROM mood_goals 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC
                """, (user_id,))
                
                goals = cursor.fetchall()
                
                # Calculate progress for each goal
                for goal in goals:
                    goal['progress_percentage'] = self._calculate_progress(goal)
                    goal['days_remaining'] = self._calculate_days_remaining(goal['target_date'])
                    goal['metadata'] = json.loads(goal['metadata']) if goal['metadata'] else {}
                
                return goals
                
        except Exception as e:
            print(f"Get goals error: {e}")
            return []
    
    def update_goal_progress(self, goal_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update goal progress"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current goal
                cursor.execute("SELECT * FROM mood_goals WHERE id = %s", (goal_id,))
                goal = cursor.fetchone()
                
                if not goal:
                    return {'success': False, 'error': 'Goal not found'}
                
                # Calculate new progress based on goal type
                new_value = self._calculate_new_progress(goal, progress_data)
                
                # Update goal
                cursor.execute("""
                    UPDATE mood_goals 
                    SET current_value = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_value, goal_id))
                
                # Check if goal is completed
                status = 'completed' if new_value >= goal['target_value'] else 'active'
                if status != goal['status']:
                    cursor.execute("""
                        UPDATE mood_goals 
                        SET status = %s 
                        WHERE id = %s
                    """, (status, goal_id))
                
                conn.commit()
                
                return {
                    'success': True,
                    'new_value': new_value,
                    'status': status,
                    'completed': status == 'completed'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_progress(self, goal: Dict[str, Any]) -> float:
        """Calculate progress percentage"""
        if not goal['target_value'] or goal['target_value'] == 0:
            return 0
        
        progress = (goal['current_value'] / goal['target_value']) * 100
        return min(100, max(0, round(progress, 1)))
    
    def _calculate_days_remaining(self, target_date) -> int:
        """Calculate days remaining until target date"""
        if not target_date:
            return -1
        
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        today = date.today()
        delta = target_date - today
        return delta.days
    
    def _calculate_new_progress(self, goal: Dict[str, Any], progress_data: Dict[str, Any]) -> float:
        """Calculate new progress value based on goal type"""
        goal_type = goal['goal_type']
        current = goal['current_value'] or 0
        
        if goal_type == 'mood_average':
            # For mood average goals, recalculate based on recent moods
            return self._calculate_mood_average_progress(goal['user_id'])
        elif goal_type == 'streak':
            # For streak goals, increment by 1
            return current + 1
        elif goal_type == 'frequency':
            # For frequency goals, increment by progress amount
            return current + progress_data.get('increment', 1)
        else:
            return current + progress_data.get('value', 0)
    
    def _calculate_mood_average_progress(self, user_id: int) -> float:
        """Calculate current mood average for mood_average goals"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get last 7 days of moods
                cursor.execute("""
                    SELECT mood FROM moods 
                    WHERE user_id = %s AND date >= %s
                """, (user_id, date.today() - timedelta(days=7)))
                
                moods = cursor.fetchall()
                if not moods:
                    return 0
                
                # Convert to numeric and calculate average
                mood_values = [self._mood_to_numeric(mood['mood']) for mood in moods]
                return round(sum(mood_values) / len(mood_values), 2)
                
        except Exception:
            return 0
    
    def _mood_to_numeric(self, mood: str) -> float:
        """Convert mood string to numeric value"""
        mood_map = {
            'very bad': 1.0, 'bad': 2.0, 'slightly bad': 3.0,
            'neutral': 4.0, 'slightly well': 5.0, 'well': 6.0, 'very well': 7.0
        }
        return mood_map.get(mood.lower(), 4.0)
