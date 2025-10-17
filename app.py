from flask import Flask, render_template, request, redirect, send_file, jsonify
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from collections import defaultdict

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('mood.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS moods 
                    (id INTEGER PRIMARY KEY, date TEXT, mood TEXT, notes TEXT)''')
    # Add notes column if it doesn't exist (for existing databases)
    try:
        conn.execute('ALTER TABLE moods ADD COLUMN notes TEXT')
    except:
        pass
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('mood.db')
    moods = conn.execute('SELECT date, mood, notes FROM moods ORDER BY date DESC').fetchall()
    
    # Calculate analytics
    analytics = calculate_analytics(conn)
    
    conn.close()
    return render_template('index.html', moods=moods, analytics=analytics)

@app.route('/save_mood', methods=['POST'])
def save_mood():
    mood = request.form['mood']
    notes = request.form.get('notes', '')
    date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('mood.db')
    conn.execute('INSERT OR REPLACE INTO moods (date, mood, notes) VALUES (?, ?, ?)', (date, mood, notes))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/export_pdf')
def export_pdf():
    conn = sqlite3.connect('mood.db')
    moods = conn.execute('SELECT date, mood FROM moods ORDER BY date').fetchall()
    conn.close()
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.drawString(100, 750, "Mood Tracker Report")
    y = 700
    
    for date, mood in moods:
        p.drawString(100, y, f"{date}: {mood}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='mood_report.pdf', mimetype='application/pdf')

def calculate_analytics(conn):
    moods = conn.execute('SELECT date, mood FROM moods ORDER BY date').fetchall()
    if not moods:
        return {'current_streak': 0, 'best_streak': 0, 'weekly_patterns': {}}
    
    mood_values = {'super sad': 1, 'sad': 2, 'neutral': 3, 'good': 4, 'super good': 5}
    
    # Calculate streaks (good = 4 or 5)
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for date, mood in reversed(moods):  # Start from most recent
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
    for date, mood in moods:
        day_of_week = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
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
    conn = sqlite3.connect('mood.db')
    moods = conn.execute('SELECT date, mood FROM moods ORDER BY date').fetchall()
    conn.close()
    
    mood_values = {'super sad': 1, 'sad': 2, 'neutral': 3, 'good': 4, 'super good': 5}
    monthly_data = defaultdict(list)
    
    for date, mood in moods:
        month = date[:7]  # YYYY-MM format
        monthly_data[month].append(mood_values[mood])
    
    # Calculate average mood per month
    chart_data = []
    for month in sorted(monthly_data.keys()):
        avg_mood = sum(monthly_data[month]) / len(monthly_data[month])
        chart_data.append({'month': month, 'mood': round(avg_mood, 1)})
    
    return jsonify(chart_data)

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
