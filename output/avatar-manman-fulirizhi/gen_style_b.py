#!/usr/bin/env python3
"""
风格B：霓虹朋克极简
- 纯黑底 + 荧光绿/青色数字线条 + 等宽字体感
- 科技感、赛博朋克、给人"算法打新"的专业印象
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_b.png")
W, H = 500, 500

C_BG     = (8, 10, 12)
C_NEON   = (0, 255, 160)    # 荧光绿
C_CYAN   = (0, 200, 230)    # 青蓝
C_PURPLE = (160, 80, 255)   # 紫
C_WHITE  = (230, 235, 230)
C_DIM    = (40, 50, 44)

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

img = Image.new("RGB", (W, H), C_BG)
draw = ImageDraw.Draw(img)

# 随机"矩阵雨"背景字符（极淡）
random.seed(42)
try:
    f_matrix = ImageFont.truetype(FONT_MONO, 11)
except:
    f_matrix = ImageFont.load_default()
chars = "01+x%▲↑$€¥"
for _ in range(120):
    cx = random.randint(0, W)
    cy = random.randint(0, H)
    c = random.choice(chars)
    draw.text((cx, cy), c, font=f_matrix, fill=(0, 80, 50))

# 扫描线效果（横向细线）
for y in range(0, H, 6):
    draw.line([(0,y),(W,y)], fill=(0,20,12), width=1)

# 左侧竖向发光边线
for x_off, col, a in [(0, C_NEON, 180),(2, C_NEON, 60),(4, C_CYAN, 30)]:
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.line([(18+x_off,20),(18+x_off,H-20)], fill=(*col,a), width=2)
    img.paste(Image.new("RGB",img.size,col),
              mask=None) if False else None
for col, a in [(C_NEON,200),(C_NEON,60),(C_CYAN,30)]:
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.line([(18,20),(18,H-20)], fill=(*col,a), width=2)
    img_r = img.convert("RGBA"); img_r.alpha_composite(bar); img=img_r.convert("RGB")
    draw=ImageDraw.Draw(img)

# 顶部水平neon线
for col, a in [(C_CYAN,160),(C_CYAN,50)]:
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.line([(20,28),(W-20,28)], fill=(*col,a), width=2)
    img_r = img.convert("RGBA"); img_r.alpha_composite(bar); img=img_r.convert("RGB")
    draw=ImageDraw.Draw(img)

# 底部横线
for col, a in [(C_NEON,160),(C_NEON,50)]:
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.line([(20,H-28),(W-20,H-28)], fill=(*col,a), width=2)
    img_r = img.convert("RGBA"); img_r.alpha_composite(bar); img=img_r.convert("RGB")
    draw=ImageDraw.Draw(img)

# 背景大字水印 "%" 极淡紫
try:
    f_bg = ImageFont.truetype(FONT_BOLD, 200)
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.text((60, 100), "%", font=f_bg, fill=(*C_PURPLE, 15))
    img_r = img.convert("RGBA"); img_r.alpha_composite(bar); img=img_r.convert("RGB")
    draw=ImageDraw.Draw(img)
except: pass

# 主文字
try:
    f_main = ImageFont.truetype(FONT_BOLD, 52)
    f_sub  = ImageFont.truetype(FONT_REG, 15)
    f_mono = ImageFont.truetype(FONT_MONO, 13)
except:
    f_main = f_sub = f_mono = ImageFont.load_default()

# "慢慢复利日记" — 中央偏上，霓虹绿
txt = "慢慢复利日记"
bb = draw.textbbox((0,0), txt, font=f_main)
tw = bb[2]-bb[0]; th=bb[3]-bb[1]
tx = (W-tw)//2; ty = H//2-th//2-20

# 发光效果（多层偏移）
for off, a in [(3,25),(2,50),(1,80)]:
    bar = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.text((tx+off, ty+off), txt, font=f_main, fill=(*C_NEON, a))
    bd.text((tx-off, ty-off), txt, font=f_main, fill=(*C_CYAN, a//2))
    img_r = img.convert("RGBA"); img_r.alpha_composite(bar); img=img_r.convert("RGB")
    draw=ImageDraw.Draw(img)
draw.text((tx, ty), txt, font=f_main, fill=C_NEON)

# 下划线（neon）
ul_y = ty+th+6
draw.line([(tx, ul_y),(tx+tw, ul_y)], fill=C_CYAN, width=2)

# 底部mono风格slogan
slogan = "> 不追涨 · 只赚确定性的钱"
bb_s = draw.textbbox((0,0), slogan, font=f_mono)
draw.text(((W-(bb_s[2]-bb_s[0]))//2, H-50), slogan, font=f_mono, fill=(0,180,110))

# 右下角版本标记
draw.text((W-52, H-22), "v.2026", font=f_mono, fill=(0,80,50))

img.save(OUT, "PNG")
print(f"✅ style_b saved: {OUT}")
