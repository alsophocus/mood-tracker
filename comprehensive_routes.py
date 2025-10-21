"""
SOLID-compliant comprehensive routes for all features
Single Responsibility Principle - handles routes for goals, reminders, export, analytics
"""

from flask import Blueprint, render_template, jsonify, session, request, send_file
from auth import login_required
from database import db
from goal_tracker_service import GoalTracker
from reminder_service import ReminderService
from data_export_service import DataExportService
from enhanced_analytics_service import EnhancedAnalyticsService
import json
import io

# Create blueprint for comprehensive features
comprehensive_bp = Blueprint('comprehensive', __name__, url_prefix='/features')


class ComprehensiveController:
    """Single Responsibility - coordinates all feature requests"""
    
    def __init__(self, db_instance):
        # Dependency Injection
        self.goal_tracker = GoalTracker(db_instance)
        self.reminder_service = ReminderService(db_instance)
        self.data_export_service = DataExportService(db_instance)
        self.enhanced_analytics = EnhancedAnalyticsService(db_instance)


# Initialize controller
comprehensive_controller = ComprehensiveController(db)


# Goals Routes
@comprehensive_bp.route('/goals')
@login_required
def goals_dashboard():
    """Goals dashboard page"""
    return render_template('goals_dashboard.html')


@comprehensive_bp.route('/api/goals', methods=['GET', 'POST'])
@login_required
def handle_goals():
    """Handle goals API requests"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        if request.method == 'GET':
            goals = comprehensive_controller.goal_tracker.get_user_goals(user_id)
            return jsonify({'success': True, 'goals': goals})
        
        elif request.method == 'POST':
            goal_data = request.get_json()
            result = comprehensive_controller.goal_tracker.create_goal(user_id, goal_data)
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_bp.route('/api/goals/<int:goal_id>/progress', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """Update goal progress"""
    try:
        progress_data = request.get_json()
        result = comprehensive_controller.goal_tracker.update_goal_progress(goal_id, progress_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Reminders Routes
@comprehensive_bp.route('/reminders')
@login_required
def reminders_dashboard():
    """Reminders dashboard page"""
    return render_template('reminders_dashboard.html')


@comprehensive_bp.route('/api/reminders', methods=['GET', 'POST'])
@login_required
def handle_reminders():
    """Handle reminders API requests"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        if request.method == 'GET':
            reminders = comprehensive_controller.reminder_service.get_user_reminders(user_id)
            return jsonify({'success': True, 'reminders': reminders})
        
        elif request.method == 'POST':
            reminder_data = request.get_json()
            result = comprehensive_controller.reminder_service.create_reminder(user_id, reminder_data)
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_bp.route('/api/reminders/check')
@login_required
def check_reminders():
    """Check if reminders should be sent"""
    try:
        user_id = session.get('user_id')
        should_remind = comprehensive_controller.reminder_service.should_send_reminder(user_id)
        return jsonify({'success': True, 'should_remind': should_remind})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Data Export Routes
@comprehensive_bp.route('/export')
@login_required
def export_dashboard():
    """Data export dashboard page"""
    return render_template('export_dashboard.html')


@comprehensive_bp.route('/api/export/<format>')
@login_required
def export_data(format):
    """Export user data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        result = comprehensive_controller.data_export_service.export_user_data(user_id, format)
        
        if result['success']:
            if format == 'json':
                # Return JSON data
                return jsonify({
                    'success': True,
                    'data': result['data'],
                    'filename': result['filename']
                })
            elif format == 'csv':
                # Return CSV file
                output = io.StringIO(result['data'])
                output.seek(0)
                return send_file(
                    io.BytesIO(output.getvalue().encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=result['filename']
                )
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_bp.route('/api/import', methods=['POST'])
@login_required
def import_data():
    """Import user data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        import_data = request.get_json()
        result = comprehensive_controller.data_export_service.import_user_data(user_id, import_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Enhanced Analytics Routes
@comprehensive_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Enhanced analytics dashboard page"""
    return render_template('analytics_dashboard.html')


@comprehensive_bp.route('/api/analytics/correlations')
@login_required
def get_correlation_analysis():
    """Get correlation analysis"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        result = comprehensive_controller.enhanced_analytics.get_correlation_analysis(user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_bp.route('/api/analytics/predictions')
@login_required
def get_predictive_insights():
    """Get predictive insights"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        result = comprehensive_controller.enhanced_analytics.get_predictive_insights(user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_bp.route('/api/analytics/comparative')
@login_required
def get_comparative_analytics():
    """Get comparative analytics"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        result = comprehensive_controller.enhanced_analytics.get_comparative_analytics(user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Quick Entry Widget Route
@comprehensive_bp.route('/quick-entry')
@login_required
def quick_entry_widget():
    """Quick entry widget page"""
    return render_template('quick_entry_widget.html')


@comprehensive_bp.route('/api/quick-mood', methods=['POST'])
@login_required
def quick_mood_entry():
    """Quick mood entry API"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        mood_data = request.get_json()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO moods (user_id, mood, date, timestamp, notes)
                VALUES (%s, %s, CURRENT_DATE, CURRENT_TIMESTAMP, %s)
                ON CONFLICT (user_id, date) 
                DO UPDATE SET mood = EXCLUDED.mood, timestamp = EXCLUDED.timestamp, notes = EXCLUDED.notes
                RETURNING id
            """, (
                user_id,
                mood_data.get('mood'),
                mood_data.get('notes', '')
            ))
            
            mood_id = cursor.fetchone()['id']
            conn.commit()
            
            return jsonify({
                'success': True,
                'mood_id': mood_id,
                'message': 'Mood logged successfully!'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
