#!/bin/bash

# Invoice Generator - Startup Script
# This script starts the Flask web application

echo "======================================================"
echo "🚀 Starting Invoice Generator Web Application"
echo "======================================================"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "   Activating .venv..."
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "❌ Failed to activate virtual environment"
        echo "   Please run: source .venv/bin/activate"
        exit 1
    fi
fi

# Check if Flask is installed
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask not installed"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Check if company_config.json exists
if [ ! -f "company_config.json" ]; then
    echo "⚠️  company_config.json not found"
    echo "   Creating from template..."
    cp company_config.template.json company_config.json
    echo "   ✓ Created company_config.json"
    echo "   📝 Please edit this file with your company details"
    echo ""
fi

echo "✓ All checks passed!"
echo ""
echo "======================================================"
echo "📝 Access your invoice generator at:"
echo "   http://localhost:5001"
echo "======================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
python app.py
