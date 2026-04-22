from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (200, 100), color='black')
draw = ImageDraw.Draw(img)

try:
    font_emoji = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 20)
    emoji = "🇺🇸"
    try:
        draw.text((10, 10), emoji, font=font_emoji, embedded_color=True)
        print("Success with embedded_color=True")
    except Exception as e:
        print("Failed with embedded_color=True:", e)
        draw.text((10, 10), emoji, font=font_emoji)
        print("Success without embedded_color")
    img.save('test_emoji_app.png')
except Exception as e:
    print("Outer exception:", e)
