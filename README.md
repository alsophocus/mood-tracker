# Mood Tracker

A secure, modern web application to track your daily mood with advanced analytics, OAuth authentication, and beautiful insights.

## Features

### Secure Authentication
- **OAuth Login** with Google & GitHub
- **User-specific data** - complete privacy and isolation
- **Session management** with Flask-Login
- **No passwords stored** - OAuth only

### Core Mood Tracking
- **7 Mood Levels**: Very Bad, Bad, Slightly Bad, Neutral, Slightly Well, Well, Very Well
- **Daily logging** with optional notes
- **Same-day updates** - modify your mood throughout the day
- **Rich text notes** with emoji support

### Advanced Analytics
- **Current Streak**: Track consecutive good days (mood 5+)
- **Weekly Patterns**: Interactive line chart showing mood trends by day of week
- **Daily Patterns**: Analyze mood trends by time of day with hourly breakdown
- **Monthly Trends**: Interactive charts showing mood over time
- **Real-time Monitoring**: Live database and analytics status indicators

### PDF Export
- **Comprehensive Reports**: Complete analytics with embedded charts
- **Professional Design**: Beautiful layout with charts and statistics
- **All Data Included**: Summary, patterns, trends, and recent history
- **Visual Charts**: Weekly and monthly trend charts embedded in PDF

## PostgreSQL Setup (Railway)

### Quick Setup
1. **Create PostgreSQL Service**: Railway Dashboard → New Service → Database → PostgreSQL
2. **Get Connection String**: From PostgreSQL service → Variables tab
3. **Set Environment Variable**: 
   ```
   DATABASE_URL=postgresql://postgres:PASSWORD@postgres-XXXX.railway.internal:5432/railway
   ```

### Technical Details
- **Library**: `psycopg[binary]==3.2.10` (Python 3.14 compatible)
- **Connection**: Internal Railway network (`postgres-XXXX.railway.internal`)
- **Security**: No public access, internal network only
- **Rollback**: Use tag `v1.0-stable` if issues occur

### Troubleshooting
- **"Servname not supported"**: Check DATABASE_URL hostname
- **"Application Failed to Respond"**: Database blocking startup
- **Debug endpoints**: `/status`, `/test-db`, `/debug-oauth`, `/health`

## Technology Stack

### Backend
- **Flask 2.3.3**: Web framework
- **PostgreSQL**: Primary database with psycopg3 driver
- **SQLite**: Development/fallback database
- **OAuth 2.0**: Google and GitHub authentication
- **ReportLab**: PDF generation with embedded charts
- **Matplotlib**: Chart generation for PDF export

### Frontend
- **Modern CSS**: Dark theme with utilitarian design
- **Chart.js**: Interactive analytics charts
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Live status monitoring

### Infrastructure
- **Railway**: Cloud deployment platform
- **PostgreSQL**: Managed database service
- **Environment Variables**: Secure configuration management
- **Git**: Version control with tagged releases

## Installation

### Local Development
1. **Clone Repository**:
   ```bash
   git clone https://github.com/alsophocus/mood-tracker.git
   cd mood-tracker
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth credentials
   ```

5. **Run Application**:
   ```bash
   python app.py
   ```

### Railway Deployment
1. **Connect GitHub Repository** to Railway
2. **Add PostgreSQL Service** to your Railway project
3. **Set Environment Variables**:
   - `DATABASE_URL`: From PostgreSQL service
   - `GOOGLE_CLIENT_ID`: From Google Cloud Console
   - `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
   - `GITHUB_CLIENT_ID`: From GitHub OAuth App
   - `GITHUB_CLIENT_SECRET`: From GitHub OAuth App
   - `SECRET_KEY`: Random secret key for sessions

## OAuth Setup

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `https://your-app.railway.app/callback/google`

### GitHub OAuth
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL: `https://your-app.railway.app/callback/github`
4. Copy Client ID and Client Secret

## API Endpoints

### Authentication
- `GET /login` - Login page
- `GET /auth/<provider>` - OAuth redirect
- `GET /callback/<provider>` - OAuth callback
- `GET /logout` - Logout user

### Mood Tracking
- `POST /save_mood` - Save mood entry
- `GET /` - Main dashboard (requires login)

### Analytics
- `GET /mood_data` - Monthly trend data
- `GET /weekly_patterns` - Weekly pattern data
- `GET /daily_patterns` - Daily pattern data
- `GET /analytics-health` - Analytics system health

### Export
- `GET /export_pdf` - Generate PDF report

### System
- `GET /status` - Basic app status
- `GET /health` - Database health check
- `GET /debug-oauth` - OAuth configuration debug

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    provider TEXT
);
```

### Moods Table
```sql
CREATE TABLE moods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE,
    mood TEXT,
    notes TEXT,
    UNIQUE(user_id, date)
);
```

## Version History

- **v1.0-stable**: Basic PostgreSQL integration
- **v1.0.1**: Daily Patterns + Real-time monitoring
- **v1.0.3**: Enhanced UI + Fixed monitoring
- **Current**: 7-level mood system with comprehensive analytics

## Security Features

- **OAuth-only Authentication**: No password storage
- **User Data Isolation**: Complete privacy between users
- **Internal Database Access**: No public database exposure
- **Session Management**: Secure Flask-Login sessions
- **Environment Variables**: Sensitive data protection

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
