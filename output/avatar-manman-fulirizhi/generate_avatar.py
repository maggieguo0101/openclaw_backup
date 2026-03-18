#!/usr/bin/env python3
"""
小红书头像生成：慢慢复利日记
风格：静谧金融美学 - 深邃底色 + 金色复利曲线 + 极简汉字
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "avatar.png")

# 小红书头像尺寸：圆形展示，用 400x400 方形出图
W, H = 400, 400

# ─────────────────────────────
# 色彩系统：深夜书房美学
# ─────────────────────────────
BG_DEEP    = (18, 20, 30)       # 几乎黑的深蓝
BG_MID     = (24, 28, 44)       # 中层
GOLD_WARM  = (212, 175, 100)    # 暖金
GOLD_LIGHT = (240, 210, 140)    # 高光金
CREAM      = (245, 238, 220)    # 米白文字
TEAL_SOFT  = (80, 160, 160)     # 点缀青色
LINE_DIM   = (50, 58, 80)       # 暗纹线条

img = Image.new("RGB", (W, H), BG_DEEP)
draw = ImageDraw.Draw(img)

# ─────────────────────────────
# 1. 背景渐变（手动逐行渐变）
# ─────────────────────────────
for y in range(H):
    t = y / H
    r = int(BG_DEEP[0] + (BG_MID[0] - BG_DEEP[0]) * t)
    g = int(BG_DEEP[1] + (BG_MID[1] - BG_DEEP[1]) * t)
    b = int(BG_DEEP[2] + (BG_MID[2] - BG_DEEP[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# ─────────────────────────────
# 2. 极细网格（坐标感 / 金融图纸）
# ─────────────────────────────
GRID_SPACING = 40
for x in range(0, W, GRID_SPACING):
    alpha = 25
    draw.line([(x, 0), (x, H)], fill=(*LINE_DIM, alpha)[:3])
for y in range(0, H, GRID_SPACING):
    draw.line([(0, y), (W, y)], fill=LINE_DIM)

# ─────────────────────────────
# 3. 复利增长曲线（核心图形）
# 指数曲线：从左下角向右上方爬升
# ─────────────────────────────
curve_points = []
n_pts = 200
for i in range(n_pts + 1):
    t = i / n_pts  # 0 → 1
    x = 40 + t * (W - 60)
    # 复利曲线：y = start * e^(k*t)，映射到画布
    val = math.exp(2.2 * t)          # 1 → ~9
    val_norm = (val - 1) / (math.e ** 2.2 - 1)   # 0 → 1
    y = H - 60 - val_norm * (H - 120)
    curve_points.append((x, y))

# 填充曲线下方区域（渐变感用半透明叠加）
fill_pts = [(40, H - 40)] + curve_points + [(W - 20, H - 40)]
# 用深金色半透明填充
fill_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fill_draw = ImageDraw.Draw(fill_img)
fill_draw.polygon(fill_pts, fill=(*GOLD_WARM, 28))
img.paste(Image.new("RGB", img.size, GOLD_WARM),
          mask=Image.fromarray(
              __import__('numpy').array(fill_img)[:, :, 3].astype('uint8')
          ) if False else None)
# 直接 alpha compose
img_rgba = img.convert("RGBA")
img_rgba.alpha_composite(fill_img)
img = img_rgba.convert("RGB")
draw = ImageDraw.Draw(img)

# 曲线主线（双层：暗金描边 + 亮金主线）
if len(curve_points) > 1:
    draw.line(curve_points, fill=(160, 130, 70), width=5)   # 暗底
    draw.line(curve_points, fill=GOLD_LIGHT, width=2)        # 亮线

# 曲线末端发光点
end_x, end_y = curve_points[-1]
for r, alpha_val, color in [
    (14, 40, GOLD_WARM),
    (8,  80, GOLD_LIGHT),
    (4, 200, (255, 245, 200)),
]:
    glow_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_img)
    gd.ellipse([end_x-r, end_y-r, end_x+r, end_y+r],
               fill=(*color, alpha_val))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(glow_img)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

# ─────────────────────────────
# 4. 辅助元素：微小复利节点（曲线上等间距小圆点）
# ─────────────────────────────
dot_indices = [int(n_pts * t) for t in [0.2, 0.4, 0.6, 0.8]]
for idx in dot_indices:
    px, py = curve_points[idx]
    draw.ellipse([px-3, py-3, px+3, py+3], fill=GOLD_WARM, outline=GOLD_LIGHT, width=1)

# ─────────────────────────────
# 5. 装饰：左上角百分比符号（极淡，作为底纹）
# ─────────────────────────────
try:
    font_large_bg = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 160)
    bg_txt_img = Image.new("RGBA", (W, H), (0,0,0,0))
    bg_txt_draw = ImageDraw.Draw(bg_txt_img)
    bg_txt_draw.text((-10, -10), "%", font=font_large_bg, fill=(*GOLD_WARM, 18))
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(bg_txt_img)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)
except:
    pass

# ─────────────────────────────
# 6. 主文字：慢慢复利日记（分两行）
# ─────────────────────────────
FONT_CN_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_CN_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF   = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

try:
    font_main = ImageFont.truetype(FONT_CN_BOLD, 52)
    font_sub  = ImageFont.truetype(FONT_SERIF, 22)
    font_tiny = ImageFont.truetype(FONT_CN_REG, 15)
except Exception as e:
    print(f"Font error: {e}")
    font_main = ImageFont.load_default()
    font_sub  = font_main
    font_tiny = font_main

# 「慢慢」- 行1，居中，金色
text1 = "慢慢"
bbox1 = draw.textbbox((0, 0), text1, font=font_main)
tw1 = bbox1[2] - bbox1[0]
draw.text(((W - tw1) // 2, 48), text1, font=font_main, fill=GOLD_LIGHT)

# 「复利日记」- 行2，居中，米白
text2 = "复利日记"
bbox2 = draw.textbbox((0, 0), text2, font=font_main)
tw2 = bbox2[2] - bbox2[0]
draw.text(((W - tw2) // 2, 106), text2, font=font_main, fill=CREAM)

# 分隔线（金色细线）
line_y = 170
draw.line([(W//2 - 60, line_y), (W//2 + 60, line_y)], fill=(*GOLD_WARM,), width=1)

# ─────────────────────────────
# 7. 副标题（极小字，底部）
# ─────────────────────────────
sub_text = "不追涨 · 只赚确定性的钱"
bbox_sub = draw.textbbox((0, 0), sub_text, font=font_tiny)
tw_sub = bbox_sub[2] - bbox_sub[0]
# 淡金色
draw.text(((W - tw_sub) // 2, H - 42), sub_text, font=font_tiny,
          fill=(180, 150, 90))

# ─────────────────────────────
# 8. 边框：细金线圆角感（用圆弧四角）
# ─────────────────────────────
border_img = Image.new("RGBA", (W, H), (0,0,0,0))
bd = ImageDraw.Draw(border_img)
# 四角小金色角标
corner_len = 20
corners = [
    [(8, 8+corner_len), (8, 8), (8+corner_len, 8)],
    [(W-8-corner_len, 8), (W-8, 8), (W-8, 8+corner_len)],
    [(8, H-8-corner_len), (8, H-8), (8+corner_len, H-8)],
    [(W-8-corner_len, H-8), (W-8, H-8), (W-8, H-8-corner_len)],
]
for pts in corners:
    bd.line(pts, fill=(*GOLD_WARM, 180), width=2)

img_rgba = img.convert("RGBA")
img_rgba.alpha_composite(border_img)
img = img_rgba.convert("RGB")

# ─────────────────────────────
# 9. 输出
# ─────────────────────────────
img.save(OUTPUT_PATH, "PNG", quality=95)
print(f"✅ Avatar saved: {OUTPUT_PATH}")
print(f"   Size: {W}x{H}px")
