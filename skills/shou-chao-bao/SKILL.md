# shou-chao-bao Skill

**为小学生生成手抄报 PNG，A4 尺寸，可直接打印。**

触发词：手抄报、小报、节日手抄报、主题手抄报、做手抄报、生成手抄报

---

## 一、手抄报设计规范（调研结论）

小学生手抄报的标准结构：

| 区域 | 说明 |
|------|------|
| **报头（大标题区）** | 顶部，主题大字 + 副标题 + 装饰图案（花、灯、星星等） |
| **内容框（2-5个）** | 各框有彩色边框标题条，内容为文字（可留空供手写）|
| **插图/绘画区** | 1-2 处预留空白框，供孩子手绘（或填 SVG 简笔画）|
| **手写区** | 横线区，供孩子填写感想/祝福语 |
| **装饰元素** | 角花、花边、星星、气球、卡通形象等，围绕主题 |
| **底部** | 姓名/班级/日期填写区 |

**版式类型：**
- 竖版（常见）：A4 竖放（794×1123px），适合节日/语文类
- 横版（参考图风格）：A4 横放（1123×794px），适合节日类高颜值手抄报

**横版真实手抄报特征（老板参考图确认）：**
- 右上角或左上角大圆形艺术标题（红底金字描边）
- 内容框为**云朵形/不规则形**，不是方形卡片
- 内容以**段落正文**排列，不是条目列表
- 背景有**浅色底纹**（如金色菱格纹）
- **大量卡通插图**穿插（可用 SVG 简笔画代替）
- 版面活泼、色彩丰富

**风格要求：**
- 儿童审美：色彩鲜亮（红黄绿蓝）、卡通风、手绘感
- 字体：系统内置中文字体（SimSun/FangSong），无外部字体依赖
- 内容：已预填文字 OR 留空白线框供手写（根据用户需求）

---

## 二、执行步骤

### Step 1：确认参数

从用户输入提取：
- `topic`：手抄报主题（如"元宵节"）
- `style`：有内容（已填文字）/ 线框（仅框架供手写）—— 默认"有内容"
- `orientation`：竖版 / 横版 —— 默认"竖版"
- `grade`：年级（低年级=简洁，高年级=丰富）—— 默认"通用"

### Step 2：生成 HTML

直接编写 HTML 文件到 `/root/.openclaw/workspace/shou_chao_bao_<topic>.html`。

**HTML 关键约束：**
```html
<!-- A4 竖版尺寸 -->
<body style="width:794px; height:1123px; overflow:hidden;">

<!-- A4 横版尺寸 -->
<body style="width:1123px; height:794px; overflow:hidden;">

<!-- 字体只用系统字体，禁止 Google Fonts 外链 -->
font-family: 'SimSun', 'FangSong', 'STSong', 'Noto Serif CJK SC', serif;
```

**禁止使用任何外部资源**（图片 CDN / Google Fonts / 在线 SVG），否则截图会卡死。

### Step 3：截图输出（固定写法，已验证可用）

```python
from playwright.sync_api import sync_playwright

# 竖版
W, H = 794, 1123
# 横版
# W, H = 1123, 794

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/usr/bin/chromium-browser',
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
    )
    page = browser.new_page(viewport={'width': W, 'height': H})
    page.goto(f'file:///root/.openclaw/workspace/shou_chao_bao_{topic}.html',
              wait_until='domcontentloaded', timeout=10000)
    page.screenshot(path=f'/root/.openclaw/workspace/shou_chao_bao_{topic}.png', full_page=False)
    browser.close()
    print('done')
```

### Step 4：发送图片

通过 `message` 工具发送（**不要尝试 S3Plus 上传，当前沙箱权限有问题**）：
```
message(action="send", channel="daxiang", media="/root/.openclaw/workspace/shou_chao_bao_{topic}.png")
```

---

## 三、版面布局规范（竖版 794×1123px）

