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
    """Material Design 3 PDF Components with Visual Polish"""
    
    def __init__(self):
        self.colors = MD3_COLORS
        self.typography = create_md3_typography()
        self.layout = LAYOUT_GRID
    
    def get_column_width(self, columns=1):
        """Calculate width for given number of columns in 12-column grid"""
        column_width = (self.layout['content_width'] - (11 * self.layout['gutter'])) / 12
        return (column_width * columns) + (self.layout['gutter'] * (columns - 1))
    
    def get_column_x(self, column_start=0):
        """Get X position for column start (0-11)"""
        column_width = (self.layout['content_width'] - (11 * self.layout['gutter'])) / 12
        return self.layout['margin_left'] + (column_start * (column_width + self.layout['gutter']))
    
    def create_gradient_header(self, canvas, x, y, width, height):
        """Create MD3 header with gradient background and enhanced elevation"""
        # Multi-layer shadow for depth (elevation level 3)
        canvas.setFillColor(HexColor('#00000008'))
        canvas.roundRect(x + 6, y - 6, width, height, 16, fill=1, stroke=0)
        canvas.setFillColor(HexColor('#00000012'))
        canvas.roundRect(x + 4, y - 4, width, height, 16, fill=1, stroke=0)
        canvas.setFillColor(HexColor('#00000018'))
        canvas.roundRect(x + 2, y - 2, width, height, 16, fill=1, stroke=0)
        
        # Gradient background simulation with multiple layers
        canvas.setFillColor(self.colors['primary'])
        canvas.roundRect(x, y, width, height, 16, fill=1, stroke=0)
        
        # Gradient overlay (lighter at top)
        canvas.setFillColor(HexColor('#FFFFFF15'))
        canvas.roundRect(x, y + height * 0.6, width, height * 0.4, 16, fill=1, stroke=0)
        
        # Subtle accent line with gradient
        canvas.setFillColor(self.colors['primary_container'])
        canvas.roundRect(x, y + height - 8, width, 8, 0, fill=1, stroke=0)
        
        # Highlight line at top
        canvas.setFillColor(HexColor('#FFFFFF25'))
        canvas.roundRect(x, y + height - 2, width, 2, 0, fill=1, stroke=0)
    
    def create_elevated_card(self, canvas, x, y, width, height, elevation=2):
        """Create MD3 card with enhanced elevation and subtle texture"""
        # Enhanced multi-layer shadow
        shadow_layers = [
            (elevation * 3, HexColor('#00000006')),
            (elevation * 2, HexColor('#00000010')),
            (elevation * 1, HexColor('#00000015'))
        ]
        
        for offset, color in shadow_layers:
            canvas.setFillColor(color)
            canvas.roundRect(x + offset, y - offset, width, height, 12, fill=1, stroke=0)
        
        # Card background with subtle texture
        canvas.setFillColor(self.colors['surface_container_high'])
        canvas.roundRect(x, y, width, height, 12, fill=1, stroke=0)
        
        # Subtle inner highlight
        canvas.setFillColor(HexColor('#FFFFFF08'))
        canvas.roundRect(x + 1, y + height - 3, width - 2, 2, 0, fill=1, stroke=0)
        
        # Enhanced border with gradient effect
        canvas.setStrokeColor(self.colors['outline_variant'])
        canvas.setLineWidth(0.5)
        canvas.roundRect(x, y, width, height, 12, fill=0, stroke=1)
        
        # Accent border (top)
        canvas.setFillColor(self.colors['primary'])
        canvas.roundRect(x, y + height - 4, width, 4, 0, fill=1, stroke=0)
        
        # Subtle gradient overlay
        canvas.setFillColor(HexColor('#FFFFFF03'))
        canvas.roundRect(x, y + height * 0.7, width, height * 0.3, 12, fill=1, stroke=0)
    
    def create_premium_chart_container(self, canvas, x, y, width, height):
        """Create premium chart container with enhanced styling"""
        # Outer glow effect
        canvas.setFillColor(HexColor('#6750A410'))
        canvas.roundRect(x - 2, y - 2, width + 4, height + 4, 10, fill=1, stroke=0)
        
        # Container background with texture
        canvas.setFillColor(self.colors['surface_container'])
        canvas.roundRect(x, y, width, height, 8, fill=1, stroke=0)
        
        # Inner frame
        canvas.setStrokeColor(self.colors['outline_variant'])
        canvas.setLineWidth(0.5)
        canvas.roundRect(x + 4, y + 4, width - 8, height - 8, 4, fill=0, stroke=1)
        
        # Corner accents
        accent_size = 12
        canvas.setFillColor(self.colors['primary'])
        # Top-left corner accent
        canvas.roundRect(x, y + height - accent_size, accent_size, accent_size, 8, fill=1, stroke=0)
        # Bottom-right corner accent
        canvas.roundRect(x + width - accent_size, y, accent_size, accent_size, 8, fill=1, stroke=0)
    
    def create_section_divider_enhanced(self, canvas, x, y, width):
        """Create enhanced section divider with gradient"""
        # Main divider line
        canvas.setStrokeColor(self.colors['outline_variant'])
        canvas.setLineWidth(1)
        canvas.line(x, y, x + width, y)
        
        # Gradient accent line above
        canvas.setStrokeColor(self.colors['primary'])
        canvas.setLineWidth(0.5)
        canvas.line(x + width * 0.2, y + 1, x + width * 0.8, y + 1)
        
        # Decorative dots
        dot_spacing = width / 20
        canvas.setFillColor(self.colors['primary'])
        for i in range(3):
            dot_x = x + width/2 + (i - 1) * dot_spacing
            canvas.circle(dot_x, y + 3, 1, fill=1, stroke=0)
    
    def get_enhanced_chart_colors(self):
        """Get enhanced MD3 color palette with gradients for charts"""
        return {
            'primary_gradient': ['#6750A4', '#8B7CC8'],
            'secondary_gradient': ['#625B71', '#7D7689'],
            'success_gradient': ['#4CAF50', '#66BB6A'],
            'warning_gradient': ['#FF9800', '#FFB74D'],
            'error_gradient': ['#BA1A1A', '#E57373'],
            'neutral': '#79747E'
        }
