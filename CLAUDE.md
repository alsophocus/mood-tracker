# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based mood tracking web application with OAuth authentication, PostgreSQL backend, and advanced analytics. The application follows **SOLID principles** with a clean layered architecture emphasizing maintainability, testability, and extensibility.

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run with custom port
PORT=5000 python app.py

# Run via shell script
./run.sh
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analytics.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_analytics.py::test_mood_values
```

### Database Operations
The application automatically initializes the database schema on startup. Manual initialization is not required, but you can force re-initialization by:
- Deleting the database and restarting the app
- Using the `/fix-schema` endpoint (requires authentication)

## Architecture

### Layered SOLID Architecture

The codebase follows strict SOLID principles with dependency injection:

```
┌─────────────────────────────────────────────────────┐
│         Routes (routes.py, auth.py)                 │  ← HTTP layer
│         Controllers handle HTTP concerns            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         Services (services.py)                      │  ← Business logic
│         MoodService, UserService, TimezoneService   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│    Repositories (database.py, database_new.py)      │  ← Data access
│    MoodRepository, UserRepository                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│    Database (PostgreSQL via psycopg3)               │  ← Persistence
└─────────────────────────────────────────────────────┘
```

### Key Architecture Patterns

**Dependency Injection Container (`container.py`)**
- Central registry for all services and repositories
- Implements the Service Locator pattern
- Usage: `from container import container; mood_service = container.get_mood_service()`

**Interface Segregation (`interfaces.py`)**
- Separates read and write operations: `MoodReader`, `MoodWriter`, `UserReader`, `UserWriter`
- Clients depend only on methods they use
- Example: Analytics only needs `MoodReader`, not write operations

**Domain Models (`models.py`)**
- `MoodEntry`: Core mood data with validation
- `User`: User authentication data
- `MoodType`: Enum for the 7-level mood scale (Very Bad → Very Well)
- All models have `to_dict()` for serialization

**Two Database Implementations**
- `database.py`: Legacy implementation, still used in `routes.py`
- `database_new.py`: New SOLID-compliant implementation with proper interfaces
- **Migration Note**: The codebase is transitioning from `database.py` to `database_new.py`. When working with routes, you may need to use the legacy `db` instance. For new features, use the container-based services.

### Critical Timezone Handling

**Chile Timezone (UTC-3)**
The application is designed for Chilean users and handles timezone conversions throughout:
- `ChileTimezoneService` in `services.py` manages all timezone operations
- Dates are stored as Chilean dates, not UTC dates
- Timestamps are converted when displaying to users
- **Important**: Always use `timezone_service.get_chile_date()` for current date operations

### Analytics System (`analytics.py`)

The analytics module is a comprehensive system with multiple specialized services:

**Core Classes**
- `MoodAnalytics`: Main analytics engine with pattern detection
- `TrendAnalysisService`: Linear regression and trend calculations
- `FourWeekComparisonService`: Multi-week comparative analysis

**Key Methods**
- `get_weekly_patterns()`: Returns mood averages by day of week
- `get_daily_patterns()`: Returns hourly mood patterns
- `get_monthly_trends()`: Returns monthly aggregated data
- `get_summary()`: Returns streak, best day, averages

**Data Flow**
1. Routes call analytics methods with mood data
2. Analytics calculates patterns using `MOOD_VALUES` mapping (1-7 scale)
3. Results returned as JSON-serializable dictionaries
4. Frontend (Chart.js) renders visualizations

### PDF Export System

**Current Implementation** (✅ Updated October 2025):
- `pdf_export.py`: Comprehensive Material Design 3 PDF exporter (810 lines)
- **Status**: Production-ready with complete MD3 implementation

**PDF Generation Flow**
1. Route handler collects user moods: `moods = db.get_user_moods(current_user.id)`
2. Create exporter instance: `exporter = PDFExporter(current_user, moods)`
3. Generate PDF buffer: `buffer = exporter.generate_report()`
4. Return via Flask: `send_file(buffer, as_attachment=True, ...)`

**Complete MD3 Color System**
- 25+ MD3-compliant color tokens
- Primary, Secondary, Tertiary palettes with containers
- Surface elevation system (6 surface variants)
- Semantic colors (success, warning, error, info)
- Mood-specific colors (7 distinct mood colors)

**MD3 Typography Scale**
- Display Large (36pt) - Main titles
- Headline Large (24pt) - Section headers
- Title Large (18pt) - Subsection headers
- Body Large/Medium/Small (14pt/12pt/10pt)
- Label Large (13pt) - Emphasis text

**4-Page Report Structure**
1. **Page 1**: Cover + Executive Summary + Key Metrics (2x2 grid)
   - Intelligent insights based on mood data
   - KPI cards: Total Entries, Current Streak, Best Day, Average Mood
2. **Page 2**: Mood Distribution (Donut Chart) + Weekly Patterns (Line Chart)
   - Last 30 days mood distribution with percentages
   - Weekly patterns with best/worst day highlighting
3. **Page 3**: Monthly Trends (with Linear Regression) + Daily Patterns (Bar Chart)
   - 12-month trend analysis with regression overlay
   - Trend statistics (slope, correlation)
   - 24-hour mood patterns with color-coded bars
4. **Page 4**: Recent History Table + Methodology + Footer
   - Last 12 mood entries with emoji indicators
   - Professional footer with generation timestamp

**Chart Types**
- **Donut Chart**: Mood distribution (300 DPI, MD3 colors)
- **Line Chart**: Weekly patterns with filled areas and markers
- **Line Chart with Regression**: Monthly trends with forecast overlay
- **Bar Chart**: Hourly daily patterns with peak highlighting

**Advanced Analytics Integration**
- Linear regression analysis via `TrendAnalysisService`
- Trend direction detection (improving/stable/declining)
- Statistical overlays (slope, correlation coefficients)
- Intelligent insights generation based on data patterns

**Technical Features**
- Matplotlib charts at 300 DPI quality
- Automatic temporary file cleanup
- Graceful error handling for missing data
- Supports multiple date formats (string, datetime, date objects)
- MD3-compliant surface backgrounds and styling

**Endpoints**
- `/export_pdf` - Primary endpoint for PDF generation
- `/api/pdf-simple` - Alternative endpoint with JSON error handling
- Both endpoints use the same `PDFExporter` class

### OAuth Authentication Flow

**Supported Providers**: Google, GitHub

**Authentication Flow**
1. User clicks login → redirects to `/auth/<provider>`
2. OAuth provider authenticates → redirects to `/callback/<provider>`
3. Callback handler validates OAuth token
4. User created/retrieved from database
5. Flask-Login session established
6. Redirect to main dashboard

**User Management**
- Users identified by email (unique)
- No password storage (OAuth only)
- User data completely isolated (user_id foreign key)

## Frontend Architecture

### Material Design 3 Implementation

The frontend has been fully migrated to Material Design 3:
- **Icons**: Uses Material Symbols (no Font Awesome)
- **Color System**: MD3 color tokens throughout
- **Components**: Cards, buttons, navigation following MD3 patterns
- **Typography**: MD3 type scale

**Key Templates**
- `index.html`: Main dashboard with mood entry and analytics
- `insights_dashboard.html`: Advanced analytics visualizations
- `analytics_dashboard.html`: Detailed mood analytics
- `goals_dashboard.html`: Goal tracking features
- `login.html`, `logout.html`: Authentication flows

### JavaScript Architecture

**Chart Configuration**
- Chart.js for interactive charts
- D3.js for calendar heatmaps
- Modular approach: `static/js/chart-factory.js`, `chart-renderer.js`, `chart-interfaces.js`

**API Integration**
- Weekly patterns: `GET /weekly_patterns?start_date=YYYY-MM-DD`
- Daily patterns: `GET /daily_patterns?date=YYYY-MM-DD`
- Monthly trends: `GET /monthly_trends?year=YYYY`
- Quick stats: `GET /api/analytics/quick-stats`

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    provider TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Moods Table
```sql
CREATE TABLE moods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    mood TEXT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggers TEXT
);
```

**Important Notes**
- No unique constraint on `(user_id, date)` - multiple moods per day allowed
- `timestamp` stores exact entry time for hourly analytics
- `mood` values: 'very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well'

## Environment Variables

Required variables (set in `.env` for local, Railway dashboard for production):
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id (optional)
GITHUB_CLIENT_SECRET=your_github_client_secret (optional)
SECRET_KEY=your_random_secret_key
```

