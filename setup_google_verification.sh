#!/bin/bash

# Google Search Console Verification Helper
echo "🔍 Google Search Console - Verification Helper"
echo "==============================================="
echo ""

echo "Choose verification method:"
echo "1) Meta Tag (Recommended - easiest)"
echo "2) HTML File (Alternative)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "📝 Meta Tag Method"
    echo "=================="
    echo ""
    echo "Steps:"
    echo "1. Go to: https://search.google.com/search-console"
    echo "2. Add your site property"
    echo "3. Choose 'HTML tag' verification"
    echo "4. Google will show: <meta name=\"google-site-verification\" content=\"ABC123...\" />"
    echo "5. Copy ONLY the content value (the long string)"
    echo ""
    read -p "Paste your verification code here: " verification_code
    
    if [ -z "$verification_code" ]; then
        echo "❌ No code provided"
        exit 1
    fi
    
    echo ""
    echo "✅ Code received: $verification_code"
    echo ""
    echo "🚀 Next steps on Render.com:"
    echo ""
    echo "1. Go to your Render dashboard"
    echo "2. Select your web service"
    echo "3. Click 'Environment' tab"
    echo "4. Click 'Add Environment Variable'"
    echo "5. Add this:"
    echo "   Key: GOOGLE_VERIFICATION"
    echo "   Value: $verification_code"
    echo "6. Click 'Save Changes'"
    echo "7. Wait 1-2 minutes for redeploy"
    echo "8. Go back to Google Search Console and click 'Verify'"
    echo ""
    echo "💡 For local testing, add to .env:"
    echo "   GOOGLE_VERIFICATION=$verification_code"
    echo ""
    
elif [ "$choice" = "2" ]; then
    echo ""
    echo "📄 HTML File Method"
    echo "==================="
    echo ""
    echo "Steps:"
    echo "1. Go to: https://search.google.com/search-console"
    echo "2. Add your site property"
    echo "3. Choose 'HTML file download' verification"
    echo "4. Download the file (e.g., google123abc.html)"
    echo "5. Open it in text editor and copy ALL content"
    echo ""
    read -p "Paste the ENTIRE file content here: " file_content
    
    if [ -z "$file_content" ]; then
        echo "❌ No content provided"
        exit 1
    fi
    
    echo ""
    echo "✅ Content received"
    echo ""
    echo "🚀 Next steps on Render.com:"
    echo ""
    echo "1. Go to your Render dashboard"
    echo "2. Select your web service"
    echo "3. Click 'Environment' tab"
    echo "4. Click 'Add Environment Variable'"
    echo "5. Add this:"
    echo "   Key: GOOGLE_VERIFICATION_FILE"
    echo "   Value: $file_content"
    echo "6. Click 'Save Changes'"
    echo "7. Wait 1-2 minutes for redeploy"
    echo "8. Go back to Google Search Console and click 'Verify'"
    echo ""
else
    echo "❌ Invalid choice"
    exit 1
fi

echo "==============================================="
echo "📖 Full guide: See GOOGLE_VERIFICATION.md"
echo "==============================================="
