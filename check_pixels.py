from PIL import Image, ImageFont
from pilmoji import Pilmoji
import numpy as np

img = Image.new('RGB', (200, 100), color='black')

font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
emoji = "🇺🇸"

with Pilmoji(img) as pilmoji:
    pilmoji.text((10, 10), emoji, (255, 255, 255), font=font)

arr = np.array(img)
if np.any(arr != 0):
    print("Has non-black pixels! pilmoji works.")
else:
    print("Entirely black. Nothing was drawn!")
