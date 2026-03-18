#!/usr/bin/env python3
"""
风格D：清新薄荷绿 × 小清新理财
- 白色/浅绿底 + 墨绿文字 + 小植物/叶子 + 轻盈圆润
- 亲切、年轻感，适合小红书主流审美
"""
from PIL import Image, ImageDraw, ImageFont
import os, math, numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_d.png")
W, H = 500, 500

C_BG     = (242, 248, 244)   # 极浅薄荷白
C_BG2    = (228, 240, 232)   # 浅绿
C_GREEN  = (62, 130, 90)     # 墨绿
C_GREEN2 = (100, 168, 120)   # 中绿
C_MINT   = (160, 215, 185)   # 薄荷
C_GOLD   = (195, 158, 72)    # 暖金（点缀）
C_DARK   = (38, 60, 48)      # 深绿文字
C_WHITE  = (255, 255, 255)

FONT_BOLD  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y/H
    for c in range(3):
        arr[y,:,c] = int(C_BG[c]+(C_BG2[c]-C_BG[c])*t)
img = Image.fromarray(arr,"RGB")
draw = ImageDraw.Draw(img)

# ── 大圆形主构图（白色圆卡）─────────────
cx, cy = W//2, H//2
R = 178
circle_layer = Image.new("RGBA",(W,H),(0,0,0,0))
cd = ImageDraw.Draw(circle_layer)
cd.ellipse([cx-R,cy-R,cx+R,cy+R], fill=(255,255,255,220))
img = img.convert("RGBA"); img.alpha_composite(circle_layer); img=img.convert("RGB")
draw = ImageDraw.Draw(img)

# 圆边线
draw.ellipse([cx-R,cy-R,cx+R,cy+R], outline=C_GREEN2, width=2)
draw.ellipse([cx-R-5,cy-R-5,cx+R+5,cy+R+5], outline=C_MINT, width=1)

# ── 叶片装饰（SVG风格简化）──────────────
def draw_leaf(draw, x, y, size, angle_deg, fill_col, outline_col):
    a = math.radians(angle_deg)
    pts = []
    for i in range(21):
        theta = i/20 * math.pi
        r = size * math.sin(theta)
        px2 = x + r * math.cos(a - math.pi/2 + theta * 0.5)
        py2 = y + r * math.sin(a - math.pi/2 + theta * 0.5)
        pts.append((px2, py2))
    if len(pts) >= 3:
        draw.polygon(pts, fill=fill_col, outline=outline_col)

# 左上角叶片组
draw_leaf(draw, cx-120, cy-130, 28, -30, C_MINT, C_GREEN2)
draw_leaf(draw, cx-100, cy-148, 20, 20, C_GREEN2, C_GREEN)
# 右下角叶片组
draw_leaf(draw, cx+115, cy+120, 28, 150, C_MINT, C_GREEN2)
draw_leaf(draw, cx+130, cy+102, 20, -200, C_GREEN2, C_GREEN)
# 右上
draw_leaf(draw, cx+105, cy-120, 22, 60, C_GREEN2, C_GREEN)
# 左下
draw_leaf(draw, cx-108, cy+118, 22, -120, C_MINT, C_GREEN2)

# ── 小圆点散落 ────────────────────────────
import random; random.seed(7)
for _ in range(12):
    px2 = random.randint(50, W-50)
    py2 = random.randint(50, H-50)
    r2 = random.randint(2, 5)
    col = random.choice([C_MINT, C_GREEN2, C_GOLD])
    draw.ellipse([px2-r2,py2-r2,px2+r2,py2+r2], fill=col)

# ── 主文字 ────────────────────────────────
try:
    f_main  = ImageFont.truetype(FONT_BOLD, 50)
    f_serif = ImageFont.truetype(FONT_SERIF, 22)
    f_tiny  = ImageFont.truetype(FONT_REG, 14)
except:
    f_main = f_serif = f_tiny = ImageFont.load_default()

t1 = "慢慢"
bb1 = draw.textbbox((0,0), t1, font=f_main)
tw1,th1 = bb1[2]-bb1[0], bb1[3]-bb1[1]
ty1 = cy - th1 - 12
draw.text(((W-tw1)//2, ty1), t1, font=f_main, fill=C_GREEN)

t2 = "复利日记"
bb2 = draw.textbbox((0,0), t2, font=f_main)
tw2,th2 = bb2[2]-bb2[0], bb2[3]-bb2[1]
ty2 = cy + 12
draw.text(((W-tw2)//2, ty2), t2, font=f_main, fill=C_DARK)

# 分隔：小叶子 + 虚线
mid_y = ty1+th1+8
for i in range(-3, 4):
    if i != 0:
        dot_x = W//2 + i*12
        draw.ellipse([dot_x-1,mid_y-1,dot_x+1,mid_y+1], fill=C_GREEN2)
# 中心小叶
draw.ellipse([W//2-5,mid_y-5,W//2+5,mid_y+5], fill=C_GREEN2)

# 底部slogan
slogan = "不追涨 · 只赚确定性的钱"
bb_s = draw.textbbox((0,0), slogan, font=f_tiny)
tw_s = bb_s[2]-bb_s[0]
draw.text(((W-tw_s)//2, H-36), slogan, font=f_tiny, fill=C_GREEN2)

# 顶部小标签
tag = "📗 低风险理财"
try:
    bb_t = draw.textbbox((0,0), tag, font=f_tiny)
    tw_t = bb_t[2]-bb_t[0]
    # 小圆角矩形背景
    tx_tag = (W-tw_t)//2 - 8
    ty_tag = 22
    draw.rounded_rectangle([tx_tag, ty_tag, tx_tag+tw_t+16, ty_tag+22], radius=11, fill=C_MINT)
    draw.text((tx_tag+8, ty_tag+4), tag, font=f_tiny, fill=C_GREEN)
except:
    pass

img.save(OUT, "PNG")
print(f"✅ style_d saved: {OUT}")
