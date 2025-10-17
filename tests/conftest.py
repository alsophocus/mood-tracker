import pytest
import tempfile
import os
from app import app, init_db
from flask_login import login_user
import factory
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """Create test client with temporary database"""
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use SQLite for testing - remove DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def authenticated_client(client):
    """Client with authenticated user session"""
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True
    return client

@pytest.fixture
def test_user():
    """Create test user data"""
    return {
        'id': 1,
        'email': 'test@example.com',
        'name': 'Test User',
        'provider': 'google'
    }

@pytest.fixture
def mock_oauth_response():
    """Mock OAuth provider response"""
    return {
        'userinfo': {
            'email': 'test@example.com',
            'name': 'Test User'
        }
    }

@pytest.fixture
def sample_moods():
    """Sample mood data for testing"""
    base_date = datetime.now().date()
    return [
        {'date': base_date - timedelta(days=i), 'mood': mood, 'notes': f'Note {i}'}
        for i, mood in enumerate(['super good', 'good', 'neutral', 'sad', 'super sad'])
    ]
