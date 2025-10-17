# Mood Tracker with OAuth Authentication - Production Ready
# Last updated: 2025-10-17 11:07 UTC
# Environment validation
import os
print("=== Environment Variables Check ===")
print(f"GOOGLE_CLIENT_ID: {'SET' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT SET'}")
print(f"GOOGLE_CLIENT_SECRET: {'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT SET'}")
print(f"GITHUB_CLIENT_ID: {'SET' if os.environ.get('GITHUB_CLIENT_ID') else 'NOT SET'}")
print(f"GITHUB_CLIENT_SECRET: {'SET' if os.environ.get('GITHUB_CLIENT_SECRET') else 'NOT SET'}")
print("=====================================")

from flask import Flask, render_template, request, redirect, send_file, jsonify, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from collections import defaultdict
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import PostgreSQL support (psycopg3)
try:
    import psycopg
    from psycopg.rows import dict_row
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Add timezone conversion filter
@app.template_filter('utc_to_local')
def utc_to_local(utc_dt):
    if not utc_dt:
        return None
    from datetime import timedelta
    # Convert UTC to UTC-3
    return utc_dt - timedelta(hours=3)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@postgres-thp7.railway.internal:5432/railway')
ACTUAL_USE_POSTGRES = False  # Will be set in init_db

# OAuth configuration
oauth = OAuth(app)

# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post'
    },
)

# GitHub OAuth  
github = oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, name, provider):
        self.id = id
        self.email = email
        self.name = name
        self.provider = provider

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    else:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        if ACTUAL_USE_POSTGRES:
            return User(user_data['id'], user_data['email'], user_data['name'], user_data['provider'])
        else:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

# Database initialization flag
DB_INITIALIZED = False

def ensure_db_initialized():
    global DB_INITIALIZED
    if not DB_INITIALIZED:
        try:
            init_db()
            DB_INITIALIZED = True
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
            # Initialize SQLite as fallback
            if not ACTUAL_USE_POSTGRES:
                conn = sqlite3.connect('mood.db')
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, mood TEXT, notes TEXT,
                                  FOREIGN KEY (user_id) REFERENCES users (id),
                                  UNIQUE(user_id, date))''')
                conn.commit()
                conn.close()
                DB_INITIALIZED = True
                print("✅ SQLite fallback initialized")
            else:
                raise

def get_db_connection():
    if not ACTUAL_USE_POSTGRES:
        raise Exception("PostgreSQL not initialized - check DATABASE_URL")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def migrate_old_moods():
    """Migrate old 5-level mood system to new 7-level system"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mapping from old to new mood system
        mood_migration = {
            'super sad': 'very bad',
            'sad': 'bad', 
            'neutral': 'neutral',
            'good': 'well',
            'super good': 'very well'
        }
        
        for old_mood, new_mood in mood_migration.items():
            if ACTUAL_USE_POSTGRES:
                cursor.execute('UPDATE moods SET mood = %s WHERE mood = %s', (new_mood, old_mood))
            else:
                cursor.execute('UPDATE moods SET mood = ? WHERE mood = ?', (new_mood, old_mood))
        
        conn.commit()
        conn.close()
        print("✅ Mood data migration completed")
        
    except Exception as e:
        print(f"⚠️ Mood migration failed: {e}")

def init_db():
    global ACTUAL_USE_POSTGRES
    
    # Force PostgreSQL usage - no fallback
    if DATABASE_URL and POSTGRES_AVAILABLE:
        ACTUAL_USE_POSTGRES = True
        print("🔧 FORCING PostgreSQL usage with psycopg3")
        
        # Test PostgreSQL connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # PostgreSQL schema
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id SERIAL PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                         (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), 
                          date DATE, mood TEXT, notes TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          UNIQUE(user_id, date))''')
        
        # Add timestamp column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE moods ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            conn.commit()
            print("✅ Added timestamp column to moods table")
        except Exception:
            pass  # Column already exists
        conn.commit()
        conn.close()
        print("✅ PostgreSQL connection successful with psycopg3")
        
        # Migrate old mood data
        migrate_old_moods()
        return
    else:
        raise Exception("PostgreSQL required but DATABASE_URL not set or psycopg not available")
    
    try:
        if ACTUAL_USE_POSTGRES:
            # PostgreSQL schema
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                             (id SERIAL PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                             (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), 
                              date DATE, mood TEXT, notes TEXT,
                              UNIQUE(user_id, date))''')
        else:
            # SQLite schema
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                             (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                             (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, mood TEXT, notes TEXT,
                              FOREIGN KEY (user_id) REFERENCES users (id),
                              UNIQUE(user_id, date))''')
        
        conn.commit()
        print("Database initialized")
        
    except Exception as e:
        print(f"Database init error: {e}")
        conn.rollback()
    finally:
        conn.close()

