// Invoice Generator - Client-side JavaScript

let itemCount = 0;
let currentInvoiceFilename = '';

// Initialize form with one item on page load
document.addEventListener('DOMContentLoaded', function() {
    addItem(); // Add first item automatically
    
    // Add event listeners for VAT rate updates
    const countrySelect = document.getElementById('buyer_country');
    const vatTypeSelect = document.getElementById('vat_rate_type');
    
    if (countrySelect && vatTypeSelect) {
        countrySelect.addEventListener('change', updateVATRateDisplay);
        vatTypeSelect.addEventListener('change', updateVATRateDisplay);
        
        // Initial update if country is pre-selected
        updateVATRateDisplay();
    }
});

// Update VAT rate display based on country and rate type
function updateVATRateDisplay() {
    const countryCode = document.getElementById('buyer_country').value;
    const rateType = document.getElementById('vat_rate_type').value;
    const display = document.getElementById('vat_rate_display');
    
    if (!countryCode) {
        display.textContent = 'Select a country to see VAT rate';
        display.style.color = '#86868B';
        return;
    }
    
    try {
        const rate = getVATRatePercentage(countryCode, rateType);
        const countryName = getCountryName(countryCode);
        display.textContent = `${countryName}: ${rate}% VAT`;
        display.style.color = '#34C759'; // Success green
    } catch (error) {
        console.error('Error getting VAT rate:', error);
        display.textContent = 'VAT rate not available';
        display.style.color = '#FF3B30'; // Error red
    }
}

// Add new item row
function addItem() {
    itemCount++;
    const container = document.getElementById('itemsContainer');
    
    const itemRow = document.createElement('div');
    itemRow.className = 'item-row';
    itemRow.id = `item-${itemCount}`;
    
    itemRow.innerHTML = `
        <div class="form-group">
            <label for="product_name_${itemCount}">Product/Service Name</label>
            <input type="text" 
                   id="product_name_${itemCount}" 
                   name="product_name_${itemCount}" 
                   placeholder="Product or service name" 
                   required>
        </div>
        
        <div class="form-group">
            <label for="sku_${itemCount}">SKU</label>
            <input type="text" 
                   id="sku_${itemCount}" 
                   name="sku_${itemCount}" 
                   placeholder="SKU-001" 
                   value="SKU-${itemCount}">
        </div>
        
        <div class="form-group">
            <label for="quantity_${itemCount}">Quantity</label>
            <input type="number" 
                   id="quantity_${itemCount}" 
                   name="quantity_${itemCount}" 
                   min="1" 
                   value="1" 
                   required>
        </div>
        
        <div class="form-group">
            <label for="unit_code_${itemCount}">Unit</label>
            <select id="unit_code_${itemCount}" name="unit_code_${itemCount}">
                <option value="C62">Units (pcs)</option>
                <option value="HUR">Hours</option>
                <option value="DAY">Days</option>
                <option value="MON">Months</option>
                <option value="KGM">Kilograms</option>
                <option value="LTR">Liters</option>
                <option value="MTR">Meters</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="unit_price_${itemCount}">Unit Price (€)</label>
            <input type="number" 
                   id="unit_price_${itemCount}" 
                   name="unit_price_${itemCount}" 
                   step="0.01" 
                   min="0" 
                   placeholder="0.00" 
                   required>
        </div>
        
        <div class="form-group">
            <label>&nbsp;</label>
            <button type="button" 
                    class="btn-danger btn-small remove-item-btn" 
                    onclick="removeItem('item-${itemCount}')">
                Remove
            </button>
        </div>
    `;
    
    container.appendChild(itemRow);
}

// Remove item row
function removeItem(itemId) {
    const itemRow = document.getElementById(itemId);
    if (itemRow) {
        // Only remove if there's more than one item
        const itemsContainer = document.getElementById('itemsContainer');
        if (itemsContainer.children.length > 1) {
            itemRow.remove();
        } else {
            showAlert('You must have at least one item in the invoice', 'error');
        }
    }
}

