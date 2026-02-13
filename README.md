# 🎯 Invoice Generator Web Platform

A beautiful, modern web application for generating professional invoices with an Apple-inspired design.

![Status](https://img.shields.io/badge/status-ready-success)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)

## ✨ Features

- 🎨 **Beautiful UI** - Clean, Apple-inspired design with Liquid Glass effects
- ⚙️ **Web Settings** - Configure company info directly in the browser
- 📄 **Professional PDFs** - Generate invoices instantly
- 💰 **Smart VAT** - Automatic tax calculations for 29 EU countries
- 🌍 **Multi-country** - Support for all EU countries with standard/reduced VAT rates
- 📜 **EN 16931 Compliant** - Meets EU electronic invoicing standards
- 🔒 **Legal Protection** - MIT License, Terms of Service, Privacy Policy included
- 🌐 **SEO Optimized** - Google Search Console verified
- ✅ **EN 16931 Compliant** - EU eInvoicing standard ready
- � **SEO Optimized** - Ready for Google search visibility
- �🚀 **Fast Setup** - Running in 3 minutes

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Configure your company
# Open http://localhost:5001/settings in your browser
# Fill in your company information

# 4. Start creating invoices
# Go to http://localhost:5001
```

## 📖 Documentation

- **[docs/INDEX.md](docs/INDEX.md)** - Documentation hub & navigation
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Get running in 3 minutes
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed setup & architecture
- **[docs/EN16931_COMPLIANCE.md](docs/EN16931_COMPLIANCE.md)** - EU eInvoicing standard guide
- **[docs/SEO_GUIDE.md](docs/SEO_GUIDE.md)** - SEO strategy & optimization tips

## 🎯 Use Cases

- **Freelancers** - Quick invoice generation
- **Small Businesses** - Professional billing
- **Service Platform** - White-label solution
- **API Integration** - Embed in your app

## 📁 Project Structure

```
├── app.py                      # Main Flask application
├── invoice_generator_web.py    # PDF generation module
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment configuration
├── render.yaml                 # Render.com config
├── runtime.txt                 # Python version (3.9.6)
│
├── static/                     # Frontend assets
│   ├── css/style.css           # Liquid Glass design
│   ├── js/                     # JavaScript files
│   │   ├── app.js              # Main app logic
│   │   ├── liquid-glass.js     # 3D effects & animations
│   │   ├── vat-rates.js        # EU VAT database (29 countries)
│   │   └── settings.js         # Settings page logic
│   └── images/                 # Assets (og-image.png, etc.)
│
├── templates/                  # HTML templates
│   ├── index.html              # Main invoice form
│   ├── settings.html           # Company settings page
│   ├── robots.txt              # SEO crawler rules
│   └── sitemap.xml             # SEO sitemap
│
├── generated_invoices/         # PDF output folder
├── company_config.json         # Your company info (gitignored)
│
└── docs/                       # 📚 Documentation
    ├── INDEX.md                # Documentation hub
    ├── QUICKSTART.md           # 3-minute setup
    ├── SETUP_GUIDE.md          # Detailed guide
    ├── EN16931_COMPLIANCE.md   # EU invoicing standard
    └── SEO_GUIDE.md            # SEO optimization
```

## 🌐 Production Status

✅ **Deployed on Render.com**  
✅ **Verified on Google Search Console**  
✅ **SEO Optimized**  
✅ **Production Ready**

## 🌐 Production Status

✅ **Deployed on Render.com**  
✅ **Verified on Google Search Console**  
✅ **SEO Optimized**  
✅ **Production Ready**

## 🚀 Next Steps

Want to enhance it further?
- User authentication & accounts
- Payment integration (Stripe/PayPal)
- Invoice history & database
- Email delivery
- Multi-language support

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed architecture.

## 📄 License

Free to use and modify for personal or commercial projects.

---

**Made with ❤️ and Python**
