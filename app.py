"""
Invoice Generator Web Application
A simple Flask app for generating professional invoices
"""

from flask import Flask, render_template, request, send_file, jsonify
from pathlib import Path
import json
from datetime import datetime, timedelta
import uuid
from invoice_generator_web import (
    InvoiceData, 
    OrderItem, 
    PDFInvoiceGenerator,
    COMPANY_INFO
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
INVOICE_DIR = Path("generated_invoices")
INVOICE_DIR.mkdir(exist_ok=True)

# Company settings file
SETTINGS_FILE = Path("company_config.json")


def load_company_settings():
    """Load company settings from JSON file or use defaults"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    # Return default COMPANY_INFO if file doesn't exist
    return COMPANY_INFO


def save_company_settings(settings):
    """Save company settings to JSON file"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    return True


def calculate_due_date(invoice_date: datetime, payment_terms: str) -> str:
    """Calculate due date based on payment terms"""
    # Extract number of days from payment terms
    if "Immediate" in payment_terms:
        days = 0
    elif "7" in payment_terms:
        days = 7
    elif "14" in payment_terms:
        days = 14
    elif "30" in payment_terms:
        days = 30
    elif "60" in payment_terms:
        days = 60
    elif "90" in payment_terms:
        days = 90
    else:
        days = 30  # Default to 30 days
    
    due_date = invoice_date + timedelta(days=days)
    return due_date.strftime("%d.%m.%Y")


@app.route('/')
def index():
    """Main page - invoice form"""
    return render_template('index.html')


@app.route('/settings')
def settings():
    """Company settings page"""
    return render_template('settings.html')


@app.route('/api/company-settings', methods=['GET'])
def get_company_settings():
    """Get current company settings"""
    try:
        settings = load_company_settings()
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/company-settings', methods=['POST'])
def update_company_settings():
    """Update company settings"""
    try:
        settings = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'address_line', 'uid', 'court', 'bank', 'iban']
        for field in required_fields:
            if field not in settings or not settings[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Save settings
        save_company_settings(settings)
        
        return jsonify({
            'success': True,
            'message': 'Company settings saved successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-invoice', methods=['POST'])
def generate_invoice():
    """
    API endpoint to generate invoice PDF
    Accepts JSON data from form submission
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['buyer_name', 'buyer_country', 'items']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate items
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'At least one item is required'}), 400
        
        # Parse items
        items = []
        for idx, item_data in enumerate(data['items']):
            try:
                quantity = int(item_data.get('quantity', 1))
                unit_price = float(item_data.get('unit_price', 0))
                unit_code = item_data.get('unit_code', 'C62')
                
                # Calculate item total
                item_total = quantity * unit_price
                
                items.append(OrderItem(
                    product_name=item_data.get('product_name', f'Item {idx + 1}'),
                    asin='N/A',
                    sku=item_data.get('sku', f'SKU-{idx + 1}'),
                    quantity=quantity,
                    unit_price_excl=unit_price,
                    unit_price_incl=unit_price,
                    item_subtotal_excl=item_total,
                    item_subtotal_incl=item_total,
                    item_total=item_total,
                    unit_code=unit_code
                ))
            except (ValueError, KeyError) as e:
                return jsonify({'error': f'Invalid item data at position {idx + 1}: {str(e)}'}), 400
        
        # Calculate totals
        item_subtotal = sum(item.item_total for item in items)
        shipping_total = float(data.get('shipping_total', 0))
        vat_rate = float(data.get('vat_rate', 0.19))  # Default 19%
        
        # Calculate VAT
        net_total = item_subtotal + shipping_total
        gross_total = net_total * (1 + vat_rate)
        vat_amount = gross_total - net_total
        
        # Generate order ID
        order_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Get payment terms and calculate due date
        payment_terms = data.get('payment_terms', 'Net 30')
        invoice_date = datetime.now()
        due_date = calculate_due_date(invoice_date, payment_terms)
        
        # Create invoice data
        invoice_data = InvoiceData(
            order_id=order_id,
            seller_order_id=order_id,
            purchase_date=invoice_date.strftime("%d.%m.%Y"),
            purchase_time=invoice_date.strftime("%H:%M"),
            buyer_name=data.get('buyer_name'),
            buyer_contact_name=data.get('buyer_name').split()[0] if data.get('buyer_name') else 'Customer',
            buyer_street=data.get('buyer_street', ''),
            buyer_city=data.get('buyer_city', ''),
            buyer_postal=data.get('buyer_postal', ''),
            buyer_country=data.get('buyer_country'),
            items=items,
            item_subtotal=net_total,
            shipping_total=shipping_total,
            vat_amount=vat_amount,
            grand_total=gross_total,
            fulfillment='Manual',
            sales_channel='Web',
            shipping_service=data.get('shipping_service', 'Standard'),
            status='Generated',
            vat_rate=vat_rate,
            currency=data.get('currency', '€'),
            vat_id=data.get('vat_id', None),
            promotion_discount=0.0,
            # EN 16931 Fields
            buyer_vat_id=data.get('buyer_vat_id', None),
            due_date=due_date,
            invoice_type_code="380",  # Commercial invoice
            payment_means=data.get('payment_means', 'Credit transfer'),
            payment_terms=payment_terms,
            payment_reference=data.get('payment_reference', order_id)
        )
        
        # Generate PDF with current company settings
        company_settings = load_company_settings()
        generator = PDFInvoiceGenerator(company_info=company_settings)
        
        # Create filename
        day = datetime.now().strftime("%d")
        country_code = data.get('buyer_country', 'XX')[:2].upper()
        buyer_first_name = invoice_data.buyer_contact_name
        pdf_filename = f"{day}_{country_code}_{buyer_first_name}.pdf"
        
        output_path = INVOICE_DIR / pdf_filename
        
        success = generator.generate(invoice_data, output_path)
        
        if not success:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        return jsonify({
            'success': True,
            'invoice_id': order_id,
            'filename': pdf_filename,
            'download_url': f'/download/{pdf_filename}'
        })
        
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_invoice(filename):
    """Download generated invoice PDF"""
    try:
        file_path = INVOICE_DIR / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview/<filename>')
def preview_invoice(filename):
    """Preview invoice PDF in browser"""
    try:
        file_path = INVOICE_DIR / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print("=" * 60)
        print("🚀 Invoice Generator Web App Starting...")
        print("=" * 60)
        print(f"📝 Access the invoice generator at: http://localhost:{port}")
        print("=" * 60)
    
    app.run(debug=debug, host='0.0.0.0', port=port)
