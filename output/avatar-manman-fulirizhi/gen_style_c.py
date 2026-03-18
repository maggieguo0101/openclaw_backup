#!/usr/bin/env python3
"""
风格C：中式国潮 × 朱砂红金
- 深墨红/朱砂底色 + 金色文字 + 传统纹样（回字纹）
- 厚重、权威感，"复利"呼应传统积累哲学
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_c.png")
W, H = 500, 500

C_BG     = (45, 12, 12)    # 深朱砂
C_BG2    = (62, 18, 16)    # 稍亮暗红
C_GOLD   = (212, 168, 80)  # 古金
C_GOLD_H = (242, 210, 120) # 高光金
C_RED    = (180, 48, 30)   # 朱砂点缀
C_CREAM  = (240, 228, 195) # 米白

FONT_BOLD  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
FONT_REG   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

import numpy as np
arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y/H
    for c in range(3):
        arr[y,:,c] = int(C_BG[c]+(C_BG2[c]-C_BG[c])*t)
img = Image.fromarray(arr,"RGB")
draw = ImageDraw.Draw(img)

# ── 回字纹边框 ──────────────────────────
def draw_fret(draw, x0, y0, x1, y1, color, step=20, width=1):
    """简化回字纹：矩形嵌套"""
    for i in range(3):
        off = i * step
        if x0+off < x1-off and y0+off < y1-off:
            draw.rectangle([x0+off, y0+off, x1-off, y1-off], outline=color, width=width)

draw_fret(draw, 14, 14, W-14, H-14, C_GOLD, step=8, width=1)
draw_fret(draw, 24, 24, W-24, H-24, (*C_GOLD,), step=0, width=1)

# ── 四角云纹（简化）──────────────────────
corner_sz = 30
for (cx2, cy2) in [(25,25),(W-25,25),(25,H-25),(W-25,H-25)]:
    draw.ellipse([cx2-corner_sz//2, cy2-corner_sz//2, cx2+corner_sz//2, cy2+corner_sz//2],
                 outline=C_GOLD, width=1)
    draw.ellipse([cx2-corner_sz//4, cy2-corner_sz//4, cx2+corner_sz//4, cy2+corner_sz//4],
                 fill=C_RED)

# ── 大圆印章感 ────────────────────────────
cx, cy = W//2, H//2
R = 165
draw.ellipse([cx-R, cy-R, cx+R, cy+R], outline=C_GOLD, width=2)
draw.ellipse([cx-R+6, cy-R+6, cx+R-6, cy+R-6], outline=(*C_GOLD,), width=1)

# ── 圆内纹饰：八卦样式简化（8段圆弧）────────
for i in range(8):
    ang = math.radians(i * 45)
    ax = cx + (R-14) * math.cos(ang)
    ay = cy + (R-14) * math.sin(ang)
    draw.ellipse([ax-3,ay-3,ax+3,ay+3], fill=C_GOLD_H)

# ── 主文字 ────────────────────────────────
try:
    f_big   = ImageFont.truetype(FONT_BOLD, 58)
    f_med   = ImageFont.truetype(FONT_SERIF, 28)
    f_small = ImageFont.truetype(FONT_REG, 14)
except:
    f_big = f_med = f_small = ImageFont.load_default()

# 「慢慢」居中上
t1 = "慢慢"
bb1 = draw.textbbox((0,0), t1, font=f_big)
tw1 = bb1[2]-bb1[0]; th1=bb1[3]-bb1[1]
ty1 = cy - th1 - 14
for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text(((W-tw1)//2+dx, ty1+dy), t1, font=f_big, fill=(80,40,10))
draw.text(((W-tw1)//2, ty1), t1, font=f_big, fill=C_GOLD_H)

# 「复利日记」居中下
t2 = "复利日记"
bb2 = draw.textbbox((0,0), t2, font=f_big)
tw2 = bb2[2]-bb2[0]; th2=bb2[3]-bb2[1]
ty2 = cy + 14
for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text(((W-tw2)//2+dx, ty2+dy), t2, font=f_big, fill=(80,40,10))
draw.text(((W-tw2)//2, ty2), t2, font=f_big, fill=C_CREAM)

# 两行之间：朱砂横线 + 菱形
mid_y = ty1+th1+8
draw.line([(W//2-55, mid_y),(W//2-8,mid_y)], fill=C_RED, width=2)
draw.polygon([(W//2-5,mid_y-5),(W//2,mid_y-10),(W//2+5,mid_y-5),(W//2,mid_y)], fill=C_GOLD)
draw.line([(W//2+8,mid_y),(W//2+55,mid_y)], fill=C_RED, width=2)

# 底部slogan
slogan = "不追涨  ·  只赚确定性的钱"
bb_s = draw.textbbox((0,0), slogan, font=f_small)
tw_s = bb_s[2]-bb_s[0]
draw.text(((W-tw_s)//2, H-36), slogan, font=f_small, fill=C_GOLD)

img.save(OUT, "PNG")
print(f"✅ style_c saved: {OUT}")
