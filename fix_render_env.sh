#!/bin/bash

# Quick Fix for Render Environment Variable Issue
echo "🔧 Render Environment Variable - Quick Fix"
echo "=========================================="
echo ""

echo "Problem: Environment variables not triggering redeploy on Render"
echo ""
echo "Choose a solution:"
echo ""
echo "1) Manual Deploy (Fastest - 2 minutes)"
echo "2) Push code change to force deploy (3 minutes)"
echo "3) Add to render.yaml and deploy (Recommended - permanent)"
echo ""
read -p "Enter choice (1, 2, or 3): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "📋 Manual Deploy Steps:"
    echo "======================="
    echo ""
    echo "1. Go to: https://dashboard.render.com"
    echo "2. Select your 'invoice-generator' service"
    echo "3. Click the 'Environment' tab (left sidebar)"
    echo "4. Add environment variable:"
    echo "   Key: GOOGLE_VERIFICATION"
    read -p "   Enter your Google verification code: " code
    echo "   Value: $code"
    echo ""
    echo "5. Click 'Save Changes'"
    echo "6. IMPORTANT: Click 'Manual Deploy' button (top right)"
    echo "7. Click 'Deploy latest commit'"
    echo "8. Wait 1-2 minutes"
    echo ""
    echo "9. Test it:"
    echo "   Visit your site and view source, look for:"
    echo "   <meta name=\"google-site-verification\" content=\"$code\" />"
    echo ""
    
elif [ "$choice" = "2" ]; then
    echo ""
    echo "🚀 Force Deploy with Code Change"
    echo "================================="
    echo ""
    echo "This will push a tiny change to trigger Render deployment:"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    # Add a comment to README to trigger deploy
    echo "" >> README.md
    echo "<!-- Deploy triggered at $(date) -->" >> README.md
    
    git add README.md
    git commit -m "Trigger Render redeploy for environment variables"
    
    echo ""
    echo "Pushing to GitHub..."
    git push origin main
    
    echo ""
    echo "✅ Pushed! Render will deploy automatically in 1-2 minutes."
    echo ""
    echo "After deploy, test at: https://your-app.onrender.com/"
    echo ""
    
elif [ "$choice" = "3" ]; then
    echo ""
    echo "📝 Add to render.yaml (Recommended)"
    echo "===================================="
    echo ""
    read -p "Enter your Google verification code: " code
    
    if [ -z "$code" ]; then
        echo "❌ No code provided"
        exit 1
    fi
    
    echo ""
    echo "Updating render.yaml..."
    
    # Update render.yaml with the actual code
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/YOUR_VERIFICATION_CODE_HERE/$code/" render.yaml
    else
        # Linux
        sed -i "s/YOUR_VERIFICATION_CODE_HERE/$code/" render.yaml
    fi
    
    echo "✅ render.yaml updated"
    echo ""
    echo "Now committing and pushing..."
    
    git add render.yaml
    git commit -m "Configure Google Search Console verification code"
    git push origin main
    
    echo ""
    echo "✅ Done! Render will deploy automatically in 1-2 minutes."
    echo ""
    echo "The verification code is now in render.yaml and will persist across deploys."
    echo ""
else
    echo "❌ Invalid choice"
    exit 1
fi

echo ""
echo "=========================================="
echo "📖 Full guide: RENDER_ENV_FIX.md"
echo "=========================================="
echo ""
echo "After Render deploys, verify it worked:"
echo "  curl https://your-app.onrender.com/ | grep google-site-verification"
echo ""
echo "Then go to Google Search Console and click 'Verify'"
echo ""
