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

# Try to import PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
# Only use PostgreSQL if we have a valid DATABASE_URL and psycopg2 is available
USE_POSTGRES = (DATABASE_URL is not None and 
                POSTGRES_AVAILABLE and 
                DATABASE_URL.startswith('postgresql://') and
                'port' not in DATABASE_URL or DATABASE_URL.count(':') >= 2)

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
    client_kwargs={'scope': 'openid email profile'},
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
    
    if USE_POSTGRES:
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    else:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        if USE_POSTGRES:
            return User(user_data['id'], user_data['email'], user_data['name'], user_data['provider'])
        else:
            return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

def get_db_connection():
    if USE_POSTGRES:
        try:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to SQLite...")
            # Fall back to SQLite if PostgreSQL fails
            conn = sqlite3.connect('mood.db')
            conn.row_factory = sqlite3.Row
            return conn
    else:
        conn = sqlite3.connect('mood.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id SERIAL PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
        # Create moods table with user_id
        cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                         (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), 
                          date DATE, mood TEXT, notes TEXT,
                          UNIQUE(user_id, date))''')
    else:
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id INTEGER PRIMARY KEY, email TEXT UNIQUE, name TEXT, provider TEXT)''')
        # Create moods table with user_id
        cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                         (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, mood TEXT, notes TEXT,
                          FOREIGN KEY (user_id) REFERENCES users (id),
                          UNIQUE(user_id, date))''')
    
    conn.commit()
    conn.close()

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
            redirect_uri = url_for('oauth_callback', provider='google', _external=True, _scheme='https')
            app.logger.info(f"Google OAuth redirect URI: {redirect_uri}")
            print(f"DEBUG: Google OAuth redirect URI: {redirect_uri}")
            return google.authorize_redirect(redirect_uri)
        elif provider == 'github':
            if not os.environ.get('GITHUB_CLIENT_ID') or not os.environ.get('GITHUB_CLIENT_SECRET'):
                flash('GitHub OAuth not configured')
                return redirect(url_for('login'))
            redirect_uri = url_for('oauth_callback', provider='github', _external=True, _scheme='https')
            return github.authorize_redirect(redirect_uri)
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
            token = google.authorize_access_token()
            if not token:
                flash('Failed to get access token from Google')
                return redirect(url_for('login'))
            
            # Get user info directly from Google's userinfo endpoint
            try:
                import requests
                headers = {'Authorization': f'Bearer {token["access_token"]}'}
                resp = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
                
                if resp.status_code != 200:
                    flash('Failed to get user information from Google')
                    return redirect(url_for('login'))
                
                user_info = resp.json()
                email = user_info.get('email')
                name = user_info.get('name')
            except Exception as e:
                flash(f'Error getting user info from Google: {str(e)}')
                return redirect(url_for('login'))
            
        elif provider == 'github':
            token = github.authorize_access_token()
            if not token:
                flash('Failed to get access token from GitHub')
                return redirect(url_for('login'))
            
            # Get user info from GitHub API
            resp = github.get('user', token=token)
            if resp.status_code != 200:
                flash('Failed to get user information from GitHub')
                return redirect(url_for('login'))
            
            user_info = resp.json()
            email = user_info.get('email')
            name = user_info.get('name') or user_info.get('login')
            
            # If email is private, get it from emails endpoint
            if not email:
                emails_resp = github.get('user/emails', token=token)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    primary_email = next((e['email'] for e in emails if e['primary']), None)
                    email = primary_email
            
        else:
            flash('Invalid OAuth provider')
            return redirect(url_for('login'))
        
        if not email:
            flash(f'Could not get email from {provider}')
            return redirect(url_for('login'))
        
        # Create or get user
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        else:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            if USE_POSTGRES:
                user = User(user_data['id'], user_data['email'], user_data['name'], user_data['provider'])
            else:
                user = User(user_data[0], user_data[1], user_data[2], user_data[3])
        else:
            # Create new user
            if USE_POSTGRES:
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
    
    if USE_POSTGRES:
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
    
    if USE_POSTGRES:
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
    
    if USE_POSTGRES:
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
        mood = row['mood'] if USE_POSTGRES else row[1]
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
        date_str = str(row['date']) if USE_POSTGRES else row[0]
        mood = row['mood'] if USE_POSTGRES else row[1]
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
    
    if USE_POSTGRES:
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
        date_str = str(row['date']) if USE_POSTGRES else row[0]
        mood = row['mood'] if USE_POSTGRES else row[1]
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
    
    if USE_POSTGRES:
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
        date_str = str(row['date']) if USE_POSTGRES else row[0]
        mood = row['mood'] if USE_POSTGRES else row[1]
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
        
        if USE_POSTGRES:
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
            'using_postgres': USE_POSTGRES
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'database_url_set': DATABASE_URL is not None,
            'postgres_available': POSTGRES_AVAILABLE,
            'using_postgres': USE_POSTGRES
        }, 500

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