@app.route('/debug-oauth')
def debug_oauth():
    try:
        ensure_db_initialized()
        return {
            'status': 'success',
            'db_initialized': DB_INITIALIZED,
            'postgres_enabled': ACTUAL_USE_POSTGRES,
            'oauth_vars': {
                'google_client_id': os.environ.get('GOOGLE_CLIENT_ID') is not None,
                'google_client_secret': os.environ.get('GOOGLE_CLIENT_SECRET') is not None,
                'github_client_id': os.environ.get('GITHUB_CLIENT_ID') is not None,
                'github_client_secret': os.environ.get('GITHUB_CLIENT_SECRET') is not None
            }
        }
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, 500

@app.route('/test-db')
def test_db():
    try:
        # Focus on internal connection only
        internal_url = "postgresql://postgres:OsFZqHiUQXvawJnFgrWowJctGiWdyznH@postgres-thp7.railway.internal:5432/railway"
        
        print(f"🔍 Testing internal connection: {internal_url}")
        conn = psycopg.connect(internal_url, row_factory=dict_row)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        conn.close()
        
        return {
            'status': 'success',
            'method': 'internal',
            'database': 'postgresql',
            'version': str(version['version']) if version else 'unknown'
        }
        
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }, 500

@app.route('/debug-env')
def debug_env():
    return {
        'DATABASE_URL_set': DATABASE_URL is not None,
        'DATABASE_URL_length': len(DATABASE_URL) if DATABASE_URL else 0,
        'POSTGRES_AVAILABLE': POSTGRES_AVAILABLE,
        'PORT': os.environ.get('PORT', 'not_set'),
        'env_vars': list(os.environ.keys())
    }

@app.route('/debug-postgres')
def debug_postgres():
    return {
        'DATABASE_URL': DATABASE_URL[:50] + "..." if DATABASE_URL and len(DATABASE_URL) > 50 else DATABASE_URL,
        'DATABASE_URL_set': DATABASE_URL is not None,
        'DATABASE_URL_length': len(DATABASE_URL) if DATABASE_URL else 0,
        'POSTGRES_AVAILABLE': POSTGRES_AVAILABLE,
        'ACTUAL_USE_POSTGRES': ACTUAL_USE_POSTGRES,
        'DB_INITIALIZED': DB_INITIALIZED,
        'psycopg_import_test': 'success' if POSTGRES_AVAILABLE else 'failed'
    }

@app.route('/debug-error')
def debug_error():
    try:
        # Test basic functionality
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if ACTUAL_USE_POSTGRES:
            cursor.execute('SELECT COUNT(*) FROM users;')
            user_count = cursor.fetchone()['count']
        else:
            cursor.execute('SELECT COUNT(*) FROM users;')
            user_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'status': 'success',
            'user_count': user_count,
            'postgres_enabled': ACTUAL_USE_POSTGRES,
            'database_url_set': DATABASE_URL is not None
        }
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'postgres_enabled': ACTUAL_USE_POSTGRES,
            'database_url_set': DATABASE_URL is not None
        }, 500

