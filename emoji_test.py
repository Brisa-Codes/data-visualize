from PIL import Image, ImageDraw, ImageFont
import sys

img = Image.new('RGB', (200, 50), color='white')
draw = ImageDraw.Draw(img)

for size in [16, 20, 24, 32, 40, 48, 64, 96, 109, 137, 160]:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", size)
        draw.text((10, 10), "🇺🇸", font=font, fill="black", embedded_color=True)
        print(f"Success with size {size}")
    except Exception as e:
        print(f"Failed with size {size}: {e}")