## Deployment (Railway)

**Start Command**: `python app.py` (configured in `railway.json`)

**Health Endpoints**
- `/health`: Database connectivity check
- `/analytics-health`: User data access verification
- Expected responses: 200 (healthy), 500 (error), 302 (redirect if auth required)

**Database Setup**
- Railway automatically provisions PostgreSQL
- Database schema auto-initializes on first run
- Internal network connection (`*.railway.internal`)

## Common Patterns & Conventions

### Adding a New Analytics Endpoint

1. **Add method to `MoodAnalytics` class** (analytics.py)
   ```python
   def get_new_pattern(self, param):
       # Calculate pattern
       return {'labels': [...], 'data': [...]}
   ```

2. **Add route handler** (routes.py)
   ```python
   @main_bp.route('/api/analytics/new-pattern')
   @login_required
   def get_new_pattern():
       moods = db.get_user_moods(current_user.id)
       analytics = MoodAnalytics(moods)
       return jsonify(analytics.get_new_pattern(param))
   ```

3. **Add frontend fetch** (JavaScript)
   ```javascript
   fetch('/api/analytics/new-pattern')
       .then(res => res.json())
       .then(data => renderChart(data));
   ```

### Adding a New Service (SOLID Way)

1. Define interface in `interfaces.py`
2. Implement service in `services.py`
3. Register in `container.py`
4. Inject via constructor in routes/controllers

