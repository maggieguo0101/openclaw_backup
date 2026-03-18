#!/usr/bin/env python3
from PIL import Image
import os

# Images to use (selecting the best 6 for 2x3 grid)
img_dir = '/root/.openclaw/workspace/'
images = [
    'xhs_img_1.jpg',  # 松果乐园
    'xhs_img_2.jpg',  # 游玩设施
    'xhs_img_3.jpg',  # 勇敢者道路
    'xhs_img_4.jpg',  # 设施
    'xhs_img_5.jpg',  # 设施
    'xhs_img_6.jpg',  # 游玩
]

# Load and resize images to same size
target_size = (800, 800)
loaded = []
for img_name in images:
    img_path = os.path.join(img_dir, img_name)
    img = Image.open(img_path)
    # Crop to square first for better composition
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    loaded.append(img)

# Create 2x3 grid
rows, cols = 2, 3
grid_width = cols * target_size[0]
grid_height = rows * target_size[1]

collage = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))

for idx, img in enumerate(loaded):
    row = idx // cols
    col = idx % cols
    x = col * target_size[0]
    y = row * target_size[1]
    collage.paste(img, (x, y))

# Save
output_path = '/root/.openclaw/workspace/xujiahui_collage.png'
collage.save(output_path, 'PNG', quality=95)
print(f'Saved to {output_path}')

# Also create a version with title text
from PIL import ImageDraw, ImageFont

# Add title at top
final = Image.new('RGB', (grid_width, grid_height + 100), (255, 255, 255))
final.paste(collage, (0, 100))

draw = ImageDraw.Draw(final)
# Try to use a font, fallback to default
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
except:
    font = ImageFont.load_default()

title = "徐家汇公园·松果乐园"
# Center the title
bbox = draw.textbbox((0, 0), title, font=font)
title_width = bbox[2] - bbox[0]
x = (grid_width - title_width) // 2
draw.text((x, 25), title, fill=(51, 51, 51), font=font)

final.save('/root/.openclaw/workspace/xujiahui_collage_with_title.png', 'PNG', quality=95)
print('Saved version with title')
