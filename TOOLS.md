# TOOLS.md - Local Notes

## Skill 安装安全规范（老板制定）

**安装任何 Skill 前，必须执行安全防护三件套：**

### 1. Skill Vetter（安检门）
- 安装前自动扫描代码
- 检查可疑网络请求、文件读写、环境变量访问
- **必须先装这个，再装其他 Skill**

### 2. Security Scanner（评级）
- 给每个 Skill 打三档评级：SAFE / CAUTION / DANGEROUS
- 🔴 DANGEROUS → 直接卸载
- 🟡 CAUTION → 仔细检查权限申请再决定
- 🟢 SAFE → 可以用

### 3. 100/3 法则（准入门槛）
- **下载量 ≥ 100 次**
- **发布历史 ≥ 3 个月**
- 不满足的不装，没有例外

---

## 北交所打新 — 各券商最早申购时间（老板整理，2026-03）

| 券商 | 最早开放时间 |
|------|------------|
| 银河证券 | **8:30** ⭐最早 |
| 中银证券 | **8:30** ⭐最早 |
| 国金证券 | 8:35 |
| 中金证券 | 8:40 |
| 招商证券 | 8:45（以前是7:00） |
| 华泰证券 | 8:45 |
| 东方证券 | 8:45 |
| 平安证券 | 8:45 |
| 国信证券 | 8:50 |

> 注：官方申购时间为9:15，部分券商9:15前接受委托后统一报送，部分直通实时递单。越早提交对碎股时间优先越有利。

---

## 环境信息

### SSO
- 学城 KM: 通过 CIBA 认证（inject-km-cookie.sh）
- 大象网页版: 未打通（需要后端支持 exchange-token 扩展域名）
- misId: guoleiping

### 搜索
- 主用：`python3 /app/skills/catclaw-search/scripts/catclaw_search.py`
- 引擎：baidu-search-v2 / bing / google-search
- web_search (Brave API) 不可用

### 图片生成
- catclaw-image: `python3 /app/skills/catclaw-image/scripts/catclaw_image.py`
- 长图：HTML → Playwright 截图 → S3Plus 上传 → **直接发链接给老板（不用 Markdown 图片语法）**

### ⚠️ 大象图片规则（老板反馈）
- **大象内嵌图片 `![]()` 格式打不开**
- **后续所有图片：直接发 S3Plus 链接文本，不要用 Markdown 图片语法**
- 格式：直接贴 `https://s3plus-bj02.vip.sankuai.com/...` 链接即可

### 快捷指令

| 指令 | 脚本 | 说明 |
|---|---|---|
| `/token` / `token看板` | `python3 /root/.openclaw/workspace/token_dashboard.py` | 生成 token 消耗看板，截图上传 S3Plus 发链接 |

### 文件上传
- S3Plus: `python3 /app/skills/s3plus-upload/scripts/upload_to_s3plus.py --env prod-corp`
- 桶：supabase-bucket

### 股票行情
- 腾讯API: `https://qt.gtimg.cn/q=hk02692,bj920036`
- 监控脚本: `/root/.openclaw/workspace/stock_monitor.py`
