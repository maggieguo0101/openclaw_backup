#!/usr/bin/env python3
"""
风格A：莫兰迪奶油色 × 手账感
- 米白/奶茶底色 + 棕金文字 + 手绘感小元素（叶片、圆圈）
- 温柔、高级感、适合女性理财博主
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_a.png")
W, H = 500, 500

# 颜色
C_BG    = (245, 240, 228)   # 暖米白
C_BG2   = (235, 228, 212)   # 稍深米
C_BROWN = (120, 88, 52)     # 棕金主色
C_GOLD  = (168, 128, 72)    # 浅棕金
C_SAGE  = (130, 148, 118)   # 雾霭绿
C_RUST  = (168, 108, 78)    # 砖红点缀
C_DARK  = (60, 48, 36)      # 深棕文字

FONT_BOLD  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

# 背景渐变
arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y / H
    for c in range(3):
        arr[y,:,c] = int(C_BG[c] + (C_BG2[c]-C_BG[c]) * t)
img = Image.fromarray(arr, "RGB")
draw = ImageDraw.Draw(img)

# 纸张纹理感：极淡圆点网格
for x in range(30, W, 30):
    for y in range(30, H, 30):
        draw.ellipse([x-1,y-1,x+1,y+1], fill=(200,192,178))

# 大圆：中心装饰圆（纸张切圆感）
cx, cy = W//2, H//2 + 20
draw.ellipse([cx-180, cy-180, cx+180, cy+180], outline=C_GOLD, width=1)
draw.ellipse([cx-160, cy-160, cx+160, cy+160], outline=(195,182,158), width=1)

# 手绘感叶片装饰（左上角、右下角）
def leaf(draw, x, y, size, angle, color):
    pts = []
    for i in range(20):
        a = math.radians(i * 18)
        r = size * math.sin(a / 2 + 0.1) 
        lx = x + r * math.cos(math.radians(angle) + a * 0.5)
        ly = y + r * math.sin(math.radians(angle) + a * 0.5)
        pts.append((lx, ly))
    if len(pts) >= 3:
        draw.polygon(pts, fill=(*color, 80) if False else color)

# 简单椭圆代替手绘叶
for (lx,ly,la,lc) in [(60,60,-30,C_SAGE),(430,420,150,C_SAGE),(80,420,60,(148,128,100)),(420,70,-120,(148,128,100))]:
    draw.ellipse([lx-20,ly-8,lx+20,ly+8], fill=lc, outline=None)
    draw.ellipse([lx-8,ly-20,lx+8,ly+20], fill=lc, outline=None)

# 小圆圈装饰
for (px,py,r,col) in [(45,H-45,12,C_RUST),(W-45,45,8,C_GOLD),(W-60,H-60,6,C_SAGE)]:
    draw.ellipse([px-r,py-r,px+r,py+r], outline=col, width=2)

# 字体
try:
    f_main  = ImageFont.truetype(FONT_SERIF, 44)
    f_sub   = ImageFont.truetype(FONT_REG,  16)
    f_tiny  = ImageFont.truetype(FONT_REG,  13)
except:
    f_main = f_sub = f_tiny = ImageFont.load_default()

# 主标题（分两行，居中）
t1, t2 = "慢慢", "复利日记"
bb1 = draw.textbbox((0,0), t1, font=f_main)
bb2 = draw.textbbox((0,0), t2, font=f_main)
tw1, th1 = bb1[2]-bb1[0], bb1[3]-bb1[1]
tw2, th2 = bb2[2]-bb2[0], bb2[3]-bb2[1]

ty1 = cy - th1 - 10
ty2 = cy + 10

draw.text(((W-tw1)//2, ty1), t1, font=f_main, fill=C_BROWN)
draw.text(((W-tw2)//2, ty2), t2, font=f_main, fill=C_DARK)

# 两行之间装饰线
mid_y = (ty1+th1+ty2)//2
draw.line([(W//2-40,mid_y),(W//2-6,mid_y)], fill=C_GOLD, width=1)
draw.ellipse([W//2-4,mid_y-3,W//2+4,mid_y+3], fill=C_RUST)
draw.line([(W//2+6,mid_y),(W//2+40,mid_y)], fill=C_GOLD, width=1)

# 底部slogan
slogan = "不追涨  ·  只赚确定性的钱"
bb_s = draw.textbbox((0,0), slogan, font=f_tiny)
tw_s = bb_s[2]-bb_s[0]
draw.text(((W-tw_s)//2, H-38), slogan, font=f_tiny, fill=C_GOLD)

img.save(OUT, "PNG")
print(f"✅ style_a saved: {OUT}")
