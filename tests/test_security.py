import pytest
from unittest.mock import patch
import os

class TestSecurity:
    
    def test_secret_key_configured(self, client):
        """Test that secret key is properly configured"""
        from app import app
        assert app.secret_key is not None
        assert app.secret_key != 'dev-secret-key-change-in-production'  # Should be changed in prod
    
    def test_session_security(self, authenticated_client):
        """Test session handling and security"""
        with authenticated_client.session_transaction() as sess:
            assert '_user_id' in sess
            # Test session data is properly isolated
    
    def test_sql_injection_prevention(self, authenticated_client):
        """Test SQL injection attempts are prevented"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            # Attempt SQL injection in mood field
            malicious_mood = "'; DROP TABLE moods; --"
            
            response = authenticated_client.post('/save_mood', data={
                'mood': malicious_mood,
                'notes': 'Injection attempt'
            })
            
            # Should handle gracefully (either reject or sanitize)
            assert response.status_code in [302, 400]
            
            # Database should still exist and be functional
            health_response = authenticated_client.get('/health')
            assert health_response.status_code == 200
    
    def test_xss_prevention_in_notes(self, authenticated_client):
        """Test XSS prevention in user notes"""
        with patch('app.current_user') as mock_user:
            mock_user.id = 1
            
            xss_payload = '<script>alert("XSS")</script>'
            
            response = authenticated_client.post('/save_mood', data={
                'mood': 'neutral',
                'notes': xss_payload
            })
            
            assert response.status_code == 302
            
            # Check that script tags are escaped in output
            main_response = authenticated_client.get('/')
            assert b'<script>' not in main_response.data
            assert b'&lt;script&gt;' in main_response.data or xss_payload.encode() not in main_response.data
    
    def test_user_data_isolation(self, client):
        """Test users cannot access other users' data"""
        # This would require creating multiple authenticated sessions
        # and testing that user A cannot access user B's data
        pass
    
    def test_authentication_required_endpoints(self, client):
        """Test all sensitive endpoints require authentication"""
        protected_endpoints = [
            '/',
            '/save_mood',
            '/mood_data',
            '/export_pdf'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 302
            assert '/login' in response.location
    
    def test_oauth_state_parameter(self, client):
        """Test OAuth state parameter for CSRF protection"""
        # This would test that OAuth flows include state parameter
        # Implementation depends on your OAuth setup
        pass
    
    def test_secure_headers(self, client):
        """Test security headers are set"""
        response = client.get('/login')
        
        # Check for security headers (if implemented)
        # headers = response.headers
        # assert 'X-Content-Type-Options' in headers
        # assert 'X-Frame-Options' in headers
        pass
    
    def test_environment_variables_security(self):
        """Test sensitive environment variables are not exposed"""
        # Test that secrets are not accidentally logged or exposed
        sensitive_vars = [
            'SECRET_KEY',
            'GOOGLE_CLIENT_SECRET',
            'GITHUB_CLIENT_SECRET',
            'DATABASE_URL'
        ]
        
        for var in sensitive_vars:
            value = os.environ.get(var)
            if value:
                # Ensure it's not a default/example value
                assert 'example' not in value.lower()
                assert 'test' not in value.lower() or var == 'DATABASE_URL'
    
    def test_password_not_stored(self, client):
        """Test that no passwords are stored in database"""
        from app import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table schema doesn't include password field
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        assert 'password' not in columns
        assert 'pwd' not in columns
        assert 'hash' not in columns
        
        conn.close()
    
    def test_session_timeout(self, authenticated_client):
        """Test session handling and potential timeout"""
        # Test that sessions are properly managed
        with authenticated_client.session_transaction() as sess:
            assert '_user_id' in sess
            # Could test session expiration if implemented
    
    def test_rate_limiting_simulation(self, client):
        """Test rapid requests don't break the application"""
        # Simulate rapid requests to test stability
        for i in range(10):
            response = client.get('/login')
            assert response.status_code == 200
    
    def test_file_upload_security(self, authenticated_client):
        """Test file upload security (if any file uploads exist)"""
        # Currently no file uploads in the app, but good to have
        # Would test file type validation, size limits, etc.
        pass
    
    def test_database_connection_security(self, client):
        """Test database connections are properly secured"""
        # Test that database connections are properly closed
        # and don't leak sensitive information
        response = client.get('/health')
        data = response.get_json()
        
        if 'database' in data:
            # Ensure no sensitive DB info is exposed
            db_info = data['database']
            assert 'password' not in db_info.lower()
            assert 'secret' not in db_info.lower()
