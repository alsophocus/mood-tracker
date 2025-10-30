"""
Comprehensive Material Design 3 PDF Export
Complete mood analytics report with beautiful MD3 styling and all charts
"""

import io
import tempfile
from datetime import datetime, timedelta
from collections import Counter
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analytics import MoodAnalytics, MOOD_VALUES, TrendAnalysisService

# Material Design 3 Complete Color System
MD3_COLORS = {
    # Primary palette (Purple)
    'primary': '#6750A4',
    'on_primary': '#FFFFFF',
    'primary_container': '#EADDFF',
    'on_primary_container': '#21005D',

    # Secondary palette
    'secondary': '#625B71',
    'on_secondary': '#FFFFFF',
    'secondary_container': '#E8DEF8',
    'on_secondary_container': '#1D192B',

    # Tertiary palette
    'tertiary': '#7D5260',
    'on_tertiary': '#FFFFFF',
    'tertiary_container': '#FFD8E4',
    'on_tertiary_container': '#31111D',

    # Surface colors
    'surface': '#FFFBFE',
    'on_surface': '#1C1B1F',
    'surface_variant': '#E7E0EC',
    'on_surface_variant': '#49454F',
    'surface_container': '#F3EDF7',
    'surface_container_high': '#ECE6F0',

    # Outline colors
    'outline': '#79747E',
    'outline_variant': '#CAC4D0',

    # Semantic colors
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#BA1A1A',
    'info': '#2196F3',

    # Mood-specific colors
    'mood_very_bad': '#BA1A1A',
    'mood_bad': '#D32F2F',
    'mood_slightly_bad': '#FF9800',
    'mood_neutral': '#79747E',
    'mood_slightly_well': '#8BC34A',
    'mood_well': '#4CAF50',
    'mood_very_well': '#6750A4'
}


