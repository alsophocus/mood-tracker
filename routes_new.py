"""
Routes refactored following SOLID principles
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date
import traceback

from container import container
from analytics import MoodAnalytics
from pdf_export import PDFExporter

main_bp = Blueprint('main', __name__)

class MoodController:
    """Mood-related routes controller - Single Responsibility Principle"""
    
    def __init__(self):
        self.mood_service = container.get_mood_service()
    
    def save_mood(self):
        """Save mood entry"""
        mood = request.form.get('mood')
        notes = request.form.get('notes', '')
        
        print(f"DEBUG: Received mood save request - mood: {mood}, notes: {notes}")
        
        # Check authentication
        if not current_user or not hasattr(current_user, 'id'):
            print("DEBUG: User not authenticated or missing ID")
            return jsonify({'error': 'User not authenticated'}), 401
        
        print(f"DEBUG: User ID: {current_user.id}")
        
        if not mood:
            print("DEBUG: No mood selected")
            return jsonify({'error': 'Please select a mood before saving.'}), 400
        
        try:
            print(f"DEBUG: Attempting to save mood for user {current_user.id}")
            result = self.mood_service.save_mood(current_user.id, mood, notes)
            print(f"DEBUG: Mood saved successfully - result: {result}")
            return jsonify(result)
        except ValueError as e:
            print(f"DEBUG: Validation error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            print(f"DEBUG: Error saving mood: {e}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500

class AnalyticsController:
    """Analytics-related routes controller - Single Responsibility Principle"""
    
    def __init__(self):
        self.mood_service = container.get_mood_service()
    
    def daily_patterns(self):
        """Get daily mood patterns for specific date or all dates"""
        selected_date = request.args.get('date')
        print(f"DEBUG: Daily patterns requested for date: {selected_date}")
        
        try:
            target_date = None
            if selected_date:
                target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            
            result = self.mood_service.get_daily_patterns(current_user.id, target_date)
            return jsonify(result)
        except Exception as e:
            print(f"DEBUG: Error in daily patterns: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    def chart_data(self):
        """Get clean chart data - raw mood data properly formatted"""
        try:
            moods = self.mood_service.get_user_moods(current_user.id)
            print(f"DEBUG: Found {len(moods)} moods for user {current_user.id}")
            
            if moods:
                print(f"DEBUG: Sample mood: {moods[0]}")
                print(f"DEBUG: Mood keys: {list(moods[0].keys())}")
            
            # Convert to chart format
            chart_moods = []
            mood_values = {
                'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4,
                'slightly well': 5, 'well': 6, 'very well': 7
            }
            
            for mood in moods:
                try:
                    chart_mood = {
                        'date': mood['date'].strftime('%Y-%m-%d') if hasattr(mood['date'], 'strftime') else str(mood['date']),
                        'timestamp': mood['timestamp'].isoformat() if hasattr(mood['timestamp'], 'isoformat') else str(mood['timestamp']),
                        'mood': mood['mood'],
                        'mood_value': mood_values.get(mood['mood'], 4),
                        'notes': mood.get('notes', ''),
                        'hour': mood['timestamp'].hour if hasattr(mood['timestamp'], 'hour') else 0
                    }
                    chart_moods.append(chart_mood)
                except Exception as e:
                    print(f"DEBUG: Error processing mood {mood}: {e}")
            
            print(f"DEBUG: Processed {len(chart_moods)} chart moods")
            if chart_moods:
                print(f"DEBUG: Sample chart mood: {chart_moods[0]}")
            
            return jsonify({
                'success': True,
                'total_moods': len(chart_moods),
                'moods': chart_moods,
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_time': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"DEBUG: Chart data error: {e}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500

# Initialize controllers
mood_controller = MoodController()
analytics_controller = AnalyticsController()

# Route definitions following Single Responsibility Principle
@main_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    mood_service = container.get_mood_service()
    recent_moods = mood_service.get_user_moods(current_user.id, limit=5)
    all_moods = mood_service.get_user_moods(current_user.id)
    
    analytics = MoodAnalytics(all_moods).get_summary()
    
    return render_template('index.html', moods=recent_moods, analytics=analytics, user=current_user)

@main_bp.route('/save_mood', methods=['POST'])
@login_required
def save_mood():
    """Save mood entry - delegates to controller"""
    return mood_controller.save_mood()

@main_bp.route('/daily_patterns')
@login_required
def daily_patterns():
    """Get daily patterns - delegates to controller"""
    return analytics_controller.daily_patterns()

@main_bp.route('/chart-data')
@login_required
def chart_data():
    """Get chart data - delegates to controller"""
    return analytics_controller.chart_data()

# Health check routes
@main_bp.route('/health')
def health():
    """System health check"""
    try:
        db_connection = container.get_db_connection()
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}, 500

@main_bp.route('/analytics-health')
@login_required
def analytics_health():
    """Analytics system health check"""
    try:
        mood_service = container.get_mood_service()
        mood_count = len(mood_service.get_user_moods(current_user.id))
        return {'status': 'healthy', 'mood_count': mood_count}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}, 500
