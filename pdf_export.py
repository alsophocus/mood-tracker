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
        """Create enhanced Material Design 3 header with professional branding"""
        header_elements = []
        
        # Professional header with branding
        user_name = self.user.name if self.user and self.user.name else "User"
        generation_date = datetime.now().strftime('%B %d, %Y')
        generation_time = datetime.now().strftime('%H:%M')
        
        # Main title with enhanced styling
        title_html = f"""
        <para align="center" spaceAfter="12">
        <font size="48" color="{MD3_COLORS['primary']}"><b>🧠 Mood Analytics</b></font><br/>
        <font size="24" color="{MD3_COLORS['on_surface']}"><b>Professional Report</b></font>
        </para>
        """
        title = Paragraph(title_html, self.typography['display_large'])
        header_elements.append(title)
        
        # Professional metadata card
        metadata_html = f"""
        <table width="100%" style="background-color: {MD3_COLORS['surface_container']}; border-radius: 12px;">
        <tr>
        <td width="50%" align="left" valign="top">
        <font color="{MD3_COLORS['primary']}" size="12"><b>Report Details</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="11">Generated for: <b>{user_name}</b></font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="10">Report Date: {generation_date}</font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="10">Generated at: {generation_time}</font>
        </td>
        <td width="50%" align="right" valign="top">
        <font color="{MD3_COLORS['secondary']}" size="12"><b>Analytics Summary</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="11">Total Entries: <b>{len(self.moods)}</b></font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="10">Period: Last 30 days</font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="10">Format: Material Design 3</font>
        </td>
        </tr>
        </table>
        """
        
        metadata = Paragraph(metadata_html, self.typography['body_medium'])
        header_elements.append(metadata)
        header_elements.append(Spacer(1, 24))
        
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
        """Create mood distribution pie chart with enhanced MD3 styling"""
        try:
            from datetime import datetime, timedelta
            from collections import Counter
            
            # Get last 30 days of moods
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
            
            # Count mood occurrences
            mood_counts = Counter(mood['mood'] for mood in recent_moods)
            
            # Enhanced MD3 color palette for moods
            mood_color_map = {
                'very bad': '#BA1A1A',     # MD3 Error
                'bad': '#D32F2F',          # Error variant
                'slightly bad': '#FF9800', # Warning
                'neutral': '#79747E',      # MD3 Outline
                'slightly well': '#8BC34A', # Success variant
                'well': '#4CAF50',         # Success
                'very well': '#6750A4'     # MD3 Primary
            }
            
            # Prepare data
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            colors = [mood_color_map.get(mood, '#79747E') for mood in moods]
            
            # Create enhanced pie chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), facecolor='#FFFBFE')
            
            # Main pie chart
            wedges, texts, autotexts = ax1.pie(counts, labels=None, colors=colors, 
                                              autopct='%1.1f%%', startangle=90,
                                              textprops={'fontsize': 10, 'color': 'white', 'weight': 'bold'},
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            
            ax1.set_title('Mood Distribution\n(Last 30 Days)', 
                         fontsize=16, fontweight='bold', color='#6750A4', pad=20)
            
            # Enhanced legend
            ax2.axis('off')
            legend_y = 0.9
            ax2.text(0.1, 0.95, 'Legend', fontsize=14, fontweight='bold', color='#6750A4')
            
            for mood, count, color in zip(moods, counts, colors):
                percentage = (count / sum(counts)) * 100
                # Create colored square
                ax2.add_patch(plt.Rectangle((0.1, legend_y-0.05), 0.08, 0.08, 
                                          facecolor=color, edgecolor='white', linewidth=1))
                # Add text
                ax2.text(0.25, legend_y, f'{mood.title()}', fontsize=11, 
                        color='#1C1B1F', va='center')
                ax2.text(0.7, legend_y, f'{count} ({percentage:.1f}%)', fontsize=10, 
                        color='#49454F', va='center')
                legend_y -= 0.12
            
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='#FFFBFE', edgecolor='none')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_md3_weekly_chart(self):
        """Create enhanced weekly patterns chart with trend analysis"""
        try:
            weekly_data = self.analytics.get_weekly_patterns()
            
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#FFFBFE')
            
            # Enhanced styling
            primary_color = '#6750A4'
            data_points = weekly_data['data']
            labels = weekly_data['labels']
            
            # Main line with enhanced styling
            line = ax.plot(labels, data_points, marker='o', linewidth=4, markersize=10, 
                          color=primary_color, markerfacecolor=primary_color, 
                          markeredgecolor='white', markeredgewidth=3, zorder=3)
            
            # Fill area with gradient effect
            ax.fill_between(labels, data_points, alpha=0.15, color=primary_color, zorder=1)
            
            # Add trend annotations
            max_mood = max(data_points)
            min_mood = min(data_points)
            max_day = labels[data_points.index(max_mood)]
            min_day = labels[data_points.index(min_mood)]
            
            # Highlight best and worst days
            ax.scatter([max_day], [max_mood], color='#4CAF50', s=150, 
                      marker='^', edgecolor='white', linewidth=2, zorder=4, label='Best Day')
            ax.scatter([min_day], [min_mood], color='#FF5722', s=150, 
                      marker='v', edgecolor='white', linewidth=2, zorder=4, label='Needs Attention')
            
            # Add annotations
            ax.annotate(f'Peak: {max_mood:.1f}', xy=(max_day, max_mood), 
                       xytext=(10, 20), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#4CAF50', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color='#4CAF50'),
                       fontsize=9, color='white', weight='bold')
            
            # Chart styling
            ax.set_ylim(1, 7)
            ax.set_ylabel('Average Mood', fontsize=12, color='#1C1B1F', weight='bold')
            ax.set_title('Weekly Mood Patterns', fontsize=16, fontweight='bold', 
                        color=primary_color, pad=25)
            
            # Enhanced grid
            ax.grid(True, alpha=0.3, color='#79747E', linestyle='--', linewidth=0.8)
            ax.set_facecolor('#F8F9FA')
            
            # Mood level indicators
            mood_levels = ['Very Bad', 'Bad', 'Slightly Bad', 'Neutral', 'Slightly Well', 'Well', 'Very Well']
            for i, level in enumerate(mood_levels, 1):
                ax.axhline(y=i, color='#E0E0E0', linestyle=':', alpha=0.5, zorder=0)
                ax.text(len(labels)-0.5, i, level, fontsize=8, color='#666', 
                       ha='left', va='center', alpha=0.7)
            
            # Style axes
            ax.tick_params(colors='#49454F', labelsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#CAB6CF')
            ax.spines['bottom'].set_color('#CAB6CF')
            
            # Add legend
            ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
                     facecolor='white', edgecolor='#CAB6CF')
            
            plt.xticks(rotation=45, ha='right')
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
        """Create enhanced Material Design 3 footer with professional branding"""
        footer_html = f"""
        <table width="100%" style="border-top: 2px solid {MD3_COLORS['outline_variant']};">
        <tr>
        <td width="33%" align="left">
        <font color="{MD3_COLORS['primary']}" size="10"><b>🧠 Mood Tracker</b></font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="8">Professional Analytics Platform</font>
        </td>
        <td width="34%" align="center">
        <font color="{MD3_COLORS['on_surface_variant']}" size="9">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        Material Design 3 • Premium Report
        </font>
        </td>
        <td width="33%" align="right">
        <font color="{MD3_COLORS['secondary']}" size="9"><b>Confidential</b></font><br/>
        <font color="{MD3_COLORS['on_surface_variant']}" size="8">Personal Analytics Report</font>
        </td>
        </tr>
        </table>
        """
        
        footer_para = Paragraph(footer_html, self.typography['body_medium'])
        
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
