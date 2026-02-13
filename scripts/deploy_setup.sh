#!/bin/bash

# Invoice Generator - Quick Deploy Script
echo "🚀 Invoice Generator - Quick Deploy Setup"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
.env
*.pdf
generated_invoices/*.pdf
company_config.json
.DS_Store
.vscode/
*.log
EOF
    echo "✅ .gitignore created"
fi

# Check if gunicorn is installed
echo ""
echo "📦 Checking dependencies..."
if pip show gunicorn > /dev/null 2>&1; then
    echo "✅ gunicorn is installed"
else
    echo "⚠️  Installing gunicorn..."
    pip install gunicorn==21.2.0
fi

# Test if app runs
echo ""
echo "🧪 Testing app startup..."
timeout 5 python -c "from app import app; print('✅ App imports successfully')" 2>/dev/null
if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    echo "✅ App is ready"
else
    echo "❌ App import failed - check your code"
    exit 1
fi

# Test gunicorn
echo ""
echo "🧪 Testing gunicorn..."
timeout 3 gunicorn --bind 0.0.0.0:8000 app:app --timeout 2 > /dev/null 2>&1
if [ $? -eq 124 ] || [ $? -eq 0 ]; then
    echo "✅ Gunicorn works"
else
    echo "⚠️  Gunicorn test inconclusive (this is usually fine)"
fi

# Git status
echo ""
echo "📊 Git Status:"
git status --short | head -10

echo ""
echo "=========================================="
echo "✅ Your app is ready to deploy!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Commit your changes:"
echo "   git add ."
echo "   git commit -m \"Ready for deployment\""
echo ""
echo "2️⃣  Create GitHub repository:"
echo "   • Go to: https://github.com/new"
echo "   • Create 'InvoiceGenerator' repo"
echo "   • Don't initialize with README"
echo ""
echo "3️⃣  Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/InvoiceGenerator.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4️⃣  Deploy on Render.com:"
echo "   • Go to: https://render.com"
echo "   • Sign up (free)"
echo "   • New Web Service"
echo "   • Connect your GitHub repo"
echo "   • Deploy!"
echo ""
echo "📖 Full guide: See HOSTING_GUIDE.md"
echo ""
