"""
Material Design 3 PDF Styles and Components
Following Google's Material Design 3 specifications for typography, colors, and layout.
"""

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import mm

# Material Design 3 Color System
MD3_COLORS = {
    # Primary Colors
    'primary': HexColor('#6750A4'),
    'on_primary': HexColor('#FFFFFF'),
    'primary_container': HexColor('#EADDFF'),
    'on_primary_container': HexColor('#21005D'),
    
    # Secondary Colors
    'secondary': HexColor('#625B71'),
    'on_secondary': HexColor('#FFFFFF'),
    'secondary_container': HexColor('#E8DEF8'),
    'on_secondary_container': HexColor('#1D192B'),
    
    # Surface Colors
    'surface': HexColor('#FFFBFE'),
    'on_surface': HexColor('#1C1B1F'),
    'surface_variant': HexColor('#E7E0EC'),
    'on_surface_variant': HexColor('#49454F'),
    'surface_container': HexColor('#F3EDF7'),
    'surface_container_high': HexColor('#ECE6F0'),
    
    # Outline Colors
    'outline': HexColor('#79747E'),
    'outline_variant': HexColor('#CAB6CF'),
    
    # Error Colors
    'error': HexColor('#BA1A1A'),
    'on_error': HexColor('#FFFFFF'),
}

# Material Design 3 Typography Scale
def create_md3_typography():
    """Create Material Design 3 typography styles"""
    
    # Note: Google Sans may not be available in ReportLab by default
    # Using Helvetica as fallback with proper sizing
    base_font = 'Helvetica'
    medium_font = 'Helvetica-Bold'
    
    return {
        'display_large': ParagraphStyle(
            'MD3DisplayLarge',
            fontName=base_font,
            fontSize=57,
            leading=64,
            textColor=MD3_COLORS['on_surface'],
            alignment=TA_CENTER,
            spaceAfter=24
        ),
        
        'headline_large': ParagraphStyle(
            'MD3HeadlineLarge',
            fontName=base_font,
            fontSize=32,
            leading=40,
            textColor=MD3_COLORS['on_surface'],
            alignment=TA_LEFT,
            spaceAfter=16
        ),
        
        'title_large': ParagraphStyle(
            'MD3TitleLarge',
            fontName=medium_font,
            fontSize=22,
            leading=28,
            textColor=MD3_COLORS['primary'],
            alignment=TA_LEFT,
            spaceAfter=12
        ),
        
        'body_large': ParagraphStyle(
            'MD3BodyLarge',
            fontName=base_font,
            fontSize=16,
            leading=24,
            textColor=MD3_COLORS['on_surface'],
            alignment=TA_LEFT,
            spaceAfter=8
        ),
        
        'body_medium': ParagraphStyle(
            'MD3BodyMedium',
            fontName=base_font,
            fontSize=14,
            leading=20,
            textColor=MD3_COLORS['on_surface_variant'],
            alignment=TA_LEFT,
            spaceAfter=6
        ),
        
        'label_large': ParagraphStyle(
            'MD3LabelLarge',
            fontName=medium_font,
            fontSize=14,
            leading=20,
            textColor=MD3_COLORS['on_surface_variant'],
            alignment=TA_LEFT,
            spaceAfter=4
        )
    }

# Layout Grid System
LAYOUT_GRID = {
    'page_width': 210 * mm,  # A4 width
    'page_height': 297 * mm,  # A4 height
    'margin_top': 24 * mm,
    'margin_bottom': 24 * mm,
    'margin_left': 20 * mm,
    'margin_right': 20 * mm,
    'content_width': 170 * mm,
    'columns': 12,
    'gutter': 4 * mm,
    'baseline': 8 * mm
}

class MD3PDFComponents:
    """Material Design 3 PDF Components"""
    
    def __init__(self):
        self.colors = MD3_COLORS
        self.typography = create_md3_typography()
        self.layout = LAYOUT_GRID
    
    def create_header_background(self, canvas, x, y, width, height):
        """Create MD3 header with primary color background"""
        canvas.setFillColor(self.colors['primary'])
        canvas.roundRect(x, y, width, height, 12, fill=1, stroke=0)
    
    def create_card_background(self, canvas, x, y, width, height, elevation=1):
        """Create MD3 card with proper elevation"""
        # Shadow effect (simplified)
        shadow_offset = elevation * 2
        canvas.setFillColor(HexColor('#00000020'))
        canvas.roundRect(x + shadow_offset, y - shadow_offset, width, height, 12, fill=1, stroke=0)
        
        # Card background
        canvas.setFillColor(self.colors['surface_container'])
        canvas.roundRect(x, y, width, height, 12, fill=1, stroke=0)
        
        # Card border
        canvas.setStrokeColor(self.colors['outline_variant'])
        canvas.setLineWidth(1)
        canvas.roundRect(x, y, width, height, 12, fill=0, stroke=1)
    
    def get_chart_colors(self):
        """Get MD3 color palette for charts"""
        return [
            self.colors['primary'],
            self.colors['secondary'],
            HexColor('#7D5260'),  # Tertiary
            HexColor('#8BC34A'),  # Success
            HexColor('#FF9800'),  # Warning
            self.colors['error']
        ]
