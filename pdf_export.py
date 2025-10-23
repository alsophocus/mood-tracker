import io
import tempfile
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analytics import MoodAnalytics, MOOD_VALUES
from pdf_md3_styles import MD3PDFComponents, MD3_COLORS, create_md3_typography, LAYOUT_GRID

class PDFExporter:
    def __init__(self, user, moods):
        self.user = user
        self.moods = moods
        self.analytics = MoodAnalytics(moods)
        self.md3 = MD3PDFComponents()
        self.typography = create_md3_typography()
    
    def generate_report(self):
        """Generate comprehensive PDF report with Material Design 3 styling"""
        buffer = io.BytesIO()
        
        # Use A4 page size for international standard
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=LAYOUT_GRID['margin_top'],
            bottomMargin=LAYOUT_GRID['margin_bottom'],
            leftMargin=LAYOUT_GRID['margin_left'],
            rightMargin=LAYOUT_GRID['margin_right']
        )
        
        story = []
        story.extend(self._create_md3_header())
        story.extend(self._create_md3_summary())
        story.extend(self._create_md3_charts())
        story.extend(self._create_md3_recent_history())
        story.extend(self._create_md3_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_md3_header(self):
        """Create Material Design 3 styled header"""
        header_elements = []
        
        # Main title with MD3 Display Large typography
        title_text = "🧠 Mood Analytics Report"
        title = Paragraph(title_text, self.typography['display_large'])
        header_elements.append(title)
        
        # Subtitle with user info and generation date
        user_name = self.user.name if self.user and self.user.name else "User"
        generation_date = datetime.now().strftime('%B %d, %Y at %H:%M')
        
        subtitle_text = f"""
        <font color="{MD3_COLORS['primary']}"><b>Generated for:</b></font> {user_name}<br/>
        <font color="{MD3_COLORS['on_surface_variant']}"><b>Report Date:</b></font> {generation_date}
        """
        
        subtitle = Paragraph(subtitle_text, self.typography['body_large'])
        header_elements.append(subtitle)
        header_elements.append(Spacer(1, 20))
        
        return header_elements
    
    def _create_md3_summary(self):
        """Create summary section with Material Design 3 grid layout"""
        if not self.moods:
            return [Paragraph("No mood data available yet.", self.typography['body_large'])]
        
        summary_elements = []
        summary = self.analytics.get_summary()
        
        # Section header
        section_title = Paragraph("📊 Analytics Overview", self.typography['headline_large'])
        summary_elements.append(section_title)
        summary_elements.append(Spacer(1, 16))
        
        # Create metrics in 2x2 grid layout
        metrics = [
            {
                'label': 'Total Entries',
                'value': str(summary['total_entries']),
                'color': MD3_COLORS['primary'],
                'icon': '📈'
            },
            {
                'label': 'Current Streak',
                'value': f"{summary['current_streak']} days",
                'color': MD3_COLORS['secondary'],
                'icon': '🔥'
            },
            {
                'label': 'Best Day',
                'value': summary['best_day'],
                'color': MD3_COLORS['primary'],
                'icon': '⭐'
            },
            {
                'label': 'Average Mood',
                'value': f"{summary['daily_average']:.1f}/7.0",
                'color': MD3_COLORS['secondary'],
                'icon': '📊'
            }
        ]
        
        # Create 2x2 grid of metric cards
        for i in range(0, len(metrics), 2):
            row_elements = []
            for j in range(2):
                if i + j < len(metrics):
                    metric = metrics[i + j]
                    metric_text = f"""
                    <para align="center">
                    <font size="24">{metric['icon']}</font><br/>
                    <font color="{metric['color']}" size="20"><b>{metric['value']}</b></font><br/>
                    <font color="{MD3_COLORS['on_surface_variant']}" size="11">{metric['label']}</font>
                    </para>
                    """
                    metric_para = Paragraph(metric_text, self.typography['body_medium'])
                    row_elements.append(metric_para)
            
            # Add row with proper spacing
            if len(row_elements) == 2:
                # Create side-by-side layout using table-like structure
                combined_text = f"""
                <table width="100%">
                <tr>
                <td width="50%" align="center">
                <font size="24">{metrics[i]['icon']}</font><br/>
                <font color="{metrics[i]['color']}" size="20"><b>{metrics[i]['value']}</b></font><br/>
                <font color="{MD3_COLORS['on_surface_variant']}" size="11">{metrics[i]['label']}</font>
                </td>
                <td width="50%" align="center">
                <font size="24">{metrics[i+1]['icon']}</font><br/>
                <font color="{metrics[i+1]['color']}" size="20"><b>{metrics[i+1]['value']}</b></font><br/>
                <font color="{MD3_COLORS['on_surface_variant']}" size="11">{metrics[i+1]['label']}</font>
                </td>
                </tr>
                </table>
                """
                combined_para = Paragraph(combined_text, self.typography['body_medium'])
                summary_elements.append(combined_para)
            else:
                summary_elements.extend(row_elements)
            
            summary_elements.append(Spacer(1, 12))
        
        summary_elements.append(Spacer(1, 24))
        return summary_elements
    
    def _create_md3_charts(self):
        """Create charts section with Material Design 3 grid layout"""
        if not self.moods:
            return []
        
        story = []
        
        # Charts section header with divider
        charts_title = Paragraph("📈 Mood Analytics", self.typography['headline_large'])
        story.append(charts_title)
        story.append(Spacer(1, 8))
        
        # Add section description
        description_text = f"""
        <font color="{MD3_COLORS['on_surface_variant']}" size="12">
        Comprehensive analysis of your mood patterns and trends over time.
        </font>
        """
        description = Paragraph(description_text, self.typography['body_medium'])
        story.append(description)
        story.append(Spacer(1, 16))
        
        # Mood distribution chart (full width)
        distribution_chart_path = self._create_md3_mood_distribution_chart()
        if distribution_chart_path:
            chart_title = Paragraph("🎯 Mood Distribution (Last 30 Days)", self.typography['title_large'])
            story.append(KeepTogether([
                chart_title,
                Spacer(1, 8),
                Image(distribution_chart_path, width=6*inch, height=3.5*inch)
            ]))
            story.append(Spacer(1, 20))
        
        # Weekly patterns chart (full width)
        weekly_chart_path = self._create_md3_weekly_chart()
        if weekly_chart_path:
            chart_title = Paragraph("📅 Weekly Patterns", self.typography['title_large'])
            story.append(KeepTogether([
                chart_title,
                Spacer(1, 8),
                Image(weekly_chart_path, width=6*inch, height=3*inch)
            ]))
            story.append(Spacer(1, 20))
        
        # Add insights section
        insights_title = Paragraph("💡 Key Insights", self.typography['title_large'])
        story.append(insights_title)
        story.append(Spacer(1, 8))
        
        # Generate insights based on data
        insights = self._generate_mood_insights(self.analytics.get_summary())
        for insight in insights:
            insight_text = f"""
            <font color="{MD3_COLORS['primary']}">•</font> 
            <font color="{MD3_COLORS['on_surface']}">{insight}</font>
            """
            insight_para = Paragraph(insight_text, self.typography['body_medium'])
            story.append(insight_para)
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 16))
        return story
    
    def _generate_mood_insights(self, summary):
        """Generate insights based on mood data"""
        insights = []
        
        if summary['total_entries'] > 0:
            avg_mood = summary['daily_average']
            if avg_mood >= 5.5:
                insights.append("Your overall mood trend is positive with an above-average rating.")
            elif avg_mood >= 4.5:
                insights.append("Your mood levels are generally balanced and stable.")
            else:
                insights.append("Consider focusing on activities that boost your mood.")
        
        if summary['current_streak'] > 7:
            insights.append(f"Excellent! You've maintained a {summary['current_streak']}-day positive mood streak.")
        elif summary['current_streak'] > 3:
            insights.append(f"Good progress with a {summary['current_streak']}-day positive streak.")
        
        if summary['best_day']:
            insights.append(f"{summary['best_day']} appears to be your most positive day of the week.")
        
        if not insights:
            insights.append("Continue tracking your mood to discover meaningful patterns.")
        
        return insights[:3]  # Limit to 3 insights
    
    def _create_md3_mood_distribution_chart(self):
        """Create mood distribution pie chart with Material Design 3 colors"""
        try:
            from datetime import datetime, timedelta
            from collections import Counter
            
            # Get last 30 days of moods
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            recent_moods = []
            for mood in self.moods:
                mood_date = mood['date']
                # Handle both string and date objects
                if isinstance(mood_date, str):
                    mood_date = datetime.fromisoformat(mood_date).date()
                elif hasattr(mood_date, 'date'):
                    mood_date = mood_date.date()
                
                if mood_date >= thirty_days_ago:
                    recent_moods.append(mood)
            
            if not recent_moods:
                return None
            
            # Count mood occurrences
            mood_counts = Counter(mood['mood'] for mood in recent_moods)
            
            # MD3 color palette for moods
            md3_mood_colors = self.md3.get_chart_colors()
            mood_color_map = {
                'very bad': '#BA1A1A',     # Error
                'bad': '#FF5722',          # Error variant
                'slightly bad': '#FF9800', # Warning
                'neutral': '#79747E',      # Outline
                'slightly well': '#8BC34A', # Success variant
                'well': '#4CAF50',         # Success
                'very well': '#6750A4'     # Primary
            }
            
            # Prepare data
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            colors = [mood_color_map.get(mood, '#79747E') for mood in moods]
            
            # Create pie chart with MD3 styling
            fig, ax = plt.subplots(figsize=(8, 6), facecolor='#FFFBFE')  # MD3 surface
            wedges, texts, autotexts = ax.pie(counts, labels=[mood.title() for mood in moods], 
                                            colors=colors, autopct='%1.1f%%', startangle=90,
                                            textprops={'fontsize': 11, 'color': '#1C1B1F'})
            
            # MD3 styling
            ax.set_title('Mood Distribution (Last 30 Days)', 
                        fontsize=16, fontweight='bold', color='#6750A4', pad=20)
            
            # Style percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='#FFFBFE', edgecolor='none')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_md3_weekly_chart(self):
        """Create weekly patterns chart with Material Design 3 styling"""
        try:
            weekly_data = self.analytics.get_weekly_patterns()
            
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#FFFBFE')  # MD3 surface
            
            # MD3 primary color for the line
            primary_color = '#6750A4'
            ax.plot(weekly_data['labels'], weekly_data['data'], 
                   marker='o', linewidth=3, markersize=8, 
                   color=primary_color, markerfacecolor=primary_color, 
                   markeredgecolor='white', markeredgewidth=2)
            
            # MD3 primary container for fill
            ax.fill_between(weekly_data['labels'], weekly_data['data'], 
                           alpha=0.2, color=primary_color)
            
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#1C1B1F')  # MD3 on-surface
            ax.set_title('Weekly Patterns', fontsize=16, fontweight='bold', 
                        color=primary_color, pad=20)
            
            # MD3 grid styling
            ax.grid(True, alpha=0.2, color='#79747E')  # MD3 outline
            ax.set_facecolor('#F3EDF7')  # MD3 surface-container
            
            # MD3 text styling
            ax.tick_params(colors='#49454F')  # MD3 on-surface-variant
            plt.xticks(rotation=45, fontsize=10)
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='#FFFBFE', edgecolor='none')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_monthly_chart(self):
        """Create monthly trends chart"""
        try:
            monthly_data = self.analytics.get_monthly_trends()
            if not monthly_data:
                return None
            
            months = [item['month'] for item in monthly_data[-12:]]  # Last 12 months
            values = [item['mood'] for item in monthly_data[-12:]]
            
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='white')
            ax.plot(months, values, marker='o', linewidth=3, markersize=8,
                   color='#3b82f6', markerfacecolor='#3b82f6', 
                   markeredgecolor='white', markeredgewidth=2)
            ax.fill_between(months, values, alpha=0.3, color='#3b82f6')
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#374151')
            ax.set_title('Monthly Trends', fontsize=14, fontweight='bold', color='#1e293b', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8fafc')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_daily_patterns_chart(self):
        """Create daily patterns (hourly) chart"""
        try:
            daily_data = self.analytics.get_daily_patterns()
            
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='white')
            ax.plot(daily_data['labels'], daily_data['data'], marker='o', linewidth=3, 
                   markersize=6, color='#8b5cf6', markerfacecolor='#8b5cf6', 
                   markeredgecolor='white', markeredgewidth=2)
            ax.fill_between(daily_data['labels'], daily_data['data'], alpha=0.3, color='#8b5cf6')
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#374151')
            ax.set_xlabel('Hour of Day', fontsize=12, color='#374151')
            ax.set_title('Daily Patterns (Average Mood by Hour)', fontsize=14, fontweight='bold', color='#1e293b', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8fafc')
            plt.xticks(range(0, 24, 2))  # Show every 2 hours
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_md3_recent_history(self):
        """Create recent mood history section with Material Design 3 grid layout"""
        if not self.moods:
            return []
        
        story = []
        
        # Section header
        history_title = Paragraph("📝 Recent Mood History", self.typography['headline_large'])
        story.append(history_title)
        story.append(Spacer(1, 8))
        
        # Section description
        description_text = f"""
        <font color="{MD3_COLORS['on_surface_variant']}" size="12">
        Your most recent mood entries with notes and patterns.
        </font>
        """
        description = Paragraph(description_text, self.typography['body_medium'])
        story.append(description)
        story.append(Spacer(1, 16))
        
        mood_emoji = {
            'very bad': '😭', 'bad': '😢', 'slightly bad': '😔', 'neutral': '😐',
            'slightly well': '🙂', 'well': '😊', 'very well': '😄'
        }
        
        # Create entries in a structured format
        for i, mood_entry in enumerate(self.moods[:8]):  # Last 8 entries
            date_str = str(mood_entry['date'])
            mood = mood_entry['mood']
            notes = mood_entry.get('notes', '')
            
            # Create structured entry
            entry_html = f"""
            <table width="100%" style="border-bottom: 1px solid {MD3_COLORS['outline_variant']};">
            <tr>
            <td width="15%" align="center">
            <font size="20">{mood_emoji.get(mood, '😐')}</font>
            </td>
            <td width="25%">
            <font color="{MD3_COLORS['primary']}" size="12"><b>{date_str}</b></font>
            </td>
            <td width="25%">
            <font color="{MD3_COLORS['on_surface']}" size="11">{mood.title()}</font>
            </td>
            <td width="35%">
            """
            
            if notes:
                notes_text = notes[:50] + "..." if len(notes) > 50 else notes
                entry_html += f'<font color="{MD3_COLORS["on_surface_variant"]}" size="10"><i>{notes_text}</i></font>'
            else:
                entry_html += f'<font color="{MD3_COLORS["on_surface_variant"]}" size="10">No notes</font>'
            
            entry_html += """
            </td>
            </tr>
            </table>
            """
            
            entry_para = Paragraph(entry_html, self.typography['body_medium'])
            story.append(entry_para)
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 16))
        return story
    
    def _create_md3_footer(self):
        """Create Material Design 3 styled footer"""
        footer_text = f"""
        <font color="{MD3_COLORS['on_surface_variant']}" size="10">
        Generated by Mood Tracker • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        Material Design 3 • Professional Analytics Report
        </font>
        """
        
        footer_para = Paragraph(footer_text, self.typography['body_medium'])
        footer_para.alignment = TA_CENTER
        
        return [
            Spacer(1, 30),
            footer_para
        ]
    
    def _get_heading_style(self):
        """Get heading paragraph style"""
        return ParagraphStyle(
            'CustomHeading',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#3b82f6'),
            borderWidth=1,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=8,
            backColor=HexColor('#f8fafc')
        )
    
    def _get_body_style(self):
        """Get body paragraph style"""
        return ParagraphStyle(
            'CustomBody',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#374151')
        )