@app.route('/status')
def status():
    return {'status': 'app_running', 'postgres': POSTGRES_AVAILABLE}

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/<provider>')
def oauth_login(provider):
    try:
        if provider == 'google':
            if not os.environ.get('GOOGLE_CLIENT_ID') or not os.environ.get('GOOGLE_CLIENT_SECRET'):
                flash('Google OAuth not configured')
                return redirect(url_for('login'))
            
            # Manual Google OAuth - bypass Authlib
            import urllib.parse
            redirect_uri = url_for('oauth_callback', provider='google', _external=True, _scheme='https')
            
            params = {
                'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                'redirect_uri': redirect_uri,
                'scope': 'openid email profile',
                'response_type': 'code',
                'access_type': 'offline'
            }
            
            auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
            return redirect(auth_url)
            
        elif provider == 'github':
            if not os.environ.get('GITHUB_CLIENT_ID') or not os.environ.get('GITHUB_CLIENT_SECRET'):
                flash('GitHub OAuth not configured')
                return redirect(url_for('login'))
            
            # Manual GitHub OAuth - bypass Authlib
            import urllib.parse
            redirect_uri = url_for('oauth_callback', provider='github', _external=True, _scheme='https')
            
            params = {
                'client_id': os.environ.get('GITHUB_CLIENT_ID'),
                'redirect_uri': redirect_uri,
                'scope': 'user:email',
                'response_type': 'code'
            }
            
            auth_url = 'https://github.com/login/oauth/authorize?' + urllib.parse.urlencode(params)
            return redirect(auth_url)
        else:
            flash('Invalid OAuth provider')
            return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f'OAuth login error for {provider}: {str(e)}')
        flash(f'OAuth configuration error: {str(e)}')
        return redirect(url_for('login'))

