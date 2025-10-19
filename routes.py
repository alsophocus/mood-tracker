from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
from database import db
from analytics import MoodAnalytics
from pdf_export import PDFExporter

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    recent_moods = db.get_user_moods(current_user.id, limit=5)
    all_moods = db.get_user_moods(current_user.id)
    
    analytics = MoodAnalytics(all_moods).get_summary()
    
    return render_template('index.html', moods=recent_moods, analytics=analytics, user=current_user)

@main_bp.route('/save_mood', methods=['POST'])
@login_required
def save_mood():
    """Save mood entry"""
    mood = request.form.get('mood')
    notes = request.form.get('notes', '')
    
    if not mood:
        flash('Please select a mood before saving.')
        return redirect(url_for('main.index'))
    
    try:
        db.save_mood(current_user.id, datetime.now().date(), mood, notes)
        flash('Mood saved successfully!')
    except Exception as e:
        flash('Error saving mood - please try again.')
    
    return redirect(url_for('main.index'))

@main_bp.route('/mood_data')
@login_required
def mood_data():
    """Get monthly mood trend data"""
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    return jsonify(analytics.get_monthly_trends())

@main_bp.route('/weekly_patterns')
@login_required
def weekly_patterns():
    """Get weekly mood patterns for specific week of month"""
    from datetime import date, timedelta
    import calendar
    
    # Get week parameters
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int) 
    week_of_month = request.args.get('week', type=int)
    
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    
    if year and month and week_of_month:
        # Calculate date range for specific week of month
        try:
            first_day = date(year, month, 1)
            first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
            
            # Calculate the start of the specified week
            days_to_first_monday = (7 - first_weekday) % 7
            first_monday = first_day + timedelta(days=days_to_first_monday)
            
            # Calculate start and end of the requested week
            week_start = first_monday + timedelta(weeks=week_of_month - 1)
            week_end = week_start + timedelta(days=6)
            
            # Ensure we don't go outside the month boundaries
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            if week_start.month == month:
                start_date = week_start
                end_date = min(week_end, last_day)
                return jsonify(analytics.get_weekly_patterns_for_period(start_date, end_date, f"Week {week_of_month} of {calendar.month_name[month]} {year}"))
            else:
                return jsonify({"error": "Week does not exist in this month"}), 400
        except Exception as e:
            return jsonify({"error": "Invalid date parameters"}), 400
    else:
        result = analytics.get_weekly_patterns()
        
    # Ensure we always return a valid structure
    if not result.get('labels') and not result.get('days'):
        result = {
            'labels': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'data': [0, 0, 0, 0, 0, 0, 0],
            'period': 'No data available'
        }
    elif result.get('labels') and not result.get('days'):
        result['days'] = result['labels']
        
    return jsonify(result)

@main_bp.route('/daily_patterns')
@login_required
def daily_patterns():
    """Get daily mood patterns for specific date or all dates"""
    selected_date = request.args.get('date')
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    
    if selected_date:
        result = analytics.get_daily_patterns_for_date(selected_date)
    else:
        result = analytics.get_daily_patterns()
    
    # Ensure we always return a valid structure
    if not result.get('labels') or not result.get('data'):
        result = {
            'labels': [f"{hour:02d}:00" for hour in range(24)],
            'data': [None] * 24,
            'period': 'No data available'
        }
    
    return jsonify(result)

@main_bp.route('/export_pdf')
@login_required
def export_pdf():
    """Export mood data as PDF"""
    moods = db.get_user_moods(current_user.id)
    exporter = PDFExporter(current_user, moods)
    buffer = exporter.generate_report()
    
    filename = f'mood_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()['version']
        
        return {
            'status': 'healthy',
            'database': f"PostgreSQL: {version}",
            'timestamp': datetime.now().isoformat(),
            'database_url_set': bool(db.url),
            'database_initialized': db._initialized
        }
    except Exception as e:
        # Return degraded status instead of 500 error
        return {
            'status': 'degraded',
            'database_status': 'unavailable',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'database_url_set': bool(db.url),
            'database_initialized': db._initialized,
            'note': 'App running but database unavailable'
        }, 200  # Return 200 instead of 500 for health checks

@main_bp.route('/debug')
def debug_info():
    """Debug information endpoint"""
    import os
    return {
        'environment_vars': {
            'DATABASE_URL': 'SET' if os.environ.get('DATABASE_URL') else 'NOT SET',
            'GOOGLE_CLIENT_ID': 'SET' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT SET',
            'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'NOT SET',
            'PORT': os.environ.get('PORT', 'NOT SET')
        },
        'config': {
            'database_url_configured': bool(db.url),
            'database_initialized': db._initialized
        },
        'timestamp': datetime.now().isoformat()
    }

@main_bp.route('/analytics-health')
@login_required
def analytics_health():
    """Analytics system health check"""
    try:
        mood_count = len(db.get_user_moods(current_user.id))
        return {'status': 'healthy', 'mood_count': mood_count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}, 500
