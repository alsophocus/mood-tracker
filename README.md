# 🌈 Mood Tracker

A secure, modern web application to track your daily mood with advanced analytics, OAuth authentication, and beautiful insights.

## ✨ Features

### 🔐 **Secure Authentication**
- **OAuth Login** with Google & GitHub
- **User-specific data** - complete privacy and isolation
- **Session management** with Flask-Login
- **No passwords stored** - OAuth only

### 😊 **Core Mood Tracking**
- **5 Mood Levels**: Super Sad, Sad, Neutral, Good, Super Good
- **Daily logging** with optional notes
- **Same-day updates** - modify your mood throughout the day
- **Rich text notes** with emoji support

### 📊 **Advanced Analytics**
- **Current Streak**: Track consecutive good days (mood 4-5)
- **Best Streak**: Your longest streak of good days ever
- **Weekly Patterns**: See which days you feel best/worst
- **Monthly Trends**: Interactive line chart showing mood over time
- **Real-time Dashboard**: System health monitoring

### 🎨 **Modern UI/UX**
- **Beautiful gradient design** with smooth animations
- **Responsive layout** - works on all devices
- **Interactive charts** powered by Chart.js
- **Hover effects** and modern card layouts
- **System status dashboard** with real-time monitoring

### 📈 **Data & Export**
- **PostgreSQL database** for persistent storage
- **PDF export** with personalized reports
- **Data visualization** with monthly trend analysis
- **User isolation** - your data stays private

### 🧪 **Enterprise Testing**
- **60+ automated tests** covering all functionality
- **80% code coverage** requirement
- **Security testing** (SQL injection, XSS prevention)
- **CI/CD pipeline** with Railway integration

## 🚀 Live Demo

**Production App**: https://mood-tracker-production-6fa4.up.railway.app/

## 🛠 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/alsophocus/mood-tracker.git
cd mood-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy .env.example to .env)
cp .env.example .env
# Edit .env with your OAuth credentials

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

### 🧪 Run Tests
```bash
# Run all tests with coverage
./run_tests.sh

# Or manually
pytest tests/ --cov=app --cov-report=html -v
```

## 🔧 Configuration

### Required Environment Variables
```bash
# Database (Railway provides this automatically)
DATABASE_URL=postgresql://username:password@host:port/database

# Security
SECRET_KEY=your-super-secret-key-here

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth (from GitHub Developer Settings)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 🌐 Deployment

### Railway Deployment (Recommended)
1. **Fork this repository**
2. **Create Railway account** at [railway.app](https://railway.app)
3. **Create PostgreSQL database** in Railway
4. **Deploy from GitHub** - connect your forked repo
5. **Set environment variables** in Railway dashboard
6. **Update OAuth redirect URIs** with your Railway URL

### OAuth Setup Guide

#### Google OAuth:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID
4. Add redirect URI: `https://your-railway-url/callback/google`

#### GitHub OAuth:
1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Create new OAuth app
3. Set callback URL: `https://your-railway-url/callback/github`

### Automated Testing Pipeline
Railway automatically runs tests before deployment:
- ✅ Authentication & OAuth tests
- ✅ Database operation tests  
- ✅ Security validation tests
- ✅ API endpoint tests
- ✅ Analytics calculation tests

**Deployment only succeeds if all tests pass!**

## 📊 Understanding Your Data

### Mood Scale
- **Super Sad** (1): 😢 Very low mood
- **Sad** (2): 😞 Below average mood  
- **Neutral** (3): 😐 Average/okay mood
- **Good** (4): 😊 Above average mood
- **Super Good** (5): 😄 Excellent mood

### Analytics Explained
- **Current Streak**: Consecutive days with "Good" or "Super Good" mood
- **Best Streak**: Your longest streak of good days
- **Weekly Patterns**: Average mood for each day of the week (1.0-5.0 scale)
- **Monthly Trends**: Visual chart showing mood progression over time

### System Dashboard
- **Database Status**: Real-time connection monitoring
- **Analytics Status**: Calculation engine health
- **Service Status**: Overall application health

