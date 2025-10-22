"""
Enhanced Data Visualization Service following SOLID principles.

This module provides advanced visualization data processing for mood insights.
Follows Single Responsibility Principle by focusing only on data visualization logic.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from dataclasses import dataclass

@dataclass
class VisualizationData:
    """Data structure for visualization components - Single Responsibility."""
    chart_type: str
    data: Dict[str, Any]
    config: Dict[str, Any]
    title: str
    description: str

class MoodVisualizationService:
    """
    Service for generating advanced mood visualizations - Single Responsibility Principle.
    
    Handles data processing for charts and graphs without UI concerns.
    """
    
    MOOD_VALUES = {
        'very bad': 1,
        'bad': 2,
        'neutral': 3,
        'good': 4,
        'very good': 5,
        'well': 4,
        'very well': 5
    }
    
    MOOD_COLORS = {
        'very bad': '#f44336',
        'bad': '#ff9800',
        'neutral': '#9e9e9e',
        'good': '#4caf50',
        'very good': '#2196f3',
        'well': '#4caf50',
        'very well': '#2196f3'
    }
    
    def generate_mood_trend_chart(self, mood_data: List[Dict]) -> VisualizationData:
        """Generate mood trend visualization data."""
        if not mood_data:
            return self._empty_chart("Mood Trend", "No mood data available")
        
        # Process data for trend analysis
        daily_averages = self._calculate_daily_averages(mood_data)
        
        return VisualizationData(
            chart_type="line",
            data={
                "labels": list(daily_averages.keys()),
                "datasets": [{
                    "label": "Daily Mood Average",
                    "data": list(daily_averages.values()),
                    "borderColor": "#2196f3",
                    "backgroundColor": "rgba(33, 150, 243, 0.1)",
                    "tension": 0.4,
                    "fill": True
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"mode": "index"}
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 5,
                        "ticks": {
                            "stepSize": 1,
                            "callback": "function(value) { return ['', 'Very Bad', 'Bad', 'Neutral', 'Good', 'Very Good'][value] || value; }"
                        }
                    }
                }
            },
            title="Mood Trend Analysis",
            description="Your mood patterns over time with daily averages"
        )
    
    def generate_mood_distribution_chart(self, mood_data: List[Dict]) -> VisualizationData:
        """Generate mood distribution pie chart data."""
        if not mood_data:
            return self._empty_chart("Mood Distribution", "No mood data available")
        
        mood_counts = defaultdict(int)
        for entry in mood_data:
            mood = entry.get('mood', '').lower()
            mood_counts[mood] += 1
        
        return VisualizationData(
            chart_type="doughnut",
            data={
                "labels": list(mood_counts.keys()),
                "datasets": [{
                    "data": list(mood_counts.values()),
                    "backgroundColor": [self.MOOD_COLORS.get(mood, '#9e9e9e') for mood in mood_counts.keys()],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"position": "bottom"},
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.parsed + ' entries'; }"
                        }
                    }
                }
            },
            title="Mood Distribution",
            description="Breakdown of your mood entries by category"
        )
    
    def generate_weekly_heatmap_data(self, mood_data: List[Dict]) -> VisualizationData:
        """Generate weekly mood heatmap data."""
        if not mood_data:
            return self._empty_chart("Weekly Heatmap", "No mood data available")
        
        # Process data for heatmap
        weekly_data = self._process_weekly_heatmap(mood_data)
        
        return VisualizationData(
            chart_type="heatmap",
            data={
                "datasets": [{
                    "label": "Mood Intensity",
                    "data": weekly_data,
                    "backgroundColor": "function(context) { return context.parsed.v > 3 ? '#4caf50' : context.parsed.v < 3 ? '#f44336' : '#9e9e9e'; }"
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "title": "function(context) { return context[0].dataset.data[context[0].dataIndex].day; }",
                            "label": "function(context) { return 'Mood: ' + context.parsed.v.toFixed(1); }"
                        }
                    }
                }
            },
            title="Weekly Mood Heatmap",
            description="Visual representation of mood intensity throughout the week"
        )
    
    def generate_trigger_correlation_chart(self, mood_data: List[Dict]) -> VisualizationData:
        """Generate trigger correlation analysis."""
        if not mood_data:
            return self._empty_chart("Trigger Analysis", "No mood data available")
        
        trigger_impact = self._analyze_trigger_impact(mood_data)
        
        return VisualizationData(
            chart_type="bar",
            data={
                "labels": list(trigger_impact.keys()),
                "datasets": [{
                    "label": "Average Mood Impact",
                    "data": list(trigger_impact.values()),
                    "backgroundColor": [
                        '#4caf50' if impact > 3 else '#f44336' if impact < 3 else '#9e9e9e'
                        for impact in trigger_impact.values()
                    ],
                    "borderWidth": 1
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return 'Impact: ' + context.parsed.y.toFixed(2); }"
                        }
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 5,
                        "title": {"display": True, "text": "Mood Impact"}
                    },
                    "x": {
                        "title": {"display": True, "text": "Triggers"}
                    }
                }
            },
            title="Trigger Impact Analysis",
            description="How different triggers affect your mood on average"
        )
    
    def _calculate_daily_averages(self, mood_data: List[Dict]) -> Dict[str, float]:
        """Calculate daily mood averages."""
        daily_moods = defaultdict(list)
        
        for entry in mood_data:
            date_str = entry.get('date', '')
            mood = entry.get('mood', '').lower()
            mood_value = self.MOOD_VALUES.get(mood, 3)
            
            if date_str:
                daily_moods[date_str].append(mood_value)
        
        return {
            date: statistics.mean(moods)
            for date, moods in daily_moods.items()
        }
    
    def _process_weekly_heatmap(self, mood_data: List[Dict]) -> List[Dict]:
        """Process data for weekly heatmap visualization."""
        weekly_data = []
        daily_averages = self._calculate_daily_averages(mood_data)
        
        for date_str, avg_mood in daily_averages.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekly_data.append({
                    'x': date_obj.weekday(),
                    'y': date_obj.isocalendar()[1],
                    'v': avg_mood,
                    'day': date_obj.strftime('%A, %B %d')
                })
            except ValueError:
                continue
        
        return weekly_data
    
    def _analyze_trigger_impact(self, mood_data: List[Dict]) -> Dict[str, float]:
        """Analyze the impact of different triggers on mood."""
        trigger_moods = defaultdict(list)
        
        for entry in mood_data:
            mood_value = self.MOOD_VALUES.get(entry.get('mood', '').lower(), 3)
            triggers = entry.get('triggers', '')
            
            if triggers:
                trigger_list = [t.strip() for t in triggers.split(',') if t.strip()]
                for trigger in trigger_list:
                    trigger_moods[trigger].append(mood_value)
        
        return {
            trigger: statistics.mean(moods)
            for trigger, moods in trigger_moods.items()
            if len(moods) >= 2  # Only include triggers with at least 2 occurrences
        }
    
    def _empty_chart(self, title: str, description: str) -> VisualizationData:
        """Return empty chart data structure."""
        return VisualizationData(
            chart_type="empty",
            data={},
            config={},
            title=title,
            description=description
        )

class VisualizationController:
    """
    Controller for visualization endpoints - Single Responsibility Principle.
    
    Handles HTTP concerns for visualization data requests.
    """
    
    def __init__(self, visualization_service: MoodVisualizationService):
        """Initialize with visualization service dependency injection."""
        self.visualization_service = visualization_service
    
    def get_visualization_data(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Get all visualization data for insights dashboard."""
        return {
            "mood_trend": self.visualization_service.generate_mood_trend_chart(mood_data).__dict__,
            "mood_distribution": self.visualization_service.generate_mood_distribution_chart(mood_data).__dict__,
            "weekly_heatmap": self.visualization_service.generate_weekly_heatmap_data(mood_data).__dict__,
            "trigger_correlation": self.visualization_service.generate_trigger_correlation_chart(mood_data).__dict__
        }
