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
        """Get mood patterns by hour of day"""
        # Initialize hourly data (0-23 hours)
        hourly_moods = {hour: [] for hour in range(24)}
        
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
            hour = utc_minus_3.hour
            
            hourly_moods[hour].append(mood_value)
        
        # Create labels and data for all 24 hours
        labels = [f"{hour:02d}:00" for hour in range(24)]
        data = []
        
        for hour in range(24):
            if hourly_moods[hour]:
                data.append(round(sum(hourly_moods[hour]) / len(hourly_moods[hour]), 2))
            else:
                data.append(None)  # No data for this hour
        
        return {
            'labels': labels,
            'data': data,
            'period': 'Average Mood by Hour (All Days)'
        }
    
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
        
        print(f"DEBUG: Filtering moods for date: {selected_date}")
        print(f"DEBUG: Total moods to filter: {len(self.moods)}")
        
        # Filter moods for the selected date
        filtered_moods = []
        for mood_entry in self.moods:
            mood_date = mood_entry.get('date')
            print(f"DEBUG: Checking mood date: {mood_date} (type: {type(mood_date)})")
            
            if isinstance(mood_date, str):
                if mood_date == selected_date:
                    filtered_moods.append(mood_entry)
                    print(f"DEBUG: String date match found")
            elif hasattr(mood_date, 'strftime'):
                formatted_date = mood_date.strftime('%Y-%m-%d')
                print(f"DEBUG: Formatted date: {formatted_date}")
                if formatted_date == selected_date:
                    filtered_moods.append(mood_entry)
                    print(f"DEBUG: Date object match found")
        
        print(f"DEBUG: Filtered moods count: {len(filtered_moods)}")
        
        # Create temporary analytics instance for filtered data
        temp_analytics = MoodAnalytics(filtered_moods)
        result = temp_analytics.get_daily_patterns()
        result['period'] = f"Daily Patterns for {selected_date}"
        
        # If no data for the date, return empty structure
        if not filtered_moods:
            print(f"DEBUG: No moods found for {selected_date}, returning empty data")
            result = {
                'labels': [f"{hour:02d}:00" for hour in range(24)],
                'data': [None] * 24,
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
    
    def get_weekly_trends_for_month(self, year, month):
        """Get weekly mood trends (averages) for a specific month"""
        from datetime import date, timedelta
        import calendar
        
        # Calculate month boundaries
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        
        # Calculate first Monday of the month for week calculation
        first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
        days_to_first_monday = (7 - first_weekday) % 7
        first_monday = first_day + timedelta(days=days_to_first_monday)
        
        # Initialize weekly data
        weekly_moods = {}
        week_labels = []
        
        # Calculate weeks in this month
        current_week_start = first_monday
        week_num = 1
        
        while current_week_start.month <= month and current_week_start.year == year:
            week_end = current_week_start + timedelta(days=6)
            # Ensure we don't go past month end
            week_end = min(week_end, last_day)
            
            weekly_moods[week_num] = []
            week_labels.append(f"Week {week_num}")
            
            # Collect moods for this week
            for mood_entry in self.moods:
                mood_date = mood_entry.get('date')
                
                # Convert mood_date to date object
                if isinstance(mood_date, str):
                    try:
                        mood_date = datetime.strptime(mood_date, '%Y-%m-%d').date()
                    except:
                        continue
                elif hasattr(mood_date, 'date'):
                    mood_date = mood_date.date()
                
                # Check if mood is in this week
                if current_week_start <= mood_date <= week_end:
                    mood_value = MOOD_VALUES[mood_entry['mood']]
                    weekly_moods[week_num].append(mood_value)
            
            # Move to next week
            current_week_start += timedelta(days=7)
            week_num += 1
            
            # Safety check
            if week_num > 6:
                break
        
        # Calculate averages for each week
        data = []
        for i in range(1, week_num):
            if weekly_moods[i]:
                avg = round(sum(weekly_moods[i]) / len(weekly_moods[i]), 1)
                data.append(avg)
            else:
                data.append(0)
        
        return {
            'labels': week_labels,
            'data': data,
            'period': f"Weekly Mood Averages for {calendar.month_name[month]} {year}",
            'year': year,
            'month': month
        }
    
    def get_monthly_trends_for_year(self, year):
        """Get monthly mood trends (averages) for a specific year"""
        import calendar
        
        # Initialize monthly data for all 12 months
        monthly_moods = {month: [] for month in range(1, 13)}
        
        # Collect moods for each month
        for mood_entry in self.moods:
            mood_date = mood_entry.get('date')
            
            # Convert mood_date to date object
            if isinstance(mood_date, str):
                try:
                    mood_date = datetime.strptime(mood_date, '%Y-%m-%d').date()
                except:
                    continue
            elif hasattr(mood_date, 'date'):
                mood_date = mood_date.date()
            
            # Check if mood is in the target year
            if mood_date.year == year:
                mood_value = MOOD_VALUES[mood_entry['mood']]
                monthly_moods[mood_date.month].append(mood_value)
        
        # Calculate averages for each month
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = []
        
        for month in range(1, 13):
            if monthly_moods[month]:
                avg = round(sum(monthly_moods[month]) / len(monthly_moods[month]), 1)
                data.append(avg)
            else:
                data.append(0)
        
        return {
            'labels': month_labels,
            'data': data,
            'period': f"Monthly Mood Averages for {year}",
            'year': year
        }
    
    def get_hourly_averages(self):
        """Get average mood per hour across all user data"""
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        hourly_totals = defaultdict(list)
        
        # Group moods by hour (same logic as get_daily_patterns)
        for mood_entry in self.moods:
            timestamp = mood_entry.get('timestamp')
            if not timestamp:
                continue
            
            mood_value = MOOD_VALUES[mood_entry['mood']]
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Convert to UTC-3
            utc_minus_3 = timestamp - timedelta(hours=3)
            hour = utc_minus_3.hour
            
            hourly_totals[hour].append(mood_value)
        
        # Calculate averages for each hour
        data = []
        for hour in range(24):
            if hourly_totals[hour]:
                avg = round(sum(hourly_totals[hour]) / len(hourly_totals[hour]), 2)
                data.append(avg)
            else:
                data.append(4)  # Neutral mood when no data available
        
        return {
            'labels': [f"{hour:02d}:00" for hour in range(24)],
            'data': data,
            'period': 'Average Mood Per Hour (All Time)'
        }