// Show alert message
function showAlert(message, type = 'success') {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Handle form submission
document.getElementById('invoiceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.classList.add('loading');
    submitButton.textContent = 'Generating...';
    
    try {
        // Collect form data
        const countryCode = document.getElementById('buyer_country').value;
        const vatRateType = document.getElementById('vat_rate_type').value;
        
        const formData = {
            buyer_name: document.getElementById('buyer_name').value,
            buyer_street: document.getElementById('buyer_street').value,
            buyer_city: document.getElementById('buyer_city').value,
            buyer_postal: document.getElementById('buyer_postal').value,
            buyer_country: countryCode,
            buyer_vat_id: document.getElementById('buyer_vat_id').value,
            vat_rate_type: vatRateType,
            shipping_total: parseFloat(document.getElementById('shipping_total').value) || 0,
            currency: document.getElementById('currency').value,
            shipping_service: document.getElementById('shipping_service').value,
            payment_terms: document.getElementById('payment_terms').value,
            payment_means: document.getElementById('payment_means').value,
            payment_reference: document.getElementById('payment_reference').value,
            items: []
        };
        
        // Collect items
        const itemRows = document.querySelectorAll('.item-row');
        itemRows.forEach((row, index) => {
            const itemId = row.id.split('-')[1];
            const item = {
                product_name: document.getElementById(`product_name_${itemId}`).value,
                sku: document.getElementById(`sku_${itemId}`).value,
                quantity: parseInt(document.getElementById(`quantity_${itemId}`).value),
                unit_price: parseFloat(document.getElementById(`unit_price_${itemId}`).value),
                unit_code: document.getElementById(`unit_code_${itemId}`).value
            };
            formData.items.push(item);
        });
        
        // Validate items
        if (formData.items.length === 0) {
            throw new Error('Please add at least one item');
        }
        
        // Send to API
        const response = await fetch('/api/generate-invoice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to generate invoice');
        }
        
        // Success! Show download section
        currentInvoiceFilename = result.filename;
        document.getElementById('formSection').style.display = 'none';
        document.getElementById('downloadSection').classList.add('show');
        
        showAlert('Invoice generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message || 'Failed to generate invoice. Please try again.', 'error');
    } finally {
        submitButton.classList.remove('loading');
        submitButton.textContent = 'Generate Invoice';
    }
});

// Download invoice
function downloadInvoice() {
    if (currentInvoiceFilename) {
        window.location.href = `/download/${currentInvoiceFilename}`;
    }
}

// Create another invoice
function createAnother() {
    // Reset form
    document.getElementById('invoiceForm').reset();
    document.getElementById('formSection').style.display = 'block';
    document.getElementById('downloadSection').classList.remove('show');
    
    // Clear items and add one fresh item
    document.getElementById('itemsContainer').innerHTML = '';
    itemCount = 0;
    addItem();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Calculate and display total (optional preview feature)
function calculateTotal() {
    let subtotal = 0;
    const itemRows = document.querySelectorAll('.item-row');
    
    itemRows.forEach((row) => {
        const itemId = row.id.split('-')[1];
        const quantity = parseFloat(document.getElementById(`quantity_${itemId}`).value) || 0;
        const unitPrice = parseFloat(document.getElementById(`unit_price_${itemId}`).value) || 0;
        subtotal += quantity * unitPrice;
    });
    
    const shipping = parseFloat(document.getElementById('shipping_total').value) || 0;
    const countryCode = document.getElementById('buyer_country').value;
    const rateType = document.getElementById('vat_rate_type').value;
    
    // Get VAT rate from country
    let vatRate = 0;
    if (countryCode) {
        try {
            vatRate = getVATRate(countryCode, rateType);
        } catch (e) {
            vatRate = 0.19; // Fallback
        }
    }
    
    const total = (subtotal + shipping) * (1 + vatRate);
    
    return {
        subtotal: subtotal.toFixed(2),
        shipping: shipping.toFixed(2),
        vat: ((subtotal + shipping) * vatRate).toFixed(2),
        total: total.toFixed(2)
    };
}
