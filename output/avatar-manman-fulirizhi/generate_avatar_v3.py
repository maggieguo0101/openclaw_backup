#!/usr/bin/env python3
"""
小红书头像 v3：慢慢复利日记
布局调整：文字小且紧凑在顶部，曲线大且占主体
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "avatar_v3.png")

W, H = 500, 500

C_BG1      = (12, 14, 22)
C_BG2      = (20, 25, 40)
C_GOLD     = (210, 168, 90)
C_GOLD_HI  = (245, 215, 145)
C_GOLD_DIM = (130, 100, 48)
C_CREAM    = (242, 234, 215)
C_GRID     = (32, 38, 58)

FONT_BOLD  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

# ── 1. 背景渐变 ───────────────────────────
arr = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    t = y / H
    for c in range(3):
        arr[y, :, c] = int(C_BG1[c] + (C_BG2[c] - C_BG1[c]) * t)
img = Image.fromarray(arr, "RGB")
draw = ImageDraw.Draw(img)

# ── 2. 网格 ───────────────────────────────
for x in range(0, W, 50):
    draw.line([(x, 0), (x, H)], fill=C_GRID, width=1)
for y in range(0, H, 50):
    draw.line([(0, y), (W, y)], fill=C_GRID, width=1)

# ── 3. 字体加载 ───────────────────────────
try:
    f_title = ImageFont.truetype(FONT_BOLD, 36)    # 账号名（缩小）
    f_sub   = ImageFont.truetype(FONT_SERIF, 15)   # slogan
    f_tag   = ImageFont.truetype(FONT_REG, 13)     # 小标签
except:
    f_title = f_sub = f_tag = ImageFont.load_default()

# ── 4. 顶部文字区（紧凑，仅占上方约90px）─
# 账号名：慢慢复利日记 —— 一行，居中
title_text = "慢慢复利日记"
bb = draw.textbbox((0, 0), title_text, font=f_title)
tw = bb[2] - bb[0]
th = bb[3] - bb[1]
tx = (W - tw) // 2
ty = 22

# 文字底部微发光
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.rectangle([tx - 10, ty - 4, tx + tw + 10, ty + th + 4], fill=(*C_GOLD_DIM, 20))
img = img.convert("RGBA"); img.alpha_composite(glow); img = img.convert("RGB")
draw = ImageDraw.Draw(img)

# 字描边
for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text((tx+dx, ty+dy), title_text, font=f_title, fill=C_GOLD_DIM)
# 主字：前半「慢慢」金色，后半「复利日记」米白
# 分段渲染
t_a, t_b = "慢慢", "复利日记"
bba = draw.textbbox((0,0), t_a, font=f_title)
twa = bba[2] - bba[0]
draw.text((tx, ty), t_a, font=f_title, fill=C_GOLD_HI)
draw.text((tx + twa, ty), t_b, font=f_title, fill=C_CREAM)

# 标题下方细分隔线
line_y = ty + th + 10
lc = W // 2
draw.line([(lc - 50, line_y), (lc - 6, line_y)], fill=C_GOLD_DIM, width=1)
draw.ellipse([lc-3, line_y-3, lc+3, line_y+3], fill=C_GOLD)
draw.line([(lc + 6, line_y), (lc + 50, line_y)], fill=C_GOLD_DIM, width=1)

# ── 5. 复利曲线（主体，占70%画面）─────────
# 曲线区域：y从 line_y+14 到 H-55
CURVE_TOP  = line_y + 14   # ≈95
CURVE_BOT  = H - 55        # ≈445
CURVE_L    = 38
CURVE_R    = W - 28

N = 300
curve_pts = []
for i in range(N + 1):
    t = i / N
    x = CURVE_L + t * (CURVE_R - CURVE_L)
    k = 2.8
    val = (math.exp(k * t) - 1) / (math.exp(k) - 1)
    y = CURVE_BOT - val * (CURVE_BOT - CURVE_TOP)
    curve_pts.append((x, y))

# 填充区
fill_pts = [(CURVE_L, CURVE_BOT)] + curve_pts + [(CURVE_R, CURVE_BOT)]
fill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fl = ImageDraw.Draw(fill_layer)
fl.polygon(fill_pts, fill=(*C_GOLD, 25))
img = img.convert("RGBA"); img.alpha_composite(fill_layer); img = img.convert("RGB")
draw = ImageDraw.Draw(img)

# 曲线三层
draw.line(curve_pts, fill=C_GOLD_DIM, width=8)
draw.line(curve_pts, fill=C_GOLD, width=5)
draw.line(curve_pts, fill=C_GOLD_HI, width=2)

# ── 6. 末端发光点 ─────────────────────────
ex, ey = curve_pts[-1]
for r, a, col in [(22, 12, C_GOLD), (14, 35, C_GOLD), (8, 90, C_GOLD_HI), (4, 220, (255, 248, 220))]:
    g2 = Image.new("RGBA", (W, H), (0,0,0,0))
    gd2 = ImageDraw.Draw(g2)
    gd2.ellipse([ex-r, ey-r, ex+r, ey+r], fill=(*col, a))
    img = img.convert("RGBA"); img.alpha_composite(g2); img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

# ── 7. 曲线节点 ───────────────────────────
for t_m in [0.3, 0.6, 0.85]:
    idx = int(t_m * N)
    px, py = curve_pts[idx]
    draw.ellipse([px-4, py-4, px+4, py+4], fill=C_BG2, outline=C_GOLD_HI, width=2)

# ── 8. 横轴 ───────────────────────────────
ax_y = CURVE_BOT
draw.line([(CURVE_L - 6, ax_y), (CURVE_R + 8, ax_y)], fill=C_GOLD_DIM, width=1)
draw.polygon([(CURVE_R+8, ax_y-3),(CURVE_R+15, ax_y),(CURVE_R+8, ax_y+3)], fill=C_GOLD_DIM)
# 纵轴
draw.line([(CURVE_L, ax_y+6), (CURVE_L, CURVE_TOP - 6)], fill=C_GOLD_DIM, width=1)
draw.polygon([(CURVE_L-3, CURVE_TOP-6),(CURVE_L, CURVE_TOP-13),(CURVE_L+3, CURVE_TOP-6)], fill=C_GOLD_DIM)

# ── 9. 底部 slogan ─────────────────────────
slogan = "不追涨  ·  只赚确定性的钱"
bb_s = draw.textbbox((0, 0), slogan, font=f_sub)
tw_s = bb_s[2] - bb_s[0]
draw.text(((W - tw_s) // 2, H - 32), slogan, font=f_sub, fill=(150, 128, 85))

# ── 10. 四角角标 ──────────────────────────
M, L = 12, 16
for pts in [
    [(M, M+L), (M, M), (M+L, M)],
    [(W-M-L, M), (W-M, M), (W-M, M+L)],
    [(M, H-M-L), (M, H-M), (M+L, H-M)],
    [(W-M-L, H-M), (W-M, H-M), (W-M, H-M-L)],
]:
    draw.line(pts, fill=C_GOLD, width=2)

img.save(OUTPUT_PATH, "PNG")
print(f"✅ v3 saved: {OUTPUT_PATH}")
