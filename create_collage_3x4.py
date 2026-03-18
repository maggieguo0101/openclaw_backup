#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

img_dir = '/root/.openclaw/workspace/'

# Select best 3 images for 3:4 ratio (vertical strip)
images = ['xhs_img_1.jpg', 'xhs_img_2.jpg', 'xhs_img_3.jpg']

# 3:4 ratio = 900x1200
target_width = 900
target_height = 1200

loaded = []
for img_name in images:
    img_path = os.path.join(img_dir, img_name)
    img = Image.open(img_path)
    # Resize to fit width, maintain aspect
    img.thumbnail((target_width, target_height // len(images)), Image.Resampling.LANCZOS)
    loaded.append(img)

# Create canvas
collage = Image.new('RGB', (target_width, target_height), (255, 255, 255))

# Paste images stacked vertically
y_offset = 0
for img in loaded:
    h = img.size[1]
    collage.paste(img, (0, y_offset))
    y_offset += h

# Add title
draw = ImageDraw.Draw(collage)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 50)
except:
    font = ImageFont.load_default()

title = "徐家汇公园·松果乐园"
bbox = draw.textbbox((0, 0), title, font=font)
title_width = bbox[2] - bbox[0]
x = (target_width - title_width) // 2
draw.text((x, 20), title, fill=(51, 51, 51), font=font)

collage.save('/root/.openclaw/workspace/xujiahui_collage_3x4.png', 'PNG', quality=95)
print('Saved 3:4 ratio version')
