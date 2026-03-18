#!/usr/bin/env python3
"""
小红书头像 v2：慢慢复利日记
风格：深夜书房 × 金融极简主义
- 深蓝黑底 + 暖金复利曲线填充区 + 精致汉字排版
- 中心圆形构图（适配小红书圆形裁剪）
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "avatar_v2.png")

W, H = 500, 500

# ── 颜色系统 ──────────────────────────────
C_BG1       = (12, 14, 22)       # 极深蓝黑
C_BG2       = (20, 24, 38)       # 稍浅
C_GOLD      = (210, 168, 90)     # 暖金主色
C_GOLD_HI   = (245, 215, 145)    # 高光金
C_GOLD_DIM  = (140, 108, 55)     # 暗金
C_CREAM     = (242, 234, 215)    # 米白
C_CREAM_DIM = (180, 172, 155)    # 灰米
C_TEAL      = (70, 155, 150)     # 画龙点睛青
C_GRID      = (35, 42, 62)       # 网格色

FONT_BOLD   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG    = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF  = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

# ── 1. 背景渐变 ───────────────────────────
arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y / H
    for c in range(3):
        arr[y, :, c] = int(C_BG1[c] + (C_BG2[c] - C_BG1[c]) * t)
img = Image.fromarray(arr, "RGB")
draw = ImageDraw.Draw(img)

# ── 2. 极细网格 ───────────────────────────
for x in range(0, W, 50):
    draw.line([(x, 0), (x, H)], fill=C_GRID, width=1)
for y in range(0, H, 50):
    draw.line([(0, y), (W, y)], fill=C_GRID, width=1)

# ── 3. 中心发光晕圈（背景装饰）─────────────
glow_layer = Image.new("RGBA", (W, H), (0,0,0,0))
gd = ImageDraw.Draw(glow_layer)
cx, cy = W//2, H//2 + 30
for r, a in [(160, 8), (120, 16), (80, 25), (50, 35)]:
    gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*C_GOLD_DIM, a))
img = img.convert("RGBA")
img.alpha_composite(glow_layer)
img = img.convert("RGB")
draw = ImageDraw.Draw(img)

# ── 4. 复利曲线（核心主视觉）─────────────
# 从画布左下到右上的指数曲线
PAD_L, PAD_R = 50, 30
PAD_B, PAD_T = 70, 180   # 给上方文字留空间
curve_pts = []
N = 300
for i in range(N + 1):
    t = i / N
    x = PAD_L + t * (W - PAD_L - PAD_R)
    k = 2.6
    val = (math.exp(k * t) - 1) / (math.exp(k) - 1)
    y = (H - PAD_B) - val * (H - PAD_B - PAD_T)
    curve_pts.append((x, y))

# 填充区域（曲线下方渐变金色）
fill_pts = [(PAD_L, H - PAD_B)] + curve_pts + [(W - PAD_R, H - PAD_B)]
fill_layer = Image.new("RGBA", (W, H), (0,0,0,0))
fl_draw = ImageDraw.Draw(fill_layer)
fl_draw.polygon(fill_pts, fill=(*C_GOLD, 22))
img = img.convert("RGBA")
img.alpha_composite(fill_layer)
img = img.convert("RGB")
draw = ImageDraw.Draw(img)

# 曲线本身（3层：底光 + 主线 + 高光线）
draw.line(curve_pts, fill=C_GOLD_DIM, width=7)
draw.line(curve_pts, fill=C_GOLD, width=4)
draw.line(curve_pts, fill=C_GOLD_HI, width=2)

# ── 5. 曲线末端：发光圆点 ──────────────────
ex, ey = curve_pts[-1]
for r, a, col in [(20, 15, C_GOLD), (12, 40, C_GOLD), (7, 100, C_GOLD_HI), (3, 255, (255,250,230))]:
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd2 = ImageDraw.Draw(glow)
    gd2.ellipse([ex-r, ey-r, ex+r, ey+r], fill=(*col, a))
    img = img.convert("RGBA"); img.alpha_composite(glow); img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

# ── 6. 曲线上节点（时间轴感）──────────────
for t_mark in [0.25, 0.5, 0.75]:
    idx = int(t_mark * N)
    px, py = curve_pts[idx]
    draw.ellipse([px-4, py-4, px+4, py+4], fill=C_BG2, outline=C_GOLD, width=2)
    # 小竖线引导
    draw.line([(px, py+5), (px, py+12)], fill=C_GOLD_DIM, width=1)

# ── 7. 底部横轴 ───────────────────────────
axis_y = H - PAD_B
draw.line([(PAD_L - 5, axis_y), (W - PAD_R + 5, axis_y)], fill=C_GOLD_DIM, width=1)
# 小箭头
draw.polygon([(W-PAD_R+5, axis_y-3), (W-PAD_R+12, axis_y), (W-PAD_R+5, axis_y+3)],
             fill=C_GOLD_DIM)

# ── 8. 主标题文字 ──────────────────────────
try:
    f_main = ImageFont.truetype(FONT_BOLD, 64)
    f_sub  = ImageFont.truetype(FONT_SERIF, 24)
    f_tiny = ImageFont.truetype(FONT_REG, 14)
except:
    f_main = f_sub = f_tiny = ImageFont.load_default()

# 「慢慢」- 上行，暖金
t1 = "慢慢"
bb1 = draw.textbbox((0,0), t1, font=f_main)
tw1 = bb1[2]-bb1[0]
tx1 = (W - tw1) // 2
ty1 = 28
# 描边感（深色底字）
for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text((tx1+dx, ty1+dy), t1, font=f_main, fill=C_GOLD_DIM)
draw.text((tx1, ty1), t1, font=f_main, fill=C_GOLD_HI)

# 「复利日记」- 下行，米白
t2 = "复利日记"
bb2 = draw.textbbox((0,0), t2, font=f_main)
tw2 = bb2[2]-bb2[0]
tx2 = (W - tw2) // 2
ty2 = ty1 + (bb1[3]-bb1[1]) + 6
for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text((tx2+dx, ty2+dy), t2, font=f_main, fill=(30,35,50))
draw.text((tx2, ty2), t2, font=f_main, fill=C_CREAM)

# ── 9. 装饰线（标题下方）──────────────────
line_y = ty2 + (bb2[3]-bb2[1]) + 12
lx1, lx2 = W//2 - 70, W//2 + 70
# 三段式：细-粗-细
draw.line([(lx1, line_y), (lx1+20, line_y)], fill=C_GOLD_DIM, width=1)
draw.line([(lx1+20, line_y), (lx2-20, line_y)], fill=C_GOLD, width=2)
draw.line([(lx2-20, line_y), (lx2, line_y)], fill=C_GOLD_DIM, width=1)
# 中心菱形
mid = W // 2
draw.polygon([(mid-4, line_y-4),(mid, line_y-8),(mid+4, line_y-4),(mid, line_y)],
             fill=C_GOLD_HI)

# ── 10. 底部 slogan ────────────────────────
slogan = "不追涨  ·  只赚确定性的钱"
bb_s = draw.textbbox((0,0), slogan, font=f_tiny)
tw_s = bb_s[2]-bb_s[0]
draw.text(((W-tw_s)//2, H-34), slogan, font=f_tiny, fill=(160, 140, 100))

# ── 11. 四角金色角标 ──────────────────────
M, L = 14, 18
corners_lines = [
    [(M, M+L), (M, M), (M+L, M)],
    [(W-M-L, M), (W-M, M), (W-M, M+L)],
    [(M, H-M-L), (M, H-M), (M+L, H-M)],
    [(W-M-L, H-M), (W-M, H-M), (W-M, H-M-L)],
]
for pts in corners_lines:
    draw.line(pts, fill=(*C_GOLD, ), width=2)

# ── 12. 右下角小标记 ─────────────────────
draw.text((W-48, H-28), "📗", font=f_tiny if False else ImageFont.load_default())
# 用文字代替 emoji
try:
    draw.text((W-52, H-26), "日", font=ImageFont.truetype(FONT_REG, 11), fill=(80, 140, 100))
except: pass

# ── 保存 ─────────────────────────────────
img.save(OUTPUT_PATH, "PNG")
print(f"✅ v2 saved: {OUTPUT_PATH}")