```
┌─────────────────────────────────┐
│  [角花]    大标题区    [角花]   │  top:16~155px
│  ═══════════════════════════════│  分割线 ~160px
│  ┌─────────────┐ ┌───────────┐  │
│  │  内容框1    │ │  内容框2  │  │  top:168~340px
│  └─────────────┘ └───────────┘  │
│  ┌─────────────┐ ┌───────────┐  │
│  │  内容框3    │ │  内容框4  │  │  top:350~530px
│  └─────────────┘ └───────────┘  │
│  ┌─────────────┐ ┌───────────┐  │
│  │  内容框5    │ │  手写/绘画│  │  top:540~710px
│  └─────────────┘ └───────────┘  │
│  ┌───────────────────────────┐   │
│  │   全宽内容区（诗词/金句）  │   │  top:720~870px
│  └───────────────────────────┘   │
│  ─────────────────────────────── │  top:880px
│  姓名：______  班级：__  日期：__│  bottom:890~950px
└─────────────────────────────────┘
```

### 内容框 CSS 模板（竖版方形卡片）

```css
.card {
  background: #fff;
  border: 2px solid [主题色];
  border-radius: 10px;
  position: absolute;
  overflow: hidden;
}
.card-title {
  background: [主题色];
  color: #fff;
  font-size: 14px;
  font-weight: bold;
  padding: 6px 14px;
  letter-spacing: 3px;
}
.card-body {
  font-size: 12px;
  line-height: 2;
  padding: 10px 14px;
}
.item { display: flex; gap: 6px; margin-bottom: 3px; }
.dot { color: [主题色]; font-size: 16px; line-height: 1.6; }
```

---

## 三-B、横版版面规范（1123×794px，真实手抄报风格）

```
┌──────────────────────────────────────────────────────┐
│  [底纹背景：菱格纹/浅色图案]                          │
│                                              ╭─────╮  │
│  ╭──云朵框1──╮   ╭──云朵框2──╮           │大标│  │
│  │ 标题+段落  │   │ 标题+段落  │           │题圆│  │
│  ╰───────────╯   ╰───────────╯           │  形│  │
│                                              ╰─────╯  │
│  ╭──云朵框3──╮   ╭──云朵框4──╮   [SVG插图区]      │
│  │ 标题+段落  │   │ 标题+段落  │                     │
│  ╰───────────╯   ╰───────────╯                     │
│  [装饰元素散落四角]          姓名：___班级：___日期：│
└──────────────────────────────────────────────────────┘
```

### 圆形大标题（右上角/左上角）

```html
<div style="
  position:absolute; top:20px; right:20px;
  width:160px; height:160px; border-radius:50%;
  background:#c0392b;
  border:4px solid #f39c12;
  box-shadow:0 0 0 6px rgba(192,57,43,0.3);
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  z-index:10;
">
  <div style="color:#f39c12;font-size:28px;font-weight:bold;letter-spacing:4px;text-shadow:1px 1px 0 #8B0000;">元宵节</div>
  <div style="color:#fff;font-size:13px;margin-top:4px;">手抄报</div>
</div>
```

### 云朵形内容框（SVG clipPath 实现）

每个云朵框需要唯一 id（cloud1/cloud2/cloud3...）：

```html
<svg width="0" height="0" style="position:absolute">
  <defs>
    <!-- 云朵路径：调整 cx/cy/r 改变形状 -->
    <clipPath id="cloud1">
      <path d="M30,80 Q10,60 20,40 Q10,10 40,15 Q50,-5 75,10 Q100,-5 120,15 Q150,5 155,35 Q175,30 175,55 Q185,75 165,85 Q160,100 140,95 Q130,110 110,105 Q90,120 70,108 Q50,120 35,108 Q15,105 10,90 Q5,80 30,80 Z"/>
    </clipPath>
  </defs>
</svg>

<div style="position:absolute; left:40px; top:60px; width:175px; height:120px;">
  <!-- 云朵背景色 -->
  <svg width="175" height="120" style="position:absolute;top:0;left:0;">
    <path d="M30,80 Q10,60 20,40 Q10,10 40,15 Q50,-5 75,10 Q100,-5 120,15 Q150,5 155,35 Q175,30 175,55 Q185,75 165,85 Q160,100 140,95 Q130,110 110,105 Q90,120 70,108 Q50,120 35,108 Q15,105 10,90 Q5,80 30,80 Z"
          fill="#fff9e6" stroke="#f39c12" stroke-width="2"/>
  </svg>
  <!-- 云朵内文字（用 clip-path 裁剪） -->
  <div style="position:absolute;top:18px;left:20px;width:135px;clip-path:url(#cloud1);">
    <div style="font-size:13px;font-weight:bold;color:#c0392b;margin-bottom:4px;">🏮 节日由来</div>
    <div style="font-size:11px;line-height:1.8;color:#333;">正月十五元宵节，又称上元节、灯节。汉文帝时期规定正月十五为元宵节。</div>
  </div>
</div>
```

