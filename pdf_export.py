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
        story.extend(self._create_executive_summary())
        story.extend(self._create_md3_summary())
        story.extend(self._create_md3_charts())
        story.extend(self._create_trend_analysis())
        story.extend(self._create_md3_recent_history())
        story.extend(self._create_methodology())
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
        
    def _create_executive_summary(self):
        """Create executive summary with key insights and recommendations"""
        if not self.moods:
            return []
        
        summary_elements = []
        summary = self.analytics.get_summary()
        
        # Executive Summary Header
        header_html = f"""
        <table width="100%" style="background-color: {MD3_COLORS['primary_container']}; border-radius: 12px;">
        <tr>
        <td align="center" style="padding: 16px;">
        <font size="18" color="{MD3_COLORS['primary']}"><b>📋 Executive Summary</b></font><br/>
        <font size="11" color="{MD3_COLORS['on_surface_variant']}">Key findings and actionable insights from your mood data</font>
        </td>
        </tr>
        </table>
        """
        summary_elements.append(Paragraph(header_html, self.typography['headline_large']))
        summary_elements.append(Spacer(1, 16))
        
        # Generate insights
        avg_mood = summary['daily_average']
        total_entries = summary['total_entries']
        streak = summary['current_streak']
        
        # Key findings
        findings_html = f"""
        <table width="100%" cellpadding="12">
        <tr>
        <td width="50%" style="background-color: {MD3_COLORS['surface_container']}; border-radius: 8px;">
        <font color="{MD3_COLORS['primary']}" size="12"><b>📊 Overall Assessment</b></font><br/>
        """
        
        if avg_mood >= 5.5:
            findings_html += f'<font color="#4CAF50" size="11"><b>Positive Trend</b></font><br/>'
            findings_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Your mood levels show a consistently positive pattern with an average of {avg_mood:.1f}/7.0.</font>'
        elif avg_mood >= 4.5:
            findings_html += f'<font color="#FF9800" size="11"><b>Balanced State</b></font><br/>'
            findings_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Your mood levels are generally stable and balanced at {avg_mood:.1f}/7.0.</font>'
        else:
            findings_html += f'<font color="#F44336" size="11"><b>Needs Attention</b></font><br/>'
            findings_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Consider focusing on mood-boosting activities. Current average: {avg_mood:.1f}/7.0.</font>'
        
        findings_html += f"""
        </td>
        <td width="50%" style="background-color: {MD3_COLORS['surface_container']}; border-radius: 8px;">
        <font color="{MD3_COLORS['secondary']}" size="12"><b>🎯 Key Metrics</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="10">
        • <b>{total_entries}</b> total mood entries tracked<br/>
        • <b>{streak} days</b> current positive streak<br/>
        • <b>{summary['best_day']}</b> is your strongest day<br/>
        • Data spans the last <b>30 days</b>
        </font>
        </td>
        </tr>
        </table>
        """
        
        summary_elements.append(Paragraph(findings_html, self.typography['body_medium']))
        summary_elements.append(Spacer(1, 16))
        
        # Recommendations
        recommendations = self._generate_recommendations(summary)
        rec_html = f"""
        <font color="{MD3_COLORS['primary']}" size="14"><b>💡 Personalized Recommendations</b></font><br/>
        """
        
        for i, rec in enumerate(recommendations, 1):
            rec_html += f"""
            <font color="{MD3_COLORS['primary']}" size="11">•</font> 
            <font color="{MD3_COLORS['on_surface']}" size="11">{rec}</font><br/>
            """
        
        summary_elements.append(Paragraph(rec_html, self.typography['body_large']))
        summary_elements.append(Spacer(1, 24))
        
        return summary_elements
    
    def _generate_recommendations(self, summary):
        """Generate personalized recommendations based on mood data"""
        recommendations = []
        avg_mood = summary['daily_average']
        streak = summary['current_streak']
        
        if avg_mood >= 5.5:
            recommendations.append("Maintain your positive momentum by continuing current wellness practices.")
            recommendations.append("Consider sharing your successful strategies with others or documenting them.")
        elif avg_mood >= 4.5:
            recommendations.append("Focus on identifying patterns that lead to your higher mood days.")
            recommendations.append("Gradually introduce new mood-boosting activities to your routine.")
        else:
            recommendations.append("Prioritize self-care activities and consider professional support if needed.")
            recommendations.append("Track specific triggers and work on developing coping strategies.")
        
        if streak > 7:
            recommendations.append(f"Excellent work maintaining a {streak}-day positive streak!")
        elif streak > 0:
            recommendations.append("Build on your current positive momentum to extend your streak.")
        else:
            recommendations.append("Focus on small, achievable daily goals to build positive momentum.")
        
        if summary['best_day']:
            recommendations.append(f"Analyze what makes {summary['best_day']} successful and apply those elements to other days.")
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _create_md3_summary(self):
        """Create premium summary section with enhanced visual effects"""
        if not self.moods:
            return [Paragraph("No mood data available yet.", self.typography['body_large'])]
        
        summary_elements = []
        summary = self.analytics.get_summary()
        
        # Enhanced section header with gradient background
        section_html = f"""
        <table width="100%" style="background: linear-gradient(135deg, {MD3_COLORS['primary_container']}, {MD3_COLORS['surface_container']}); border-radius: 16px;">
        <tr>
        <td align="center" style="padding: 16px;">
        <font size="24" color="{MD3_COLORS['primary']}"><b>📊 Analytics Overview</b></font><br/>
        <font size="12" color="{MD3_COLORS['on_surface_variant']}">Comprehensive insights from your mood tracking data</font>
        </td>
        </tr>
        </table>
        """
        section_title = Paragraph(section_html, self.typography['headline_large'])
        summary_elements.append(section_title)
        summary_elements.append(Spacer(1, 20))
        
        # Premium metrics with enhanced styling
        metrics = [
            {
                'label': 'Total Entries',
                'value': str(summary['total_entries']),
                'color': MD3_COLORS['primary'],
                'icon': '📈',
                'description': 'Mood records tracked'
            },
            {
                'label': 'Current Streak',
                'value': f"{summary['current_streak']} days",
                'color': MD3_COLORS['secondary'],
                'icon': '🔥',
                'description': 'Consecutive positive days'
            },
            {
                'label': 'Best Day',
                'value': summary['best_day'],
                'color': MD3_COLORS['primary'],
                'icon': '⭐',
                'description': 'Highest average mood'
            },
            {
                'label': 'Average Mood',
                'value': f"{summary['daily_average']:.1f}/7.0",
                'color': MD3_COLORS['secondary'],
                'icon': '📊',
                'description': 'Overall mood rating'
            }
        ]
        
        # Create premium 2x2 grid with enhanced styling
        for i in range(0, len(metrics), 2):
            row_html = f"""
            <table width="100%" cellpadding="8" style="margin-bottom: 12px;">
            <tr>
            """
            
            for j in range(2):
                if i + j < len(metrics):
                    metric = metrics[i + j]
                    # Calculate mood quality indicator
                    if 'Average' in metric['label']:
                        avg_val = float(metric['value'].split('/')[0])
                        quality = "Excellent" if avg_val >= 6 else "Good" if avg_val >= 5 else "Fair" if avg_val >= 4 else "Needs Attention"
                        quality_color = "#4CAF50" if avg_val >= 6 else "#8BC34A" if avg_val >= 5 else "#FF9800" if avg_val >= 4 else "#F44336"
                    else:
                        quality = "Active"
                        quality_color = metric['color']
                    
                    row_html += f"""
                    <td width="50%" align="center" style="background-color: {MD3_COLORS['surface_container_high']}; border-radius: 16px; padding: 20px; margin: 4px;">
                    <font size="32">{metric['icon']}</font><br/>
                    <font color="{metric['color']}" size="24"><b>{metric['value']}</b></font><br/>
                    <font color="{MD3_COLORS['on_surface']}" size="13"><b>{metric['label']}</b></font><br/>
                    <font color="{MD3_COLORS['on_surface_variant']}" size="10">{metric['description']}</font><br/>
                    <font color="{quality_color}" size="9"><b>{quality}</b></font>
                    </td>
                    """
            
            row_html += """
            </tr>
            </table>
            """
            
            row_para = Paragraph(row_html, self.typography['body_medium'])
            summary_elements.append(row_para)
        
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
        
    def _create_trend_analysis(self):
        """Create comprehensive trend analysis section"""
        if not self.moods or len(self.moods) < 7:
            return []
        
        story = []
        
        # Trend Analysis Header
        header_html = f"""
        <table width="100%" style="background-color: {MD3_COLORS['secondary_container']}; border-radius: 12px;">
        <tr>
        <td align="center" style="padding: 16px;">
        <font size="18" color="{MD3_COLORS['secondary']}"><b>📈 Trend Analysis</b></font><br/>
        <font size="11" color="{MD3_COLORS['on_surface_variant']}">Statistical analysis of your mood patterns and trajectories</font>
        </td>
        </tr>
        </table>
        """
        story.append(Paragraph(header_html, self.typography['headline_large']))
        story.append(Spacer(1, 16))
        
        # Calculate trends
        recent_moods = [MOOD_VALUES.get(mood['mood'], 4) for mood in self.moods[:14]]  # Last 2 weeks
        older_moods = [MOOD_VALUES.get(mood['mood'], 4) for mood in self.moods[14:28]]  # Previous 2 weeks
        
        recent_avg = sum(recent_moods) / len(recent_moods) if recent_moods else 4
        older_avg = sum(older_moods) / len(older_moods) if older_moods else 4
        trend_change = recent_avg - older_avg
        
        # Trend analysis content
        trend_html = f"""
        <table width="100%" cellpadding="12">
        <tr>
        <td width="33%" style="background-color: {MD3_COLORS['surface_container_high']}; border-radius: 8px;">
        <font color="{MD3_COLORS['primary']}" size="12"><b>📊 Recent Trend</b></font><br/>
        """
        
        if trend_change > 0.3:
            trend_html += f'<font color="#4CAF50" size="20"><b>↗️</b></font><br/>'
            trend_html += f'<font color="#4CAF50" size="11"><b>Improving</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">+{trend_change:.1f} point increase over last 2 weeks</font>'
        elif trend_change < -0.3:
            trend_html += f'<font color="#F44336" size="20"><b>↘️</b></font><br/>'
            trend_html += f'<font color="#F44336" size="11"><b>Declining</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">{trend_change:.1f} point decrease over last 2 weeks</font>'
        else:
            trend_html += f'<font color="#FF9800" size="20"><b>→</b></font><br/>'
            trend_html += f'<font color="#FF9800" size="11"><b>Stable</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Consistent pattern with minimal variation</font>'
        
        # Volatility analysis
        mood_values = [MOOD_VALUES.get(mood['mood'], 4) for mood in self.moods[:30]]
        volatility = sum(abs(mood_values[i] - mood_values[i-1]) for i in range(1, len(mood_values))) / (len(mood_values) - 1) if len(mood_values) > 1 else 0
        
        trend_html += f"""
        </td>
        <td width="33%" style="background-color: {MD3_COLORS['surface_container_high']}; border-radius: 8px;">
        <font color="{MD3_COLORS['secondary']}" size="12"><b>📉 Volatility</b></font><br/>
        """
        
        if volatility < 0.5:
            trend_html += f'<font color="#4CAF50" size="11"><b>Low</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Stable mood patterns with minimal fluctuation</font>'
        elif volatility < 1.0:
            trend_html += f'<font color="#FF9800" size="11"><b>Moderate</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Some variation in daily mood levels</font>'
        else:
            trend_html += f'<font color="#F44336" size="11"><b>High</b></font><br/>'
            trend_html += f'<font color="{MD3_COLORS["on_surface"]}" size="10">Significant daily mood fluctuations</font>'
        
        # Consistency score
        consistency = max(0, 100 - (volatility * 50))
        
        trend_html += f"""
        </td>
        <td width="34%" style="background-color: {MD3_COLORS['surface_container_high']}; border-radius: 8px;">
        <font color="{MD3_COLORS['primary']}" size="12"><b>🎯 Consistency</b></font><br/>
        <font color="{MD3_COLORS['primary']}" size="16"><b>{consistency:.0f}%</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="10">Mood stability score based on daily variations</font>
        </td>
        </tr>
        </table>
        """
        
        story.append(Paragraph(trend_html, self.typography['body_medium']))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_md3_mood_distribution_chart(self):
        """Create premium mood distribution chart with enhanced visual effects"""
        try:
            from datetime import datetime, timedelta
            from collections import Counter
            import numpy as np
            
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
            
            # Premium color palette with gradients
            mood_colors = {
                'very bad': ['#BA1A1A', '#D32F2F'],     # Error gradient
                'bad': ['#D32F2F', '#F44336'],          # Error variant
                'slightly bad': ['#FF9800', '#FFB74D'], # Warning gradient
                'neutral': ['#79747E', '#9E9E9E'],      # Neutral gradient
                'slightly well': ['#8BC34A', '#AED581'], # Success variant
                'well': ['#4CAF50', '#66BB6A'],         # Success gradient
                'very well': ['#6750A4', '#8B7CC8']     # Primary gradient
            }
            
            # Prepare data
            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            colors = [mood_colors.get(mood, ['#79747E', '#9E9E9E'])[0] for mood in moods]
            
            # Create premium chart with enhanced layout
            fig = plt.figure(figsize=(14, 8), facecolor='#FFFBFE')
            gs = fig.add_gridspec(2, 3, height_ratios=[1, 3], width_ratios=[2, 1, 1])
            
            # Title section
            ax_title = fig.add_subplot(gs[0, :])
            ax_title.text(0.5, 0.5, 'Mood Distribution Analysis', 
                         fontsize=20, fontweight='bold', color='#6750A4',
                         ha='center', va='center', transform=ax_title.transAxes)
            ax_title.text(0.5, 0.1, f'Based on {sum(counts)} entries from the last 30 days', 
                         fontsize=12, color='#49454F',
                         ha='center', va='center', transform=ax_title.transAxes)
            ax_title.axis('off')
            
            # Main pie chart with premium effects
            ax_pie = fig.add_subplot(gs[1, 0])
            wedges, texts, autotexts = ax_pie.pie(counts, labels=None, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90,
                                                 textprops={'fontsize': 11, 'color': 'white', 'weight': 'bold'},
                                                 wedgeprops={'edgecolor': 'white', 'linewidth': 3,
                                                           'antialiased': True},
                                                 explode=[0.05 if count == max(counts) else 0 for count in counts])
            
            # Add shadow effect to pie chart
            shadow_wedges, _, _ = ax_pie.pie(counts, labels=None, colors=['#00000020']*len(counts),
                                           startangle=90, radius=0.98,
                                           wedgeprops={'edgecolor': 'none', 'linewidth': 0})
            
            # Enhanced legend with statistics
            ax_legend = fig.add_subplot(gs[1, 1:])
            ax_legend.axis('off')
            
            legend_y = 0.95
            ax_legend.text(0.05, legend_y, 'Detailed Breakdown', 
                          fontsize=14, fontweight='bold', color='#6750A4')
            legend_y -= 0.12
            
            # Sort moods by count for better presentation
            sorted_data = sorted(zip(moods, counts, colors), key=lambda x: x[1], reverse=True)
            
            for mood, count, color in sorted_data:
                percentage = (count / sum(counts)) * 100
                
                # Colored indicator with gradient effect
                rect = plt.Rectangle((0.05, legend_y-0.03), 0.06, 0.06, 
                                   facecolor=color, edgecolor='white', linewidth=1.5)
                ax_legend.add_patch(rect)
                
                # Mood name and statistics
                ax_legend.text(0.15, legend_y, mood.title(), fontsize=12, 
                              color='#1C1B1F', va='center', weight='bold')
                ax_legend.text(0.15, legend_y-0.04, f'{count} entries • {percentage:.1f}%', 
                              fontsize=10, color='#49454F', va='center')
                
                # Progress bar
                bar_width = percentage / 100 * 0.3
                ax_legend.add_patch(plt.Rectangle((0.5, legend_y-0.01), bar_width, 0.02,
                                                facecolor=color, alpha=0.6))
                ax_legend.add_patch(plt.Rectangle((0.5, legend_y-0.01), 0.3, 0.02,
                                                facecolor='none', edgecolor='#CAB6CF', linewidth=1))
                
                legend_y -= 0.15
            
            ax_legend.set_xlim(0, 1)
            ax_legend.set_ylim(0, 1)
            
            plt.tight_layout()
            
            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='#FFFBFE', edgecolor='none')
            plt.close()
            
            return chart_file.name
        except Exception as e:
            print(f"Chart generation error: {e}")
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
    
    def _create_methodology(self):
        """Create methodology section with technical details"""
        story = []
        
        # Methodology Header
        header_html = f"""
        <table width="100%" style="background-color: {MD3_COLORS['surface_container']}; border-radius: 12px; border: 1px solid {MD3_COLORS['outline_variant']};">
        <tr>
        <td align="center" style="padding: 12px;">
        <font size="16" color="{MD3_COLORS['on_surface']}"><b>📋 Methodology & Data Sources</b></font><br/>
        <font size="10" color="{MD3_COLORS['on_surface_variant']}">Technical details about data collection and analysis methods</font>
        </td>
        </tr>
        </table>
        """
        story.append(Paragraph(header_html, self.typography['title_large']))
        story.append(Spacer(1, 12))
        
        # Methodology content
        methodology_html = f"""
        <table width="100%" cellpadding="8">
        <tr>
        <td width="50%">
        <font color="{MD3_COLORS['primary']}" size="11"><b>Data Collection</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="9">
        • 7-point mood scale (Very Bad to Very Well)<br/>
        • Self-reported daily entries with optional notes<br/>
        • Timestamp accuracy to minute precision<br/>
        • Timezone: Chile (UTC-3) standardization
        </font><br/><br/>
        
        <font color="{MD3_COLORS['secondary']}" size="11"><b>Analysis Methods</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="9">
        • Statistical averages and trend calculations<br/>
        • Pattern recognition across weekly cycles<br/>
        • Volatility analysis using standard deviation<br/>
        • Streak calculation for consecutive positive days
        </font>
        </td>
        <td width="50%">
        <font color="{MD3_COLORS['primary']}" size="11"><b>Report Specifications</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="9">
        • Material Design 3 compliance<br/>
        • 300 DPI print-quality charts<br/>
        • A4 international paper format<br/>
        • Professional typography (Helvetica family)
        </font><br/><br/>
        
        <font color="{MD3_COLORS['secondary']}" size="11"><b>Data Privacy</b></font><br/>
        <font color="{MD3_COLORS['on_surface']}" size="9">
        • User-specific data isolation<br/>
        • No cross-user data sharing<br/>
        • Local processing and analysis<br/>
        • Confidential personal analytics
        </font>
        </td>
        </tr>
        </table>
        
        <font color="{MD3_COLORS['on_surface_variant']}" size="8">
        <b>Disclaimer:</b> This report is generated for personal wellness tracking purposes. 
        Mood data is self-reported and should not be used as a substitute for professional mental health assessment. 
        Consult healthcare providers for clinical concerns.
        </font>
        """
        
        story.append(Paragraph(methodology_html, self.typography['body_medium']))
        story.append(Spacer(1, 20))
        
        return story

    # End of PDFExporter class
    
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
