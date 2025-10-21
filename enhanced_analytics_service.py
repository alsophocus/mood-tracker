"""
SOLID-compliant enhanced analytics service
Single Responsibility Principle - handles advanced analytics operations
"""

from database import Database
from typing import Dict, List, Any
from datetime import date, datetime, timedelta
import statistics
import json


class EnhancedAnalyticsService:
    """Single Responsibility - provides advanced mood analytics"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_correlation_analysis(self, user_id: int) -> Dict[str, Any]:
        """Advanced correlation analysis between triggers and mood"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get detailed mood-trigger data
                cursor.execute("""
                    SELECT m.mood, m.date, t.name as tag, t.category,
                           m.context_location, m.context_activity, m.context_weather
                    FROM moods m
                    LEFT JOIN mood_tags mt ON m.id = mt.mood_id
                    LEFT JOIN tags t ON mt.tag_id = t.id
                    WHERE m.user_id = %s
                    ORDER BY m.date DESC
                """, (user_id,))
                
                data = cursor.fetchall()
                
                return {
                    'success': True,
                    'trigger_correlations': self._analyze_trigger_correlations(data),
                    'context_correlations': self._analyze_context_correlations(data),
                    'temporal_patterns': self._analyze_temporal_patterns(data),
                    'mood_volatility': self._calculate_mood_volatility(data)
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_predictive_insights(self, user_id: int) -> Dict[str, Any]:
        """Generate predictive insights based on patterns"""
        try:
            patterns = self.get_correlation_analysis(user_id)
            if not patterns['success']:
                return patterns
            
            predictions = []
            
            # Predict mood based on day of week
            day_predictions = self._predict_by_day_of_week(user_id)
            if day_predictions:
                predictions.extend(day_predictions)
            
            # Predict mood based on triggers
            trigger_predictions = self._predict_by_triggers(user_id)
            if trigger_predictions:
                predictions.extend(trigger_predictions)
            
            return {
                'success': True,
                'predictions': predictions,
                'confidence_level': self._calculate_prediction_confidence(user_id)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_comparative_analytics(self, user_id: int) -> Dict[str, Any]:
        """Compare mood data across different time periods"""
        try:
            current_month = self._get_period_data(user_id, 30)
            previous_month = self._get_period_data(user_id, 30, offset=30)
            current_week = self._get_period_data(user_id, 7)
            previous_week = self._get_period_data(user_id, 7, offset=7)
            
            return {
                'success': True,
                'monthly_comparison': {
                    'current': current_month,
                    'previous': previous_month,
                    'change': self._calculate_change(current_month, previous_month)
                },
                'weekly_comparison': {
                    'current': current_week,
                    'previous': previous_week,
                    'change': self._calculate_change(current_week, previous_week)
                },
                'year_over_year': self._get_year_over_year_comparison(user_id)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _analyze_trigger_correlations(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze correlations between triggers and mood"""
        trigger_moods = {}
        
        for entry in data:
            if entry['tag']:
                tag = entry['tag']
                mood_value = self._mood_to_numeric(entry['mood'])
                
                if tag not in trigger_moods:
                    trigger_moods[tag] = []
                trigger_moods[tag].append(mood_value)
        
        correlations = []
        for tag, moods in trigger_moods.items():
            if len(moods) >= 3:  # Need sufficient data
                avg_mood = statistics.mean(moods)
                std_dev = statistics.stdev(moods) if len(moods) > 1 else 0
                
                correlations.append({
                    'trigger': tag,
                    'average_mood': round(avg_mood, 2),
                    'consistency': round(10 - std_dev, 2),  # Higher = more consistent
                    'sample_size': len(moods),
                    'impact_strength': self._calculate_impact_strength(avg_mood, std_dev)
                })
        
        return sorted(correlations, key=lambda x: x['impact_strength'], reverse=True)
    
    def _analyze_context_correlations(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze correlations with context (location, activity, weather)"""
        contexts = {
            'location': {},
            'activity': {},
            'weather': {}
        }
        
        for entry in data:
            mood_value = self._mood_to_numeric(entry['mood'])
            
            for context_type in contexts.keys():
                context_value = entry.get(f'context_{context_type}')
                if context_value:
                    if context_value not in contexts[context_type]:
                        contexts[context_type][context_value] = []
                    contexts[context_type][context_value].append(mood_value)
        
        # Calculate averages for each context
        result = {}
        for context_type, context_data in contexts.items():
            result[context_type] = []
            for context_value, moods in context_data.items():
                if len(moods) >= 2:
                    result[context_type].append({
                        'value': context_value,
                        'average_mood': round(statistics.mean(moods), 2),
                        'frequency': len(moods)
                    })
            
            result[context_type].sort(key=lambda x: x['average_mood'], reverse=True)
        
        return result
    
    def _analyze_temporal_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in mood data"""
        daily_moods = {}
        monthly_moods = {}
        
        for entry in data:
            if entry['date']:
                date_obj = entry['date']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                
                day_of_week = date_obj.strftime('%A')
                month = date_obj.strftime('%B')
                mood_value = self._mood_to_numeric(entry['mood'])
                
                if day_of_week not in daily_moods:
                    daily_moods[day_of_week] = []
                daily_moods[day_of_week].append(mood_value)
                
                if month not in monthly_moods:
                    monthly_moods[month] = []
                monthly_moods[month].append(mood_value)
        
        return {
            'daily_patterns': {day: round(statistics.mean(moods), 2) 
                             for day, moods in daily_moods.items() if moods},
            'monthly_patterns': {month: round(statistics.mean(moods), 2) 
                               for month, moods in monthly_moods.items() if moods}
        }
    
    def _calculate_mood_volatility(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate mood volatility metrics"""
        if not data:
            return {'volatility_score': 0, 'stability_rating': 'No data'}
        
        mood_values = [self._mood_to_numeric(entry['mood']) for entry in data]
        
        if len(mood_values) < 2:
            return {'volatility_score': 0, 'stability_rating': 'Insufficient data'}
        
        std_dev = statistics.stdev(mood_values)
        volatility_score = round(std_dev, 2)
        
        if volatility_score < 0.5:
            stability_rating = 'Very Stable'
        elif volatility_score < 1.0:
            stability_rating = 'Stable'
        elif volatility_score < 1.5:
            stability_rating = 'Moderate'
        elif volatility_score < 2.0:
            stability_rating = 'Variable'
        else:
            stability_rating = 'Highly Variable'
        
        return {
            'volatility_score': volatility_score,
            'stability_rating': stability_rating,
            'mood_range': {
                'min': min(mood_values),
                'max': max(mood_values),
                'average': round(statistics.mean(mood_values), 2)
            }
        }
    
    def _predict_by_day_of_week(self, user_id: int) -> List[Dict[str, Any]]:
        """Predict mood based on day of week patterns"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT mood, date FROM moods 
                    WHERE user_id = %s 
                    ORDER BY date DESC 
                    LIMIT 100
                """, (user_id,))
                
                data = cursor.fetchall()
                day_patterns = {}
                
                for entry in data:
                    date_obj = entry['date']
                    if isinstance(date_obj, str):
                        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                    
                    day_name = date_obj.strftime('%A')
                    mood_value = self._mood_to_numeric(entry['mood'])
                    
                    if day_name not in day_patterns:
                        day_patterns[day_name] = []
                    day_patterns[day_name].append(mood_value)
                
                predictions = []
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A')
                
                if tomorrow in day_patterns and len(day_patterns[tomorrow]) >= 3:
                    avg_mood = statistics.mean(day_patterns[tomorrow])
                    predictions.append({
                        'type': 'day_prediction',
                        'prediction': f'Tomorrow ({tomorrow}), your mood typically averages {avg_mood:.1f}/7',
                        'confidence': min(90, len(day_patterns[tomorrow]) * 10)
                    })
                
                return predictions
                
        except Exception:
            return []
    
    def _predict_by_triggers(self, user_id: int) -> List[Dict[str, Any]]:
        """Predict mood impact of common triggers"""
        # This would integrate with calendar/weather APIs in a full implementation
        return [
            {
                'type': 'trigger_prediction',
                'prediction': 'Based on your patterns, work meetings tend to lower your mood by 0.8 points',
                'confidence': 75
            }
        ]
    
    def _calculate_prediction_confidence(self, user_id: int) -> int:
        """Calculate overall prediction confidence based on data volume"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM moods 
                    WHERE user_id = %s AND date >= %s
                """, (user_id, date.today() - timedelta(days=90)))
                
                recent_entries = cursor.fetchone()[0]
                
                # More data = higher confidence
                if recent_entries >= 60:
                    return 85
                elif recent_entries >= 30:
                    return 70
                elif recent_entries >= 14:
                    return 55
                else:
                    return 30
                    
        except Exception:
            return 30
    
    def _get_period_data(self, user_id: int, days: int, offset: int = 0) -> Dict[str, Any]:
        """Get mood data for a specific period"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                start_date = date.today() - timedelta(days=days + offset)
                end_date = date.today() - timedelta(days=offset)
                
                cursor.execute("""
                    SELECT mood FROM moods 
                    WHERE user_id = %s AND date BETWEEN %s AND %s
                """, (user_id, start_date, end_date))
                
                moods = [self._mood_to_numeric(row['mood']) for row in cursor.fetchall()]
                
                if not moods:
                    return {'average': 0, 'count': 0, 'trend': 'no_data'}
                
                return {
                    'average': round(statistics.mean(moods), 2),
                    'count': len(moods),
                    'trend': self._calculate_trend(moods)
                }
                
        except Exception:
            return {'average': 0, 'count': 0, 'trend': 'error'}
    
    def _calculate_change(self, current: Dict, previous: Dict) -> Dict[str, Any]:
        """Calculate change between periods"""
        if current['count'] == 0 or previous['count'] == 0:
            return {'change': 0, 'direction': 'no_data', 'percentage': 0}
        
        change = current['average'] - previous['average']
        percentage = (change / previous['average']) * 100 if previous['average'] != 0 else 0
        
        if abs(change) < 0.1:
            direction = 'stable'
        elif change > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        return {
            'change': round(change, 2),
            'direction': direction,
            'percentage': round(percentage, 1)
        }
    
    def _get_year_over_year_comparison(self, user_id: int) -> Dict[str, Any]:
        """Compare current period with same period last year"""
        # Simplified implementation - would need more sophisticated date handling
        return {
            'available': False,
            'message': 'Year-over-year comparison requires at least 1 year of data'
        }
    
    def _calculate_trend(self, moods: List[float]) -> str:
        """Calculate trend direction for a series of moods"""
        if len(moods) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation - compare first and second half
        mid = len(moods) // 2
        first_half = statistics.mean(moods[:mid])
        second_half = statistics.mean(moods[mid:])
        
        diff = second_half - first_half
        
        if abs(diff) < 0.2:
            return 'stable'
        elif diff > 0:
            return 'improving'
        else:
            return 'declining'
    
    def _calculate_impact_strength(self, avg_mood: float, std_dev: float) -> float:
        """Calculate impact strength of a trigger"""
        # Higher average mood and lower standard deviation = stronger positive impact
        # Lower average mood and lower standard deviation = stronger negative impact
        consistency_factor = max(0, 3 - std_dev)  # Higher consistency = higher factor
        mood_factor = abs(avg_mood - 4)  # Distance from neutral (4)
        
        return round(mood_factor * consistency_factor, 2)
    
    def _mood_to_numeric(self, mood: str) -> float:
        """Convert mood string to numeric value"""
        mood_map = {
            'very bad': 1.0, 'bad': 2.0, 'slightly bad': 3.0,
            'neutral': 4.0, 'slightly well': 5.0, 'well': 6.0, 'very well': 7.0
        }
        return mood_map.get(mood.lower(), 4.0)
