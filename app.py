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

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
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
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
            raise

def get_db_connection():
    ensure_db_initialized()
    if ACTUAL_USE_POSTGRES:
        print(f"🔍 DATABASE_URL: {DATABASE_URL}")
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)
    else:
        conn = sqlite3.connect('mood.db')
        conn.row_factory = sqlite3.Row
        return conn

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
                          date DATE, mood TEXT, notes TEXT,
                          UNIQUE(user_id, date))''')
        conn.commit()
        conn.close()
        print("✅ PostgreSQL connection successful with psycopg3")
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

@app.route('/debug-env')
def debug_env():
    return {
        'DATABASE_URL_set': DATABASE_URL is not None,
        'DATABASE_URL_length': len(DATABASE_URL) if DATABASE_URL else 0,
        'POSTGRES_AVAILABLE': POSTGRES_AVAILABLE,
        'PORT': os.environ.get('PORT', 'not_set'),
        'env_vars': list(os.environ.keys())
    }

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
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('SELECT date, mood, notes FROM moods WHERE user_id = %s ORDER BY date DESC', 
                      (current_user.id,))
    else:
        cursor.execute('SELECT date, mood, notes FROM moods WHERE user_id = ? ORDER BY date DESC', 
                      (current_user.id,))
    
    moods = cursor.fetchall()
    
    # Calculate analytics
    analytics = calculate_analytics(conn)
    
    conn.close()
    return render_template('index.html', moods=moods, analytics=analytics, user=current_user)

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

def calculate_analytics(conn):
    cursor = conn.cursor()
    
    if ACTUAL_USE_POSTGRES:
        cursor.execute('SELECT date, mood FROM moods WHERE user_id = %s ORDER BY date', 
                      (current_user.id,))
    else:
        cursor.execute('SELECT date, mood FROM moods WHERE user_id = ? ORDER BY date', 
                      (current_user.id,))
    
    moods = cursor.fetchall()
    
    if not moods:
        return {'current_streak': 0, 'best_streak': 0, 'weekly_patterns': {}}
    
    mood_values = {'super sad': 1, 'sad': 2, 'neutral': 3, 'good': 4, 'super good': 5}
    
    # Calculate streaks (good = 4 or 5)
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for row in reversed(list(moods)):  # Start from most recent
        mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
        if mood_values[mood] >= 4:  # good or super good
            temp_streak += 1
            if current_streak == 0:  # First good day from recent
                current_streak = temp_streak
        else:
            if temp_streak > best_streak:
                best_streak = temp_streak
            temp_streak = 0
    
    if temp_streak > best_streak:
        best_streak = temp_streak
    
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
        'current_streak': current_streak,
        'best_streak': best_streak,
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
    
    mood_values = {'super sad': 1, 'sad': 2, 'neutral': 3, 'good': 4, 'super good': 5}
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

@app.route('/export_pdf')
@login_required
def export_pdf():
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
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.drawString(100, 750, f"Mood Tracker Report - {current_user.name}")
    y = 700
    
    for row in moods:
        date_str = str(row['date']) if ACTUAL_USE_POSTGRES else row[0]
        mood = row['mood'] if ACTUAL_USE_POSTGRES else row[1]
        p.drawString(100, y, f"{date_str}: {mood}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
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

@app.route('/health')
def health_check():
    """Health check endpoint to verify database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if ACTUAL_USE_POSTGRES:
            cursor.execute('SELECT version();')
            db_info = f"PostgreSQL: {cursor.fetchone()[0]}"
        else:
            cursor.execute('SELECT sqlite_version();')
            db_info = f"SQLite: {cursor.fetchone()[0]}"
        
        cursor.execute('SELECT COUNT(*) FROM moods;')
        mood_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'status': 'healthy',
            'database': db_info,
            'mood_entries': mood_count,
            'database_url_set': DATABASE_URL is not None,
            'postgres_available': POSTGRES_AVAILABLE,
            'using_postgres': ACTUAL_USE_POSTGRES
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'database_url_set': DATABASE_URL is not None,
            'postgres_available': POSTGRES_AVAILABLE,
            'using_postgres': ACTUAL_USE_POSTGRES
        }, 500

if __name__ == '__main__':
    # Skip database initialization completely on startup
    print("🚀 Starting app without database initialization")
    
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
