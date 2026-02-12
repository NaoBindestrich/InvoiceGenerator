import re
import time
import random
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# Logging configuration - set to False to reduce console output
VERBOSE_LOGGING = False

def _log(message: str, force: bool = False):
    """Print message only if verbose logging is enabled or forced"""
    if VERBOSE_LOGGING or force:
        print(message)

# Hardcoded Tasnim Configuration
TASNIM_INFO = {
    "name": "Tasnim e.U.",
    "address_line": "Tasnim e.U., Ullmannstrasse 22, 1150 Vienna, Austria",
    "court": "Handelsgericht Wien, FN 330337s",
    "uid": "ATU64180745, DE322543231",
    "ceo": "Adam Landsberg",
    "control": "Kontrollstellencode (AT-BIO-902)",
    "bank": "Erste Bank",
    "iban": "AT72 2011 1296 2471 9301"
}

# VAT Configuration
VAT_CONFIG_FILE = Path(__file__).parent / "vat_config.json"
VAT_CONFIG_CACHE = None

def load_vat_config() -> Dict:
    """Load VAT configuration from JSON file."""
    global VAT_CONFIG_CACHE
    
    if VAT_CONFIG_CACHE is not None:
        return VAT_CONFIG_CACHE
    
    if not VAT_CONFIG_FILE.exists():
        print(f"⚠ VAT config file not found: {VAT_CONFIG_FILE}")
        print(f"   Using default keyword-based configuration. Run vat_config_generator.py to create config.")
        # Return default config (empty lists, will use fallback logic)
        VAT_CONFIG_CACHE = {
            "type": "sku-based",
            "reduced_rate_skus": [],
            "standard_rate_skus": [],
            "sku_to_product": {},
            "reduced_rate_keywords": [],
            "standard_rate_keywords": []
        }
        return VAT_CONFIG_CACHE
    
    try:
        with open(VAT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            VAT_CONFIG_CACHE = json.load(f)
            config_type = VAT_CONFIG_CACHE.get('type', 'keyword-based')
            _log(f"✓ Loaded VAT configuration from {VAT_CONFIG_FILE} (type: {config_type})", force=True)
            if 'statistics' in VAT_CONFIG_CACHE:
                stats = VAT_CONFIG_CACHE['statistics']
                if config_type == 'sku-based':
                    _log(f"   SKU-based: {stats.get('total_products', 0)} products")
                    _log(f"   Reduced rate: {stats.get('reduced_rate_count', 0)}")
                    _log(f"   Standard rate: {stats.get('standard_rate_count', 0)}")
                    _log(f"   Fallback keywords: {stats.get('total_keywords', 0)}")
                elif config_type == 'keyword-based':
                    _log(f"   Total keywords: {stats.get('total_keywords', 0)}")
                    _log(f"   Reduced rate: {stats.get('reduced_rate_count', 0)}")
                    _log(f"   Standard rate: {stats.get('standard_rate_count', 0)}")
                else:
                    _log(f"   Total products: {stats.get('total_products', 0)}")
                    _log(f"   Reduced rate: {stats.get('reduced_rate_count', 0)}")
                    _log(f"   Standard rate: {stats.get('standard_rate_count', 0)}")
            return VAT_CONFIG_CACHE
    except Exception as e:
        print(f"⚠ Error loading VAT config: {e}")
        print(f"   Using default configuration.")
        VAT_CONFIG_CACHE = {
            "type": "sku-based",
            "reduced_rate_skus": [],
            "standard_rate_skus": [],
            "sku_to_product": {},
            "reduced_rate_keywords": [],
            "standard_rate_keywords": []
        }
        return VAT_CONFIG_CACHE

@dataclass
class OrderItem:
    """Represents a single item in an order"""
    product_name: str
    asin: str
    sku: str
    quantity: int
    unit_price_excl: float
    unit_price_incl: float
    item_subtotal_excl: float
    item_subtotal_incl: float
    item_total: float

@dataclass
class InvoiceData:
    """Complete invoice data structure"""
    order_id: str
    seller_order_id: str
    purchase_date: str
    purchase_time: str
    buyer_name: str
    buyer_contact_name: str  # Contact buyer name for filename
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
    promotion_discount: float = 0.0  # Item promotion/discount amount


class OrderScraper:
    """Scrapes order details from Amazon order page"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
    
    def random_delay(self, min_sec=0.5, max_sec=1.5):
        """Add random delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def scrape_order_details(self, order_id: str) -> Optional[InvoiceData]:
        """
        Navigate to order details page and extract all invoice information.
        """
        try:
            order_url = f"https://sellercentral.amazon.de/orders-v3/order/{order_id}"
            _log(f"   🔗 Opening order details: {order_url}")
            self.driver.get(order_url)
            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='order-id-value']"))
            )
            self.random_delay(1, 2)
            
            # Extract order information
            extracted_order_id = self._extract_text("[data-test-id='order-id-value']")
            purchase_date_full = self._extract_text("[data-test-id='order-summary-purchase-date-value']")
            fulfillment = self._extract_text("[data-test-id='order-summary-fulfillment-channel-value']")
            sales_channel = self._extract_text("[data-test-id='order-summary-sales-channel-value']")
            shipping_service = self._extract_text("[data-test-id='order-summary-shipping-service-value']")
            
            # Extract buyer information
            # Contact buyer name (for filename) vs full name from address (for invoice)
            buyer_contact_name = self._extract_text("[data-test-id='shipping-section-contact-buyer-value']") or "Unknown"
            # Remove any HTML tags or extra formatting from contact name
            buyer_contact_name = buyer_contact_name.strip().split('\n')[0] if buyer_contact_name else "Unknown"
            
            buyer_address = self._extract_text("[data-test-id='shipping-section-buyer-address']")
            
            # Parse buyer address
            address_lines = [line.strip() for line in buyer_address.split("\n") if line.strip()]
            
            # Extract full name from first line of address (for invoice display)
            buyer_name = address_lines[0] if address_lines else buyer_contact_name
            
            # Identify country (usually last line)
            if address_lines:
                buyer_country = address_lines[-1]
                
                # Handle different address formats
                # Format 1: [Name] [Street] [Postal City] [Country]
                # Format 2: [Name] [Street] [City] [Postal] [Country] (French style)
                if len(address_lines) >= 3:
                    # Check if second-to-last line is just a postal code
                    postal_line = address_lines[-2]
                    if postal_line.strip().replace(' ', '').isdigit():
                        # Format 2: Postal code on separate line
                        buyer_postal = postal_line.strip()
                        buyer_city = address_lines[-3] if len(address_lines) >= 4 else ""
                        # Street is everything except first line (name), city, postal, and country
                        buyer_street = "\n".join(address_lines[1:-3]) if len(address_lines) > 4 else ""
                    else:
                        # Format 1: Try to parse "Postal City" from second-to-last line
                        city_zip = postal_line
                        parts = city_zip.split()
                        if parts and parts[0].replace('-', '').isdigit():
                            buyer_postal = parts[0]
                            buyer_city = " ".join(parts[1:])
                        elif parts and parts[-1].replace('-', '').isdigit():
                            buyer_postal = parts[-1]
                            buyer_city = " ".join(parts[:-1])
                        else:
                            buyer_postal = ""
                            buyer_city = city_zip
                        # Street is everything except first line (name) and last 2 lines (city/postal, country)
                        buyer_street = "\n".join(address_lines[1:-2]) if len(address_lines) > 3 else ""
                elif len(address_lines) >= 2:
                    # Only name and country, no street
                    buyer_street = ""
                    buyer_city = ""
                    buyer_postal = ""
                else:
                    buyer_street = address_lines[0] if address_lines else ""
                    buyer_city = ""
                    buyer_postal = ""
            else:
                buyer_street = ""
                buyer_city = ""
                buyer_postal = ""
                buyer_country = ""

            
            # Extract items
            items = self._extract_items()
            
            # Extract financial information (pass items to determine VAT rate)
            item_subtotal, shipping_total, vat_amount, grand_total, status, vat_rate, currency, promotion_discount = self._extract_financial_info(buyer_country, items)
            
            # Parse purchase date from "Sun, 2 Nov 2025, 15:20 MET" to "02.11.2025"
            purchase_date_str = self._parse_purchase_date(purchase_date_full)
            
            invoice_data = InvoiceData(
                order_id=extracted_order_id,
                seller_order_id=extracted_order_id,
                purchase_date=purchase_date_str,
                purchase_time="",
                buyer_name=buyer_name,
                buyer_contact_name=buyer_contact_name,
                buyer_street=buyer_street,
                buyer_city=buyer_city,
                buyer_postal=buyer_postal,
                buyer_country=buyer_country,
                items=items,
                item_subtotal=item_subtotal,
                shipping_total=shipping_total,
                vat_amount=vat_amount,
                grand_total=grand_total,
                fulfillment=fulfillment,
                sales_channel=sales_channel,
                shipping_service=shipping_service,
                status=status,
                vat_rate=vat_rate,
                currency=currency,
                promotion_discount=promotion_discount,
            )
            
            _log(f"   ✔ Successfully scraped order {extracted_order_id}")
            return invoice_data
            
        except Exception as e:
            print(f"   ❗ Failed to scrape order details: {e}")  # Keep error visible
            return None
    
    def _extract_text(self, selector: str) -> str:
        """Safely extract text from element"""
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            return elem.text.strip()
        except:
            return ""
    
    def _extract_items(self) -> List[OrderItem]:
        """Extract all items from order contents table"""
        items = []
        seen_asins = set()  # Track ASINs to avoid duplicates from Package table
        try:
            # Only get the FIRST a-keyvalue table (Order contents), not Package tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table.a-keyvalue")
            if not tables:
                _log(f"   ⚠ No item tables found")
                return []
            
            # Use only the first table (Order contents)
            order_table = tables[0]
            rows = order_table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                try:
                    # Extract product name
                    product_elem = row.find_element(By.CSS_SELECTOR, "div.myo-list-orders-product-name-cell div a")
                    product_name = product_elem.text.strip()
                    
                    # Extract ASIN and SKU from row text
                    row_text = row.text
                    asin_match = re.search(r'ASIN:\s*([A-Z0-9]+)', row_text)
                    asin = asin_match.group(1) if asin_match else "N/A"
                    
                    sku_match = re.search(r'SKU:\s*([^\n]+)', row_text)
                    sku = sku_match.group(1).strip() if sku_match else "N/A"
                    
                    # Extract quantity from the dedicated quantity cell
                    quantity = 1
                    qty_cells = row.find_elements(By.CSS_SELECTOR, "td")
                    for cell in qty_cells:
                        cell_text = cell.text.strip()
                        if cell_text.isdigit() and int(cell_text) < 100:  # Reasonable quantity limit
                            quantity = int(cell_text)
                            break
                    
                    # Extract prices from the specific price columns (not the whole row)
                    # The table has specific columns for unit prices:
                    # - data-test-id="item-unit-price-exclusive-heading" -> VAT exclusive
                    # - data-test-id="item-unit-price-inclusive-heading" -> VAT inclusive
                    # These columns have class "a-text-right"
                    
                    unit_price_excl = 0.0
                    unit_price_incl = 0.0
                    
                    # Find all td cells with class "a-text-right" that contain a single price
                    price_cells = row.find_elements(By.CSS_SELECTOR, "td.a-text-right")
                    
                    # Extract prices from the first two price cells (excl and incl)
                    # These cells should contain ONLY the unit price, not the VAT breakdown
                    price_pattern = r'€\s*([\d.,]+)'
                    
                    extracted_prices = []
                    for cell in price_cells:
                        cell_text = cell.text.strip()
                        # Skip cells that contain VAT breakdown info (Proceeds column)
                        if 'subtotal' in cell_text.lower() or 'Item total' in cell_text:
                            continue
                        # Extract the FIRST price from the cell (ignore "Business Price" annotations)
                        match = re.search(price_pattern, cell_text)
                        if match:
                            try:
                                price_val = float(match.group(1).replace(',', '.'))
                                if price_val > 0:
                                    extracted_prices.append(price_val)
                            except:
                                pass
                    
                    # We expect 2 prices: unit price excl and unit price incl
                    if len(extracted_prices) >= 2:
                        unit_price_excl = extracted_prices[0]
                        unit_price_incl = extracted_prices[1]
                    elif len(extracted_prices) == 1:
                        # Only one price found, use it as incl and calculate excl later
                        unit_price_incl = extracted_prices[0]
                        unit_price_excl = unit_price_incl  # Will be recalculated based on VAT rate
                    
                    # Sanity check: incl should be >= excl (since it includes VAT)
                    # If not, swap them
                    if unit_price_excl > unit_price_incl and unit_price_incl > 0:
                        unit_price_excl, unit_price_incl = unit_price_incl, unit_price_excl
                    
                    item_total = unit_price_incl * quantity
                    
                    # Skip duplicate items (same ASIN already processed)
                    if asin in seen_asins:
                        continue
                    seen_asins.add(asin)
                    
                    items.append(OrderItem(
                        product_name=product_name,
                        asin=asin,
                        sku=sku,
                        quantity=quantity,
                        unit_price_excl=unit_price_excl,
                        unit_price_incl=unit_price_incl,
                        item_subtotal_excl=unit_price_excl * quantity,
                        item_subtotal_incl=unit_price_incl * quantity,
                        item_total=item_total,
                    ))
                except Exception as e:
                    _log(f"     ⚠ Could not extract item: {e}")
                    continue
            
            _log(f"   ✔ Extracted {len(items)} items")
            return items
            
        except Exception as e:
            print(f"   ⚠ Error extracting items: {e}")  # Keep errors visible
            return []
    
    def _is_food_bio_product(self, items: List[OrderItem]) -> bool:
        """
        Determine if items should use reduced VAT rate based on VAT configuration.
        Supports SKU-based (preferred), keyword-based, and ASIN-based (legacy) configurations.
        Priority: SKU match > Keyword match > Fallback keywords
        Returns True if all items should have reduced rate, False otherwise.
        """
        if not items:
            return False  # Default to standard rate if no items
        
        # Load VAT configuration
        vat_config = load_vat_config()
        config_type = vat_config.get('type', 'keyword-based')
        
        # SKU-BASED MATCHING (Preferred - most accurate)
        if config_type == 'sku-based':
            _log(f"   ℹ Using SKU-based VAT classification")
            
            reduced_skus = frozenset(vat_config.get('reduced_rate_skus', []))
            standard_skus = frozenset(vat_config.get('standard_rate_skus', []))
            sku_to_product = vat_config.get('sku_to_product', {})
            
            # Also get keyword lists for fallback (use frozenset for performance)
            reduced_keywords = frozenset(vat_config.get('reduced_rate_keywords', []))
            standard_keywords = frozenset(vat_config.get('standard_rate_keywords', []))
            
            # Check each item
            for item in items:
                sku = item.sku
                product_name = sku_to_product.get(sku, item.product_name)
                product_lower = item.product_name.lower()
                
                # 1. Try SKU match first (most reliable)
                if sku in standard_skus:
                    _log(f"   ℹ Product '{product_name}' (SKU: {sku}) → Standard rate (19%) [SKU match]")
                    return False
                
                if sku in reduced_skus:
                    _log(f"   ℹ Product '{product_name}' (SKU: {sku}) → Reduced rate (7%) [SKU match]")
                    continue  # Check next item
                
                # 2. SKU not in config - fall back to keyword matching
                _log(f"   ℹ SKU '{sku}' not in config, using keyword fallback")
                
                # Check standard keywords (highest priority)
                matched_standard = False
                for keyword in standard_keywords:
                    if keyword.lower() in product_lower:
                        _log(f"   ℹ Product '{item.product_name}' matches standard keyword '{keyword}' → Standard rate (19%) [keyword fallback]")
                        return False
                
                # Check reduced keywords
                matched_reduced = False
                for keyword in reduced_keywords:
                    if keyword.lower() in product_lower:
                        _log(f"   ℹ Product '{item.product_name}' matches reduced keyword '{keyword}' → Reduced rate (7%) [keyword fallback]")
                        matched_reduced = True
                        break
                
                # 3. No SKU or keyword match - use built-in fallback
                if not matched_reduced:
                    _log(f"   ℹ Product '{item.product_name}' (SKU: {sku}) not matched, using built-in fallback")
                    if not self._fallback_keyword_matching([item]):
                        return False
            
            # All items matched reduced rate
            _log(f"   ✓ All products use reduced VAT rate (7%)")
            return True
        
        # KEYWORD-BASED MATCHING (New approach)
        elif config_type == 'keyword-based':
            _log(f"   ℹ Using keyword-based VAT classification")
            
            reduced_keywords = frozenset(vat_config.get('reduced_rate_keywords', []))
            standard_keywords = frozenset(vat_config.get('standard_rate_keywords', []))
            
            # If no keywords in config, use fallback logic
            if not reduced_keywords and not standard_keywords:
                _log(f"   ℹ No keywords in config, using fallback classification")
                return self._fallback_keyword_matching(items)
            
            # Check each item against keywords
            for item in items:
                product_lower = item.product_name.lower()
                
                # Check if product name contains any standard rate keywords (highest priority)
                for keyword in standard_keywords:
                    if keyword.lower() in product_lower:
                        _log(f"   ℹ Product '{item.product_name}' matches standard keyword '{keyword}' → Standard rate (19%)")
                        return False
                
                # Check if product name contains any reduced rate keywords
                matched_reduced = False
                for keyword in reduced_keywords:
                    if keyword.lower() in product_lower:
                        _log(f"   ℹ Product '{item.product_name}' matches reduced keyword '{keyword}' → Reduced rate (7%)")
                        matched_reduced = True
                        break
                
                # If no reduced keyword match, default to standard rate
                if not matched_reduced:
                    _log(f"   ℹ Product '{item.product_name}' doesn't match any reduced keywords → Standard rate (19%)")
                    return False
            
            # All items matched reduced keywords
            _log(f"   ✓ All products use reduced VAT rate (7%)")
            return True
        
        # ASIN-BASED MATCHING (Legacy approach for backward compatibility)
        else:
            _log(f"   ℹ Using ASIN-based VAT classification (legacy mode)")
            
            reduced_asins = frozenset(vat_config.get('reduced_rate_asins', []))
            standard_asins = frozenset(vat_config.get('standard_rate_asins', []))
            asin_to_product = vat_config.get('asin_to_product', {})
            
            # If config has ASINs, use ASIN-based matching
            if reduced_asins or standard_asins:
                for item in items:
                    asin = item.asin
                    product_name = asin_to_product.get(asin, item.product_name)
                    
                    # Check if ASIN is in standard rate list (highest priority)
                    if asin in standard_asins:
                        _log(f"   ℹ Product '{product_name}' (ASIN: {asin}) → Standard rate (19%)")
                        return False
                    
                    # Check if ASIN is in reduced rate list
                    if asin in reduced_asins:
                        _log(f"   ℹ Product '{product_name}' (ASIN: {asin}) → Reduced rate (7%)")
                        continue
                    
                    # ASIN not in config - default to standard rate
                    _log(f"   ℹ Product '{product_name}' (ASIN: {asin}) not in config → Standard rate (19%)")
                    return False
                
                # All items are in reduced rate list
                _log(f"   ✓ All products use reduced VAT rate (7%)")
                return True
            
            # Fallback: No ASINs in config, use keyword matching
            _log(f"   ℹ No ASIN configuration found, using keyword-based fallback")
            return self._fallback_keyword_matching(items)
    
    def _fallback_keyword_matching(self, items: List[OrderItem]) -> bool:
        """
        Fallback keyword matching when no configuration is available.
        Uses built-in keyword lists to classify products.
        """
        # Exception keywords (cosmetics/hygiene - always standard rate)
        exception_keywords = [
            'zahncreme', 'zahnpasta', 'toothpaste', 'creme', 'cream',
            'haaröl', 'bartöl', 'massageöl', 'hair oil', 'beard oil',
            'seife', 'soap', 'shampoo', 'kosmetik', 'cosmetic', 'lotion'
        ]
        
        # Keywords for reduced VAT (food, edible supplements)
        reduced_keywords = [
            'speiseöl', 'kapseln', 'vitamin', 'nahrung', 'supplement',
            'kürbis', 'schwarzkümmel', 'kurkuma', 'kokosöl', 'tee',
            'samen', 'lebensmittel', 'bio', 'organic'
        ]
        
        for item in items:
            product_lower = item.product_name.lower()
            
            # Check exception keywords first (cosmetics override everything)
            is_exception = any(keyword in product_lower for keyword in exception_keywords)
            if is_exception:
                _log(f"   ℹ Product '{item.product_name}' contains cosmetic keyword → Standard rate (19%)")
                return False
            
            # Check reduced rate keywords (food/edible supplements)
            is_reduced = any(keyword in product_lower for keyword in reduced_keywords)
            
            if not is_reduced:
                _log(f"   ℹ Product '{item.product_name}' not recognized as food → Standard rate (19%)")
                return False
        
        # All items appear to be reduced rate products
        _log(f"   ✓ All products recognized as food/supplements → Reduced rate (7%)")
        return True
    
    def _extract_financial_info(self, country: str = "Deutschland", items: List[OrderItem] = None) -> tuple:
        """Extract totals and financial information"""
        try:
            page_text = self.driver.page_source
            
            # Currency: Always use Euro (€) for all invoices
            # User confirmed all invoices should use Euro
            currency = "€"
            
            # Generic Price Regex using detected currency or catch-all
            # If currency is Euro, look for €
            # If kr, look for kr
            
            def extract_val(label_pattern):
                # Pattern to find label then price.
                # Regex: Label ... (Currency? Amount | Amount Currency?)
                # Allow colon and whitespace between label and price
                
                # Try specific patterns first
                pat_start = label_pattern + r'[:\s]*' + re.escape(currency) + r'\s*([\d,\.]+)'
                pat_end = label_pattern + r'[:\s]*' + r'([\d,\.]+)\s*' + re.escape(currency)
                
                # Check start (e.g. € 100)
                val = self._extract_price_from_text(page_text, pat_start)
                if val == 0.0:
                    # Check end (e.g. 100 kr)
                    val = self._extract_price_from_text(page_text, pat_end)
                return val

            # Calculate subtotal from items (more reliable than extracting from page)
            # Sum up all item totals (gross prices)
            raw_subtotal = 0.0
            if items:
                raw_subtotal = sum(item.item_total for item in items)
            
            # Extract shipping and grand total from page (fallback to calculated if extraction fails)
            # Try multiple patterns to find shipping total in the HTML structure
            # HTML may have tags/whitespace between "Shipping total:" and the price
            shipping_total = 0.0
            
            # Pattern 1: "Shipping total" with optional colon, then HTML/tags, then currency and amount
            # Handles: "Shipping total:</span>...<span>€3.99"
            shipping_total = self._extract_price_from_text(page_text, r'Shipping\s+total[:\s]*[^€]*€([\d,\.]+)', case_insensitive=True)
            
            # Pattern 2: "Shipping total" with amount and currency (reversed)
            if shipping_total == 0.0:
                shipping_total = self._extract_price_from_text(page_text, r'Shipping\s+total[:\s]*[^€]*([\d,\.]+)\s*€', case_insensitive=True)
            
            # Pattern 3: Try with any currency symbol (more flexible)
            if shipping_total == 0.0:
                shipping_total = self._extract_price_from_text(page_text, r'Shipping\s+total[:\s]*[^€$£kr]*[€$£](\d+[,\d]*\.?\d*)', case_insensitive=True)
            
            # Pattern 4: Try the extract_val function as fallback
            if shipping_total == 0.0:
                shipping_total = extract_val(r'Shipping total')
            if shipping_total == 0.0:
                shipping_total = extract_val(r'Shipping')
            
            # Extract promotion amount (can apply to shipping or items)
            # HTML structure: <span>Promotion</span>:</span></div>...<span class="a-color-state">-€3.63</span>
            # Need flexible pattern to match across multiple HTML tags
            promotion_total = 0.0
            
            # Pattern 1: Look for "Promotion" followed (within 200 chars) by "-€" and amount
            promo_match = re.search(r'Promotion.{0,200}?-€([\d,\.]+)', page_text, re.IGNORECASE | re.DOTALL)
            if promo_match:
                promotion_total = float(promo_match.group(1).replace(',', '.'))
            else:
                # Pattern 2: Look for "Promotion total" variant
                promo_match = re.search(r'Promotion\s+total.{0,200}?-€([\d,\.]+)', page_text, re.IGNORECASE | re.DOTALL)
                if promo_match:
                    promotion_total = float(promo_match.group(1).replace(',', '.'))
            
            # Determine how to apply the promotion
            item_promotion = 0.0  # Promotion applied to items
            
            if promotion_total > 0:
                _log(f"   ℹ Promotion found: -{currency}{promotion_total:.2f}")
                
                if shipping_total > 0 and abs(promotion_total - shipping_total) < 0.01:
                    # Promotion exactly covers shipping - shipping is free
                    _log(f"   ℹ Promotion covers shipping - setting shipping to €0.00")
                    shipping_total = 0.0
                elif shipping_total > 0 and promotion_total < shipping_total:
                    # Partial promotion on shipping
                    shipping_total = shipping_total - promotion_total
                    _log(f"   ℹ After promotion, shipping is: {currency}{shipping_total:.2f}")
                elif shipping_total == 0.0 or promotion_total > shipping_total:
                    # No shipping or promotion exceeds shipping - applies to items
                    if shipping_total > 0:
                        # First cover shipping, rest goes to items
                        item_promotion = promotion_total - shipping_total
                        shipping_total = 0.0
                    else:
                        # All promotion goes to items
                        item_promotion = promotion_total
                    _log(f"   ℹ Item promotion/discount: -{currency}{item_promotion:.2f}")
            
            grand_total = extract_val(r'Item total')
            
            if shipping_total == 0.0:
                _log(f"   ℹ Shipping total: {currency}0.00 (free shipping)")
            else:
                _log(f"   ℹ Extracted shipping total: {currency} {shipping_total:.2f}")
            
            # Fallback: if extraction failed, calculate grand total from items + shipping
            if grand_total == 0.0:
                grand_total = raw_subtotal + shipping_total
            
            status = self._extract_text("[data-test-id='item-status-label']")
            
            # VAT Rates - Standard (Normal) Rates
            # Based on official EU VAT rates table
            EU_STANDARD_VAT_RATES = {
                "Belgien": 0.21,      # 21%
                "Bulgarien": 0.20,    # 20%
                "Dänemark": 0.25,     # 25%
                "Deutschland": 0.19,  # 19%
                "Estland": 0.24,      # 24%
                "Finnland": 0.255,    # 25.5%
                "Frankreich": 0.20,   # 20%
                "Griechenland": 0.24, # 24%
                "Irland": 0.23,       # 23%
                "Italien": 0.22,      # 22%
                "Kroatien": 0.25,     # 25%
                "Lettland": 0.21,     # 21%
                "Litauen": 0.21,      # 21%
                "Luxemburg": 0.17,    # 17%
                "Malta": 0.18,        # 18%
                "Niederlande": 0.21,  # 21%
                "Nordirland": 0.20,   # 20%
                "Österreich": 0.20,   # 20%
                "Polen": 0.23,        # 23%
                "Portugal": 0.23,     # 23% (Festland)
                "Rumänien": 0.21,     # 21%
                "Schweden": 0.25,     # 25%
                "Slowakei": 0.23,     # 23%
                "Slowenien": 0.22,    # 22%
                "Spanien": 0.21,      # 21%
                "Tschechien": 0.21,   # 21%
                "Ungarn": 0.27,       # 27%
                "Zypern": 0.19,       # 19%
            }
            
            # VAT Rates - Reduced (Ermäßigt) Rates
            # Based on official EU VAT rates table
            # Using the lowest non-zero reduced rate for Bio/Food where multiple exist
            EU_REDUCED_VAT_RATES = {
                "Belgien": 0.06,      # 12/6 - Using 6%
                "Bulgarien": 0.09,    # 9%
                "Dänemark": 0.25,     # No reduced rate, using standard 25%
                "Deutschland": 0.07,  # 7%
                "Estland": 0.09,      # 9%
                "Finnland": 0.10,     # 14/10 - Using 10%
                "Frankreich": 0.055,  # 10/5.5/2.1 - Using 5.5% typical for food
                "Griechenland": 0.06, # 13/6 - Using 6%
                "Irland": 0.048,      # 13.5/9/4.8 - Using 4.8%
                "Italien": 0.10,      # 10/5/4/0 - Using 10% typical for food
                "Kroatien": 0.05,     # 13/5/0 - Using 5%
                "Lettland": 0.05,     # 12/5 - Using 5%
                "Litauen": 0.05,      # 9/5/0 - Using 5%
                "Luxemburg": 0.03,    # 14/8/3 - Using 3%
                "Malta": 0.05,        # 7/5/0 - Using 5%
                "Niederlande": 0.09,  # 9%
                "Nordirland": 0.00,   # 5/0 - Using 0%
                "Österreich": 0.10,   # 13/10 - Using 10%
                "Polen": 0.05,        # 8/5/0 - Using 5%
                "Portugal": 0.06,     # 13/6 - Using 6% (Festland)
                "Rumänien": 0.11,     # 11%
                "Schweden": 0.06,     # 12/6 - Using 6% (reduced rate)
                "Slowakei": 0.05,     # 19/5 - Using 5%
                "Slowenien": 0.05,    # 9.5/5 - Using 5%
                "Spanien": 0.10,      # 10%
                "Tschechien": 0.12,   # 12/0 - Using 12%
                "Ungarn": 0.05,       # 18/5/0 - Using 5%
                "Zypern": 0.05,       # 9/5 - Using 5%
            }
            
            # Normalize country for lookup
            country_norm = country.strip()
            
            # Map common English variations to German keys
            COUNTRY_MAPPING = {
                "Germany": "Deutschland",
                "Austria": "Österreich",
                "France": "Frankreich",
                "Belgium": "Belgien",
                "Bulgaria": "Bulgarien",
                "Denmark": "Dänemark",
                "Estonia": "Estland",
                "Finland": "Finnland",
                "Greece": "Griechenland",
                "Ireland": "Irland",
                "Italy": "Italien",
                "Croatia": "Kroatien",
                "Latvia": "Lettland",
                "Lithuania": "Litauen",
                "Luxembourg": "Luxemburg",
                "Netherlands": "Niederlande",
                "Poland": "Polen",
                "Romania": "Rumänien",
                "Sweden": "Schweden",
                "Slovakia": "Slowakei",
                "Slovenia": "Slowenien",
                "Spain": "Spanien",
                "Czech Republic": "Tschechien",
                "Czechia": "Tschechien",
                "Hungary": "Ungarn",
                "Cyprus": "Zypern",
                "Switzerland": "Schweiz",
            }
            country_norm = COUNTRY_MAPPING.get(country_norm, country_norm)
            
            # Determine if products are food/bio (use reduced rate) or regular products (use standard rate)
            is_food_bio = self._is_food_bio_product(items if items else [])
            
            # Get VAT Rate based on product type
            if is_food_bio:
                # Use reduced rate for food/bio products
                vat_rate = EU_REDUCED_VAT_RATES.get(country_norm, 0.0)
            else:
                # Use standard rate for regular products
                vat_rate = EU_STANDARD_VAT_RATES.get(country_norm, 0.0)
            
            # Special case for 0% VAT (non-EU countries like Switzerland)
            # For these orders, Amazon is the Marketplace Facilitator and collects VAT
            # Our invoice should use VAT-exclusive prices (net proceeds)
            if vat_rate == 0.0:
                # Use VAT-exclusive prices for 0% VAT countries
                raw_subtotal = sum(item.unit_price_excl * item.quantity for item in items) if items else 0.0
                # Update item totals to use exclusive prices
                for item in items:
                    item.unit_price_incl = item.unit_price_excl  # Use excl price for display
                    item.item_total = item.unit_price_excl * item.quantity
            
            # Apply item promotion to subtotal (gross amount before VAT calculation)
            if item_promotion > 0:
                raw_subtotal = raw_subtotal - item_promotion
            
            # Calculate Net and VAT Amount
            # Gross = Net * (1 + rate)
            # Item calculations
            if vat_rate > 0:
                item_net = raw_subtotal / (1 + vat_rate)
                item_vat = raw_subtotal - item_net
            else:
                # 0% VAT - net = gross, no VAT
                item_net = raw_subtotal
                item_vat = 0.0
            
            # Shipping also includes VAT - calculate shipping net and VAT
            shipping_net = shipping_total / (1 + vat_rate) if vat_rate > 0 else shipping_total
            shipping_vat = shipping_total - shipping_net
            
            # Total net = item net + shipping net
            net_total = item_net + shipping_net
            
            # Total VAT = item VAT + shipping VAT
            vat_amount = item_vat + shipping_vat
            
            # Calculate grand total (always: net + VAT)
            # Don't use extracted grand_total as it may include VAT we're not charging
            grand_total = net_total + vat_amount
            
            return net_total, shipping_total, vat_amount, grand_total, status, vat_rate, currency, item_promotion
        except Exception as e:
            _log(f"   ⚠ Could not extract financial info: {e}")
            return 0.0, 0.0, 0.0, 0.0, "Unknown", 0.0, "€", 0.0
    
    def _extract_price_from_text(self, text: str, pattern: str, case_insensitive: bool = False) -> float:
        """Extract price from text using regex"""
        try:
            flags = re.IGNORECASE if case_insensitive else 0
            match = re.search(pattern, text, flags)
            if match:
                return float(match.group(1).replace(',', '.'))
        except:
            pass
        return 0.0
    
    def _parse_purchase_date(self, date_str: str) -> str:
        """Parse Amazon date format to DD.MM.YYYY"""
        # Input: "Sun, 2 Nov 2025, 15:20 MET" or similar
        # Output: "02.11.2025"
        try:
            # Remove day of week and time parts
            # Split by comma and take the date part
            parts = date_str.split(',')
            if len(parts) >= 2:
                date_part = parts[1].strip()  # "2 Nov 2025"
                
                # Parse the date
                date_components = date_part.split()
                if len(date_components) >= 3:
                    day = date_components[0].zfill(2)
                    month_name = date_components[1]
                    year = date_components[2]
                    
                    # Convert month name to number
                    months = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    month = months.get(month_name, '01')
                    
                    return f"{day}.{month}.{year}"
        except Exception as e:
            _log(f"   ⚠ Could not parse date '{date_str}': {e}")
        
        # Fallback: return as-is
        return date_str


