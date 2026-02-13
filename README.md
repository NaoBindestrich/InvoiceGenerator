# 🎯 Invoice Generator Web Platform

A beautiful, modern web application for generating professional invoices with an Apple-inspired design.

![Status](https://img.shields.io/badge/status-ready-success)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)

## ✨ Features

- 🎨 **Beautiful UI** - Clean, Apple-inspired design
- ⚙️ **Web Settings** - Configure company info directly in the browser
- 📄 **Professional PDFs** - Generate invoices instantly
- 💰 **Smart VAT** - Automatic tax calculations
- 🌍 **Multi-country** - Support for all EU countries
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

- **[docs/DEPLOY.md](docs/DEPLOY.md)** - 5-minute Render.com deployment guide
- **[docs/HOSTING_GUIDE.md](docs/HOSTING_GUIDE.md)** - All hosting platforms compared
- **[docs/SEO_GUIDE.md](docs/SEO_GUIDE.md)** - Complete SEO & Google visibility strategy
- **[docs/SEO_CHECKLIST.md](docs/SEO_CHECKLIST.md)** - Quick SEO implementation checklist
- **[docs/EN16931_COMPLIANCE.md](docs/EN16931_COMPLIANCE.md)** - EU eInvoicing standard guide
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed setup walkthrough

## 🎯 Use Cases

- **Freelancers** - Quick invoice generation
- **Small Businesses** - Professional billing
- **Service Platform** - White-label solution
- **API Integration** - Embed in your app

## 📁 Project Structure

```
├── app.py                      # Main Flask application
├── invoice_generator.py        # Original CLI tool
├── invoice_generator_web.py    # PDF generation module
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment configuration
├── render.yaml                 # Render.com config
├── runtime.txt                 # Python version
│
├── static/                     # Frontend assets
│   ├── css/                    # Stylesheets (Liquid Glass design)
│   ├── js/                     # JavaScript (app.js, liquid-glass.js, vat-rates.js)
│   └── images/                 # Images & icons
│
├── templates/                  # HTML templates
│   ├── index.html              # Main invoice form
│   └── settings.html           # Company settings page
│docs/SETUP_GUIDE.md](docs/
├── generated_invoices/         # PDF output folder
├── company_config.json         # Your company info (gitignored)
│
├── docs/                       # 📚 Documentation
│   ├── DEPLOY.md               # Deployment guide
│   ├── HOSTING_GUIDE.md        # Platform comparison
│   ├── SEO_GUIDE.md            # SEO strategy
│   ├── SEO_CHECKLIST.md        # SEO tasks
│   ├── EN16931_COMPLIANCE.md   # EU standard info
│   ├── SETUP_GUIDE.md          # Setup walkthrough
│   └── QUICKSTART.md           # Quick reference
│
├── scripts/                    # 🛠️ Utility scripts
│   ├── deploy_setup.sh         # Deployment validator
│   ├── submit_to_search_engines.sh  # SEO submission
│   ├── create_og_image.py      # Social media image generator
│   └── start.sh                # App launcher
│
└── config/                     # ⚙️ Configuration templates
    ├── .env.template           # Environment variables
    └── company_config.template.json  # Company info template
```

## 🌐 Next Steps

Ready to make this a paid service? Check out:
- User authentication
- Payment integration (Stripe/PayPal)
- Cloud deployment (Heroku/Railway)
- Database integration
- Email delivery

See the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed roadmap.

## 📄 License

Free to use and modify for personal or commercial projects.

---

**Made with ❤️ and Python**
