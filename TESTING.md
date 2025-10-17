# 🧪 Mood Tracker Test Suite

Comprehensive testing for the Mood Tracker application covering authentication, database operations, analytics, security, and API endpoints.

## 📋 Test Coverage

### 🔐 Authentication Tests (`test_auth.py`)
- OAuth login flows (Google & GitHub)
- User session management
- Login/logout functionality
- Authentication redirects
- Invalid provider handling
- User isolation verification

### 🗄️ Database Tests (`test_database.py`)
- Database initialization
- User CRUD operations
- Mood entry management
- Data isolation between users
- Duplicate date handling
- Foreign key relationships

### 😊 Mood Tracking Tests (`test_mood_tracking.py`)
- Mood saving functionality
- Form validation
- Authentication requirements
- Valid mood values
- Notes handling (empty, long, special characters)
- Same-date updates

### 📊 Analytics Tests (`test_analytics.py`)
- Streak calculations (current & best)
- Weekly pattern analysis
- Mood value mapping
- Empty data handling
- Single entry scenarios
- Complex streak scenarios

### 🌐 API Tests (`test_api.py`)
- Health endpoint monitoring
- Mood data API responses
- PDF export functionality
- Authentication requirements
- JSON response formats
- Error handling (404, 405)
- Performance testing

### 🛡️ Security Tests (`test_security.py`)
- SQL injection prevention
- XSS protection
- Session security
- Authentication enforcement
- Environment variable security
- Database schema security
- Rate limiting simulation

## 🚀 Running Tests

### Quick Test Run
```bash
./run_tests.sh
```

### Manual Test Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py::TestAuthentication::test_login_page_accessible
```

### Test Categories
```bash
# Authentication tests only
pytest tests/test_auth.py -v

# Database tests only
pytest tests/test_database.py -v

# Security tests only
pytest tests/test_security.py -v

# API tests only
pytest tests/test_api.py -v
```

## 📊 Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Paths**: 100% (auth, data security)

### Coverage Report
After running tests, view detailed coverage:
```bash
open htmlcov/index.html
```

## 🔧 Test Configuration

### Environment Setup
Tests use SQLite in-memory database for isolation:
- No external dependencies required
- Automatic cleanup after each test
- Fast execution

### Mocking Strategy
- OAuth providers (Google/GitHub)
- Database connections (when needed)
- User sessions
- External API calls

### Fixtures Available
- `client`: Flask test client
- `authenticated_client`: Pre-authenticated client
- `test_user`: Sample user data
- `mock_oauth_response`: OAuth response mock
- `sample_moods`: Test mood data

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest -v -s tests/
```

### Debug Specific Test
```bash
pytest -v -s tests/test_auth.py::TestAuthentication::test_login_page_accessible
```

### Print Debug Info
```bash
pytest --capture=no tests/
```

## 📈 Test Metrics

### Performance Benchmarks
- Health endpoint: < 5 seconds
- Authentication flow: < 10 seconds
- Database operations: < 1 second
- PDF generation: < 5 seconds

### Security Validations
- ✅ No SQL injection vulnerabilities
- ✅ XSS prevention in user inputs
- ✅ Authentication required for sensitive endpoints
- ✅ User data isolation
- ✅ Secure session management

## 🔄 Continuous Integration

### Pre-commit Hooks
```bash
# Run tests before commit
git add .
./run_tests.sh && git commit -m "Your message"
```

### GitHub Actions (Future)
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=80
```

## 🎯 Test Best Practices

### Writing New Tests
1. **Arrange**: Set up test data
2. **Act**: Execute the function
3. **Assert**: Verify the results
4. **Cleanup**: Handled by fixtures

### Test Naming
- `test_function_name_scenario`
- `test_save_mood_authenticated`
- `test_analytics_empty_data`

### Mock Usage
- Mock external services (OAuth, APIs)
- Don't mock your own code unless necessary
- Use fixtures for common setup

## 📝 Adding New Tests

### For New Features
1. Create test file: `tests/test_feature.py`
2. Add test class: `class TestFeature:`
3. Write test methods: `def test_feature_scenario:`
4. Update this documentation

### Test Template
```python
import pytest
from unittest.mock import patch

class TestNewFeature:
    
    def test_feature_success(self, authenticated_client):
        """Test successful feature operation"""
        response = authenticated_client.post('/new-endpoint', data={
            'param': 'value'
        })
        
        assert response.status_code == 200
        assert b'expected content' in response.data
    
    def test_feature_authentication_required(self, client):
        """Test feature requires authentication"""
        response = client.post('/new-endpoint')
        assert response.status_code == 302
        assert '/login' in response.location
```

## 🏆 Quality Gates

Before deployment, ensure:
- ✅ All tests pass
- ✅ Coverage > 80%
- ✅ No security test failures
- ✅ Performance benchmarks met
- ✅ No critical vulnerabilities

---

**Happy Testing! 🎉**
