"""
Working PDF Export with Material Design 3 principles
Focuses on functionality and proper ReportLab implementation
"""

import io
import tempfile
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from analytics import MoodAnalytics, MOOD_VALUES

# Material Design 3 Colors (simplified)
MD3_PRIMARY = HexColor('#6750A4')
MD3_SECONDARY = HexColor('#625B71')
MD3_SURFACE = HexColor('#FFFBFE')
MD3_ON_SURFACE = HexColor('#1C1B1F')
MD3_ON_SURFACE_VARIANT = HexColor('#49454F')
MD3_SUCCESS = HexColor('#4CAF50')
MD3_WARNING = HexColor('#FF9800')
MD3_ERROR = HexColor('#BA1A1A')

class WorkingPDFExporter:
    def __init__(self, user, moods):
        self.user = user
        self.moods = moods
        self.analytics = MoodAnalytics(moods)
        self.styles = self._create_working_styles()
    
    def _create_working_styles(self):
        """Create working styles that actually render properly"""
        styles = getSampleStyleSheet()
        
        return {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=28,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=MD3_PRIMARY,
                fontName='Helvetica-Bold'
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=16,
                spaceBefore=24,
                textColor=MD3_PRIMARY,
                fontName='Helvetica-Bold'
            ),
            'subheading': ParagraphStyle(
                'SubHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=16,
                textColor=MD3_SECONDARY,
                fontName='Helvetica-Bold'
            ),
            'body': ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=8,
                textColor=MD3_ON_SURFACE,
                fontName='Helvetica'
            ),
            'small': ParagraphStyle(
                'Small',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                textColor=MD3_ON_SURFACE_VARIANT,
                fontName='Helvetica'
            )
        }
    
    def generate_report(self):
        """Generate working PDF report"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=25*mm,
            bottomMargin=25*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )
        
        story = []
        
        # Header
        story.extend(self._create_header())
        
        # Executive Summary
        story.extend(self._create_executive_summary())
        
        # Key Metrics
        story.extend(self._create_metrics_table())
        
        # Charts
        story.extend(self._create_charts())
        
        # Recent History
        story.extend(self._create_recent_history())
        
        # Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self):
        """Create professional header"""
        elements = []
        
        # Title
        title = Paragraph("🧠 Mood Analytics Report", self.styles['title'])
        elements.append(title)
        
        # Subtitle
        user_name = self.user.name if self.user and self.user.name else "User"
        date_str = datetime.now().strftime('%B %d, %Y')
        
        subtitle_text = f"Generated for <b>{user_name}</b> on {date_str}"
        subtitle = Paragraph(subtitle_text, self.styles['body'])
        subtitle.alignment = TA_CENTER
        elements.append(subtitle)
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_executive_summary(self):
        """Create executive summary"""
        if not self.moods:
            return [Paragraph("No mood data available for analysis.", self.styles['body'])]
        
        elements = []
        summary = self.analytics.get_summary()
        
        # Section header
        header = Paragraph("Executive Summary", self.styles['heading'])
        elements.append(header)
        
        # Analysis
        avg_mood = summary['daily_average']
        total_entries = summary['total_entries']
        streak = summary['current_streak']
        
        if avg_mood >= 5.5:
            assessment = "positive and stable"
            color = MD3_SUCCESS
        elif avg_mood >= 4.5:
            assessment = "generally balanced"
            color = MD3_WARNING
        else:
            assessment = "showing room for improvement"
            color = MD3_ERROR
        
        summary_text = f"""
        Based on <b>{total_entries}</b> mood entries, your emotional well-being is <b>{assessment}</b> 
        with an average rating of <b>{avg_mood:.1f}/7.0</b>. 
        
        You currently have a <b>{streak}-day</b> positive mood streak.
        
        <b>Data Quality:</b> {"Excellent" if total_entries > 20 else "Good" if total_entries > 10 else "Limited"} 
        tracking consistency.
        """
        
        summary_para = Paragraph(summary_text, self.styles['body'])
        elements.append(summary_para)
        elements.append(Spacer(1, 16))
        
        return elements
    
    def _create_metrics_table(self):
        """Create metrics table"""
        if not self.moods:
            return []
        
        elements = []
        summary = self.analytics.get_summary()
        
        # Section header
        header = Paragraph("Key Metrics", self.styles['heading'])
        elements.append(header)
        
        # Create table data
        data = [
            ['Metric', 'Value', 'Status'],
            ['Total Entries', str(summary['total_entries']), 'Active'],
            ['Average Mood', f"{summary['daily_average']:.1f}/7.0", 
             'Good' if summary['daily_average'] >= 5 else 'Fair'],
            ['Current Streak', f"{summary['current_streak']} days", 
             'Strong' if summary['current_streak'] > 7 else 'Building'],
            ['Best Day', summary['best_day'], 'Identified']
        ]
        
        # Create table
        table = Table(data, colWidths=[60*mm, 40*mm, 30*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), MD3_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F9FA'), HexColor('#FFFFFF')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_charts(self):
        """Create charts section"""
        if not self.moods:
            return []
        
        elements = []
        
        # Section header
        header = Paragraph("Mood Analysis Charts", self.styles['heading'])
        elements.append(header)
        
        # Mood distribution chart
        dist_chart = self._create_mood_distribution_chart()
        if dist_chart:
            chart_title = Paragraph("Mood Distribution (Last 30 Days)", self.styles['subheading'])
            elements.append(chart_title)
            elements.append(Image(dist_chart, width=6*inch, height=4*inch))
            elements.append(Spacer(1, 16))
        
        # Weekly patterns chart
        weekly_chart = self._create_weekly_patterns_chart()
        if weekly_chart:
            chart_title = Paragraph("Weekly Mood Patterns", self.styles['subheading'])
            elements.append(chart_title)
            elements.append(Image(weekly_chart, width=6*inch, height=3*inch))
            elements.append(Spacer(1, 16))
        
        return elements
    
    def _create_mood_distribution_chart(self):
        """Create working mood distribution chart"""
        try:
            # Get last 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            recent_moods = []
            
            for mood in self.moods:
                mood_date = mood['date']
                if isinstance(mood_date, str):
                    mood_date = datetime.fromisoformat(mood_date).date()
                elif hasattr(mood_date, 'date'):
                    mood_date = mood_date.date()
                
                if mood_date >= thirty_days_ago:
                    recent_moods.append(mood)
            
            if not recent_moods:
                return None
            
            # Count moods
            mood_counts = Counter(mood['mood'] for mood in recent_moods)
            
            # Colors
            colors = {
                'very bad': '#BA1A1A', 'bad': '#D32F2F', 'slightly bad': '#FF9800',
                'neutral': '#79747E', 'slightly well': '#8BC34A', 
                'well': '#4CAF50', 'very well': '#6750A4'
            }
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
            
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            chart_colors = [colors.get(mood, '#79747E') for mood in moods]
            
            wedges, texts, autotexts = ax.pie(
                counts, 
                labels=[mood.title() for mood in moods],
                colors=chart_colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            ax.set_title('Mood Distribution (Last 30 Days)', 
                        fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Save chart
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_file.name
            
        except Exception as e:
            print(f"Chart error: {e}")
            return None
    
    def _create_weekly_patterns_chart(self):
        """Create working weekly patterns chart"""
        try:
            weekly_data = self.analytics.get_weekly_patterns()
            
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
            
            ax.plot(weekly_data['labels'], weekly_data['data'], 
                   marker='o', linewidth=3, markersize=8, 
                   color='#6750A4', markerfacecolor='#6750A4')
            
            ax.fill_between(weekly_data['labels'], weekly_data['data'], 
                           alpha=0.3, color='#6750A4')
            
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12)
            ax.set_title('Weekly Mood Patterns', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_file.name
            
        except Exception as e:
            print(f"Weekly chart error: {e}")
            return None
    
    def _create_recent_history(self):
        """Create recent history table"""
        if not self.moods:
            return []
        
        elements = []
        
        # Section header
        header = Paragraph("Recent Mood History", self.styles['heading'])
        elements.append(header)
        
        # Create table data
        data = [['Date', 'Mood', 'Rating', 'Notes']]
        
        mood_emoji = {
            'very bad': '😭', 'bad': '😢', 'slightly bad': '😔', 'neutral': '😐',
            'slightly well': '🙂', 'well': '😊', 'very well': '😄'
        }
        
        for mood_entry in self.moods[:10]:  # Last 10 entries
            date_str = str(mood_entry['date'])
            mood = mood_entry['mood']
            rating = MOOD_VALUES.get(mood, 4)
            notes = mood_entry.get('notes', 'No notes')[:50]
            
            emoji = mood_emoji.get(mood, '😐')
            mood_display = f"{emoji} {mood.title()}"
            
            data.append([date_str, mood_display, f"{rating}/7", notes])
        
        # Create table
        table = Table(data, colWidths=[30*mm, 50*mm, 20*mm, 70*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), MD3_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F9FA'), HexColor('#FFFFFF')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self):
        """Create footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = f"""
        Generated by Mood Tracker • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        Material Design 3 • Professional Analytics Report
        """
        
        footer = Paragraph(footer_text, self.styles['small'])
        footer.alignment = TA_CENTER
        elements.append(footer)
        
        return elements
