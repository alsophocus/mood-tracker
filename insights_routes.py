"""
Insights routes following SOLID principles.

This module contains HTTP controllers for insights dashboard.
Follows Single Responsibility Principle by separating HTTP concerns from business logic.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from typing import Dict, Any
from models import MoodEntry
from visualization_service import MoodVisualizationService, VisualizationController

insights_bp = Blueprint('insights', __name__)

class InsightsController:
    """
    Controller for insights features - Single Responsibility Principle.
    
    Handles HTTP concerns only, delegates business logic to services.
    """
    
    def __init__(self, visualization_controller: VisualizationController):
        """Initialize controller with visualization service dependency injection."""
        self.visualization_controller = visualization_controller
    
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
            
            # Convert to dict format for visualization service
            mood_data = [
                {
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'mood': entry.mood,
                    'triggers': entry.triggers or '',
                    'notes': entry.notes or ''
                }
                for entry in mood_entries
            ]
            
            # Get visualization data
            visualization_data = self.visualization_controller.get_visualization_data(mood_data)
            
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

# Initialize services following Dependency Injection principle
visualization_service = MoodVisualizationService()
visualization_controller = VisualizationController(visualization_service)
controller = InsightsController(visualization_controller)

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
