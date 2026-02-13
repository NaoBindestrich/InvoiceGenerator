"""
Simplified Invoice Generator for Web Application
Contains only PDF generation logic (no web scraping)
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# Company Configuration (customizable)
COMPANY_INFO = {
    "name": "Your Company Name",
    "address_line": "Your Company Address",
    "court": "Registration Details",
    "uid": "Tax/VAT ID",
    "control": "Additional Info",
    "bank": "Bank Name",
    "iban": "IBAN Number",
    "bic": "BIC/SWIFT Code",
    "company_registration": "Company Registration Number",
    "vat_id": "VAT ID Number"
}


@dataclass
class OrderItem:
    """Represents a single item in an invoice"""
    product_name: str
    asin: str
    sku: str
    quantity: int
    unit_price_excl: float
    unit_price_incl: float
    item_subtotal_excl: float
    item_subtotal_incl: float
    item_total: float
    unit_code: str = "C62"  # C62 = units, HUR = hours, DAY = days, etc.


@dataclass
class InvoiceData:
    """Complete invoice data structure"""
    order_id: str
    seller_order_id: str
    purchase_date: str
    purchase_time: str
    buyer_name: str
    buyer_contact_name: str
    buyer_street: str
    buyer_city: str
    buyer_postal: str
    buyer_country: str
    items: List[OrderItem]
    item_subtotal: float
    shipping_total: float
    vat_amount: float
    grand_total: float
    fulfillment: str
    sales_channel: str
    shipping_service: str
    status: str
    vat_rate: float
    currency: str = "€"
    vat_id: str = None
    promotion_discount: float = 0.0
    # EN 16931 Required Fields
    buyer_vat_id: str = None
    due_date: str = None
    invoice_type_code: str = "380"  # 380 = Commercial invoice
    payment_means: str = "Credit transfer"
    payment_terms: str = "Net 30"
    payment_reference: str = None


class PDFInvoiceGenerator:
    """Generates professional invoices in PDF format"""
    
    PAGE_HEIGHT = 842.0
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    
    def __init__(self, company_info: Dict = None):
        """
        Initialize generator with company information
        
        Args:
            company_info: Dictionary with company details (uses COMPANY_INFO if None)
        """
        self.company_info = company_info or COMPANY_INFO

    def _to_pdf_y(self, user_y, height=0):
        """Convert Top-Left user coordinate to Bottom-Left PDF coordinate"""
        return self.PAGE_HEIGHT - user_y - height

    def _translate_country_to_german(self, country: str) -> str:
        """Translate English country names to German for invoice display"""
        translations = {
            "Germany": "Deutschland",
            "Austria": "Österreich",
            "Switzerland": "Schweiz",
            "France": "Frankreich",
            "Italy": "Italien",
            "Spain": "Spanien",
            "Netherlands": "Niederlande",
            "Belgium": "Belgien",
            "Luxembourg": "Luxemburg",
            "Poland": "Polen",
            "Czech Republic": "Tschechien",
            "Czechia": "Tschechien",
            "Hungary": "Ungarn",
            "Romania": "Rumänien",
            "Bulgaria": "Bulgarien",
            "Slovakia": "Slowakei",
            "Slovenia": "Slowenien",
            "Croatia": "Kroatien",
            "Lithuania": "Litauen",
            "Latvia": "Lettland",
            "Estonia": "Estland",
            "Greece": "Griechenland",
            "Portugal": "Portugal",
            "Ireland": "Irland",
            "Denmark": "Dänemark",
            "Sweden": "Schweden",
            "Finland": "Finnland",
            "Norway": "Norwegen",
            "Iceland": "Island",
            "United Kingdom": "Vereinigtes Königreich",
            "Great Britain": "Großbritannien",
            "England": "England",
            "Scotland": "Schottland",
            "Wales": "Wales",
            "Northern Ireland": "Nordirland",
            "Cyprus": "Zypern",
            "Malta": "Malta",
        }
        return translations.get(country, country)

    def _format_price(self, amount: float, currency: str = "€") -> str:
        """Format price with proper decimal separator and currency"""
        s = f"{amount:.2f}".replace('.', ',')
        if currency in ["kr", "SEK", "DKK", "NOK"]:
            return f"{s} {currency}"
        elif currency == "£":
            return f"£{s}"
        elif currency == "$":
            return f"${s}"
        return f"{currency} {s}"

    def generate(self, invoice_data: InvoiceData, output_path: Path) -> bool:
        """
        Generate invoice PDF
        
        Args:
            invoice_data: InvoiceData object with all invoice details
            output_path: Path where PDF should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            c = canvas.Canvas(str(output_path), pagesize=A4)
            c.setFont(self.FONT_NORMAL, 10)
            
            # Generate invoice date (current date in DD.MM.YYYY format)
            invoice_date = datetime.now().strftime("%d.%m.%Y")
            
            # --- Logo Section ---
            logo_x = 447.42
            logo_y_user = 33.45
            logo_w = 97.35
            logo_h = 24.66
            logo_y_pdf = self._to_pdf_y(logo_y_user, logo_h)
            
            # Draw logo or company name
            logo_path = Path("company_logo.png")
            if logo_path.exists():
                c.drawImage(str(logo_path), logo_x, logo_y_pdf, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
            else:
                c.saveState()
                c.setFillColor(colors.black)
                c.setFont(self.FONT_BOLD, 16)
                c.drawString(logo_x + 10, logo_y_pdf + 8, self.company_info["name"][:10].upper())
                c.restoreState()
            
            # --- Delivery Address Block ---
            addr_start_y = 91.75
            
            c.setFont(self.FONT_NORMAL, 7)
            c.drawString(57.58, self._to_pdf_y(addr_start_y), "Lieferadresse:")
            
            c.setFont(self.FONT_NORMAL, 10)
            text_obj = c.beginText(57.58, self._to_pdf_y(addr_start_y + 12))
            text_obj.textLine(invoice_data.buyer_name)
            if invoice_data.buyer_street:
                for street_line in invoice_data.buyer_street.split('\n'):
                    text_obj.textLine(street_line)
            text_obj.textLine(f"{invoice_data.buyer_postal} {invoice_data.buyer_city}")
            country_german = self._translate_country_to_german(invoice_data.buyer_country)
            text_obj.textLine(country_german.upper())
            c.drawText(text_obj)
            
            # --- Sender Line ---
            sender_y_user = 172.26
            sender_y_pdf = self._to_pdf_y(sender_y_user) - 6
            
            c.setFont(self.FONT_NORMAL, 6)
            c.drawString(56.16, sender_y_pdf, f"Abs.: {self.company_info['address_line']}")
            
            line_y_user = 180.345
            line_y_pdf = self._to_pdf_y(line_y_user)
            c.setLineWidth(0.75)
            c.line(56.16, line_y_pdf, 269.15, line_y_pdf)
            
            # --- Billing Address ---
            billing_y = 199.55
            text_obj = c.beginText(57.58, self._to_pdf_y(billing_y) - 9)
            text_obj.setFont(self.FONT_NORMAL, 10)
            
            billing_address_lines = 1
            if invoice_data.buyer_street:
                billing_address_lines += len([line for line in invoice_data.buyer_street.split('\n') if line.strip()])
            billing_address_lines += 2
            if invoice_data.buyer_vat_id:
                billing_address_lines += 1
            
            text_obj.textLine(invoice_data.buyer_name)
            if invoice_data.buyer_street:
                for street_line in invoice_data.buyer_street.split('\n'):
                    text_obj.textLine(street_line)
            text_obj.textLine(f"{invoice_data.buyer_postal} {invoice_data.buyer_city}")
            text_obj.textLine(country_german.upper())
            if invoice_data.buyer_vat_id:
                text_obj.textLine(f"USt-IdNr: {invoice_data.buyer_vat_id}")
            c.drawText(text_obj)
            
            # --- Title & Meta Section ---
            title_y_base = 243.63
            line_height = 12
            billing_address_height = billing_address_lines * line_height
            min_spacing_after_address = 15
            
            billing_end_y = billing_y + billing_address_height
            required_title_y = billing_end_y + min_spacing_after_address
            title_y = max(title_y_base, required_title_y)
            
            c.setFont(self.FONT_BOLD, 18)
            c.drawString(57.58, self._to_pdf_y(title_y) - 14, "Rechnung")
            
            layout_shift = title_y - 243.63
            if layout_shift < 0:
                layout_shift = 0
            
            # Meta information
            label_x = 57.58
            value_x = 168.164
            
            c.setFont(self.FONT_NORMAL, 9)
            
            y1 = self._to_pdf_y(title_y + 29.007)
            c.drawString(label_x, y1, "Rechnung")
            c.drawString(value_x, y1, invoice_data.order_id)
            
            y2 = self._to_pdf_y(title_y + 40.346)
            c.drawString(label_x, y2, "Rechnungsdatum")
            c.drawString(value_x, y2, invoice_date)
            
            y3 = self._to_pdf_y(title_y + 51.836)
            c.drawString(label_x, y3, "Bestelldatum")
            c.drawString(value_x, y3, invoice_data.purchase_date)
            
            y4 = self._to_pdf_y(title_y + 62.966)
            c.drawString(label_x, y4, "Fälligkeitsdatum")
            c.drawString(value_x, y4, invoice_data.due_date)
            
            y5 = self._to_pdf_y(title_y + 74.817)
            c.drawString(label_x, y5, "Zahlart")
            c.drawString(value_x, y5, invoice_data.payment_means or invoice_data.sales_channel)
            
            y_ord = self._to_pdf_y(365.0 + layout_shift)
            c.drawString(56.16, y_ord, f"Bestellnummer: {invoice_data.order_id}")
            
            # --- Items Table ---
            header_rect_y_user = 376.106 + layout_shift
            header_h = 18.0
            header_rect_y_pdf = self._to_pdf_y(header_rect_y_user, header_h)
            
            c.setFillColorRGB(0.9, 0.9, 0.9)
            c.rect(56.16, header_rect_y_pdf, 494.362, header_h, fill=1, stroke=0)
            c.setFillColor(colors.black)
            
            target_top_y = self._to_pdf_y(376.106 + layout_shift)
            target_bot_y = self._to_pdf_y(394.248 + layout_shift)
            
            c.setLineWidth(0.75)
            c.line(56.16, target_top_y, 56.16 + 494.36, target_top_y)
            c.line(56.16, target_bot_y, 56.16 + 494.36, target_bot_y)
            
            header_text_y = self._to_pdf_y(379.90 + layout_shift) - 7
            
            cols = [
                (65.57, "Pos"),
                (93.01, "Nummer"),
                (175.22, "Artikel"),
                (398.06, "Anzahl"),
                (467.36, "Preis"),
                (508.70, "Summe")
            ]
            
            for i, (x, title) in enumerate(cols):
                if title in ["Anzahl", "Preis", "Summe"]:
                    c.drawRightString(x + 40, header_text_y, title)
                else:
                    c.drawString(x, header_text_y, title)
            
            # Draw items
            current_y_user = 395.00 + layout_shift
            
            for i, item in enumerate(invoice_data.items, 1):
                y_pos = self._to_pdf_y(current_y_user) - 9
                
                c.drawString(cols[0][0], y_pos, str(i))
                c.drawString(cols[1][0], y_pos, item.sku)
                c.drawString(cols[2][0], y_pos, item.product_name[:45])
                
                c.drawRightString(435.0, y_pos, f"{item.quantity},00")
                c.drawRightString(505.0, y_pos, self._format_price(item.unit_price_incl, invoice_data.currency))
                c.drawRightString(547.62, y_pos, self._format_price(item.item_total, invoice_data.currency))
                
                line_y = self._to_pdf_y(current_y_user + 25.20)
                c.line(56.16, line_y, 550.52, line_y)
                
                current_y_user += 25.20
            
            # --- Totals ---
            label_x_totals = 332.81
            value_right_x = 547.62
            
            item_count_shift = (len(invoice_data.items) - 1) * 25.20
            
            def draw_total_row_fixed(user_y, label, val_str, bold=False):
                y = self._to_pdf_y(user_y + layout_shift + item_count_shift) - 8
                if bold:
                    c.setFont(self.FONT_BOLD, 9)
                else:
                    c.setFont(self.FONT_NORMAL, 9)
                
                c.drawString(label_x_totals, y, label)
                c.drawRightString(value_right_x, y, val_str)
            
            vat_percent = f"{invoice_data.vat_rate*100:.1f}".replace('.', ',') + "%"
            
            item_gross = sum(item.item_total for item in invoice_data.items)
            has_promotion = invoice_data.promotion_discount > 0
            
            if has_promotion:
                item_net_before_discount = item_gross / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else item_gross
                discount_net = invoice_data.promotion_discount
                item_net = item_net_before_discount - discount_net
            else:
                item_net = item_gross / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else item_gross
            
            shipping_net = invoice_data.shipping_total / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else invoice_data.shipping_total
            total_net = item_net + shipping_net
            
            if has_promotion:
                draw_total_row_fixed(425.33, "Zwischensumme (netto)", self._format_price(item_net_before_discount, invoice_data.currency))
                draw_total_row_fixed(439.65, "Rabatt", "-" + self._format_price(discount_net, invoice_data.currency))
                draw_total_row_fixed(453.95, "Versand", self._format_price(invoice_data.shipping_total, invoice_data.currency))
                draw_total_row_fixed(468.12, "Gesamt netto", self._format_price(total_net, invoice_data.currency))
                draw_total_row_fixed(482.29, f"Umsatzsteuer ({vat_percent})", self._format_price(invoice_data.vat_amount, invoice_data.currency))
                draw_total_row_fixed(501.97, "Gesamtsumme", self._format_price(invoice_data.grand_total, invoice_data.currency), bold=True)
            else:
                draw_total_row_fixed(425.33, "Zwischensumme (netto)", self._format_price(item_net, invoice_data.currency))
                draw_total_row_fixed(439.65, "Versand", self._format_price(invoice_data.shipping_total, invoice_data.currency))
                draw_total_row_fixed(453.95, "Gesamt netto", self._format_price(total_net, invoice_data.currency))
                draw_total_row_fixed(468.12, f"Umsatzsteuer ({vat_percent})", self._format_price(invoice_data.vat_amount, invoice_data.currency))
                draw_total_row_fixed(487.97, "Gesamtsumme", self._format_price(invoice_data.grand_total, invoice_data.currency), bold=True)
            
            # --- Thank You Message ---
            ty_y = self._to_pdf_y(542.24 + layout_shift + item_count_shift) - 8
            c.setFont(self.FONT_NORMAL, 8)
            c.drawString(57.58, ty_y, "Vielen Dank für Ihre Bestellung!")
            c.drawString(57.58, ty_y - 12, "Thank you for your order!")
            
            # --- SKU Reference ---
            sku_section_y = ty_y - 36
            c.setFont(self.FONT_BOLD, 8)
            c.drawString(57.58, sku_section_y, "Artikelnummern (SKU):")
            
            c.setFont(self.FONT_NORMAL, 8)
            current_sku_y = sku_section_y - 12
            for item in invoice_data.items:
                sku_info = f"{item.sku} - {item.product_name[:60]}"
                c.drawString(57.58, current_sku_y, sku_info)
                current_sku_y -= 10
            
            # --- Footer ---
            footer_y = self._to_pdf_y(773.29) - 8
            
            text_obj = c.beginText(56.16, footer_y)
            text_obj.setFont(self.FONT_NORMAL, 8)
            text_obj.setLeading(10)
            text_obj.textLine(self.company_info["control"])
            text_obj.textLine(f"Bankverbindung: {self.company_info['bank']}")
            text_obj.textLine(f"IBAN: {self.company_info['iban']}")
            if self.company_info.get('bic'):
                text_obj.textLine(f"BIC: {self.company_info['bic']}")
            if invoice_data.payment_terms:
                text_obj.textLine(f"Zahlungsbedingungen: {invoice_data.payment_terms}")
            if invoice_data.payment_reference:
                text_obj.textLine(f"Verwendungszweck: {invoice_data.payment_reference}")
            c.drawText(text_obj)
            
            text_obj = c.beginText(304.56, footer_y)
            text_obj.setFont(self.FONT_NORMAL, 8)
            text_obj.setLeading(10)
            text_obj.textLine(self.company_info["court"])
            text_obj.textLine(f"UID: {self.company_info['uid']}")
            if self.company_info.get('vat_id'):
                text_obj.textLine(f"USt-IdNr: {self.company_info['vat_id']}")
            if self.company_info.get('company_registration'):
                text_obj.textLine(f"Registrierung: {self.company_info['company_registration']}")
            if self.company_info.get('ceo'):
                text_obj.textLine(f"Geschäftsführung: {self.company_info['ceo']}")
            c.drawText(text_obj)
            
            # Copyright notice at bottom
            copyright_y = 20
            c.setFont(self.FONT_NORMAL, 7)
            c.setFillColor(colors.grey)
            c.drawCentredString(297.64, copyright_y, "© 2026 Invoice Generator. All rights reserved.")
            
            c.showPage()
            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
