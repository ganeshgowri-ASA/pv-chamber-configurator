"""
Script to create placeholder assets for reports
"""

from PIL import Image, ImageDraw, ImageFont

def create_logo_placeholder():
    """Create a placeholder logo"""
    # Create image
    width, height = 400, 150
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([10, 10, width-10, height-10], outline='#2c5aa0', width=3)

    # Draw text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    text = "ZENITEK"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 10

    draw.text((x, y), text, fill='#2c5aa0', font=font)

    # Draw subtitle
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_small = ImageFont.load_default()

    subtitle = "Solutions for PV Testing"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2

    draw.text((x, y + 50), subtitle, fill='#1f4788', font=font_small)

    # Save
    img.save('assets/logo.png')
    print("Created: assets/logo.png")

def create_watermark_placeholder():
    """Create a placeholder watermark"""
    width, height = 600, 200
    img = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()

    text = "DRAFT"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw with transparency
    draw.text((x, y), text, fill=(128, 128, 128, 50), font=font)

    img.save('assets/watermark.png')
    print("Created: assets/watermark.png")

def create_signature_placeholder():
    """Create a placeholder signature"""
    width, height = 300, 100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw signature line
    draw.line([(20, 70), (280, 70)], fill='black', width=2)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 24)
    except:
        font = ImageFont.load_default()

    text = "Authorized Signature"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2

    draw.text((x, 30), text, fill='#333333', font=font)

    # Draw date placeholder
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_small = ImageFont.load_default()

    draw.text((20, 80), "Date: __________", fill='#666666', font=font_small)

    img.save('assets/signature_placeholder.png')
    print("Created: assets/signature_placeholder.png")

if __name__ == '__main__':
    create_logo_placeholder()
    create_watermark_placeholder()
    create_signature_placeholder()
    print("\nAll placeholder assets created successfully!")