**简化方案（不用 clipPath，直接 border-radius 大圆角）：**

```html
<div style="
  position:absolute; left:40px; top:60px;
  width:220px; min-height:130px;
  background:#fff9e6;
  border:2px solid #f39c12;
  border-radius:60% 40% 55% 45% / 45% 55% 40% 60%;  /* 不规则椭圆 */
  padding:18px 22px;
  box-shadow:2px 3px 0 rgba(192,57,43,0.15);
">
  <div style="font-size:13px;font-weight:bold;color:#c0392b;margin-bottom:6px;">🏮 节日由来</div>
  <div style="font-size:11px;line-height:1.9;color:#444;">正月十五元宵节，又称上元节。汉文帝时期规定正月十五为元宵节，是春节后的第一个重要节日。</div>
</div>
```

### 底纹背景（菱格纹 SVG pattern）

```html
<svg width="0" height="0" style="position:absolute">
  <defs>
    <pattern id="diamond" width="30" height="30" patternUnits="userSpaceOnUse">
      <rect width="30" height="30" fill="#fffdf0"/>
      <path d="M15,0 L30,15 L15,30 L0,15 Z" fill="none" stroke="rgba(212,170,80,0.25)" stroke-width="1"/>
    </pattern>
  </defs>
</svg>
<div style="position:absolute;top:0;left:0;width:1123px;height:794px;
     background:url(\"data:image/svg+xml,...\")">
<!-- 或直接用 SVG rect 铺底 -->
<svg style="position:absolute;top:0;left:0;z-index:0" width="1123" height="794">
  <rect width="1123" height="794" fill="url(#diamond)"/>
</svg>
```

### 装饰元素（纯 SVG/CSS/Emoji，禁止外部图片）

- **角花**：Emoji（根据主题选，见下表）
- **边框**：CSS border + box-shadow
- **分隔线**：`background: linear-gradient(to right, transparent, [色], transparent)`
- **简笔画**：内联 SVG 元素
- **手写横线**：`border-bottom: 1px solid #xxx` 的 div

---

## 四、主题配色方案

| 主题 | 主色 | 辅色 | 背景色 | 角花 |
|------|------|------|--------|------|
| 元宵节 | #c0392b | #e67e22 | #fffdf5 | 🏮🌙 |
| 春节 | #c0392b | #f39c12 | #fff9f0 | 🧧🎆 |
| 清明节 | #27ae60 | #2980b9 | #f0fff4 | 🌿🌸 |
| 端午节 | #16a085 | #8e44ad | #f0fffe | 🐉🎐 |
| 中秋节 | #e67e22 | #8e44ad | #fff8f0 | 🥮🌕 |
| 国庆节 | #c0392b | #f39c12 | #fff5f5 | 🎉🎋 |
| 环保/地球 | #27ae60 | #3498db | #f0fff8 | 🌍🌱 |
| 读书/语文 | #2980b9 | #e74c3c | #f0f8ff | 📚✏️ |
| 科学/探索 | #2c3e50 | #f39c12 | #f0f8ff | 🔭⭐ |
| 通用/默认 | #3498db | #e74c3c | #f5f9ff | ⭐🌟 |

---

## 五、内容填充规范

### 有内容版（已填文字）
- 每条内容以 `▸` 开头，每条 ≤30 汉字
- 每框 3-5 条，字号 12-13px，行高 2

### 线框版（供手写）
- 标题条保留，内容区全部为空白横线
- 横线：低年级 3 条，高年级 5 条
- 灰色提示文字：`color:#bbb; font-size:11px`

---

## 六、⚠️ 必须遵守的技术约束

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 截图卡死/超时 | HTML 含外部资源，网络不通 | 删所有 `@import url(...)` 和 `<img src="http...">`，用 `domcontentloaded` |
| 字体乱码/方块 | 字体未安装 | 用 `'SimSun','FangSong','Noto Serif CJK SC',serif` |
| S3Plus 403 | 沙箱 bucket 权限 | **直接用 message(media=本地路径) 发图，跳过上传** |
| 内容溢出页面 | position:absolute 超出 1123px | 所有卡片 top+height ≤ 1090px |
