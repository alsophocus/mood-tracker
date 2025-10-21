"""
SOLID-compliant insights routes
Single Responsibility Principle - handles only insights-related routes
"""

from flask import Blueprint, render_template, jsonify, session
from auth import login_required
from database import db
from mood_analyzer_service import MoodAnalyzer
from insight_generator_service import InsightGenerator
import traceback

# Create blueprint for insights
insights_bp = Blueprint('insights', __name__, url_prefix='/insights')


class InsightsController:
    """Single Responsibility - coordinates insights requests"""
    
    def __init__(self, db_instance):
        # Dependency Injection
        self.mood_analyzer = MoodAnalyzer(db_instance)
        self.insight_generator = InsightGenerator(self.mood_analyzer)
    
    def get_dashboard_data(self, user_id: int) -> dict:
        """Get all data needed for insights dashboard"""
        insights = self.insight_generator.generate_insights(user_id)
        trends = self.insight_generator.get_mood_trends(user_id, 'month')
        correlations = self.mood_analyzer.get_trigger_correlations(user_id)
        patterns = self.mood_analyzer.analyze_mood_patterns(user_id, 30)
        
        return {
            'insights': insights,
            'trends': trends,
            'correlations': correlations[:10],  # Top 10
            'patterns': patterns
        }


# Initialize controller
insights_controller = InsightsController(db)


@insights_bp.route('/')
@login_required
def dashboard():
    """Mood insights dashboard page"""
    return render_template('insights_dashboard.html')


@insights_bp.route('/api/dashboard-data')
@login_required
def get_dashboard_data():
    """API endpoint for dashboard data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        data = insights_controller.get_dashboard_data(user_id)
        return jsonify({'success': True, **data})
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@insights_bp.route('/api/insights')
@login_required
def get_insights():
    """API endpoint for insights only"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        insights = insights_controller.insight_generator.generate_insights(user_id)
        return jsonify({'success': True, 'insights': insights})
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@insights_bp.route('/api/trends/<period>')
@login_required
def get_trends(period):
    """API endpoint for mood trends"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        trends = insights_controller.insight_generator.get_mood_trends(user_id, period)
        return jsonify({'success': True, 'trends': trends})
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@insights_bp.route('/api/correlations')
@login_required
def get_correlations():
    """API endpoint for trigger correlations"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        correlations = insights_controller.mood_analyzer.get_trigger_correlations(user_id)
        return jsonify({'success': True, 'correlations': correlations})
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
