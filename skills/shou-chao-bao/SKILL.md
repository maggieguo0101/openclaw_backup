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
- 竖版（常见）：A4 竖放，适合节日/语文类
- 横版（可选）：A4 横放，适合科学/活动类

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

<!-- 字体只用系统字体，禁止 Google Fonts 外链 -->
font-family: 'SimSun', 'FangSong', 'STSong', 'Noto Serif CJK SC', serif;
```

**禁止使用任何外部资源**（图片 CDN / Google Fonts / 在线 SVG），否则截图会卡死。

### Step 3：截图输出（固定写法，已验证可用）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/usr/bin/chromium-browser',
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
    )
    page = browser.new_page(viewport={'width': 794, 'height': 1123})
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

### 内容框 CSS 模板

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
