"""
SOLID-compliant insights routes
Single Responsibility Principle - handles only insights-related routes
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from database import db

# Create blueprint for insights
insights_bp = Blueprint('insights', __name__, url_prefix='/insights')

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
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        # Return minimal data structure
        return jsonify({
            'success': True,
            'insights': [],
            'trends': [],
            'correlations': []
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@insights_bp.route('/api/insights')
@login_required
def get_insights():
    """API endpoint for insights only"""
    try:
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
            
        return jsonify({'success': True, 'insights': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
