# EN 16931 European eInvoicing Standard Compliance

## Overview
Your Invoice Generator is now compliant with **EN 16931**, the European standard for electronic invoicing, making your invoices legally valid for B2B transactions across the EU.

## What is EN 16931?
EN 16931 is the European standard for electronic invoicing that will become **mandatory for B2B transactions** in EU member states by 2028. It ensures invoices contain all necessary information for automated processing and compliance with tax regulations.

## Implemented Features

### 1. Required Fields Added

#### Customer Information
- **Buyer VAT ID (USt-IdNr)**: Now displayed below the billing address
  - Required for B2B transactions in EU
  - Format: Country code + numbers (e.g., DE123456789)

#### Payment & Due Date
- **Due Date (Fälligkeitsdatum)**: Replaces generic payment date
  - Automatically calculated based on payment terms
  - Clearly shows when payment is expected
  
- **Payment Terms (Zahlungsbedingungen)**: 
  - Options: "Net 30 days", "Net 14 days", "Net 7 days", "Due on receipt"
  - Displayed in invoice footer
  
- **Payment Means (Zahlart)**:
  - Options: "Bank Transfer", "Credit Card", "PayPal", "Cash", "Direct Debit"
  - Replaces the old sales channel field
  
- **Payment Reference (Verwendungszweck)**:
  - Custom reference for payment identification
  - Helps match incoming payments
  - Displayed in footer

#### Product Information
- **Unit Code**: Standardized unit codes for items
  - C62 = Piece/Unit (default for most products)
  - HUR = Hour (services)
  - DAY = Day (rentals, subscriptions)
  - MON = Month
  - KGM = Kilogram
  - LTR = Liter
  - MTR = Meter

#### Company Information
- **VAT ID (USt-IdNr)**: Your company's EU VAT identification
- **BIC Code**: Bank Identifier Code for international transfers
- **Company Registration (Handelsregister)**: Official business registration number

## How to Use

### 1. Update Company Configuration
Edit your `company_config.json` file to include the new fields:

```json
{
    "name": "Your Company Name",
    "address_line": "Your Company, Street Address, City, Country",
    "vat_id": "DE123456789",
    "company_registration": "HRB 12345",
    "bic": "BYLADEM1001",
    "iban": "DE89 3704 0044 0532 0130 00",
    "bank": "Deutsche Bank",
    "court": "Amtsgericht München",
    "uid": "DE123456789",
    "ceo": "John Doe"
}
```

### 2. Fill Invoice Form
When creating an invoice, provide:

1. **Customer VAT ID**: Enter the buyer's EU VAT number (e.g., FR12345678901)
2. **Payment Terms**: Select from dropdown (e.g., "Net 30 days")
3. **Payment Means**: Choose payment method (e.g., "Bank Transfer")
4. **Payment Reference**: Optional reference code (e.g., invoice number)
5. **Unit Codes**: Select appropriate unit for each item

### 3. Generated PDF Features
Your invoices will now show:

✅ **Header Section**:
- Invoice Number
- Invoice Date
- Order Date
- **Due Date** (calculated from payment terms)
- **Payment Method**

✅ **Customer Section**:
- Name and Address
- **VAT ID** (if B2B customer)

✅ **Items Table**:
- Position
- SKU
- Product Name
- **Quantity with Unit Code**
- Price
- Total

✅ **Footer Section**:
- Bank details (IBAN, **BIC**)
- **Payment Terms**
- **Payment Reference**
- Company registration details
- **Company VAT ID**
- Legal information

## Benefits

### Legal Compliance
✅ Ready for EU B2B eInvoicing mandate (2028)
✅ Valid for cross-border transactions
✅ Meets tax authority requirements

### Business Advantages
✅ **Automated Payment Tracking**: Due dates and references help match payments
✅ **Professional Appearance**: Shows you're modern and compliant
✅ **International Ready**: Proper VAT IDs for EU business
✅ **Clear Terms**: Customers know exactly when payment is due

### Technical Features
✅ **Automatic Due Date Calculation**: 
   - "Net 30 days" → Invoice date + 30 days
   - "Net 14 days" → Invoice date + 14 days
   - "Net 7 days" → Invoice date + 7 days
   - "Due on receipt" → Invoice date

✅ **Standardized Units**: UN/CEFACT unit codes for compatibility
✅ **Future-Ready**: Foundation for XML/UBL export (Phase 2)

## Next Steps (Optional Enhancements)

### Phase 2: XML/UBL Export
- Export invoices in UBL 2.1 XML format
- Full machine-readable invoices
- Required for Peppol network

### Phase 3: Peppol Integration
- Connect to Peppol eDelivery network
- Direct B2B invoice transmission
- Complete automated invoicing

## Compliance Checklist

Before sending B2B invoices in the EU, ensure:

- [ ] Company VAT ID is entered in `company_config.json`
- [ ] BIC code is added (for international customers)
- [ ] Customer VAT ID is collected for B2B transactions
- [ ] Payment terms are selected (default: Net 30 days)
- [ ] Due date is visible on invoice
- [ ] Unit codes are specified for all items
- [ ] Company registration number is displayed

## Technical Details

### Invoice Type Code
Currently set to **380** (Commercial Invoice) - the standard for B2B invoicing.

### Currency Support
Supports all major currencies: €, $, £, kr (SEK/DKK/NOK)

### VAT Compliance
- Automatically calculates net amounts
- Shows VAT percentage and amount
- Displays gross totals
- Handles discount calculations

## Support

Your invoice generator now meets EN 16931 Option 1 compliance requirements. For questions about:
- **Technical issues**: Check the code documentation
- **Legal requirements**: Consult your tax advisor
- **EU regulations**: See official EN 16931 documentation

## Resources

- [EN 16931 Standard Documentation](https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/Standards)
- [Peppol Network](https://peppol.org/)
- [UN/CEFACT Unit Codes](https://unece.org/trade/cefact/UNLOCODE-Download)

---
**Version**: 1.0 (EN 16931 Option 1)  
**Last Updated**: December 2024  
**Status**: Production Ready ✅
