from collections import defaultdict
from datetime import datetime

MOOD_VALUES = {
    'very bad': 1, 'bad': 2, 'slightly bad': 3, 'neutral': 4,
    'slightly well': 5, 'well': 6, 'very well': 7
}

class MoodAnalytics:
    def __init__(self, moods):
        self.moods = moods
    
    def calculate_streak(self):
        """Calculate current good mood streak"""
        streak = 0
        for mood_entry in reversed(self.moods):
            mood_value = MOOD_VALUES[mood_entry['mood']]
            if mood_value >= 5:  # slightly well or better
                streak += 1
            else:
                break
        return streak
    
    def calculate_averages(self):
        """Calculate mood averages"""
        if not self.moods:
            return {'daily': 0, 'good_days': 0, 'bad_days': 0, 'total_entries': 0}
        
        daily_moods = defaultdict(list)
        for mood_entry in self.moods:
            date = mood_entry['date']
            mood_value = MOOD_VALUES[mood_entry['mood']]
            daily_moods[date].append(mood_value)
        
        daily_averages = []
        good_days = []
        bad_days = []
        
        for date, mood_list in daily_moods.items():
            daily_avg = sum(mood_list) / len(mood_list)
            daily_averages.append(daily_avg)
            
            if daily_avg >= 5:
                good_days.append(daily_avg)
            elif daily_avg <= 3:
                bad_days.append(daily_avg)
        
        return {
            'daily': round(sum(daily_averages) / len(daily_averages), 2) if daily_averages else 0,
            'good_days': round(sum(good_days) / len(good_days), 2) if good_days else 0,
            'bad_days': round(sum(bad_days) / len(bad_days), 2) if bad_days else 0,
            'total_entries': len(daily_averages)
        }
    
    def get_weekly_patterns(self):
        """Get mood patterns by day of week"""
        weekly_patterns = defaultdict(list)
        
        for mood_entry in self.moods:
            date_str = str(mood_entry['date'])
            mood_value = MOOD_VALUES[mood_entry['mood']]
            day_of_week = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
            weekly_patterns[day_of_week].append(mood_value)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {
            'labels': days,
            'data': [
                round(sum(weekly_patterns[day]) / len(weekly_patterns[day]), 2) 
                if day in weekly_patterns else 4
                for day in days
            ]
        }
    
    def get_monthly_trends(self):
        """Get monthly mood trends"""
        monthly_data = defaultdict(list)
        
        for mood_entry in self.moods:
            date_str = str(mood_entry['date'])
            mood_value = MOOD_VALUES[mood_entry['mood']]
            month = date_str[:7]  # YYYY-MM
            monthly_data[month].append(mood_value)
        
        chart_data = []
        for month in sorted(monthly_data.keys()):
            avg_mood = sum(monthly_data[month]) / len(monthly_data[month])
            chart_data.append({'month': month, 'mood': round(avg_mood, 1)})
        
        return chart_data
    
    def get_daily_patterns(self):
        """Get mood patterns by time of day"""
        time_data = []
        
        for mood_entry in self.moods:
            timestamp = mood_entry.get('timestamp')
            if not timestamp:
                continue
            
            mood_value = MOOD_VALUES[mood_entry['mood']]
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Convert to UTC-3
            from datetime import timedelta
            utc_minus_3 = timestamp - timedelta(hours=3)
            precise_time = utc_minus_3.hour + (utc_minus_3.minute / 60.0)
            
            time_data.append({
                'time': round(precise_time, 2),
                'mood_value': mood_value,
                'timestamp': utc_minus_3.isoformat()
            })
        
        return {'time_data': time_data}
    
    def get_summary(self):
        """Get complete analytics summary"""
        averages = self.calculate_averages()
        streak = self.calculate_streak()
        weekly = self.get_weekly_patterns()
        
        # Find best day
        best_day = "N/A"
        best_avg = 0
        for i, day in enumerate(weekly['labels']):
            if weekly['data'][i] > best_avg:
                best_avg = weekly['data'][i]
                best_day = day
        
        return {
            'current_streak': streak,
            'daily_average': averages['daily'],
            'good_days_average': averages['good_days'],
            'bad_days_average': averages['bad_days'],
            'total_entries': averages['total_entries'],
            'best_day': best_day,
            'weekly_patterns': weekly
        }
    
    def get_daily_patterns_for_date(self, selected_date):
        """Get mood patterns for a specific date"""
        from datetime import datetime
        
        # Filter moods for the selected date
        filtered_moods = []
        for mood_entry in self.moods:
            mood_date = mood_entry.get('date')
            if isinstance(mood_date, str):
                if mood_date == selected_date:
                    filtered_moods.append(mood_entry)
            elif hasattr(mood_date, 'strftime'):
                if mood_date.strftime('%Y-%m-%d') == selected_date:
                    filtered_moods.append(mood_entry)
        
        # Create temporary analytics instance for filtered data
        temp_analytics = MoodAnalytics(filtered_moods)
        result = temp_analytics.get_daily_patterns()
        result['period'] = f"Daily Patterns for {selected_date}"
        
        # If no data for the date, return empty structure
        if not filtered_moods:
            result = {
                'time_data': [],
                'labels': ['Morning', 'Afternoon', 'Evening', 'Night'],
                'data': [0, 0, 0, 0],
                'period': f"No data for {selected_date}"
            }
        
        return result
    
    def get_weekly_patterns_for_period(self, start_date, end_date, period_label):
        """Get weekly patterns for a specific date range"""
        from datetime import datetime
        
        # Filter moods for the date range
        filtered_moods = []
        for mood_entry in self.moods:
            mood_date = mood_entry.get('date')
            
            # Convert mood_date to date object for comparison
            if isinstance(mood_date, str):
                try:
                    mood_date = datetime.strptime(mood_date, '%Y-%m-%d').date()
                except:
                    continue
            elif hasattr(mood_date, 'date'):
                mood_date = mood_date.date()
            
            if start_date <= mood_date <= end_date:
                filtered_moods.append(mood_entry)
        
        # Create temporary analytics instance for filtered data
        temp_analytics = MoodAnalytics(filtered_moods)
        result = temp_analytics.get_weekly_patterns()
        result['period'] = period_label
        result['start_date'] = start_date.isoformat()
        result['end_date'] = end_date.isoformat()
        
        # Ensure we have the right structure for the frontend
        if 'labels' not in result:
            result['labels'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if 'data' not in result:
            result['data'] = [0, 0, 0, 0, 0, 0, 0]
        
        # Rename labels to days for consistency with frontend
        result['days'] = result['labels']
        
        return result
