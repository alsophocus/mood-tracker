from flask import Flask, render_template, request, redirect, send_file, jsonify
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from collections import defaultdict

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

def get_db_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect('mood.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                         (id SERIAL PRIMARY KEY, date DATE UNIQUE, mood TEXT, notes TEXT)''')
    else:
        cursor.execute('''CREATE TABLE IF NOT EXISTS moods 
                         (id INTEGER PRIMARY KEY, date TEXT UNIQUE, mood TEXT, notes TEXT)''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT date, mood, notes FROM moods ORDER BY date DESC')
    moods = cursor.fetchall()
    
    # Calculate analytics
    analytics = calculate_analytics(conn)
    
    conn.close()
    return render_template('index.html', moods=moods, analytics=analytics)

@app.route('/save_mood', methods=['POST'])
def save_mood():
    mood = request.form['mood']
    notes = request.form.get('notes', '')
    date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute('''INSERT INTO moods (date, mood, notes) VALUES (%s, %s, %s)
                         ON CONFLICT (date) DO UPDATE SET mood = %s, notes = %s''',
                      (date, mood, notes, mood, notes))
    else:
        cursor.execute('INSERT OR REPLACE INTO moods (date, mood, notes) VALUES (?, ?, ?)',
                      (date, mood, notes))
    
    conn.commit()
    conn.close()
    
    return redirect('/')

def calculate_analytics(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT date, mood FROM moods ORDER BY date')
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
def mood_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT date, mood FROM moods ORDER BY date')
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
def export_pdf():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT date, mood FROM moods ORDER BY date')
    moods = cursor.fetchall()
    conn.close()
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.drawString(100, 750, "Mood Tracker Report")
    y = 700
    
    for row in moods:
        date_str = str(row['date']) if USE_POSTGRES else row[0]
        mood = row['mood'] if USE_POSTGRES else row[1]
        p.drawString(100, y, f"{date_str}: {mood}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='mood_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
