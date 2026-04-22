from PIL import Image, ImageFont, ImageDraw
from pilmoji import Pilmoji
import time

img1 = Image.new('RGB', (200, 100), color='black')
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
emoji = "🇺🇸"

pilmoji = Pilmoji(img1)

pilmoji.text((10, 10), emoji, (255, 255, 255), font=font)

img2 = Image.new('RGB', (200, 100), color='black')
pilmoji.image = img2
pilmoji.draw = ImageDraw.Draw(img2)

pilmoji.text((10, 10), emoji, (255, 255, 255), font=font)

img2.save('test_img2.png')
print("Done")