### PDF Export Modifications

When modifying PDF exports:
- Test with small datasets first (chart generation can fail with no data)
- Always use `tempfile.NamedTemporaryFile(delete=False)` for chart images
- Clean up temp files in the `generate_report()` method after PDF generation
- Material Design 3 colors defined as `HexColor()` objects from `MD3_COLORS` dictionary
- Use `KeepTogether()` for elements that shouldn't break across pages
- All chart methods should return `None` on failure (graceful degradation)
- Use `try/except` blocks in all chart generation methods
- Set matplotlib backend to 'Agg' at import time: `matplotlib.use('Agg')`
- Charts should be 300 DPI for publication quality
- Use MD3 surface colors for chart backgrounds (`MD3_COLORS['surface']`)

**Chart Best Practices**:
- Donut charts: Use `wedgeprops=dict(width=0.4)` for proper donut hole
- Line charts: Add `markeredgecolor='white'` for better visibility
- Bar charts: Use semantic colors (green/orange/red) based on mood values
- All charts: Include proper titles, labels, and legends with MD3 colors

**Adding New Charts**:
1. Create chart method: `def _create_<name>_chart(self)`
2. Wrap in try/except block
3. Save to temp file with `tempfile.NamedTemporaryFile(delete=False, suffix='.png')`
4. Append temp file path to `self.temp_files` for cleanup
5. Return temp file path or `None` on failure
6. Add chart to appropriate page in `generate_report()`

## Testing Strategy

The test suite covers:
- **Database operations** (`test_database.py`)
- **Analytics calculations** (`test_analytics.py`)
- **Authentication flows** (`test_auth.py`)
- **API endpoints** (`test_api.py`, `test_routes.py`)
- **Security** (`test_security.py`)
- **Mood tracking** (`test_mood_tracking.py`)

**Test Configuration**: `tests/conftest.py` sets up fixtures and test database

## Known Issues & Gotchas

1. **Two Database Systems**: Legacy `database.py` vs new `database_new.py` - be consistent within a feature
2. **Timezone Confusion**: Always use `ChileTimezoneService` for dates, never `datetime.now().date()`
3. **PDF Chart Generation**: Can fail if matplotlib backend not set to 'Agg' - already configured in exporters
4. **Multiple Moods Per Day**: Recent change removed unique constraint - analytics must handle multiple entries
5. **Material Symbols Only**: No Font Awesome icons - use Material Symbols syntax: `<span class="material-symbols-outlined">mood</span>`

## Code Quality Requirements

From README.md documentation standards:
- All functions/classes must have detailed docstrings with type hints
- Complex logic requires inline comments explaining WHY
- SOLID principles enforced in all new code
- Dependency injection for testability
- Single responsibility per class/function

## File Organization

**Core Application Files**
- `app.py`: Application factory and initialization
- `config.py`: Environment configuration
- `auth.py`: OAuth authentication handlers
- `routes.py`: Main application routes (uses legacy database)
- `routes_new.py`: New SOLID-compliant routes (not yet in use)

**Data Layer**
- `interfaces.py`: Abstract interfaces
- `models.py`: Domain models
- `database.py`: Legacy database implementation
- `database_new.py`: SOLID database implementation
- `services.py`: Business logic services
- `container.py`: Dependency injection

**Analytics & Export**
- `analytics.py`: Analytics engine with `MoodAnalytics`, `TrendAnalysisService`
- `pdf_export.py`: Comprehensive Material Design 3 PDF exporter (810 lines, production-ready)

**Frontend**
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JavaScript, assets
