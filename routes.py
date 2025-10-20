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

@main_bp.route('/fix-schema')
def fix_schema():
    """Fix database schema constraints"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check current table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'moods'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            # Check existing constraints
            cursor.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints
                WHERE table_name = 'moods'
            """)
            constraints = cursor.fetchall()
            
            # Drop and recreate the moods table with proper constraints
            cursor.execute('DROP TABLE IF EXISTS moods CASCADE')
            
            cursor.execute('''
                CREATE TABLE moods (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    mood TEXT NOT NULL,
                    notes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, date)
                )
            ''')
            
            # Recreate indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_user_date ON moods(user_id, date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_timestamp ON moods(timestamp)')
            
            return jsonify({
                'success': True,
                'message': 'Schema fixed successfully',
                'old_columns': [dict(col) for col in columns],
                'old_constraints': [dict(cons) for cons in constraints]
            })
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/debug-save')
def debug_save():
    """Debug save without authentication"""
    try:
        # Test database connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users')
            user_count = cursor.fetchone()['count']
            
            # Try to get first user
            cursor.execute('SELECT id FROM users LIMIT 1')
            first_user = cursor.fetchone()
            
            if first_user:
                user_id = first_user['id']
                # Try to save a test mood
                result = db.save_mood(user_id, datetime.now().date(), 'well', 'debug test')
                return jsonify({
                    'success': True,
                    'message': 'Debug save successful',
                    'user_count': user_count,
                    'test_user_id': user_id,
                    'save_result': str(result)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No users found in database',
                    'user_count': user_count
                })
                
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/test-save')
@login_required
def test_save():
    """Test saving a mood to debug issues"""
    try:
        # Try to save a test mood
        result = db.save_mood(current_user.id, datetime.now().date(), 'well', 'test mood')
        return jsonify({
            'success': True,
            'message': 'Test mood saved successfully',
            'result': str(result),
            'user_id': current_user.id,
            'date': datetime.now().date().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'user_id': current_user.id,
            'date': datetime.now().date().isoformat()
        }), 500

@main_bp.route('/save_mood', methods=['POST'])
@login_required
def save_mood():
    """Save mood entry"""
    mood = request.form.get('mood')
    notes = request.form.get('notes', '')
    
    print(f"DEBUG: Received mood save request - mood: {mood}, notes: {notes}")
    
    # Check if user is authenticated
    if not current_user or not hasattr(current_user, 'id'):
        print("DEBUG: User not authenticated or missing ID")
        return jsonify({'error': 'User not authenticated'}), 401
    
    print(f"DEBUG: User ID: {current_user.id}")
    
    if not mood:
        print("DEBUG: No mood selected")
        return jsonify({'error': 'Please select a mood before saving.'}), 400
    
    try:
        print(f"DEBUG: Attempting to save mood for user {current_user.id}")
        
        # Use Chile timezone (UTC-3) for the date
        from datetime import timedelta
        chile_time = datetime.now() - timedelta(hours=3)
        chile_date = chile_time.date()
        
        print(f"DEBUG: Server time: {datetime.now()}, Chile time: {chile_time}, Chile date: {chile_date}")
        
        result = db.save_mood(current_user.id, chile_date, mood, notes)
        print(f"DEBUG: Mood saved successfully - result: {result}")
        
        return jsonify({
            'success': True,
            'message': 'Mood saved successfully!',
            'mood': mood,
            'notes': notes,
            'date': chile_date.isoformat()
        })
            
    except Exception as e:
        print(f"DEBUG: Error saving mood - {e}")
        import traceback
        print(f"DEBUG: Traceback - {traceback.format_exc()}")
        return jsonify({'error': f'Error saving mood: {str(e)}'}), 500

@main_bp.route('/recent_moods')
@login_required
def recent_moods():
    """Get recent moods as JSON for AJAX updates"""
    recent_moods = db.get_user_moods(current_user.id, limit=5)
    return jsonify({'moods': recent_moods})

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

@main_bp.route('/weekly_trends')
@login_required
def weekly_trends():
    """Get weekly mood trends (sums) for specific month"""
    from datetime import date, timedelta
    import calendar
    
    # Get month parameters
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    
    if year and month:
        try:
            result = analytics.get_weekly_trends_for_month(year, month)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": "Invalid date parameters"}), 400
    else:
        # Default to current month
        today = date.today()
        result = analytics.get_weekly_trends_for_month(today.year, today.month)
        return jsonify(result)

@main_bp.route('/monthly_trends')
@login_required
def monthly_trends():
    """Get monthly mood trends (averages) for specific year"""
    from datetime import date
    
    # Get year parameter
    year = request.args.get('year', type=int)
    
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    
    if year:
        try:
            result = analytics.get_monthly_trends_for_year(year)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": "Invalid year parameter"}), 400
    else:
        # Default to current year
        today = date.today()
        result = analytics.get_monthly_trends_for_year(today.year)
        return jsonify(result)

@main_bp.route('/daily_patterns')
@login_required
def daily_patterns():
    """Get daily mood patterns for specific date or all dates"""
    selected_date = request.args.get('date')
    print(f"DEBUG: Daily patterns requested for date: {selected_date}")
    
    moods = db.get_user_moods(current_user.id)
    print(f"DEBUG: Found {len(moods)} total moods for user {current_user.id}")
    
    if moods and selected_date:
        print(f"DEBUG: Sample mood dates: {[str(mood.get('date')) for mood in moods[:3]]}")
    
    analytics = MoodAnalytics(moods)
    
    if selected_date:
        result = analytics.get_daily_patterns_for_date(selected_date)
        print(f"DEBUG: Result for {selected_date}: {len([x for x in result.get('data', []) if x is not None])} non-null values")
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

