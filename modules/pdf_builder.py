"""
PDF Builder Module
Utilities for creating professional PDF reports using ReportLab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
from typing import List, Dict, Tuple, Optional


class PDFBuilder:
    """Professional PDF document builder with corporate branding"""

    def __init__(self, output_path: str, page_size: str = 'A4',
                 title: str = "Report", author: str = ""):
        """
        Initialize PDF builder

        Args:
            output_path: Path to save the PDF file
            page_size: Paper size ('A4' or 'letter')
            title: Document title
            author: Document author
        """
        self.output_path = output_path
        self.page_size = A4 if page_size == 'A4' else letter
        self.width, self.height = self.page_size
        self.title = title
        self.author = author

        # Margins (in mm converted to points)
        self.margin_top = 20 * mm
        self.margin_bottom = 20 * mm
        self.margin_left = 15 * mm
        self.margin_right = 15 * mm

        # Header and footer heights
        self.header_height = 30 * mm
        self.footer_height = 20 * mm

        # Story (content) list for platypus
        self.story = []

        # Styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

        # Metadata
        self.metadata = {}

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))

        # Caption style
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

    def add_cover_page(self, logo_path: Optional[str] = None,
                       company_name: str = "", subtitle: str = ""):
        """
        Add a cover page to the report

        Args:
            logo_path: Path to company logo image
            company_name: Company name
            subtitle: Report subtitle
        """
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            img = Image(logo_path, width=100*mm, height=40*mm, kind='proportional')
            img.hAlign = 'CENTER'
            self.story.append(img)
            self.story.append(Spacer(1, 20*mm))
        else:
            self.story.append(Spacer(1, 60*mm))

        # Add title
        title_para = Paragraph(self.title, self.styles['CustomTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 10*mm))

        # Add subtitle
        if subtitle:
            subtitle_para = Paragraph(subtitle, self.styles['Heading2'])
            self.story.append(subtitle_para)
            self.story.append(Spacer(1, 5*mm))

        # Add company name
        if company_name:
            company_para = Paragraph(company_name, self.styles['Heading3'])
            self.story.append(company_para)
            self.story.append(Spacer(1, 40*mm))

        # Add generation date
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        self.story.append(date_para)

        # Page break after cover
        self.story.append(PageBreak())

    def add_section(self, title: str, content: str = "", level: int = 1):
        """
        Add a section to the report

        Args:
            title: Section title
            content: Section content text
            level: Header level (1, 2, or 3)
        """
        # Choose style based on level
        if level == 1:
            style = self.styles['SectionHeader']
        elif level == 2:
            style = self.styles['SubsectionHeader']
        else:
            style = self.styles['Heading3']

        # Add title
        title_para = Paragraph(title, style)
        self.story.append(title_para)

        # Add content if provided
        if content:
            content_para = Paragraph(content, self.styles['CustomBody'])
            self.story.append(content_para)
            self.story.append(Spacer(1, 5*mm))

    def add_paragraph(self, text: str, style_name: str = 'CustomBody'):
        """
        Add a paragraph to the report

        Args:
            text: Paragraph text (can include HTML tags)
            style_name: Style to use
        """
        para = Paragraph(text, self.styles[style_name])
        self.story.append(para)
        self.story.append(Spacer(1, 3*mm))

    def add_table(self, data: List[List], headers: Optional[List[str]] = None,
                  col_widths: Optional[List[float]] = None,
                  style: str = 'default'):
        """
        Add a table to the report

        Args:
            data: Table data as list of lists
            headers: Optional header row
            col_widths: Column widths in mm
            style: Table style ('default', 'grid', 'minimal')
        """
        # Prepare table data
        if headers:
            table_data = [headers] + data
        else:
            table_data = data

        # Convert column widths to points
        if col_widths:
            widths = [w * mm for w in col_widths]
        else:
            # Auto-calculate widths
            num_cols = len(table_data[0])
            available_width = self.width - self.margin_left - self.margin_right
            widths = [available_width / num_cols] * num_cols

        # Create table
        table = Table(table_data, colWidths=widths)

        # Apply style
        if style == 'default':
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ])
        elif style == 'grid':
            table_style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ])
        else:  # minimal
            table_style = TableStyle([
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ])

        table.setStyle(table_style)
        self.story.append(table)
        self.story.append(Spacer(1, 5*mm))

    def add_image(self, image_path: str, caption: str = "",
                  width: float = 150, height: Optional[float] = None):
        """
        Add an image to the report

        Args:
            image_path: Path to image file
            caption: Image caption
            width: Image width in mm
            height: Image height in mm (None for proportional)
        """
        if not os.path.exists(image_path):
            self.add_paragraph(f"[Image not found: {image_path}]", 'Caption')
            return

        try:
            if height:
                img = Image(image_path, width=width*mm, height=height*mm)
            else:
                img = Image(image_path, width=width*mm, height=width*mm, kind='proportional')

            img.hAlign = 'CENTER'
            self.story.append(img)

            if caption:
                caption_para = Paragraph(caption, self.styles['Caption'])
                self.story.append(caption_para)

            self.story.append(Spacer(1, 5*mm))
        except Exception as e:
            self.add_paragraph(f"[Error loading image: {str(e)}]", 'Caption')

    def add_spacer(self, height_mm: float = 5):
        """Add vertical space"""
        self.story.append(Spacer(1, height_mm * mm))

    def add_page_break(self):
        """Add a page break"""
        self.story.append(PageBreak())

    def add_bullet_list(self, items: List[str]):
        """
        Add a bulleted list

        Args:
            items: List of items
        """
        for item in items:
            bullet_text = f"• {item}"
            para = Paragraph(bullet_text, self.styles['CustomBody'])
            self.story.append(para)
        self.story.append(Spacer(1, 3*mm))

    def add_key_value_table(self, data: Dict[str, str], title: str = ""):
        """
        Add a key-value table (two columns)

        Args:
            data: Dictionary of key-value pairs
            title: Optional table title
        """
        if title:
            self.add_section(title, level=3)

        table_data = [[k, v] for k, v in data.items()]
        self.add_table(table_data, headers=["Parameter", "Value"],
                      col_widths=[80, 80], style='minimal')

    def build(self, header_footer: bool = True):
        """
        Build and save the PDF document

        Args:
            header_footer: Whether to include header and footer
        """
        # Create document
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=self.page_size,
            rightMargin=self.margin_right,
            leftMargin=self.margin_left,
            topMargin=self.margin_top + (self.header_height if header_footer else 0),
            bottomMargin=self.margin_bottom + (self.footer_height if header_footer else 0),
            title=self.title,
            author=self.author
        )

        # Build PDF
        if header_footer:
            doc.build(self.story, onFirstPage=self._add_header_footer,
                     onLaterPages=self._add_header_footer)
        else:
            doc.build(self.story)

    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to pages"""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.drawString(self.margin_left, self.height - 15*mm, self.title)
        canvas_obj.line(self.margin_left, self.height - 18*mm,
                       self.width - self.margin_right, self.height - 18*mm)

        # Footer
        canvas_obj.setFont('Helvetica', 9)
        footer_text = f"Page {doc.page}"
        canvas_obj.drawRightString(self.width - self.margin_right, 10*mm, footer_text)

        date_text = datetime.now().strftime('%Y-%m-%d')
        canvas_obj.drawString(self.margin_left, 10*mm, date_text)

        canvas_obj.restoreState()


def create_pdf_canvas(output_path: str, page_size: str = 'A4') -> canvas.Canvas:
    """
    Create a raw PDF canvas for low-level drawing

    Args:
        output_path: Path to save PDF
        page_size: Paper size

    Returns:
        Canvas object
    """
    size = A4 if page_size == 'A4' else letter
    return canvas.Canvas(output_path, pagesize=size)


def add_watermark(canvas_obj: canvas.Canvas, text: str, opacity: float = 0.1):
    """
    Add a watermark to a canvas

    Args:
        canvas_obj: Canvas object
        text: Watermark text
        opacity: Opacity (0-1)
    """
    canvas_obj.saveState()
    canvas_obj.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
    canvas_obj.setFont('Helvetica-Bold', 60)

    width, height = canvas_obj._pagesize
    canvas_obj.translate(width/2, height/2)
    canvas_obj.rotate(45)
    canvas_obj.drawCentredString(0, 0, text)

    canvas_obj.restoreState()