@app.route('/callback/<provider>')
def oauth_callback(provider):
    ensure_db_initialized()  # Initialize database before user operations
    try:
        if provider == 'google':
            # Manual Google OAuth callback - bypass Authlib
            try:
                code = request.args.get('code')
                if not code:
                    flash('No authorization code received from Google')
                    return redirect(url_for('login'))
                
                # Exchange code for access token
                import requests
                redirect_uri = url_for('oauth_callback', provider='google', _external=True, _scheme='https')
                
                token_data = {
                    'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                    'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                }
                
                token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
                
                if token_response.status_code != 200:
                    flash('Failed to exchange code for access token')
                    return redirect(url_for('login'))
                
                token_json = token_response.json()
                access_token = token_json.get('access_token')
                
                if not access_token:
                    flash('No access token received from Google')
                    return redirect(url_for('login'))
                
                # Get user info
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
                
                if user_response.status_code != 200:
                    flash('Failed to get user information from Google')
                    return redirect(url_for('login'))
                
                user_info = user_response.json()
                email = user_info.get('email')
                name = user_info.get('name')
                
            except Exception as e:
                app.logger.error(f'Manual Google OAuth error: {str(e)}')
                flash(f'Google authentication failed: {str(e)}')
                return redirect(url_for('login'))
            
        elif provider == 'github':
            # Manual GitHub OAuth callback
            try:
                code = request.args.get('code')
                if not code:
                    flash('No authorization code received from GitHub')
                    return redirect(url_for('login'))
                
                # Exchange code for access token
                import requests
                redirect_uri = url_for('oauth_callback', provider='github', _external=True, _scheme='https')
                
                token_data = {
                    'client_id': os.environ.get('GITHUB_CLIENT_ID'),
                    'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
                    'code': code,
                    'redirect_uri': redirect_uri
                }
                
                headers = {'Accept': 'application/json'}
                token_response = requests.post('https://github.com/login/oauth/access_token', 
                                             data=token_data, headers=headers)
                
                if token_response.status_code != 200:
                    flash('Failed to exchange code for access token')
                    return redirect(url_for('login'))
                
                token_json = token_response.json()
                access_token = token_json.get('access_token')
                
                if not access_token:
                    flash('No access token received from GitHub')
                    return redirect(url_for('login'))
                
                # Get user info
                headers = {'Authorization': f'token {access_token}'}
                user_response = requests.get('https://api.github.com/user', headers=headers)
                
                if user_response.status_code != 200:
                    flash('Failed to get user information from GitHub')
                    return redirect(url_for('login'))
                
                user_info = user_response.json()
                email = user_info.get('email')
                name = user_info.get('name') or user_info.get('login')
                
                # If email is private, get it from emails endpoint
                if not email:
                    emails_response = requests.get('https://api.github.com/user/emails', headers=headers)
                    if emails_response.status_code == 200:
                        emails = emails_response.json()
                        primary_email = next((e['email'] for e in emails if e['primary']), None)
                        email = primary_email
                
                if not email:
                    flash('Could not get email from GitHub')
                    return redirect(url_for('login'))
                
            except Exception as e:
                app.logger.error(f'Manual GitHub OAuth error: {str(e)}')
                flash(f'GitHub authentication failed: {str(e)}')
                return redirect(url_for('login'))
        
        else:
            flash('Invalid OAuth provider')
            return redirect(url_for('login'))
        
        if not email:
            flash(f'Could not get email from {provider}')
            return redirect(url_for('login'))
        
        # Create or get user
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if ACTUAL_USE_POSTGRES:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            else:
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                if ACTUAL_USE_POSTGRES:
                    user = User(user_data['id'], user_data['email'], user_data['name'], user_data['provider'])
                else:
                    user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            else:
                # Create new user
                if ACTUAL_USE_POSTGRES:
                    cursor.execute('INSERT INTO users (email, name, provider) VALUES (%s, %s, %s) RETURNING id',
                                  (email, name, provider))
                    user_id = cursor.fetchone()['id']
                else:
                    cursor.execute('INSERT INTO users (email, name, provider) VALUES (?, ?, ?)',
                                  (email, name, provider))
                    user_id = cursor.lastrowid
                
                conn.commit()
                user = User(user_id, email, name, provider)
            
            conn.close()
            login_user(user)
            flash(f'Successfully logged in with {provider.title()}!')
            return redirect(url_for('index'))
            
        except Exception as db_error:
            conn.close()
            app.logger.error(f'Database error during {provider} login: {str(db_error)}')
            flash(f'Database error: {str(db_error)}')
            return redirect(url_for('login'))
        
    except Exception as e:
        app.logger.error(f'OAuth callback error for {provider}: {str(e)}')
        flash(f'Authentication failed: {str(e)}')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, mood, notes, timestamp FROM moods WHERE user_id = %s ORDER BY date DESC LIMIT 5', 
                  (current_user.id,))
    
    recent_moods = cursor.fetchall()
    
    # Get all moods for analytics
    cursor.execute('SELECT date, mood, notes FROM moods WHERE user_id = %s ORDER BY date DESC', 
                  (current_user.id,))
    
    all_moods = cursor.fetchall()
    
    # Calculate analytics
    analytics = calculate_analytics(all_moods)
    
    conn.close()
    return render_template('index.html', moods=recent_moods, analytics=analytics, user=current_user)