class PDFInvoiceGenerator:
    """Generates invoices matching Tasnim e.U. format with pixel-perfect precision"""
    
    PAGE_HEIGHT = 842.0
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    
    def __init__(self):
        pass

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
        # Return German translation if found, otherwise return original
        return translations.get(country, country)

    def _format_price(self, amount: float, currency: str = "€") -> str:
        s = f"{amount:.2f}".replace('.', ',')
        # Format based on currency
        if currency in ["kr", "SEK", "DKK", "NOK"]:
            return f"{s} {currency}" # 100,00 kr
        elif currency == "£":
            return f"£{s}"
        elif currency == "$":
            return f"${s}"
        return f"{currency} {s}" # Default € 100,00

    def generate(self, invoice_data: InvoiceData, output_path: Path) -> bool:
        try:
            c = canvas.Canvas(str(output_path), pagesize=A4)
            c.setFont(self.FONT_NORMAL, 10)
            
            # Generate invoice date (current date in DD.MM.YYYY format)
            invoice_date = datetime.now().strftime("%d.%m.%Y")
            
            # --- 1A. Logo (Top Right) ---
            # Box: x=447.42, y=33.45, w=97.35, h=24.66
            logo_x = 447.42
            logo_y_user = 33.45
            logo_w = 97.35
            logo_h = 24.66
            logo_y_pdf = self._to_pdf_y(logo_y_user, logo_h)
            
            # Draw real logo (if file exists, else fallback)
            logo_path = Path("Tasnim-logo-white-black-TransparentBG (2).png")
            if logo_path.exists():
                # mask='auto' for transparency
                c.drawImage(str(logo_path), logo_x, logo_y_pdf, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
            else:
                # Fallback
                c.saveState()
                c.setFillColor(colors.black)
                c.setFont(self.FONT_BOLD, 16)
                c.drawString(logo_x + 10, logo_y_pdf + 8, "TASNIM") 
                c.restoreState()
            
            # --- 2. Address Block ---
            # "Lieferadresse:" label at x=57.58
            # Original text height ~8.94pt.
            # Block moved DOWN by ~20.77pt.
            # Original y=70.98. New y approx 91.75?
            # User said: "Move the whole delivery-address block DOWN by ~20.77pt".
            # Base Y for Address Block Content.
            
            # Label "Lieferadresse:"
            # User says label height is ~8.94pt? Or font size? 
            # "Lieferadresse:" word box height is ~8.94pt -> Font size approx 7-8pt?
            # Let's use 8pt for the label.
            # Position: The label itself was at ~70.98? 
            # If "Lieferadresse block is too high", we move it down.
            
            addr_start_y = 70.98 + 20.77
            
            c.setFont(self.FONT_NORMAL, 7) # Smaller label
            c.drawString(57.58, self._to_pdf_y(addr_start_y), "Lieferadresse:")
            
            # Address Text
            # Below label.
            c.setFont(self.FONT_NORMAL, 10)
            text_obj = c.beginText(57.58, self._to_pdf_y(addr_start_y + 12)) 
            text_obj.textLine(invoice_data.buyer_name)
            # Handle multi-line street addresses
            if invoice_data.buyer_street:
                for street_line in invoice_data.buyer_street.split('\n'):
                    if street_line.strip():
                        text_obj.textLine(street_line.strip())
            text_obj.textLine(f"{invoice_data.buyer_postal} {invoice_data.buyer_city}")
            # Translate country to German for invoice display
            country_german = self._translate_country_to_german(invoice_data.buyer_country)
            text_obj.textLine(country_german.upper())
            c.drawText(text_obj)
            
            
            # --- 3. Sender Line ---
            # x=56.16, y=162.26
            # Underline: x=56.16 to 269.15 at y=170.345 (User coordinates)
            # Add extra spacing to prevent overlap with delivery address
            
            sender_y_user = 162.26 + 10  # Add 10pt spacing
            sender_y_pdf = self._to_pdf_y(sender_y_user) - 6 # Adjust for baseline
            
            c.setFont(self.FONT_NORMAL, 6)
            c.drawString(56.16, sender_y_pdf, f"Abs.: {TASNIM_INFO['address_line']}")
            
            # Underline
            line_y_user = 170.345 + 10  # Add 10pt spacing
            line_y_pdf = self._to_pdf_y(line_y_user)
            c.setLineWidth(0.75)
            c.line(56.16, line_y_pdf, 269.15, line_y_pdf)
            
            
            # --- Billing Address (Same as Delivery Address) ---
            # x=57.58, y=179.55
            # Add extra spacing to prevent overlap with sender line and title
            billing_y = 179.55 + 20  # Add 20pt spacing
            text_obj = c.beginText(57.58, self._to_pdf_y(billing_y) - 9)
            text_obj.setFont(self.FONT_NORMAL, 10)
            
            # Count address lines for dynamic spacing calculation
            billing_address_lines = 1  # buyer_name
            if invoice_data.buyer_street:
                billing_address_lines += len([line for line in invoice_data.buyer_street.split('\n') if line.strip()])
            billing_address_lines += 1  # postal + city
            billing_address_lines += 1  # country
            
            text_obj.textLine(invoice_data.buyer_name)
            # Handle multi-line street addresses
            if invoice_data.buyer_street:
                for street_line in invoice_data.buyer_street.split('\n'):
                    if street_line.strip():
                        text_obj.textLine(street_line.strip())
            text_obj.textLine(f"{invoice_data.buyer_postal} {invoice_data.buyer_city}")
            # Translate country to German for invoice display
            country_german = self._translate_country_to_german(invoice_data.buyer_country)
            text_obj.textLine(country_german.upper())
            c.drawText(text_obj)
            
            
            # --- 4. Title & Meta Section ---
            # 4A. Invoice Number Row
            # Use Amazon Order ID as invoice number
            invoice_num = invoice_data.order_id  # e.g., "303-3015679-9805908"
            order_num = invoice_data.order_id
            
            # Title "Rechnung"
            # x=57.58, y=243.63 (original)
            # Dynamically adjust based on billing address height to prevent overlap
            # Each line is approximately 12pt tall
            line_height = 12
            billing_address_height = billing_address_lines * line_height
            min_spacing_after_address = 15  # Minimum gap between address and title
            
            # Calculate dynamic title position
            title_y_base = 243.63
            billing_end_y = billing_y + billing_address_height
            required_title_y = billing_end_y + min_spacing_after_address
            
            # Use the larger of the two to ensure no overlap
            title_y = max(title_y_base, required_title_y)
            
            c.setFont(self.FONT_BOLD, 18)
            c.drawString(57.58, self._to_pdf_y(title_y) - 14, "Rechnung")
            
            # Calculate vertical shift for subsequent elements
            # This ensures that if the title is pushed down, everything following it is also pushed down
            layout_shift = title_y - 243.63
            if layout_shift < 0: layout_shift = 0 # Should not happen given max() above, but safety check
            
            # 1B. Barcode (Right side near invoice number)
            # REMOVED as per user request
            # x=499.75, y=274.10, w=48.47, h=15.81
            
            
            # 4B. Meta Columns
            # Col 1 (Label): x=57.58
            # Col 2 (Value): x=168.164
            
            label_x = 57.58
            value_x = 168.164
            
            c.setFont(self.FONT_NORMAL, 9)
            
            # Row 1: Invoice Number (y=272.637 originally, now relative to title_y)
            # Original offset from title: 272.637 - 243.63 = 29.007
            y1 = self._to_pdf_y(title_y + 29.007)
            c.drawString(label_x, y1, "Rechnung")
            c.drawString(value_x, y1, invoice_num)
            
            # Row 2: Rechnungsdatum - Use current generation date
            # Original offset: 283.976 - 243.63 = 40.346
            y2 = self._to_pdf_y(title_y + 40.346)
            c.drawString(label_x, y2, "Rechnungsdatum")
            c.drawString(value_x, y2, invoice_date)
            
            # Row 3: Bestelldatum
            # Original offset: 295.466 - 243.63 = 51.836
            y3 = self._to_pdf_y(title_y + 51.836)
            c.drawString(label_x, y3, "Bestelldatum")
            c.drawString(value_x, y3, invoice_data.purchase_date)
            
            # Row 4: Zahldatum
            # Original offset: 306.596 - 243.63 = 62.966
            y4 = self._to_pdf_y(title_y + 62.966)
            c.drawString(label_x, y4, "Zahldatum")
            c.drawString(value_x, y4, invoice_data.purchase_date)
            
            # Row 5: Zahlart
            # Original offset: 318.447 - 243.63 = 74.817
            y5 = self._to_pdf_y(title_y + 74.817)
            c.drawString(label_x, y5, "Zahlart")
            
            # Value starts on same line
            c.drawString(value_x, y5, "via Amazon")
            
            # 4A. Order Number Line
            # Shifted down to avoid overlap with multi-line text (User request for space)
            # Original y=365.0. Apply dynamic layout shift.
            y_ord = self._to_pdf_y(365.0 + layout_shift)
            c.drawString(56.16, y_ord, f"Bestellnummer: {order_num}")
            
            
            # --- 5. Items Table ---
            # Header Background: x=56.160, y=376.106, w=494.362, h=18.0
            header_rect_y_user = 376.106 + layout_shift
            header_h = 18.0
            header_rect_y_pdf = self._to_pdf_y(header_rect_y_user, header_h)
            
            c.setFillColorRGB(0.9, 0.9, 0.9) # Light grey
            c.rect(56.16, header_rect_y_pdf, 494.362, header_h, fill=1, stroke=0)
            c.setFillColor(colors.black)
            
            # Header Lines
            # Top: y=376.106
            # target_top_y = self._to_pdf_y(376.106 + layout_shift) # This is likely the Top of the rect?
            
            target_top_y = self._to_pdf_y(376.106 + layout_shift) # Exact line position
            target_bot_y = self._to_pdf_y(394.248 + layout_shift)
            
            c.setLineWidth(0.75)
            c.line(56.16, target_top_y, 56.16 + 494.36, target_top_y)
            c.line(56.16, target_bot_y, 56.16 + 494.36, target_bot_y)
            
            # Header Text
            # y=379.90 (User) -> PDF Y
            # Note: 379.90 is inside the 376-394 range.
            header_text_y = self._to_pdf_y(379.90 + layout_shift) - 7 # Adjust for baseline
            
            cols = [
                (65.57, "Pos"),
                (93.01, "Nummer"),
                (175.22, "Artikel"),
                (398.06, "Anzahl"),
                (467.36, "Preis"),
                (508.70, "Summe")
            ]
            
            # Draw headers - right-align numeric columns to match values
            for i, (x, title) in enumerate(cols):
                if title in ["Anzahl", "Preis", "Summe"]:
                    # Right-align these headers to match their values
                    if title == "Anzahl":
                        c.drawRightString(435.0, header_text_y, title)
                    elif title == "Preis":
                        c.drawRightString(505.0, header_text_y, title)
                    else:  # Summe
                        c.drawRightString(547.62, header_text_y, title)
                else:
                    c.drawString(x, header_text_y, title)
                
            # Items
            current_y_user = 395.00 + layout_shift # Start of items
            
            for i, item in enumerate(invoice_data.items, 1):
                y_pos = self._to_pdf_y(current_y_user) - 9 # Baseline
                
                c.drawString(cols[0][0], y_pos, str(i))
                c.drawString(cols[1][0], y_pos, item.sku)
                c.drawString(cols[2][0], y_pos, item.product_name[:45])
                
                # Right align numeric columns for proper alignment
                # Anzahl, Preis, and Summe are all right-aligned
                c.drawRightString(435.0, y_pos, f"{item.quantity},00")
                # Right align unit price at a position that aligns with totals
                c.drawRightString(505.0, y_pos, self._format_price(item.unit_price_incl, invoice_data.currency))
                # Right align item total at 547.62 (same as totals section)
                c.drawRightString(547.62, y_pos, self._format_price(item.item_total, invoice_data.currency))
                
                # Separator Line
                # y=420.2049 (User) relative to this row? Or absolute for 1st row?
                # User said: "And the item row separator line: y=420.2049pt".
                # This implies fixed position for single item invoice?
                # If multiple items, we'd need dynamic lines. 
                # Assuming single item for "Tasnim" style for now, or delta.
                # 420.20 - 395.00 = 25.2. Item height approx 25pt.
                
                line_y = self._to_pdf_y(current_y_user + 25.20)
                c.line(56.16, line_y, 550.52, line_y)
                
                current_y_user += 25.20
            
            
            # --- 6. Totals ---
            # Labels Shift Left. Target x (Labels)?
            # User: "Zwischensumme... Original x reduced by 31.17pt".
            # Original was ~332? So new x ~ 300?
            # Or "Original x approx 332.812". User says "Test x approx 363 -> Shift Left by 31".
            # So Target X is 332.812.
            
            label_x_totals = 332.81
            value_right_x = 547.62
            
            # Y Positions
            # subtotal_net_block y=425.33
            # shipping_block y=439.65
            # total_net_block y=453.95
            # vat_block y=468.12
            # grand_total_block y=487.97
            
            # Adjust Y for item count (assuming 1 item baseline)
            item_count_shift = (len(invoice_data.items) - 1) * 25.20
            
            def draw_total_row_fixed(user_y, label, val_str, bold=False):
                # Apply BOTH layout_shift (from address size) AND item_count_shift (from item count)
                y = self._to_pdf_y(user_y + layout_shift + item_count_shift) - 8
                if bold:
                    c.setFont(self.FONT_BOLD, 10)
                else:
                    c.setFont(self.FONT_NORMAL, 9)
                
                # Draw Label (Left align at 332.81?)
                c.drawString(label_x_totals, y, label)
                
                # Draw Value (Right align at 547.62)
                c.drawRightString(value_right_x, y, val_str)
            
            vat_percent = f"{invoice_data.vat_rate*100:.1f}".replace('.', ',') + "%"
            
            # Calculate item gross total from items
            item_gross = sum(item.item_total for item in invoice_data.items)
            
            # Check if there's a promotion discount
            has_promotion = invoice_data.promotion_discount > 0
            
            # If promotion, show original subtotal, then discount, then calculate net from discounted amount
            if has_promotion:
                # Subtotal before discount
                item_net_before_discount = item_gross / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else item_gross
                # Discount amount - promotion_discount is ALREADY NET (not gross)
                # Amazon shows €0.70 as the NET discount, so VAT is calculated on the final net amount
                discount_net = invoice_data.promotion_discount
                # Net after discount
                item_net = item_net_before_discount - discount_net
            else:
                item_net = item_gross / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else item_gross
            
            # Calculate shipping net (shipping_total includes VAT)
            shipping_net = invoice_data.shipping_total / (1 + invoice_data.vat_rate) if invoice_data.vat_rate > 0 else invoice_data.shipping_total
            
            # Total net = item net + shipping net
            total_net = item_net + shipping_net
            
            # Draw totals - adjust Y positions if we have a promotion line
            if has_promotion:
                # With promotion: Zwischensumme, Rabatt, Versand, Gesamt netto, USt, Gesamtsumme
                draw_total_row_fixed(425.33, "Zwischensumme (netto)", self._format_price(item_net_before_discount, invoice_data.currency))
                draw_total_row_fixed(439.65, "Rabatt", "-" + self._format_price(discount_net, invoice_data.currency))
                draw_total_row_fixed(453.95, "Versand", self._format_price(invoice_data.shipping_total, invoice_data.currency))
                draw_total_row_fixed(468.12, "Gesamt netto", self._format_price(total_net, invoice_data.currency))
                draw_total_row_fixed(482.29, f"Umsatzsteuer ({vat_percent})", self._format_price(invoice_data.vat_amount, invoice_data.currency))
                draw_total_row_fixed(501.97, "Gesamtsumme", self._format_price(invoice_data.grand_total, invoice_data.currency), bold=True)
            else:
                # Without promotion: original layout
                draw_total_row_fixed(425.33, "Zwischensumme (netto)", self._format_price(item_net, invoice_data.currency))
                draw_total_row_fixed(439.65, "Versand", self._format_price(invoice_data.shipping_total, invoice_data.currency))
                draw_total_row_fixed(453.95, "Gesamt netto", self._format_price(total_net, invoice_data.currency))
                draw_total_row_fixed(468.12, f"Umsatzsteuer ({vat_percent})", self._format_price(invoice_data.vat_amount, invoice_data.currency))
                draw_total_row_fixed(487.97, "Gesamtsumme", self._format_price(invoice_data.grand_total, invoice_data.currency), bold=True)
            
            
            # --- 7. Thank You ---
            # Move LEFT by ~60.4pt. Original x approx 57.58.
            # Fix: "Keep it starting at x approx 57.58 and is left-aligned."
            
            # Apply layout shift and item count shift to Thank You text as well to keep it below totals
            # Or just layout shift? Currently hardcoded at 542.24.
            # If totals move down due to items, Thank You should also move down.
            # So apply both shifts.
            
            ty_y = self._to_pdf_y(542.24 + layout_shift + item_count_shift) - 8
            c.setFont(self.FONT_NORMAL, 8)
            c.drawString(57.58, ty_y, "Wir bedanken uns für Ihre Bestellung uns freuen uns Sie bald wieder bei Tasnim begrüßen zu dürfen!")
            c.drawString(57.58, ty_y - 12, "Thank you for your order and we look forward to welcoming you back to Tasnim soon!")
            
            
            # --- SKU Reference Section (Above Footer) ---
            # Add SKU information for all items
            sku_section_y = ty_y - 36  # Position below thank you message
            c.setFont(self.FONT_BOLD, 8)
            c.drawString(57.58, sku_section_y, "Artikelnummern (SKU):")
            
            c.setFont(self.FONT_NORMAL, 8)
            sku_list = []
            for item in invoice_data.items:
                sku_info = f"{item.sku} - {item.product_name[:60]}"
                sku_list.append(sku_info)
            
            # Draw SKU list
            current_sku_y = sku_section_y - 12
            for sku_info in sku_list:
                c.drawString(57.58, current_sku_y, sku_info)
                current_sku_y -= 10
            
            
            # --- Footer (As before) ---
            footer_y = self._to_pdf_y(773.29) - 8
            
            text_obj = c.beginText(56.16, footer_y)
            text_obj.setFont(self.FONT_NORMAL, 8)
            text_obj.setLeading(10)
            text_obj.textLine(TASNIM_INFO["control"])
            text_obj.textLine(f"Bankverbindung: {TASNIM_INFO['bank']}")
            text_obj.textLine(f"IBAN: {TASNIM_INFO['iban']}")
            c.drawText(text_obj)
            
            text_obj = c.beginText(304.56, footer_y)
            text_obj.setFont(self.FONT_NORMAL, 8)
            text_obj.setLeading(10)
            text_obj.textLine(TASNIM_INFO["court"])
            text_obj.textLine(f"UID: {TASNIM_INFO['uid']}")
            text_obj.textLine(f"Geschäftsführung: {TASNIM_INFO['ceo']}")
            c.drawText(text_obj)
            
            c.showPage()
            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
            


def generate_invoice(driver, order_id, save_dir):
    """Bridge function called by generate_manual_invoices.py"""
    try:
        # Open a new tab for scraping order details to preserve the main list page validation
        original_window = driver.current_window_handle
        driver.switch_to.new_window('tab')
        
        # Scrape in the new tab
        scraper = OrderScraper(driver)
        invoice_data = scraper.scrape_order_details(order_id)
        
        # Close the tab and switch back
        driver.close()
        driver.switch_to.window(original_window)
        
        if not invoice_data:
            print("   ⚠ Data extraction failed")  # Keep visible
            return False
        
        # Extract filename components from scraped data
        # Parse day from purchase_date (format: "02.11.2025")
        day = invoice_data.purchase_date.split('.')[0] if '.' in invoice_data.purchase_date else "01"
        
        # Extract country code from buyer_country
        country_mapping = {
            "Germany": "DE", "Deutschland": "DE",
            "Austria": "AT", "Österreich": "AT",
            "France": "FR", "Frankreich": "FR",
            "Belgium": "BE", "Belgien": "BE",
            "Netherlands": "NL", "Niederlande": "NL",
            "Italy": "IT", "Italien": "IT",
            "Spain": "ES", "Spanien": "ES",
            "Poland": "PL", "Polen": "PL",
            "Sweden": "SE", "Schweden": "SE",
            "Denmark": "DK", "Dänemark": "DK",
            "Luxembourg": "LU", "Luxemburg": "LU",
            "Portugal": "PT",
            "Ireland": "IE", "Irland": "IE",
            "Greece": "GR", "Griechenland": "GR",
            "Finland": "FI", "Finnland": "FI",
            "Czech Republic": "CZ", "Czechia": "CZ", "Tschechien": "CZ",
            "Hungary": "HU", "Ungarn": "HU",
            "Romania": "RO", "Rumänien": "RO",
            "Bulgaria": "BG", "Bulgarien": "BG",
            "Slovakia": "SK", "Slowakei": "SK",
            "Slovenia": "SI", "Slowenien": "SI",
            "Croatia": "HR", "Kroatien": "HR",
            "Lithuania": "LT", "Litauen": "LT",
            "Latvia": "LV", "Lettland": "LV",
            "Estonia": "EE", "Estland": "EE",
            "Cyprus": "CY", "Zypern": "CY",
            "Malta": "MT",
            "Northern Ireland": "NI", "Nordirland": "NI",
            "Switzerland": "CH", "Schweiz": "CH",
        }
        country_code = country_mapping.get(invoice_data.buyer_country, "DE")
        
        # Use contact buyer name for filename (first name only)
        buyer_name = invoice_data.buyer_contact_name.split()[0] if invoice_data.buyer_contact_name else "Unknown"
        
        generator = PDFInvoiceGenerator()
        # Create filename from extracted data
        pdf_filename = f"{day} {country_code} am {buyer_name}.pdf"
        output_path = save_dir / pdf_filename
        
        _log(f"   ℹ Filename: {pdf_filename}")
        
        success = generator.generate(invoice_data, output_path)
        
        # No need to navigate back anymore as we used a separate tab
        # _navigate_back_to_orders_list(driver)
        
        return success
        
    except Exception as e:
        print(f"Error in generate_invoice: {e}")
        # Ensure we are back on the main window if something crashed
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                 # If we are somehow on the main tab and it's the only one, don't close it
                 pass
        except:
            pass
        return False

