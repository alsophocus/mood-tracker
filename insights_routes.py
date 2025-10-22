"""
Insights routes following SOLID principles.

This module contains HTTP controllers for insights dashboard.
Follows Single Responsibility Principle by separating HTTP concerns from business logic.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from typing import Dict, Any
from models import MoodEntry

insights_bp = Blueprint('insights', __name__)

class InsightsController:
    """
    Controller for insights features - Single Responsibility Principle.
    
    Handles HTTP concerns only, delegates business logic to services.
    """
    
    def __init__(self):
        """Initialize controller with minimal dependencies."""
        pass
    
    def render_insights_dashboard(self, additional_context: Dict[str, Any] = None) -> str:
        """
        Render insights dashboard with proper context.
        
        Args:
            additional_context: Additional context variables for the template
            
        Returns:
            Rendered HTML template
        """
        context = {
            'user': current_user
        }
        
        if additional_context:
            context.update(additional_context)
            
        return render_template('insights_dashboard.html', **context)
    
    def get_insights_data(self) -> Dict[str, Any]:
        """
        Get insights data for API endpoint.
        
        Returns:
            JSON response with insights data
        """
        try:
            # Fetch user's mood data
            mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).limit(100).all()
            
            # Simple data processing for now
            mood_data = []
            mood_counts = {}
            
            for entry in mood_entries:
                mood_data.append({
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'mood': entry.mood,
                    'triggers': entry.triggers or '',
                    'notes': entry.notes or ''
                })
                
                # Count moods for distribution
                mood = entry.mood.lower()
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Generate simple visualization data
            visualization_data = {
                'mood_trend': {
                    'chart_type': 'line',
                    'data': {
                        'labels': [entry['date'] for entry in mood_data[-30:]],  # Last 30 days
                        'datasets': [{
                            'label': 'Mood Trend',
                            'data': [self._mood_to_value(entry['mood']) for entry in mood_data[-30:]],
                            'borderColor': '#2196f3',
                            'backgroundColor': 'rgba(33, 150, 243, 0.1)',
                            'tension': 0.4,
                            'fill': True
                        }]
                    }
                },
                'mood_distribution': {
                    'chart_type': 'doughnut',
                    'data': {
                        'labels': list(mood_counts.keys()),
                        'datasets': [{
                            'data': list(mood_counts.values()),
                            'backgroundColor': ['#f44336', '#ff9800', '#9e9e9e', '#4caf50', '#2196f3'],
                            'borderWidth': 2,
                            'borderColor': '#ffffff'
                        }]
                    }
                }
            }
            
            return {
                'success': True,
                'visualizations': visualization_data,
                'total_entries': len(mood_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'visualizations': {}
            }
    
    def _mood_to_value(self, mood: str) -> int:
        """Convert mood string to numeric value."""
        mood_values = {
            'very bad': 1,
            'bad': 2,
            'neutral': 3,
            'good': 4,
            'very good': 5,
            'well': 4,
            'very well': 5
        }
        return mood_values.get(mood.lower(), 3)

# Initialize controller instance
controller = InsightsController()

@insights_bp.route('/insights')
@login_required
def dashboard():
    """
    Insights dashboard route - Single Responsibility Principle.
    
    Handles HTTP request for insights dashboard, delegates rendering to controller.
    """
    return controller.render_insights_dashboard()

@insights_bp.route('/api/insights/visualizations')
@login_required
def get_visualizations():
    """
    API endpoint for visualization data - Single Responsibility Principle.
    
    Returns JSON data for enhanced visualizations.
    """
    return jsonify(controller.get_insights_data())
