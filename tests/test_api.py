import pytest
import json
from unittest.mock import patch
from datetime import datetime, timedelta

class TestAPIEndpoints:
    
    def test_health_endpoint_healthy(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'database' in data
        assert 'mood_entries' in data
    
    def test_health_endpoint_database_error(self, client):
        """Test health endpoint handles database errors"""
        with patch('app.get_db_connection', side_effect=Exception('DB Error')):
            response = client.get('/health')
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'DB Error' in data['error']
    
    def test_mood_data_authenticated(self, authenticated_client):
        """Test mood data API requires authentication"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.get('/mood_data')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    def test_mood_data_unauthenticated(self, client):
        """Test mood data API redirects unauthenticated users"""
        response = client.get('/mood_data')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_mood_data_format(self, authenticated_client):
        """Test mood data API returns correct format"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            # Mock database response
            with patch('app.get_db_connection') as mock_conn:
                mock_cursor = mock_conn.return_value.cursor.return_value
                mock_cursor.fetchall.return_value = [
                    {'date': '2024-01-01', 'mood': 'good'},
                    {'date': '2024-01-02', 'mood': 'super good'}
                ]
                
                response = authenticated_client.get('/mood_data')
                data = json.loads(response.data)
                
                assert isinstance(data, list)
                for item in data:
                    assert 'month' in item
                    assert 'mood' in item
                    assert isinstance(item['mood'], (int, float))
    
    def test_export_pdf_authenticated(self, authenticated_client):
        """Test PDF export requires authentication"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            mock_user.name = 'Test User'
            
            response = authenticated_client.get('/export_pdf')
            assert response.status_code == 200
            assert response.content_type == 'application/pdf'
    
    def test_export_pdf_unauthenticated(self, client):
        """Test PDF export redirects unauthenticated users"""
        response = client.get('/export_pdf')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_export_pdf_filename(self, authenticated_client):
        """Test PDF export has correct filename"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            mock_user.name = 'Test User'
            
            response = authenticated_client.get('/export_pdf')
            assert 'attachment; filename=mood_report.pdf' in response.headers.get('Content-Disposition', '')
    
    def test_index_page_authenticated(self, authenticated_client):
        """Test main page loads for authenticated users"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            mock_user.name = 'Test User'
            
            response = authenticated_client.get('/')
            assert response.status_code == 200
            assert b'How are you feeling today?' in response.data
            assert b'Test User' in response.data
    
    def test_index_page_unauthenticated(self, client):
        """Test main page redirects unauthenticated users"""
        response = client.get('/')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_404_error_handling(self, client):
        """Test 404 error for non-existent endpoints"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed errors"""
        response = client.put('/save_mood')  # PUT not allowed
        assert response.status_code == 405
    
    def test_csrf_protection(self, authenticated_client):
        """Test CSRF protection on forms"""
        # This test depends on your CSRF implementation
        # For now, testing that forms work without CSRF in test mode
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'good',
                'notes': 'Test'
            })
            
            # Should work in test mode (CSRF disabled)
            assert response.status_code == 302
    
    def test_json_response_headers(self, authenticated_client):
        """Test JSON endpoints return correct headers"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            response = authenticated_client.get('/mood_data')
            assert response.content_type == 'application/json'
    
    def test_health_endpoint_performance(self, client):
        """Test health endpoint responds quickly"""
        import time
        
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        assert response.status_code in [200, 500]  # Either works or fails fast
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