## 🛡️ Security Features

### Authentication Security
- **OAuth 2.0** with Google & GitHub (no password storage)
- **CSRF protection** on all forms
- **Secure session management** with Flask-Login
- **User data isolation** - users can only access their own data

### Data Protection
- **SQL injection prevention** with parameterized queries
- **XSS protection** with input sanitization
- **Environment variable security** for sensitive credentials
- **HTTPS enforcement** in production

### Testing Coverage
- **Authentication flow testing**
- **SQL injection attempt simulation**
- **XSS payload testing**
- **Session security validation**
- **User isolation verification**

## 🧪 Testing

### Test Categories
- **Authentication Tests** (`test_auth.py`) - OAuth flows, session management
- **Database Tests** (`test_database.py`) - CRUD operations, data isolation
- **Mood Tracking Tests** (`test_mood_tracking.py`) - Core functionality
- **Analytics Tests** (`test_analytics.py`) - Streak calculations, patterns
- **API Tests** (`test_api.py`) - Endpoints, JSON responses, PDF export
- **Security Tests** (`test_security.py`) - Injection prevention, XSS protection

### Coverage Requirements
- **Minimum**: 80% code coverage
- **Target**: 90%+ coverage
- **Critical paths**: 100% coverage (auth, security)

## 🛠 Technical Stack

### Backend
- **Flask** - Web framework
- **PostgreSQL** - Production database
- **SQLite** - Local development database
- **Flask-Login** - Session management
- **Authlib** - OAuth 2.0 implementation

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript** - Interactive features
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

### Testing & CI/CD
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **Railway** - Deployment platform with CI/CD
- **Nixpacks** - Build system

### Security
- **OAuth 2.0** - Authentication
- **CSRF protection** - Form security
- **Parameterized queries** - SQL injection prevention
- **Input sanitization** - XSS prevention

## 📁 Project Structure
```
mood-tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── railway.json          # Railway deployment config
├── nixpacks.toml         # Build configuration with testing
├── templates/
│   ├── index.html        # Main dashboard
│   └── login.html        # OAuth login page
├── tests/                # Comprehensive test suite
│   ├── conftest.py       # Test fixtures
│   ├── test_auth.py      # Authentication tests
│   ├── test_database.py  # Database tests
│   ├── test_mood_tracking.py # Core functionality tests
│   ├── test_analytics.py # Analytics tests
│   ├── test_api.py       # API endpoint tests
│   └── test_security.py  # Security tests
├── .env.example          # Environment variables template
├── run_tests.sh          # Test runner script
├── TESTING.md            # Testing documentation
└── README.md             # This file
```

## 🔍 Debugging

### Health Check
Visit `/health` to check system status:
```json
{
  "status": "healthy",
  "database": "PostgreSQL 14.x",
  "mood_entries": 42,
  "using_postgres": true
}
```

### OAuth Debug (Development Only)
Visit `/debug/oauth` to verify OAuth configuration.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`./run_tests.sh`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Maintain 80%+ test coverage
- Follow security best practices
- Write tests for new features
- Update documentation

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Roadmap

### Completed ✅
- OAuth authentication (Google/GitHub)
- User-specific data isolation
- Advanced analytics dashboard
- Real-time system monitoring
- Comprehensive test suite (60+ tests)
- CI/CD pipeline with automated testing
- Modern responsive UI
- PDF export functionality

### Future Enhancements 🚀
- Mobile app (React Native)
- Data import/export (CSV/JSON)
- Mood triggers and tags
- Push notifications
- Advanced analytics (predictions)
- Multi-language support
- Dark mode theme
- Social features (optional sharing)

## 💡 Support

- **Issues**: [GitHub Issues](https://github.com/alsophocus/mood-tracker/issues)
- **Documentation**: This README and `TESTING.md`
- **Live Demo**: https://mood-tracker-production-6fa4.up.railway.app/

---

**Start tracking your mood today and discover patterns in your emotional well-being!** 🌟

Built with ❤️ using Flask, PostgreSQL, and modern web technologies.