@app.route('/save_mood', methods=['POST'])
@login_required
def save_mood():
    mood = request.form['mood']
    notes = request.form.get('notes', '')
    date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('''INSERT INTO moods (user_id, date, mood, notes) VALUES (%s, %s, %s, %s)
                         ON CONFLICT (user_id, date) DO UPDATE SET mood = %s, notes = %s''',
                      (current_user.id, date, mood, notes, mood, notes))
    else:
        cursor.execute('INSERT OR REPLACE INTO moods (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                      (current_user.id, date, mood, notes))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

def calculate_analytics(moods):
    if not moods:
        return {
            'daily_average': 0, 
            'good_days_average': 0,
            'bad_days_average': 0,
            'total_entries': 0,
            'weekly_patterns': {}
        }
    
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    
    # Group moods by date and calculate daily averages
    daily_moods = defaultdict(list)
    for row in moods:
        date = row['date']
        mood_value = mood_values[row['mood']]
        daily_moods[date].append(mood_value)
    
    # Calculate daily averages
    daily_averages = []
    good_days = []  # Days with average >= 5
    bad_days = []   # Days with average <= 3
    
    for date, mood_list in daily_moods.items():
        daily_avg = sum(mood_list) / len(mood_list)
        daily_averages.append(daily_avg)
        
        if daily_avg >= 5:
            good_days.append(daily_avg)
        elif daily_avg <= 3:
            bad_days.append(daily_avg)
    
    # Calculate overall averages
    daily_average = round(sum(daily_averages) / len(daily_averages), 2) if daily_averages else 0
    good_days_average = round(sum(good_days) / len(good_days), 2) if good_days else 0
    bad_days_average = round(sum(bad_days) / len(bad_days), 2) if bad_days else 0
    
    # Weekly patterns
    weekly_patterns = defaultdict(list)
    for row in moods:
        date_str = str(row['date']) if ACTUAL_USE_POSTGRES else row[0]
        mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
        day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
        weekly_patterns[day_of_week].append(mood_values[mood])
    
    # Calculate average mood per day
    weekly_avg = {}
    for day, mood_list in weekly_patterns.items():
        weekly_avg[day] = round(sum(mood_list) / len(mood_list), 1)
    
    return {
        'daily_average': daily_average,
        'good_days_average': good_days_average,
        'bad_days_average': bad_days_average,
        'total_entries': len(daily_averages),
        'weekly_patterns': weekly_avg
    }

@app.route('/mood_data')
@login_required
def mood_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('SELECT date, mood FROM moods WHERE user_id = %s ORDER BY date', 
                      (current_user.id,))
    else:
        cursor.execute('SELECT date, mood FROM moods WHERE user_id = ? ORDER BY date', 
                      (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    monthly_data = defaultdict(list)
    
    for row in moods:
        date_str = str(row['date']) if ACTUAL_USE_POSTGRES else row[0]
        mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
        month = date_str[:7]  # YYYY-MM format
        monthly_data[month].append(mood_values[mood])
    
    # Calculate average mood per month
    chart_data = []
    for month in sorted(monthly_data.keys()):
        avg_mood = sum(monthly_data[month]) / len(monthly_data[month])
        chart_data.append({'month': month, 'mood': round(avg_mood, 1)})
    
    return jsonify(chart_data)

@app.route('/weekly_patterns')
@login_required
def weekly_patterns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, mood FROM moods WHERE user_id = %s ORDER BY date', 
                  (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    # Group by day of week with numerical values
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    weekly_patterns = defaultdict(list)
    
    for row in moods:
        date_str = str(row['date'])
        mood = row['mood']
        day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
        weekly_patterns[day_of_week].append(mood_values[mood])
    
    # Calculate numerical average for each day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_averages = []
    
    for day in days:
        if day in weekly_patterns:
            avg = sum(weekly_patterns[day]) / len(weekly_patterns[day])
            weekly_averages.append(round(avg, 2))
        else:
            weekly_averages.append(4)  # Default neutral (4, not 4.0)
    
    return jsonify({
        'labels': days,
        'data': weekly_averages
    })

@app.route('/daily_patterns')
@login_required
def daily_patterns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT timestamp, mood FROM moods WHERE user_id = %s AND timestamp IS NOT NULL ORDER BY timestamp', 
                  (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    # Convert each mood entry to hourly data points
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    hourly_data = []
    
    for row in moods:
        timestamp = row['timestamp']
        mood = row['mood']
        
        if timestamp:
            from datetime import datetime, timedelta
            
            # Convert to UTC-3 timezone
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Convert to UTC-3 (subtract 3 hours from UTC)
            utc_minus_3 = timestamp - timedelta(hours=3)
            hour = utc_minus_3.hour
            
            hourly_data.append({
                'hour': hour,
                'mood_value': mood_values[mood]
            })
    
    return jsonify({
        'hourly_data': hourly_data
    })

@app.route('/weekly_trends')
@login_required
def weekly_trends():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, mood FROM moods WHERE user_id = %s ORDER BY date', 
                  (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    
    # Group by week
    from datetime import datetime
    weekly_moods = defaultdict(list)
    
    for row in moods:
        date = datetime.strptime(str(row['date']), '%Y-%m-%d')
        # Get year, week number
        year_week = f"{date.year}-W{date.isocalendar()[1]:02d}"
        weekly_moods[year_week].append(mood_values[row['mood']])
    
    # Calculate weekly averages
    labels = []
    data = []
    
    for week in sorted(weekly_moods.keys()):
        mood_list = weekly_moods[week]
        weekly_average = sum(mood_list) / len(mood_list)
        labels.append(week)
        data.append(round(weekly_average, 2))
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/monthly_trends')
@login_required
def monthly_trends():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, mood FROM moods WHERE user_id = %s ORDER BY date', 
                  (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    
    # Group by month
    from datetime import datetime
    monthly_moods = defaultdict(list)
    
    for row in moods:
        date = datetime.strptime(str(row['date']), '%Y-%m-%d')
        year_month = f"{date.year}-{date.month:02d}"
        monthly_moods[year_month].append(mood_values[row['mood']])
    
    # Calculate monthly averages
    labels = []
    data = []
    
    for month in sorted(monthly_moods.keys()):
        mood_list = monthly_moods[month]
        monthly_average = sum(mood_list) / len(mood_list)
        labels.append(month)
        data.append(round(monthly_average, 2))
    
    return jsonify({
        'labels': labels,
        'data': data
    })
@login_required
def export_pdf():
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import tempfile
    import os
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.units import inch
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('SELECT date, mood, notes FROM moods WHERE user_id = %s ORDER BY date DESC', 
                      (current_user.id,))
    else:
        cursor.execute('SELECT date, mood, notes FROM moods WHERE user_id = ? ORDER BY date DESC', 
                      (current_user.id,))
    
    moods = cursor.fetchall()
    conn.close()
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#1e293b'),
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=HexColor('#3b82f6'),
        borderWidth=1,
        borderColor=HexColor('#e2e8f0'),
        borderPadding=8,
        backColor=HexColor('#f8fafc')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=HexColor('#374151')
    )
    
    # Story (content) list
    story = []
    
    # Title
    story.append(Paragraph(f"🌈 Mood Tracker Report", title_style))
    story.append(Paragraph(f"<b>User:</b> {current_user.name}<br/><b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}", body_style))
    story.append(Spacer(1, 20))
    
    # Analytics calculations
    mood_values = {'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4, 'slightly well': 5, 'well': 6, 'very well': 7}
    
    if moods:
        # Calculate analytics
        current_streak = 0
        temp_streak = 0
        total_entries = len(moods)
        
        # Calculate current streak
        for row in reversed(list(moods)):
            mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
            if mood_values[mood] >= 5:  # slightly well or better
                temp_streak += 1
            else:
                break
        current_streak = temp_streak
        
        # Weekly and monthly patterns
        weekly_patterns = defaultdict(list)
        monthly_data = defaultdict(list)
        daily_data = []
        
        for row in moods:
            date_str = str(row['date']) if ACTUAL_USE_POSTGRES else row[0]
            mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
            day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
            month = date_str[:7]
            
            weekly_patterns[day_of_week].append(mood_values[mood])
            monthly_data[month].append(mood_values[mood])
            daily_data.append((date_str, mood_values[mood]))
        
        # Best day calculation
        best_day = "N/A"
        best_avg = 0
        for day, values in weekly_patterns.items():
            avg = sum(values) / len(values)
            if avg > best_avg:
                best_avg = avg
                best_day = day
        
        avg_mood = sum(mood_values[row['mood'] if ACTUAL_USE_POSTGRES else row[1]] for row in moods) / len(moods)
        
        # Summary section
        story.append(Paragraph("📊 Summary", heading_style))
        summary_text = f"""
        <b>Total Mood Entries:</b> {total_entries}<br/>
        <b>Current Good Mood Streak:</b> {current_streak} days<br/>
        <b>Best Day of Week:</b> {best_day}<br/>
        <b>Overall Average Mood:</b> {avg_mood:.2f}/5.0
        """
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 20))
        
        # Create charts
        plt.style.use('default')
        fig_size = (8, 4)
        
        # Weekly patterns chart
        if weekly_patterns:
            fig, ax = plt.subplots(figsize=fig_size, facecolor='white')
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_averages = []
            
            for day in days:
                if day in weekly_patterns:
                    avg = sum(weekly_patterns[day]) / len(weekly_patterns[day])
                    weekly_averages.append(avg)
                else:
                    weekly_averages.append(3)
            
            ax.plot(days, weekly_averages, marker='o', linewidth=3, markersize=8, 
                   color='#f59e0b', markerfacecolor='#f59e0b', markeredgecolor='white', markeredgewidth=2)
            ax.fill_between(days, weekly_averages, alpha=0.3, color='#f59e0b')
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#374151')
            ax.set_title('Weekly Patterns', fontsize=14, fontweight='bold', color='#1e293b', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8fafc')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            weekly_chart = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(weekly_chart.name, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            story.append(Paragraph("📅 Weekly Patterns", heading_style))
            story.append(Image(weekly_chart.name, width=6*inch, height=3*inch))
            story.append(Spacer(1, 20))
        
        # Monthly trends chart
        if monthly_data:
            fig, ax = plt.subplots(figsize=fig_size, facecolor='white')
            sorted_months = sorted(monthly_data.keys())[-12:]  # Last 12 months
            monthly_averages = []
            
            for month in sorted_months:
                avg = sum(monthly_data[month]) / len(monthly_data[month])
                monthly_averages.append(avg)
            
            ax.plot(sorted_months, monthly_averages, marker='o', linewidth=3, markersize=8,
                   color='#3b82f6', markerfacecolor='#3b82f6', markeredgecolor='white', markeredgewidth=2)
            ax.fill_between(sorted_months, monthly_averages, alpha=0.3, color='#3b82f6')
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#374151')
            ax.set_title('Monthly Trends', fontsize=14, fontweight='bold', color='#1e293b', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8fafc')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            monthly_chart = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(monthly_chart.name, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            story.append(Paragraph("📈 Monthly Trends", heading_style))
            story.append(Image(monthly_chart.name, width=6*inch, height=3*inch))
            story.append(Spacer(1, 20))
        
        # Recent mood history
        story.append(Paragraph("📝 Recent Mood History", heading_style))
        for i, row in enumerate(moods[:15]):  # Last 15 entries
            date_str = str(row['date']) if ACTUAL_USE_POSTGRES else row[0]
            mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
            notes = row['notes'] if ACTUAL_USE_POSTGRES else row[2]
            
            mood_emoji = {'very bad': '😭', 'bad': '😢', 'slightly bad': '😔', 'neutral': '😐', 'slightly well': '🙂', 'well': '😊', 'very well': '😄'}
            entry_text = f"<b>{date_str}</b> {mood_emoji.get(mood, '😐')} {mood.title()}"
            
            if notes:
                notes_text = notes[:100] + "..." if len(notes) > 100 else notes
                entry_text += f"<br/><i>Notes: {notes_text}</i>"
            
            story.append(Paragraph(entry_text, body_style))
            story.append(Spacer(1, 8))
    
    else:
        story.append(Paragraph("No mood data available yet. Start tracking your moods to see analytics!", body_style))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#6b7280'),
        alignment=1
    )
    story.append(Paragraph(f"Generated by Mood Tracker • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Clean up temporary files
    try:
        if 'weekly_chart' in locals():
            os.unlink(weekly_chart.name)
        if 'monthly_chart' in locals():
            os.unlink(monthly_chart.name)
    except:
        pass
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, 
                    download_name=f'mood_report_{datetime.now().strftime("%Y%m%d")}.pdf', 
                    mimetype='application/pdf')
    
    return send_file(buffer, as_attachment=True, download_name='mood_report.pdf', mimetype='application/pdf')

@app.route('/test-oauth')
def test_oauth():
    """Simple test page to show OAuth redirect URIs"""
    google_redirect = url_for('oauth_callback', provider='google', _external=True, _scheme='https')
    github_redirect = url_for('oauth_callback', provider='github', _external=True, _scheme='https')
    
    html = f"""
    <h1>OAuth Debug Info (Fixed)</h1>
    <p><strong>Google Redirect URI:</strong> {google_redirect}</p>
    <p><strong>GitHub Redirect URI:</strong> {github_redirect}</p>
    <p><strong>Current Host:</strong> {request.host}</p>
    <p><strong>Current Scheme:</strong> {request.scheme} (but using HTTPS for OAuth)</p>
    <hr>
    <p>✅ Now using HTTPS for OAuth redirects!</p>
    <p>Copy the Google Redirect URI above and make sure it matches EXACTLY in Google Cloud Console</p>
    <a href="/">Back to App</a>
    """
    return html

@app.route('/analytics-health')
@login_required
def analytics_health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test analytics queries
        if ACTUAL_USE_POSTGRES:
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = %s', (current_user.id,))
        else:
            cursor.execute('SELECT COUNT(*) FROM moods WHERE user_id = ?', (current_user.id,))
        
        mood_count = cursor.fetchone()[0] if not ACTUAL_USE_POSTGRES else cursor.fetchone()['count']
        conn.close()
        
        return {'status': 'healthy', 'mood_count': mood_count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}, 500

@app.route('/health')
def health_check():
    """Health check endpoint to verify database connection"""
    try:
        ensure_db_initialized()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if ACTUAL_USE_POSTGRES:
            cursor.execute('SELECT version();')
            db_info = f"PostgreSQL: {cursor.fetchone()['version']}"
        else:
            cursor.execute('SELECT sqlite_version();')
            db_info = f"SQLite: {cursor.fetchone()[0]}"
        
        cursor.execute('SELECT COUNT(*) FROM moods;')
        mood_count = cursor.fetchone()[0] if not ACTUAL_USE_POSTGRES else cursor.fetchone()['count']
        conn.close()
        
        return {
            'status': 'healthy',
            'database': db_info,
            'mood_count': mood_count,
            'db_initialized': DB_INITIALIZED,
            'postgres_enabled': ACTUAL_USE_POSTGRES,
            'database_url_set': DATABASE_URL is not None,
            'postgres_available': POSTGRES_AVAILABLE,
            'using_postgres': ACTUAL_USE_POSTGRES
        }
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'database_url_set': DATABASE_URL is not None,
            'postgres_available': POSTGRES_AVAILABLE,
            'using_postgres': ACTUAL_USE_POSTGRES
        }, 500

if __name__ == '__main__':
    # Force database initialization on startup
    print("🚀 Starting app and initializing database")
    try:
        init_db()
        print(f"✅ Database initialized - PostgreSQL: {ACTUAL_USE_POSTGRES}")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
    
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
