import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from app import calculate_analytics, get_db_connection

class TestAnalytics:
    
    def setup_test_moods(self, user_id, moods_data):
        """Helper to create test mood data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create user first
        cursor.execute('INSERT INTO users (id, email, name, provider) VALUES (?, ?, ?, ?)',
                      (user_id, f'user{user_id}@test.com', f'User {user_id}', 'google'))
        
        for mood_data in moods_data:
            cursor.execute('INSERT INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                          (user_id, mood_data['date'], mood_data['mood'], mood_data.get('notes', '')))
        
        conn.commit()
        conn.close()
    
    def test_empty_analytics(self, client):
        """Test analytics with no mood data"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            assert analytics['current_streak'] == 0
            assert analytics['best_streak'] == 0
            assert analytics['weekly_patterns'] == {}
    
    def test_current_streak_calculation(self, client):
        """Test current good mood streak calculation"""
        user_id = 1
        base_date = datetime.now().date()
        
        # Create streak: good, good, super good (3 days)
        moods_data = [
            {'date': base_date - timedelta(days=2), 'mood': 'good'},
            {'date': base_date - timedelta(days=1), 'mood': 'good'},
            {'date': base_date, 'mood': 'super good'},
        ]
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            assert analytics['current_streak'] == 3
    
    def test_broken_streak(self, client):
        """Test streak breaks with bad mood"""
        user_id = 1
        base_date = datetime.now().date()
        
        # Streak broken by sad day
        moods_data = [
            {'date': base_date - timedelta(days=3), 'mood': 'good'},
            {'date': base_date - timedelta(days=2), 'mood': 'good'},
            {'date': base_date - timedelta(days=1), 'mood': 'sad'},  # Breaks streak
            {'date': base_date, 'mood': 'good'},  # New streak starts
        ]
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            assert analytics['current_streak'] == 1  # Only today
            assert analytics['best_streak'] == 2  # Previous 2-day streak
    
    def test_best_streak_calculation(self, client):
        """Test best streak is tracked correctly"""
        user_id = 1
        base_date = datetime.now().date()
        
        moods_data = [
            # First streak: 4 days
            {'date': base_date - timedelta(days=10), 'mood': 'good'},
            {'date': base_date - timedelta(days=9), 'mood': 'super good'},
            {'date': base_date - timedelta(days=8), 'mood': 'good'},
            {'date': base_date - timedelta(days=7), 'mood': 'good'},
            # Break
            {'date': base_date - timedelta(days=6), 'mood': 'sad'},
            # Second streak: 2 days
            {'date': base_date - timedelta(days=2), 'mood': 'good'},
            {'date': base_date - timedelta(days=1), 'mood': 'good'},
            # Break
            {'date': base_date, 'mood': 'neutral'},
        ]
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            assert analytics['best_streak'] == 4
            assert analytics['current_streak'] == 0  # Broken by neutral
    
    def test_weekly_patterns(self, client):
        """Test weekly pattern calculations"""
        user_id = 1
        
        # Create moods for different days of week
        moods_data = []
        base_date = datetime(2024, 1, 1)  # Monday
        
        for i in range(14):  # Two weeks
            date = base_date + timedelta(days=i)
            day_name = date.strftime('%A')
            
            # Mondays are sad, Fridays are good, others neutral
            if day_name == 'Monday':
                mood = 'sad'
            elif day_name == 'Friday':
                mood = 'super good'
            else:
                mood = 'neutral'
            
            moods_data.append({'date': date.date(), 'mood': mood})
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            patterns = analytics['weekly_patterns']
            assert patterns['Monday'] == 2.0  # Sad = 2
            assert patterns['Friday'] == 5.0  # Super good = 5
            assert patterns['Tuesday'] == 3.0  # Neutral = 3
    
    def test_mood_values_mapping(self, client):
        """Test mood string to numeric conversion"""
        user_id = 1
        base_date = datetime.now().date()
        
        moods_data = [
            {'date': base_date - timedelta(days=4), 'mood': 'super sad'},    # 1
            {'date': base_date - timedelta(days=3), 'mood': 'sad'},          # 2
            {'date': base_date - timedelta(days=2), 'mood': 'neutral'},      # 3
            {'date': base_date - timedelta(days=1), 'mood': 'good'},         # 4
            {'date': base_date, 'mood': 'super good'},                       # 5
        ]
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            # Should have current streak of 2 (good + super good)
            assert analytics['current_streak'] == 2
    
    def test_single_mood_entry(self, client):
        """Test analytics with only one mood entry"""
        user_id = 1
        base_date = datetime.now().date()
        
        moods_data = [
            {'date': base_date, 'mood': 'good'}
        ]
        
        self.setup_test_moods(user_id, moods_data)
        
        with patch('app.current_user') as mock_user:
            mock_user.id = user_id
            
            conn = get_db_connection()
            analytics = calculate_analytics(conn)
            conn.close()
            
            assert analytics['current_streak'] == 1
            assert analytics['best_streak'] == 1
            assert len(analytics['weekly_patterns']) == 1
