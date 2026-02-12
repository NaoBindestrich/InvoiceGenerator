#!/bin/bash

# SEO Submission Helper Script
# Run after deploying to Render.com

echo "🔍 Invoice Generator - SEO Submission Helper"
echo "============================================"
echo ""

# Get the URL
read -p "Enter your Render.com URL (e.g., https://invoice-generator.onrender.com): " SITE_URL

if [ -z "$SITE_URL" ]; then
    echo "❌ URL is required"
    exit 1
fi

# Clean URL (remove trailing slash)
SITE_URL=$(echo "$SITE_URL" | sed 's:/*$::')

echo ""
echo "🌐 Your Site: $SITE_URL"
echo ""

# Check if site is accessible
echo "📡 Checking if site is online..."
if curl -s -o /dev/null -w "%{http_code}" "$SITE_URL" | grep -q "200"; then
    echo "✅ Site is online and responding"
else
    echo "⚠️  Site might not be responding. Check your Render deployment."
fi

echo ""
echo "🔍 Checking SEO files..."

# Check robots.txt
if curl -s "$SITE_URL/robots.txt" | grep -q "User-agent"; then
    echo "✅ robots.txt is accessible"
else
    echo "❌ robots.txt not found"
fi

# Check sitemap.xml
if curl -s "$SITE_URL/sitemap.xml" | grep -q "urlset"; then
    echo "✅ sitemap.xml is accessible"
else
    echo "❌ sitemap.xml not found"
fi

echo ""
echo "============================================"
echo "📋 Manual Submission Links"
echo "============================================"
echo ""

echo "1️⃣  Google Search Console:"
echo "   https://search.google.com/search-console"
echo "   → Add property: $SITE_URL"
echo "   → Submit sitemap: $SITE_URL/sitemap.xml"
echo ""

echo "2️⃣  Bing Webmaster Tools:"
echo "   https://www.bing.com/webmasters"
echo "   → Add site: $SITE_URL"
echo "   → Submit sitemap: $SITE_URL/sitemap.xml"
echo ""

echo "3️⃣  Google Index Request (Quick):"
echo "   https://www.google.com/ping?sitemap=$SITE_URL/sitemap.xml"
echo ""

echo "============================================"
echo "📱 Share on Social Media"
echo "============================================"
echo ""

echo "Twitter/X:"
echo "   🎉 Just launched my free Invoice Generator!"
echo "   ✅ EN 16931 Compliant"
echo "   📄 Creates professional PDF invoices"
echo "   🆓 100% Free to use"
echo "   "
echo "   Try it: $SITE_URL"
echo "   #invoicing #freelance #smallbusiness"
echo ""

echo "LinkedIn:"
echo "   Excited to share my new project: Invoice Generator!"
echo "   "
echo "   🎯 Features:"
echo "   • EN 16931 Compliant (EU standard)"
echo "   • Professional PDF generation"
echo "   • Automatic VAT calculation"
echo "   • Multi-currency support"
echo "   • Completely free"
echo "   "
echo "   Perfect for freelancers and small businesses."
echo "   Check it out: $SITE_URL"
echo ""

echo "============================================"
echo "📊 Directory Submissions"
echo "============================================"
echo ""

echo "Submit your tool to these directories:"
echo ""
echo "✅ Product Hunt: https://www.producthunt.com/posts/new"
echo "✅ AlternativeTo: https://alternativeto.net/software/register/"
echo "✅ Capterra: https://www.capterra.com/vendors/sign-up"
echo "✅ SaaSHub: https://www.saashub.com/submit"
echo "✅ Indie Hackers: https://www.indiehackers.com"
echo ""

echo "============================================"
echo "🎯 Next Steps"
echo "============================================"
echo ""
echo "1. Submit to Google Search Console (5 min)"
echo "2. Create social media accounts"
echo "3. Share on Twitter/LinkedIn"
echo "4. Post on Product Hunt"
echo "5. Submit to 3-5 directories"
echo ""
echo "📖 Full guide: See SEO_GUIDE.md"
echo ""
echo "Your site will start appearing in Google within 1-2 weeks! 🚀"
echo ""
