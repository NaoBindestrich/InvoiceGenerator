#!/usr/bin/env python3
"""
Generate a simple Open Graph image for social media sharing
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_og_image():
    """Create a simple 1200x630 Open Graph image"""
    
    # Image dimensions for Open Graph
    width, height = 1200, 630
    
    # Create gradient background
    img = Image.new('RGB', (width, height), color='#007AFF')
    draw = ImageDraw.Draw(img)
    
    # Add gradient effect (simple version)
    for y in range(height):
        alpha = int(255 * (1 - y / height * 0.3))
        color = (0, 122, 255 - int(50 * y / height))
        draw.rectangle([(0, y), (width, y + 1)], fill=color)
    
    # Add text
    try:
        # Try to use a nice font
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Title
    title = "Invoice Generator"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 200), title, fill='white', font=title_font)
    
    # Subtitle
    subtitle = "Create Professional Invoices in Seconds"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, 320), subtitle, fill='white', font=subtitle_font)
    
    # Features
    features = "Free • PDF Export • EN 16931 Compliant"
    features_bbox = draw.textbbox((0, 0), features, font=subtitle_font)
    features_width = features_bbox[2] - features_bbox[0]
    features_x = (width - features_width) // 2
    draw.text((features_x, 420), features, fill='white', font=subtitle_font)
    
    # Save
    output_path = Path(__file__).parent / 'static' / 'images' / 'og-image.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG', optimize=True)
    
    print(f"✅ Open Graph image created: {output_path}")
    print(f"📐 Size: {width}x{height}px")
    print(f"📊 File size: {output_path.stat().st_size / 1024:.1f} KB")
    print()
    print("🎨 Customize it:")
    print("   - Use Canva: https://canva.com")
    print("   - Use Figma: https://figma.com")
    print("   - Edit with any image editor")

if __name__ == '__main__':
    try:
        create_og_image()
    except ImportError:
        print("❌ Pillow not installed")
        print("Install it: pip install pillow")
        print()
        print("Alternative: Create image manually")
        print("- Size: 1200x630 pixels")
        print("- Save as: static/images/og-image.png")
        print("- Use Canva (free): https://canva.com")