class PDFExporter:
    """Comprehensive Material Design 3 PDF Exporter"""

    def __init__(self, user, moods):
        self.user = user
        self.moods = moods or []
        self.analytics = MoodAnalytics(self.moods)
        self.trend_service = TrendAnalysisService()
        self.styles = self._create_md3_styles()
        self.temp_files = []

    def _create_md3_styles(self):
        """Create Material Design 3 typography styles"""
        styles = getSampleStyleSheet()

        return {
            'display_large': ParagraphStyle(
                'DisplayLarge',
                parent=styles['Title'],
                fontSize=36,
                leading=44,
                spaceAfter=24,
                alignment=TA_CENTER,
                textColor=HexColor(MD3_COLORS['primary']),
                fontName='Helvetica-Bold'
            ),
            'headline_large': ParagraphStyle(
                'HeadlineLarge',
                parent=styles['Heading1'],
                fontSize=24,
                leading=32,
                spaceAfter=16,
                spaceBefore=24,
                textColor=HexColor(MD3_COLORS['on_surface']),
                fontName='Helvetica-Bold'
            ),
            'title_large': ParagraphStyle(
                'TitleLarge',
                parent=styles['Heading2'],
                fontSize=18,
                leading=24,
                spaceAfter=12,
                spaceBefore=16,
                textColor=HexColor(MD3_COLORS['primary']),
                fontName='Helvetica-Bold'
            ),
            'body_large': ParagraphStyle(
                'BodyLarge',
                parent=styles['Normal'],
                fontSize=14,
                leading=20,
                spaceAfter=12,
                textColor=HexColor(MD3_COLORS['on_surface']),
                fontName='Helvetica'
            ),
            'body_medium': ParagraphStyle(
                'BodyMedium',
                parent=styles['Normal'],
                fontSize=12,
                leading=18,
                spaceAfter=8,
                textColor=HexColor(MD3_COLORS['on_surface']),
                fontName='Helvetica'
            ),
            'body_small': ParagraphStyle(
                'BodySmall',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=6,
                textColor=HexColor(MD3_COLORS['on_surface_variant']),
                fontName='Helvetica'
            ),
            'label_large': ParagraphStyle(
                'LabelLarge',
                parent=styles['Normal'],
                fontSize=13,
                leading=18,
                textColor=HexColor(MD3_COLORS['on_surface']),
                fontName='Helvetica-Bold'
            )
        }

    def generate_report(self):
        """Generate comprehensive 4-5 page Material Design 3 PDF report"""
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        story = []

        # Page 1: Cover + Executive Summary + Key Metrics
        story.extend(self._create_cover())
        story.extend(self._create_executive_summary())
        story.extend(self._create_key_metrics())
        story.append(PageBreak())

        # Page 2: Mood Distribution + Weekly Patterns
        story.extend(self._create_charts_page())
        story.append(PageBreak())

        # Page 3: Monthly Trends with Regression + Daily Patterns
        story.extend(self._create_trends_page())
        story.append(PageBreak())

        # Page 4: Recent History + Footer
        story.extend(self._create_recent_history())
        story.extend(self._create_footer())

        doc.build(story)
        buffer.seek(0)

        # Cleanup temp files
        for temp_file in self.temp_files:
            try:
                import os
                os.unlink(temp_file)
            except:
                pass

        return buffer

    def _create_cover(self):
        """Create beautiful MD3 cover page header"""
        elements = []

        # Main title with icon
        title = Paragraph("🧠 Mood Analytics Report", self.styles['display_large'])
        elements.append(title)

        # User info card
        user_name = self.user.name if self.user and self.user.name else "User"
        date_str = datetime.now().strftime('%B %d, %Y')
        time_str = datetime.now().strftime('%H:%M')

        info_text = f"""
        <para align="center" spaceAfter="8">
        <font size="14" color="{MD3_COLORS['on_surface']}"><b>Generated for: {user_name}</b></font><br/>
        <font size="11" color="{MD3_COLORS['on_surface_variant']}">Report Date: {date_str} at {time_str}</font><br/>
        <font size="10" color="{MD3_COLORS['on_surface_variant']}">Material Design 3 • Professional Analytics</font>
        </para>
        """

        info = Paragraph(info_text, self.styles['body_medium'])
        elements.append(info)
        elements.append(Spacer(1, 16))

        return elements

    def _create_executive_summary(self):
        """Create executive summary with insights"""
        if not self.moods:
            return [Paragraph("No mood data available for analysis.", self.styles['body_large'])]

        elements = []

        # Get summary with error handling
        try:
            summary = self.analytics.get_summary()
        except Exception as e:
            print(f"Error getting summary: {e}")
            return [Paragraph("Unable to generate summary due to insufficient data.", self.styles['body_large'])]

        # Validate summary data structure
        if not summary or not isinstance(summary, dict):
            return [Paragraph("Unable to generate summary due to insufficient data.", self.styles['body_large'])]

        # Section header
        header = Paragraph("📊 Executive Summary", self.styles['headline_large'])
        elements.append(header)

        # Generate insights with safe defaults
        avg_mood = summary.get('daily_average', 4.0)
        total_entries = summary.get('total_entries', 0)
        streak = summary.get('current_streak', 0)
        best_day = summary.get('best_day', 'N/A')

        # Additional validation - ensure best_day is a string and not empty
        if not isinstance(best_day, str) or not best_day or best_day == "N/A":
            best_day = 'N/A'

        # Determine assessment
        if avg_mood >= 5.5:
            assessment = "positive and consistently strong"
            assessment_color = MD3_COLORS['success']
            trend_icon = "↗️"
        elif avg_mood >= 4.5:
            assessment = "balanced and stable"
            assessment_color = MD3_COLORS['warning']
            trend_icon = "→"
        else:
            assessment = "showing room for growth"
            assessment_color = MD3_COLORS['error']
            trend_icon = "↘️"

        # Create best_day text with conditional wording
        if best_day != "N/A":
            best_day_text = f"<b>{best_day}</b> appears to be your strongest day of the week."
        else:
            best_day_text = "Continue tracking to identify your strongest day of the week."

        summary_text = f"""
        <para align="left" spaceAfter="12">
        <font size="12" color="{MD3_COLORS['on_surface']}">
        Based on <b>{total_entries}</b> mood entries, your emotional well-being is
        <font color="{assessment_color}"><b>{trend_icon} {assessment}</b></font>
        with an average rating of <b>{avg_mood:.1f}/7.0</b>.
        </font>
        </para>
        <para align="left" spaceAfter="12">
        <font size="12" color="{MD3_COLORS['on_surface']}">
        You currently maintain a <font color="{MD3_COLORS['primary']}"><b>{streak}-day</b></font> positive mood streak.
        {best_day_text}
        </font>
        </para>
        <para align="left" spaceAfter="12">
        <font size="11" color="{MD3_COLORS['on_surface_variant']}">
        <b>Data Quality:</b> {"Excellent" if total_entries > 30 else "Good" if total_entries > 15 else "Building"}
        tracking consistency with comprehensive analytics available.
        </font>
        </para>
        """

        summary_para = Paragraph(summary_text, self.styles['body_medium'])
        elements.append(summary_para)
        elements.append(Spacer(1, 16))

        return elements

    def _create_key_metrics(self):
        """Create key metrics grid (2x2)"""
        if not self.moods:
            return []

        elements = []
        summary = self.analytics.get_summary()

        # Section header
        header = Paragraph("📈 Key Performance Indicators", self.styles['title_large'])
        elements.append(header)
        elements.append(Spacer(1, 8))

        # Create 2x2 metrics table
        data = [
            [
                self._format_metric_cell("📊", str(summary['total_entries']), "Total Entries", "Mood records tracked"),
                self._format_metric_cell("🔥", f"{summary['current_streak']} days", "Current Streak", "Consecutive positive days")
            ],
            [
                self._format_metric_cell("⭐", summary['best_day'], "Best Day", "Highest average mood"),
                self._format_metric_cell("📉", f"{summary['daily_average']:.1f}/7.0", "Average Mood", "Overall rating")
            ]
        ]

        table = Table(data, colWidths=[8*cm, 8*cm], rowHeights=[2.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor(MD3_COLORS['surface_container'])),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor(MD3_COLORS['outline_variant'])),
            ('INNERGRID', (0, 0), (-1, -1), 1, HexColor(MD3_COLORS['outline_variant'])),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 16))

        return elements

    def _format_metric_cell(self, icon, value, label, description):
        """Format a metric cell with MD3 styling"""
        return f"""
        <para align="center">
        <font size="24">{icon}</font><br/>
        <font size="20" color="{MD3_COLORS['primary']}"><b>{value}</b></font><br/>
        <font size="12" color="{MD3_COLORS['on_surface']}"><b>{label}</b></font><br/>
        <font size="9" color="{MD3_COLORS['on_surface_variant']}">{description}</font>
        </para>
        """

    def _create_charts_page(self):
        """Create page 2: Mood Distribution + Weekly Patterns"""
        elements = []

        # Mood Distribution
        header1 = Paragraph("🎯 Mood Distribution Analysis", self.styles['headline_large'])
        elements.append(header1)

        dist_chart = self._create_mood_distribution_chart()
        if dist_chart:
            elements.append(Image(dist_chart, width=16*cm, height=10*cm))
            elements.append(Spacer(1, 12))

        # Weekly Patterns
        header2 = Paragraph("📅 Weekly Mood Patterns", self.styles['title_large'])
        elements.append(header2)

        weekly_chart = self._create_weekly_patterns_chart()
        if weekly_chart:
            elements.append(Image(weekly_chart, width=16*cm, height=9*cm))

        return elements

    def _create_trends_page(self):
        """Create page 3: Monthly Trends + Daily Patterns"""
        elements = []

        # Monthly Trends with Regression
        header1 = Paragraph("📈 Monthly Trends & Forecast", self.styles['headline_large'])
        elements.append(header1)

        monthly_chart = self._create_monthly_trends_chart()
        if monthly_chart:
            elements.append(Image(monthly_chart, width=16*cm, height=9*cm))
            elements.append(Spacer(1, 12))

        # Daily Patterns
        header2 = Paragraph("⏰ Daily Mood Patterns", self.styles['title_large'])
        elements.append(header2)

        daily_chart = self._create_daily_patterns_chart()
        if daily_chart:
            elements.append(Image(daily_chart, width=16*cm, height=8*cm))

        return elements

    def _create_mood_distribution_chart(self):
        """Create beautiful donut chart for mood distribution"""
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

            # MD3 mood colors
            mood_color_map = {
                'very bad': MD3_COLORS['mood_very_bad'],
                'bad': MD3_COLORS['mood_bad'],
                'slightly bad': MD3_COLORS['mood_slightly_bad'],
                'neutral': MD3_COLORS['mood_neutral'],
                'slightly well': MD3_COLORS['mood_slightly_well'],
                'well': MD3_COLORS['mood_well'],
                'very well': MD3_COLORS['mood_very_well']
            }

            moods = list(mood_counts.keys())
            counts = list(mood_counts.values())
            colors = [mood_color_map.get(mood, MD3_COLORS['neutral']) for mood in moods]

            # Create donut chart
            fig, ax = plt.subplots(figsize=(12, 8), facecolor=MD3_COLORS['surface'])

            wedges, texts, autotexts = ax.pie(
                counts,
                labels=[m.replace('_', ' ').title() for m in moods],
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3),
                textprops={'fontsize': 11, 'fontweight': 'bold', 'color': MD3_COLORS['on_surface']}
            )

            # Style the percentages
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            # Center text
            total = sum(counts)
            ax.text(0, 0, f'{total}\nTotal\nEntries',
                   ha='center', va='center',
                   fontsize=16, fontweight='bold',
                   color=MD3_COLORS['on_surface'])

            ax.set_title('Mood Distribution (Last 30 Days)',
                        fontsize=18, fontweight='bold',
                        color=MD3_COLORS['primary'], pad=20)

            plt.tight_layout()

            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight',
                       facecolor=MD3_COLORS['surface'], edgecolor='none')
            plt.close()

            self.temp_files.append(chart_file.name)
            return chart_file.name

        except Exception as e:
            print(f"Chart generation error: {e}")
            return None

    def _create_weekly_patterns_chart(self):
        """Create weekly patterns line chart"""
        try:
            weekly_data = self.analytics.get_weekly_patterns()

            if not weekly_data or not weekly_data.get('data'):
                return None

            labels = weekly_data.get('labels', [])
            data_points = weekly_data.get('data', [])

            # Validate data structure
            if not labels or not data_points or len(labels) != len(data_points):
                print(f"Invalid weekly data structure: labels={len(labels)}, data={len(data_points)}")
                return None

            # Filter out zero values (days with no data)
            non_zero_data = [d for d in data_points if d > 0]
            if not non_zero_data:
                print("No valid weekly mood data available")
                return None

            fig, ax = plt.subplots(figsize=(12, 7), facecolor=MD3_COLORS['surface'])

            # Main line with filled area
            line = ax.plot(labels, data_points,
                          marker='o', linewidth=3.5, markersize=10,
                          color=MD3_COLORS['primary'],
                          markerfacecolor=MD3_COLORS['primary'],
                          markeredgecolor='white', markeredgewidth=2.5,
                          label='Average Mood', zorder=3)

            ax.fill_between(labels, data_points, alpha=0.2,
                           color=MD3_COLORS['primary'], zorder=1)

            # Highlight best and worst days (only if we have valid data)
            try:
                max_mood = max(data_points)
                min_mood = min(data_points)

                if max_mood > 0:  # Only highlight if there's actual data
                    max_idx = data_points.index(max_mood)
                    min_idx = data_points.index(min_mood)

                    if 0 <= max_idx < len(labels):
                        max_day = labels[max_idx]
                    else:
                        max_day = None

                    if 0 <= min_idx < len(labels):
                        min_day = labels[min_idx]
                    else:
                        min_day = None
                else:
                    max_day = None
                    min_day = None
            except (ValueError, IndexError) as e:
                print(f"Error finding best/worst days: {e}")
                max_day = None
                min_day = None

            # Only add highlights if we have valid day labels
            if max_day is not None:
                ax.scatter([max_day], [max_mood],
                          color=MD3_COLORS['success'], s=200, marker='^',
                          edgecolor='white', linewidth=2.5, zorder=4,
                          label='Best Day')

            if max_mood != min_mood and min_day is not None:
                ax.scatter([min_day], [min_mood],
                          color=MD3_COLORS['warning'], s=200, marker='v',
                          edgecolor='white', linewidth=2.5, zorder=4,
                          label='Needs Focus')

            # Styling
            ax.set_ylim(0.5, 7.5)
            ax.set_ylabel('Average Mood Rating', fontsize=13,
                         color=MD3_COLORS['on_surface'], fontweight='bold')
            ax.set_title('Weekly Mood Patterns', fontsize=16,
                        fontweight='bold', color=MD3_COLORS['primary'], pad=20)

            # Grid
            ax.grid(True, alpha=0.2, color=MD3_COLORS['outline'],
                   linestyle='--', linewidth=0.8)
            ax.set_facecolor(MD3_COLORS['surface_container'])

            # Mood level reference lines
            mood_levels = ['Very Bad', 'Bad', 'Slightly Bad', 'Neutral',
                          'Slightly Well', 'Well', 'Very Well']
            for i, level in enumerate(mood_levels, 1):
                ax.axhline(y=i, color=MD3_COLORS['outline_variant'],
                          linestyle=':', alpha=0.4, zorder=0)

            # Style axes
            ax.tick_params(colors=MD3_COLORS['on_surface'], labelsize=11)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(MD3_COLORS['outline'])
            ax.spines['bottom'].set_color(MD3_COLORS['outline'])

            # Legend
            ax.legend(loc='upper right', frameon=True, fancybox=True,
                     shadow=True, facecolor='white',
                     edgecolor=MD3_COLORS['outline'])

            plt.xticks(rotation=0)
            plt.tight_layout()

            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight',
                       facecolor=MD3_COLORS['surface'], edgecolor='none')
            plt.close()

            self.temp_files.append(chart_file.name)
            return chart_file.name

        except Exception as e:
            print(f"Weekly chart error: {e}")
            return None

    def _create_monthly_trends_chart(self):
        """Create monthly trends with linear regression overlay"""
        try:
            monthly_data = self.analytics.get_monthly_trends()

            if not monthly_data or len(monthly_data) < 1:
                print("No monthly trend data available")
                return None

            # Get last 12 months
            recent_data = monthly_data[-12:] if len(monthly_data) > 0 else []

            if not recent_data:
                print("No recent monthly data to display")
                return None

            # Validate data structure
            try:
                months = [item['month'] for item in recent_data]
                values = [item['mood'] for item in recent_data]
            except (KeyError, TypeError) as e:
                print(f"Invalid monthly data structure: {e}")
                return None

            if not months or not values or len(months) != len(values):
                print(f"Monthly data mismatch: months={len(months)}, values={len(values)}")
                return None

            # Calculate linear regression
            regression = self.trend_service.calculate_linear_regression(values)
            trend_direction = self.trend_service.get_trend_direction(regression['slope'])
            trend_line = self.trend_service.generate_trend_line_data(values, regression)

            fig, ax = plt.subplots(figsize=(12, 7), facecolor=MD3_COLORS['surface'])

            # Main trend line
            ax.plot(months, values,
                   marker='o', linewidth=3, markersize=9,
                   color=MD3_COLORS['primary'],
                   markerfacecolor=MD3_COLORS['primary'],
                   markeredgecolor='white', markeredgewidth=2,
                   label='Actual Mood', zorder=3)

            ax.fill_between(months, values, alpha=0.15,
                           color=MD3_COLORS['primary'], zorder=1)

            # Linear regression line
            ax.plot(months, trend_line,
                   linestyle='--', linewidth=2.5,
                   color=trend_direction['color'],
                   label=f'Trend ({trend_direction["description"]})',
                   alpha=0.8, zorder=2)

            # Styling
            ax.set_ylim(0.5, 7.5)
            ax.set_ylabel('Average Mood Rating', fontsize=13,
                         color=MD3_COLORS['on_surface'], fontweight='bold')
            ax.set_xlabel('Month', fontsize=13,
                         color=MD3_COLORS['on_surface'], fontweight='bold')

            # Title with trend indicator
            title_text = f'Monthly Trends - {trend_direction["description"].title()} Pattern'
            ax.set_title(title_text, fontsize=16, fontweight='bold',
                        color=MD3_COLORS['primary'], pad=20)

            # Add statistics box
            stats_text = f'Slope: {regression["slope"]:.3f} | Correlation: {regression["correlation"]:.3f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor=MD3_COLORS['surface_container'],
                            alpha=0.8, edgecolor=MD3_COLORS['outline']))

            # Grid
            ax.grid(True, alpha=0.2, color=MD3_COLORS['outline'],
                   linestyle='--', linewidth=0.8)
            ax.set_facecolor(MD3_COLORS['surface_container'])

            # Style axes
            ax.tick_params(colors=MD3_COLORS['on_surface'], labelsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(MD3_COLORS['outline'])
            ax.spines['bottom'].set_color(MD3_COLORS['outline'])

            # Legend
            ax.legend(loc='upper left', frameon=True, fancybox=True,
                     shadow=True, facecolor='white',
                     edgecolor=MD3_COLORS['outline'])

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight',
                       facecolor=MD3_COLORS['surface'], edgecolor='none')
            plt.close()

            self.temp_files.append(chart_file.name)
            return chart_file.name

        except Exception as e:
            print(f"Monthly trends error: {e}")
            return None

    def _create_daily_patterns_chart(self):
        """Create daily patterns (hourly) bar chart"""
        try:
            daily_data = self.analytics.get_daily_patterns()

            if not daily_data or not daily_data.get('data'):
                return None

            # Filter out None values
            hours = []
            values = []
            for i, val in enumerate(daily_data['data']):
                if val is not None:
                    hours.append(f"{i:02d}:00")
                    values.append(val)

            if not values:
                return None

            fig, ax = plt.subplots(figsize=(12, 6), facecolor=MD3_COLORS['surface'])

            # Create gradient colors for bars
            colors = [MD3_COLORS['primary'] if v >= 5 else MD3_COLORS['warning'] if v >= 4 else MD3_COLORS['error'] for v in values]

            bars = ax.bar(hours, values, color=colors, alpha=0.8,
                         edgecolor='white', linewidth=1.5)

            # Highlight peak hours
            if values:
                max_val = max(values)
                for bar, val in zip(bars, values):
                    if val == max_val:
                        bar.set_edgecolor(MD3_COLORS['success'])
                        bar.set_linewidth(3)

            # Styling
            ax.set_ylim(0, 8)
            ax.set_ylabel('Average Mood Rating', fontsize=13,
                         color=MD3_COLORS['on_surface'], fontweight='bold')
            ax.set_xlabel('Hour of Day', fontsize=13,
                         color=MD3_COLORS['on_surface'], fontweight='bold')
            ax.set_title('Daily Mood Patterns (Hourly Average)',
                        fontsize=16, fontweight='bold',
                        color=MD3_COLORS['primary'], pad=20)

            # Grid
            ax.grid(True, alpha=0.2, color=MD3_COLORS['outline'],
                   linestyle='--', linewidth=0.8, axis='y')
            ax.set_facecolor(MD3_COLORS['surface_container'])

            # Style axes
            ax.tick_params(colors=MD3_COLORS['on_surface'], labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(MD3_COLORS['outline'])
            ax.spines['bottom'].set_color(MD3_COLORS['outline'])

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            chart_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(chart_file.name, dpi=300, bbox_inches='tight',
                       facecolor=MD3_COLORS['surface'], edgecolor='none')
            plt.close()

            self.temp_files.append(chart_file.name)
            return chart_file.name

        except Exception as e:
            print(f"Daily patterns error: {e}")
            return None

    def _create_recent_history(self):
        """Create recent mood history table"""
        if not self.moods:
            return []

        elements = []

        # Section header
        header = Paragraph("📝 Recent Mood History", self.styles['headline_large'])
        elements.append(header)
        elements.append(Spacer(1, 8))

        # Mood emoji mapping
        mood_emoji = {
            'very bad': '😭', 'bad': '😢', 'slightly bad': '😔',
            'neutral': '😐', 'slightly well': '🙂', 'well': '😊',
            'very well': '😄'
        }

        # Table data
        data = [['Date', 'Mood', 'Rating', 'Notes']]

        for mood_entry in self.moods[:12]:  # Last 12 entries
            date_str = str(mood_entry['date'])
            mood = mood_entry['mood']
            rating = MOOD_VALUES.get(mood, 4)
            notes = mood_entry.get('notes', 'No notes')[:60]
            if len(mood_entry.get('notes', '')) > 60:
                notes += '...'

            emoji = mood_emoji.get(mood, '😐')
            mood_display = f"{emoji} {mood.replace('_', ' ').title()}"

            data.append([date_str, mood_display, f"{rating}/7", notes])

        # Create table
        table = Table(data, colWidths=[2.5*cm, 4.5*cm, 1.8*cm, 7.2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(MD3_COLORS['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(MD3_COLORS['on_primary'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor(MD3_COLORS['outline_variant'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor(MD3_COLORS['surface']), HexColor(MD3_COLORS['surface_container'])]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 16))

        return elements

    def _create_footer(self):
        """Create professional MD3 footer"""
        elements = []

        elements.append(Spacer(1, 20))

        # Methodology note
        methodology_text = f"""
        <para align="left" spaceAfter="8">
        <font size="9" color="{MD3_COLORS['on_surface_variant']}">
        <b>Methodology:</b> This report analyzes mood data using a 7-point scale (1-7).
        Analytics include trend analysis with linear regression, pattern recognition,
        and statistical aggregations. All data is user-specific and confidential.
        </font>
        </para>
        """
        methodology = Paragraph(methodology_text, self.styles['body_small'])
        elements.append(methodology)

        # Footer with metadata
        footer_text = f"""
        <para align="center" spaceAfter="4">
        <font size="10" color="{MD3_COLORS['primary']}"><b>🧠 Mood Tracker</b></font><br/>
        <font size="8" color="{MD3_COLORS['on_surface_variant']}">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} •
        Material Design 3 • Professional Analytics Report
        </font>
        </para>
        """

        footer = Paragraph(footer_text, self.styles['body_small'])
        elements.append(footer)

        return elements
