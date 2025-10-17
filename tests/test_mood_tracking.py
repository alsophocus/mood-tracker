import pytest
from unittest.mock import patch
from datetime import datetime
from app import get_db_connection

class TestMoodTracking:
    
    def test_save_mood_authenticated(self, authenticated_client, test_user):
        """Test saving mood when authenticated"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'good',
                'notes': 'Feeling great today!'
            })
            
            assert response.status_code == 302  # Redirect after save
    
    def test_save_mood_unauthenticated(self, client):
        """Test saving mood requires authentication"""
        response = client.post('/save_mood', data={
            'mood': 'good',
            'notes': 'Should not work'
        })
        
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_valid_mood_values(self, authenticated_client, test_user):
        """Test all valid mood values are accepted"""
        valid_moods = ['super sad', 'sad', 'neutral', 'good', 'super good']
        
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            for mood in valid_moods:
                response = authenticated_client.post('/save_mood', data={
                    'mood': mood,
                    'notes': f'Testing {mood}'
                })
                assert response.status_code == 302
    
    def test_mood_with_empty_notes(self, authenticated_client, test_user):
        """Test saving mood without notes"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'neutral'
                # No notes field
            })
            
            assert response.status_code == 302
    
    def test_mood_update_same_date(self, authenticated_client, test_user):
        """Test updating mood for the same date"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            # Save first mood
            authenticated_client.post('/save_mood', data={
                'mood': 'sad',
                'notes': 'Morning mood'
            })
            
            # Update mood for same date
            response = authenticated_client.post('/save_mood', data={
                'mood': 'good',
                'notes': 'Evening mood - much better!'
            })
            
            assert response.status_code == 302
            
            # Verify only one entry exists for today
            conn = get_db_connection()
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = ? AND date = ?', (1, today))
            count = cursor.fetchone()[0]
            assert count == 1
            conn.close()
    
    def test_mood_form_validation(self, authenticated_client, test_user):
        """Test form handles missing mood field"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.post('/save_mood', data={
                'notes': 'No mood selected'
                # Missing mood field
            })
            
            # Should handle gracefully (might redirect or show error)
            assert response.status_code in [302, 400]
    
    def test_long_notes_handling(self, authenticated_client, test_user):
        """Test handling of very long notes"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            long_note = 'A' * 1000  # Very long note
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'neutral',
                'notes': long_note
            })
            
            assert response.status_code == 302
    
    def test_special_characters_in_notes(self, authenticated_client, test_user):
        """Test notes with special characters and emojis"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            special_note = "Today was 😊 great! Had coffee ☕ & met friends 👥. Cost $15.99 (worth it!)"
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'super good',
                'notes': special_note
            })
            
            assert response.status_code == 302
