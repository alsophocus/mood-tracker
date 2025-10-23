import io
import tempfile
from datetime import datetime, timedelta
from collections import Counter
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from analytics import MoodAnalytics, MOOD_VALUES

# Set modern color palette
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class BeautifulPDFExporter:
    def __init__(self, user, moods):
        self.user = user
        self.moods = moods
        self.analytics = MoodAnalytics(moods)
        
        # Modern color palette
        self.colors = {
            'primary': HexColor('#667eea'),
            'secondary': HexColor('#764ba2'),
            'accent': HexColor('#f093fb'),
            'success': HexColor('#4facfe'),
            'warning': HexColor('#43e97b'),
            'text_dark': HexColor('#2d3748'),
            'text_light': HexColor('#718096'),
            'background': HexColor('#f7fafc'),
            'white': HexColor('#ffffff')
        }
        
        self.styles = self._create_modern_styles()
    
    def _create_modern_styles(self):
        """Create beautiful, modern typography styles"""
        return {
            'title': ParagraphStyle(
                'ModernTitle',
                fontName='Helvetica-Bold',
                fontSize=32,
                leading=38,
                textColor=self.colors['primary'],
                alignment=TA_CENTER,
                spaceAfter=8*mm
            ),
            'subtitle': ParagraphStyle(
                'ModernSubtitle',
                fontName='Helvetica',
                fontSize=14,
                leading=18,
                textColor=self.colors['text_light'],
                alignment=TA_CENTER,
                spaceAfter=12*mm
            ),
            'section_title': ParagraphStyle(
                'SectionTitle',
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=self.colors['text_dark'],
                spaceBefore=8*mm,
                spaceAfter=6*mm
            ),
            'body': ParagraphStyle(
                'ModernBody',
                fontName='Helvetica',
                fontSize=11,
                leading=16,
                textColor=self.colors['text_dark'],
                spaceAfter=4*mm,
                alignment=TA_JUSTIFY
            ),
            'metric_value': ParagraphStyle(
                'MetricValue',
                fontName='Helvetica-Bold',
                fontSize=24,
                leading=28,
                textColor=self.colors['primary'],
                alignment=TA_CENTER
            ),
            'metric_label': ParagraphStyle(
                'MetricLabel',
                fontName='Helvetica',
                fontSize=10,
                leading=12,
                textColor=self.colors['text_light'],
                alignment=TA_CENTER
            )
        }
    
    def generate_report(self):
        """Generate beautiful, modern PDF report"""
        buffer = io.BytesIO()
        
        # Custom page template with proper margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=25*mm,
            bottomMargin=25*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )
        
        story = []
        story.extend(self._create_beautiful_header())
        story.extend(self._create_metrics_cards())
        story.extend(self._create_beautiful_charts())
        story.extend(self._create_insights_section())
        story.extend(self._create_elegant_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_beautiful_header(self):
        """Create stunning header with gradient effect"""
        elements = []
        
        # Main title
        title = Paragraph("Mood Analytics", self.styles['title'])
        elements.append(title)
        
        # Elegant subtitle
        user_name = self.user.name if self.user and self.user.name else "User"
        date_str = datetime.now().strftime('%B %d, %Y')
        
        subtitle_text = f"Personal Insights Report for {user_name} • {date_str}"
        subtitle = Paragraph(subtitle_text, self.styles['subtitle'])
        elements.append(subtitle)
        
        return elements
    
    def _create_metrics_cards(self):
        """Create beautiful metric cards without stretching"""
        if not self.moods:
            return []
        
        elements = []
        summary = self.analytics.get_summary()
        
        # Section title
        section_title = Paragraph("Key Metrics", self.styles['section_title'])
        elements.append(section_title)
        
        # Create 2x2 grid of metrics with fixed widths
        metrics_data = [
            [
                self._create_metric_cell("Total Entries", str(summary['total_entries'])),
                self._create_metric_cell("Current Streak", f"{summary['current_streak']} days")
            ],
            [
                self._create_metric_cell("Best Day", summary['best_day']),
                self._create_metric_cell("Average Mood", f"{summary['daily_average']:.1f}/7")
            ]
        ]
        
        # Fixed column widths to prevent stretching
        metrics_table = Table(metrics_data, colWidths=[8*cm, 8*cm], rowHeights=[3*cm, 3*cm])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _create_metric_cell(self, label, value):
        """Create individual metric cell with beautiful styling"""
        cell_content = f"""
        <para align="center">
        <font name="Helvetica-Bold" size="24" color="#667eea">{value}</font><br/>
        <font name="Helvetica" size="10" color="#718096">{label}</font>
        </para>
        """
        return Paragraph(cell_content, self.styles['body'])
    
    def _create_beautiful_charts(self):
        """Create stunning, modern charts"""
        if not self.moods:
            return []
        
        elements = []
        
        # Section title
        section_title = Paragraph("Mood Analysis", self.styles['section_title'])
        elements.append(section_title)
        
        # Create beautiful charts
        chart_paths = self._create_modern_charts()
        
        for chart_path in chart_paths:
            if chart_path:
                # Fixed size to prevent stretching
                elements.append(Image(chart_path, width=16*cm, height=10*cm))
                elements.append(Spacer(1, 6*mm))
        
        return elements
    
    def _create_modern_charts(self):
        """Create beautiful, modern charts with proper styling"""
        chart_paths = []
        
        try:
            # Get recent moods
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
                return []
            
            # Modern color palette
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#38ef7d', '#ff9a9e']
            
            # Create beautiful donut chart
            mood_counts = Counter(mood['mood'] for mood in recent_moods)
            
            fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
            
            # Create donut chart (more modern than pie)
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            
            wedges, texts, autotexts = ax.pie(
                counts, 
                labels=[m.replace('_', ' ').title() for m in moods],
                colors=colors[:len(moods)],
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
                textprops={'fontsize': 11, 'fontweight': 'bold'}
            )
            
            # Beautiful styling
            ax.set_title('Mood Distribution (Last 30 Days)', 
                        fontsize=18, fontweight='bold', pad=30, color='#2d3748')
            
            # Add center circle for donut effect
            centre_circle = plt.Circle((0,0), 0.35, fc='white', linewidth=2, edgecolor='#e2e8f0')
            ax.add_artist(centre_circle)
            
            # Add total in center
            total_entries = sum(counts)
            ax.text(0, 0, f'{total_entries}\nEntries', ha='center', va='center', 
                   fontsize=16, fontweight='bold', color='#4a5568')
            
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            chart_paths.append(chart_file.name)
            
        except Exception as e:
            print(f"Chart error: {e}")
        
        return chart_paths
    
    def _create_insights_section(self):
        """Create beautiful insights section"""
        if not self.moods:
            return []
        
        elements = []
        
        # Section title
        section_title = Paragraph("Insights & Recommendations", self.styles['section_title'])
        elements.append(section_title)
        
        # Generate insights
        summary = self.analytics.get_summary()
        insights = self._generate_insights(summary)
        
        for insight in insights:
            insight_text = f"• {insight}"
            insight_para = Paragraph(insight_text, self.styles['body'])
            elements.append(insight_para)
        
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _generate_insights(self, summary):
        """Generate personalized insights"""
        insights = []
        avg_mood = summary['daily_average']
        
        if avg_mood >= 5.5:
            insights.append("Your mood levels show a consistently positive trend. Keep up the great work!")
        elif avg_mood >= 4.5:
            insights.append("Your mood levels are well-balanced. Consider identifying what contributes to your higher mood days.")
        else:
            insights.append("Focus on activities that boost your mood. Consider tracking specific triggers.")
        
        if summary['current_streak'] > 7:
            insights.append(f"Excellent! You've maintained a {summary['current_streak']}-day positive streak.")
        
        if summary['best_day']:
            insights.append(f"{summary['best_day']} appears to be your strongest day of the week.")
        
        return insights[:3]
    
    def _create_elegant_footer(self):
        """Create elegant footer"""
        footer_text = f"Generated by Mood Tracker • {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        footer = Paragraph(footer_text, ParagraphStyle(
            'Footer',
            fontName='Helvetica',
            fontSize=9,
            textColor=self.colors['text_light'],
            alignment=TA_CENTER
        ))
        
        return [Spacer(1, 15*mm), footer]