@main_bp.route('/hourly_average_mood')
@login_required
def hourly_average_mood():
    """Get average mood per hour across all user data"""
    moods = db.get_user_moods(current_user.id)
    analytics = MoodAnalytics(moods)
    result = analytics.get_hourly_averages()
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

@main_bp.route('/test-db')
def test_database():
    """Test database operations"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM moods')
            result = cursor.fetchone()
            return {'mood_count': result['count'], 'status': 'success'}
    except Exception as e:
        return {'error': str(e), 'status': 'error'}, 500

@main_bp.route('/reset-database-confirm-delete-all-data')
def reset_database():
    """Reset database - DELETE ALL MOOD DATA"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count existing data
            cursor.execute('SELECT COUNT(*) as count FROM moods')
            mood_result = cursor.fetchone()
            mood_count = mood_result['count'] if mood_result else 0
            
            cursor.execute('SELECT COUNT(*) as count FROM users')
            user_result = cursor.fetchone()
            user_count = user_result['count'] if user_result else 0
            
            # Delete all moods
            cursor.execute('DELETE FROM moods')
            deleted_count = cursor.rowcount
            
            # Reset sequence
            cursor.execute('ALTER SEQUENCE moods_id_seq RESTART WITH 1')
            
            return {
                'status': 'success',
                'message': 'Database reset completed',
                'deleted_moods': deleted_count,
                'remaining_users': user_count,
                'original_mood_count': mood_count,
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

@main_bp.route('/analytics-health')
@login_required
def analytics_health():
    """Analytics system health check"""
    try:
        mood_count = len(db.get_user_moods(current_user.id))
        return {'status': 'healthy', 'mood_count': mood_count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}, 500

@main_bp.route('/fix-mood-dates')
@login_required
def fix_mood_dates():
    """Fix mood dates that were saved with wrong timezone"""
    try:
        from datetime import timedelta
        
        # Get all user moods
        moods = db.get_user_moods(current_user.id)
        print(f"DEBUG: Found {len(moods)} moods to potentially fix")
        
        fixed_count = 0
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            for mood in moods:
                mood_id = mood['id']
                current_date = mood['date']
                timestamp = mood['timestamp']
                
                # Check if this mood was likely saved with UTC timezone
                # (if timestamp hour suggests it was saved late at night Chile time)
                if hasattr(timestamp, 'hour'):
                    # If timestamp is between 00:00-05:59 UTC, it was likely saved 
                    # the previous day in Chile time (21:00-02:59 Chile time)
                    if 0 <= timestamp.hour <= 5:
                        # Shift date back by one day
                        corrected_date = current_date - timedelta(days=1)
                        
                        cursor.execute('''
                            UPDATE moods 
                            SET date = %s 
                            WHERE id = %s
                        ''', (corrected_date, mood_id))
                        
                        fixed_count += 1
                        print(f"DEBUG: Fixed mood {mood_id}: {current_date} -> {corrected_date}")
        
        return jsonify({
            'success': True,
            'message': f'Fixed {fixed_count} mood dates',
            'total_moods': len(moods),
            'fixed_count': fixed_count
        })
        
    except Exception as e:
        import traceback
        print(f"DEBUG: Error fixing mood dates: {e}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
@main_bp.route('/add-fake-data')
@login_required
def add_fake_data():
    """Add fake mood data for current week for testing"""
    try:
        import random
        from datetime import datetime, date, timedelta
        
        # Get current week dates (Sunday to Saturday)
        timezone_service = container.get_timezone_service()
        today = timezone_service.get_chile_date()
        
        # Find Sunday of current week (start of week)
        days_since_sunday = today.weekday() + 1  # Monday=0, so Sunday=6, adjust to Sunday=0
        if days_since_sunday == 7:  # If today is Sunday
            days_since_sunday = 0
        
        week_start = today - timedelta(days=days_since_sunday)
        
        moods = ['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well']
        notes_options = ['', 'feeling good', 'rough day', 'work stress', 'relaxing', 'productive', 'tired']
        
        added_count = 0
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Add mood entries for each day of the current week
            for day_offset in range(7):  # Sunday to Saturday
                current_date = week_start + timedelta(days=day_offset)
                
                # Add 3-8 random moods per day
                moods_per_day = random.randint(3, 8)
                
                for _ in range(moods_per_day):
                    # Random hour between 6 AM and 11 PM
                    hour = random.randint(6, 23)
                    minute = random.randint(0, 59)
                    
                    # Create timestamp for the specific date
                    fake_timestamp = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                    
                    # Random mood and notes
                    mood = random.choice(moods)
                    notes = random.choice(notes_options)
                    
                    cursor.execute('''
                        INSERT INTO moods (user_id, date, mood, notes, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (current_user.id, current_date, mood, notes, fake_timestamp))
                    
                    added_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Added {added_count} fake mood entries for current week',
            'week_start': week_start.isoformat(),
            'week_end': (week_start + timedelta(days=6)).isoformat(),
            'added_count': added_count
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
