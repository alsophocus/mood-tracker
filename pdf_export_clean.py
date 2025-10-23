import io
import tempfile
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analytics import MoodAnalytics, MOOD_VALUES

class PDFExporter:
    def __init__(self, user, moods):
        self.user = user
        self.moods = moods
        self.analytics = MoodAnalytics(moods)
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create consistent professional styles"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=HexColor('#1a365d')
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=HexColor('#2d3748')
            ),
            'body': ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                textColor=HexColor('#4a5568')
            ),
            'metric': ParagraphStyle(
                'Metric',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                textColor=HexColor('#2d3748')
            )
        }
        
        return custom_styles
    
    def generate_report(self):
        """Generate clean, professional PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, bottomMargin=30*mm, 
                               leftMargin=25*mm, rightMargin=25*mm)
        
        story = []
        story.extend(self._create_header())
        story.extend(self._create_summary())
        story.extend(self._create_charts())
        story.extend(self._create_recent_entries())
        story.extend(self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self):
        """Create professional header"""
        elements = []
        
        # Title
        title = Paragraph("Mood Analytics Report", self.styles['title'])
        elements.append(title)
        
        # User info
        user_name = self.user.name if self.user and self.user.name else "User"
        date_str = datetime.now().strftime('%B %d, %Y')
        
        info_text = f"<b>Generated for:</b> {user_name}<br/><b>Report Date:</b> {date_str}"
        info = Paragraph(info_text, self.styles['body'])
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_summary(self):
        """Create clean summary section"""
        if not self.moods:
            return [Paragraph("No mood data available.", self.styles['body'])]
        
        elements = []
        summary = self.analytics.get_summary()
        
        # Section heading
        heading = Paragraph("Summary", self.styles['heading'])
        elements.append(heading)
        
        # Metrics table
        data = [
            ['Metric', 'Value'],
            ['Total Entries', str(summary['total_entries'])],
            ['Current Streak', f"{summary['current_streak']} days"],
            ['Best Day', summary['best_day']],
            ['Average Mood', f"{summary['daily_average']:.1f}/7.0"]
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_charts(self):
        """Create charts section"""
        if not self.moods:
            return []
        
        elements = []
        
        # Charts heading
        heading = Paragraph("Mood Analysis", self.styles['heading'])
        elements.append(heading)
        
        # Mood distribution chart
        chart_path = self._create_clean_chart()
        if chart_path:
            elements.append(Image(chart_path, width=5*inch, height=3*inch))
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_clean_chart(self):
        """Create clean, professional chart"""
        try:
            from datetime import datetime, timedelta
            from collections import Counter
            
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
                return None
            
            # Count moods
            mood_counts = Counter(mood['mood'] for mood in recent_moods)
            
            # Professional colors
            colors = ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5', '#dd6b20', '#319795']
            
            # Create clean pie chart
            fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')
            
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            
            wedges, texts, autotexts = ax.pie(counts, labels=[m.title() for m in moods], 
                                            colors=colors[:len(moods)], autopct='%1.1f%%',
                                            startangle=90, textprops={'fontsize': 10})
            
            ax.set_title('Mood Distribution (Last 30 Days)', fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_file.name
        except Exception:
            return None
    
    def _create_recent_entries(self):
        """Create recent entries section"""
        if not self.moods:
            return []
        
        elements = []
        
        # Section heading
        heading = Paragraph("Recent Entries", self.styles['heading'])
        elements.append(heading)
        
        # Recent entries table
        data = [['Date', 'Mood', 'Notes']]
        
        for mood_entry in self.moods[:10]:
            date_str = str(mood_entry['date'])
            mood = mood_entry['mood'].title()
            notes = mood_entry.get('notes', '')[:50] + ('...' if len(mood_entry.get('notes', '')) > 50 else '')
            data.append([date_str, mood, notes or 'No notes'])
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self):
        """Create simple footer"""
        footer_text = f"Generated by Mood Tracker on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        footer = Paragraph(footer_text, ParagraphStyle('Footer', fontSize=9, 
                          textColor=HexColor('#718096'), alignment=TA_CENTER))
        
        return [Spacer(1, 30), footer]
