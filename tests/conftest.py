import pytest
import tempfile
import os
from app import app, init_db, get_db_connection
from flask_login import login_user
import factory
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """Create test client with temporary database"""
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use SQLite for testing
    os.environ.pop('DATABASE_URL', None)
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def authenticated_client(client, test_user):
    """Client with authenticated user"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client

class UserFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n)
    email = factory.Faker('email')
    name = factory.Faker('name')
    provider = 'google'

@pytest.fixture
def test_user():
    """Create test user"""
    return UserFactory()

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
