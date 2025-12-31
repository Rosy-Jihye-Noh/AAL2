"""
PDF Generator for Request for Quotation (RFQ)
Generates professional PDF documents with ALIGNED branding
"""

import os
from datetime import datetime
from typing import Optional, List, Any
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class RFQPDFGenerator:
    """
    Generates Request for Quotation PDF with ALIGNED branding
    
    Layout:
    - Header: Logo + Bidding No + Date
    - Shipment Information
    - Route & Schedule
    - Cargo Details Table
    - Additional Services
    - Special Remarks
    - Quotation Deadline
    - Customer Information
    - Footer
    """
    
    # Brand Colors
    PRIMARY_COLOR = HexColor("#000000")      # Black - ALIGNED brand
    ACCENT_COLOR = HexColor("#3b82f6")       # Blue accent
    LIGHT_GRAY = HexColor("#f3f4f6")         # Light gray for backgrounds
    BORDER_COLOR = HexColor("#e5e7eb")       # Border gray
    TEXT_GRAY = HexColor("#6b7280")          # Text gray
    
    # Page settings
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN_LEFT = 20 * mm
    MARGIN_RIGHT = 20 * mm
    MARGIN_TOP = 20 * mm
    MARGIN_BOTTOM = 20 * mm
    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    
    def __init__(self, bidding_no: str, quote_request: Any, deadline: datetime):
        """
        Initialize PDF Generator
        
        Args:
            bidding_no: Bidding number (e.g., IMAIR00000)
            quote_request: QuoteRequest model instance
            deadline: Quotation submission deadline
        """
        self.bidding_no = bidding_no
        self.quote = quote_request
        self.deadline = deadline
        self.y_position = self.PAGE_HEIGHT - self.MARGIN_TOP
        
        # Get assets path
        self.assets_path = Path(__file__).parent / "assets"
        self.logo_path = self.assets_path / "aligned_logo.png"
        
    def generate(self, output_path: str) -> str:
        """
        Generate the RFQ PDF document
        
        Args:
            output_path: Path to save the generated PDF
            
        Returns:
            Path to the generated PDF file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create canvas
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # Draw all sections
        self._draw_header(c)
        self._draw_title(c)
        self._draw_shipment_info(c)
        self._draw_route_schedule(c)
        self._draw_cargo_table(c)
        self._draw_additional_services(c)
        self._draw_remarks(c)
        self._draw_deadline(c)
        self._draw_customer_info(c)
        self._draw_footer(c)
        
        # Save PDF
        c.save()
        
        return output_path
    
    def _draw_header(self, c: canvas.Canvas):
        """Draw header with logo, bidding no, and date"""
        y = self.PAGE_HEIGHT - self.MARGIN_TOP
        
        # Draw ALIGNED text logo (since we may not have the actual logo file)
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(self.PRIMARY_COLOR)
        
        # Draw cube icon placeholder (simple box)
        box_x = self.MARGIN_LEFT
        box_y = y - 5
        box_size = 18
        c.setStrokeColor(self.PRIMARY_COLOR)
        c.setLineWidth(2)
        # Draw a simple 3D cube representation
        c.line(box_x, box_y, box_x + box_size, box_y)
        c.line(box_x + box_size, box_y, box_x + box_size, box_y - box_size)
        c.line(box_x + box_size, box_y - box_size, box_x, box_y - box_size)
        c.line(box_x, box_y - box_size, box_x, box_y)
        # 3D effect lines
        c.line(box_x + 5, box_y + 5, box_x + box_size + 5, box_y + 5)
        c.line(box_x + box_size + 5, box_y + 5, box_x + box_size + 5, box_y - box_size + 5)
        c.line(box_x + box_size, box_y, box_x + box_size + 5, box_y + 5)
        c.line(box_x + box_size, box_y - box_size, box_x + box_size + 5, box_y - box_size + 5)
        
        # Draw ALIGNED text
        c.drawString(box_x + box_size + 12, y - 15, "ALIGNED")
        
        # Right side: Bidding No and Date
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(self.ACCENT_COLOR)
        bidding_text = f"Bidding No: {self.bidding_no}"
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN_RIGHT, y - 5, bidding_text)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.TEXT_GRAY)
        date_text = f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN_RIGHT, y - 18, date_text)
        
        # Draw separator line
        self.y_position = y - 35
        c.setStrokeColor(self.BORDER_COLOR)
        c.setLineWidth(1)
        c.line(self.MARGIN_LEFT, self.y_position, self.PAGE_WIDTH - self.MARGIN_RIGHT, self.y_position)
        
        self.y_position -= 25  # Increased spacing before title
    
    def _draw_title(self, c: canvas.Canvas):
        """Draw document title"""
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(self.PRIMARY_COLOR)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.y_position, "REQUEST FOR QUOTATION")
        self.y_position -= 30  # Increased spacing after title
    
    def _draw_section_header(self, c: canvas.Canvas, title: str):
        """Draw a section header with background"""
        # Background rectangle
        c.setFillColor(self.LIGHT_GRAY)
        c.rect(self.MARGIN_LEFT, self.y_position - 5, self.CONTENT_WIDTH, 18, fill=True, stroke=False)
        
        # Section title
        c.setFillColor(self.PRIMARY_COLOR)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.MARGIN_LEFT + 5, self.y_position, title)
        
        self.y_position -= 20
    
    def _draw_shipment_info(self, c: canvas.Canvas):
        """Draw shipment information section"""
        self._draw_section_header(c, "SHIPMENT INFORMATION")
        
        # Create info table
        data = [
            ["Trade Mode", self._format_trade_mode(self.quote.trade_mode)],
            ["Shipping Type", self._format_shipping_type(self.quote.shipping_type)],
            ["Load Type", self.quote.load_type or "N/A"],
            ["Incoterms", self.quote.incoterms or "N/A"],
        ]
        
        self._draw_info_table(c, data)
        self.y_position -= 10
    
    def _draw_route_schedule(self, c: canvas.Canvas):
        """Draw route and schedule section"""
        self._draw_section_header(c, "ROUTE & SCHEDULE")
        
        eta_str = self.quote.eta.strftime('%Y-%m-%d') if self.quote.eta else "N/A"
        etd_str = self.quote.etd.strftime('%Y-%m-%d') if self.quote.etd else "N/A"
        
        data = [
            ["Origin (POL)", self.quote.pol or "N/A"],
            ["Destination (POD)", self.quote.pod or "N/A"],
            ["ETD (Estimated Departure)", etd_str],
            ["ETA (Estimated Arrival)", eta_str],
        ]
        
        self._draw_info_table(c, data)
        self.y_position -= 10
    
    def _draw_cargo_table(self, c: canvas.Canvas):
        """Draw cargo details table"""
        self._draw_section_header(c, "CARGO DETAILS")
        
        cargo_details = self.quote.cargo_details if hasattr(self.quote, 'cargo_details') else []
        
        if not cargo_details:
            c.setFont("Helvetica", 9)
            c.setFillColor(self.TEXT_GRAY)
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, "No cargo details provided")
            self.y_position -= 20
            return
        
        # Determine table structure based on load type
        load_type = self.quote.load_type or ""
        
        if load_type in ["FCL"]:
            headers = ["No.", "Container Type", "G.Weight (KG)", "CBM", "Qty"]
            col_widths = [25, 120, 80, 60, 40]
            rows = [[
                str(i + 1),
                cargo.container_type or "N/A",
                self._format_number(cargo.gross_weight),
                self._format_number(cargo.cbm),
                str(cargo.qty or 1)
            ] for i, cargo in enumerate(cargo_details)]
        elif load_type == "Air":
            headers = ["No.", "L(cm)", "W(cm)", "H(cm)", "Qty", "G.W(kg)", "Vol.W", "C.W"]
            col_widths = [25, 45, 45, 45, 35, 55, 55, 55]
            rows = [[
                str(i + 1),
                str(cargo.length or 0),
                str(cargo.width or 0),
                str(cargo.height or 0),
                str(cargo.qty or 1),
                self._format_number(cargo.gross_weight),
                str(cargo.volume_weight or 0),
                str(cargo.chargeable_weight or 0)
            ] for i, cargo in enumerate(cargo_details)]
        elif load_type in ["FTL"]:
            headers = ["No.", "Truck Type", "Qty"]
            col_widths = [25, 200, 60]
            rows = [[
                str(i + 1),
                cargo.truck_type or "N/A",
                str(cargo.qty or 1)
            ] for i, cargo in enumerate(cargo_details)]
        else:  # LCL, LTL, Bulk, All
            headers = ["No.", "L(cm)", "W(cm)", "H(cm)", "Qty", "G.W(kg)", "CBM"]
            col_widths = [25, 50, 50, 50, 40, 65, 55]
            rows = [[
                str(i + 1),
                str(cargo.length or 0),
                str(cargo.width or 0),
                str(cargo.height or 0),
                str(cargo.qty or 1),
                self._format_number(cargo.gross_weight),
                self._format_number(cargo.cbm)
            ] for i, cargo in enumerate(cargo_details)]
        
        # Create table
        table_data = [headers] + rows
        table = Table(table_data, colWidths=col_widths)
        
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), self.ACCENT_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.PRIMARY_COLOR),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        # Calculate table height and draw
        table_width, table_height = table.wrap(0, 0)
        table.drawOn(c, self.MARGIN_LEFT, self.y_position - table_height)
        self.y_position -= (table_height + 10)
        
        # Draw DG info if applicable
        if self.quote.is_dg:
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(HexColor("#dc2626"))  # Red for DG
            dg_text = f"⚠ Dangerous Goods: Class {self.quote.dg_class or 'N/A'}, UN {self.quote.dg_un or 'N/A'}"
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, dg_text)
            self.y_position -= 15
        
        self.y_position -= 5
    
    def _draw_additional_services(self, c: canvas.Canvas):
        """Draw additional services section"""
        self._draw_section_header(c, "ADDITIONAL SERVICES REQUIRED")
        
        # Colors for checkmarks
        CHECK_GREEN = HexColor("#10b981")  # Green for YES
        CROSS_RED = HexColor("#9ca3af")    # Gray for NO
        
        # Service checkboxes - show all with V (YES) or X (NO)
        services = [
            ("Export Customs Clearance", self.quote.export_cc),
            ("Import Customs Clearance", self.quote.import_cc),
            ("Shipping Insurance", self.quote.shipping_insurance),
            ("Pickup Required", self.quote.pickup_required),
            ("Delivery Required", self.quote.delivery_required),
        ]
        
        x_pos = self.MARGIN_LEFT + 5
        
        for i, (label, checked) in enumerate(services):
            if i == 3:  # Move to second row after 3 items
                self.y_position -= 16
                x_pos = self.MARGIN_LEFT + 5
            
            # Draw check/cross mark
            if checked:
                # Green checkmark for YES
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(CHECK_GREEN)
                c.drawString(x_pos, self.y_position, "V")
                c.setFont("Helvetica", 9)
                c.setFillColor(self.PRIMARY_COLOR)
                c.drawString(x_pos + 12, self.y_position, label)
            else:
                # Gray X for NO
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(CROSS_RED)
                c.drawString(x_pos, self.y_position, "X")
                c.setFont("Helvetica", 9)
                c.setFillColor(self.TEXT_GRAY)
                c.drawString(x_pos + 12, self.y_position, label)
            
            x_pos += 125
        
        # Pickup/Delivery addresses if YES and address provided
        self.y_position -= 18
        
        if self.quote.pickup_required and self.quote.pickup_address:
            c.setFont("Helvetica", 8)
            c.setFillColor(self.PRIMARY_COLOR)
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, f"Pickup Address: {self.quote.pickup_address}")
            self.y_position -= 12
        
        if self.quote.delivery_required and self.quote.delivery_address:
            c.setFont("Helvetica", 8)
            c.setFillColor(self.PRIMARY_COLOR)
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, f"Delivery Address: {self.quote.delivery_address}")
            self.y_position -= 12
        
        # Invoice value
        c.setFillColor(self.PRIMARY_COLOR)
        c.setFont("Helvetica-Bold", 9)
        invoice_val = self._format_number(self.quote.invoice_value) if self.quote.invoice_value else "0"
        c.drawString(self.MARGIN_LEFT + 5, self.y_position, f"Invoice Value: USD {invoice_val}")
        
        self.y_position -= 15
    
    def _draw_remarks(self, c: canvas.Canvas):
        """Draw special remarks section"""
        self._draw_section_header(c, "SPECIAL REMARKS")
        
        remark = self.quote.remark or "No special remarks"
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.PRIMARY_COLOR)
        
        # Word wrap for long remarks
        max_width = self.CONTENT_WIDTH - 10
        lines = self._wrap_text(remark, max_width, c)
        
        for line in lines[:5]:  # Limit to 5 lines
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, line)
            self.y_position -= 12
        
        if len(lines) > 5:
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, "...")
            self.y_position -= 12
        
        self.y_position -= 5
    
    def _draw_deadline(self, c: canvas.Canvas):
        """Draw quotation deadline section"""
        self._draw_section_header(c, "QUOTATION DEADLINE")
        
        # Add spacing before the deadline box
        self.y_position -= 5
        
        # Deadline box with highlight - increased height
        box_height = 32
        c.setFillColor(HexColor("#fef3c7"))  # Light yellow background
        c.rect(self.MARGIN_LEFT, self.y_position - 12, self.CONTENT_WIDTH, box_height, fill=True, stroke=False)
        
        c.setStrokeColor(HexColor("#f59e0b"))  # Orange border
        c.setLineWidth(1)
        c.rect(self.MARGIN_LEFT, self.y_position - 12, self.CONTENT_WIDTH, box_height, fill=False, stroke=True)
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor("#b45309"))  # Dark orange text
        
        deadline_str = self.deadline.strftime('%Y-%m-%d %H:%M') if self.deadline else "N/A"
        c.drawString(self.MARGIN_LEFT + 10, self.y_position, f"Please submit your quotation by: {deadline_str} (KST)")
        
        # Increased spacing after deadline box
        self.y_position -= 45
    
    def _draw_customer_info(self, c: canvas.Canvas):
        """Draw customer information section - Company only (contact details are internal)"""
        self._draw_section_header(c, "REQUESTED BY")
        
        customer = self.quote.customer if hasattr(self.quote, 'customer') else None
        
        # Only show Company name - contact details are kept internal
        data = [
            ["Company", customer.company if customer else "N/A"],
        ]
        
        self._draw_info_table(c, data)
        self.y_position -= 10
    
    def _draw_footer(self, c: canvas.Canvas):
        """Draw footer with branding"""
        footer_y = self.MARGIN_BOTTOM + 20
        
        # Separator line
        c.setStrokeColor(self.BORDER_COLOR)
        c.setLineWidth(0.5)
        c.line(self.MARGIN_LEFT, footer_y + 25, self.PAGE_WIDTH - self.MARGIN_RIGHT, footer_y + 25)
        
        # ALIGNED logo (text version)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.PRIMARY_COLOR)
        c.drawCentredString(self.PAGE_WIDTH / 2, footer_y + 10, "ALIGNED")
        
        # Tagline
        c.setFont("Helvetica", 8)
        c.setFillColor(self.TEXT_GRAY)
        c.drawCentredString(self.PAGE_WIDTH / 2, footer_y, "AAL Platform - All About Logistics")
        
        # Page number (optional)
        c.setFont("Helvetica", 7)
        c.drawRightString(self.PAGE_WIDTH - self.MARGIN_RIGHT, footer_y - 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    def _draw_info_table(self, c: canvas.Canvas, data: List[List[str]]):
        """Draw a simple two-column info table"""
        c.setFont("Helvetica", 9)
        
        for label, value in data:
            # Label
            c.setFillColor(self.TEXT_GRAY)
            c.drawString(self.MARGIN_LEFT + 5, self.y_position, label)
            
            # Value
            c.setFillColor(self.PRIMARY_COLOR)
            c.drawString(self.MARGIN_LEFT + 130, self.y_position, str(value))
            
            self.y_position -= 14
    
    def _wrap_text(self, text: str, max_width: float, c: canvas.Canvas) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 9) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _format_trade_mode(self, trade_mode: str) -> str:
        """Format trade mode for display"""
        mapping = {
            "export": "Export",
            "import": "Import",
            "domestic": "Domestic"
        }
        return mapping.get(trade_mode, trade_mode.title())
    
    def _format_shipping_type(self, shipping_type: str) -> str:
        """Format shipping type for display"""
        mapping = {
            "ocean": "Ocean Freight",
            "air": "Air Freight",
            "truck": "Trucking",
            "all": "All (Ocean + Air)"
        }
        return mapping.get(shipping_type, shipping_type.title())
    
    def _format_number(self, value) -> str:
        """Format number with thousand separators"""
        if value is None:
            return "0"
        try:
            num = float(value)
            if num == int(num):
                return f"{int(num):,}"
            return f"{num:,.2f}"
        except (ValueError, TypeError):
            return str(value)
