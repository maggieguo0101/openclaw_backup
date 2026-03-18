---
name: fund-allocation
description: 资金分配工具：将总资金按目标金额分配到多个账户，自动生成分配表格图片。适用于新股申购、合资打款、AA分账等场景。当用户提到"资金分配"、"分配到账户"、"打新分配"、"拆分资金"、"XX元分到几个账户"时使用。
---

# 资金分配 Skill

## 核心算法（三阶段）

1. **第一阶段：本人+相关人优先放对应账户**（相关人放一起，不拆分）
2. **第二阶段：公共资金完整匹配**（尽量不拆分，先完美匹配，再最优容纳）
3. **第三阶段：不得已拆分**（大额填大坑，贪心策略）

## 使用流程

### 1. 准备输入 JSON

创建 `input.json`：

```json
{
  "title": "资金分配方案",
  "subtitle": "3.11新恒泰 · 发行价9.4元 · 总计2400元",
  "accounts": {
    "maggie": 800,
    "长月": 800,
    "ziqi": 800
  },
  "funds": {
    "maggie": 490,
    "Maggie朋友": 40,
    "坤": 455,
    "长月": 321,
    "长月朋友": 25,
    "tu": 235,
    "ziqi": 240,
    "ziqi同事": 125,
    "小拉": 55,
    "coco": 140,
    "柏总": 104,
    "小月": 125,
    "徐雪": 45
  },
  "ownership": {
    "maggie": "maggie",
    "Maggie朋友": "maggie",
    "坤": "maggie",
    "长月": "长月",
    "长月朋友": "长月",
    "tu": "长月",
    "ziqi": "ziqi",
    "ziqi同事": "ziqi",
    "小拉": "ziqi",
    "coco": "ziqi",
    "柏总": "ziqi",
    "小月": "ziqi",
    "徐雪": "ziqi"
  }
}
```

**字段说明：**
- `accounts`：账户名 → 目标金额（必须）
- `funds`：出资人 → 出资金额（必须）
- `ownership`：出资人 → 所属账户名（可选，未列出的视为公共资金）
- `title` / `subtitle`：图片标题/副标题（可选）

### 2. 运行脚本

```bash
python3 scripts/allocate.py input.json --png --title "资金分配方案" --subtitle "描述信息"
```

参数：
- `--png`：生成 PNG 图片（需要 Playwright）
- `--html`：生成 HTML 文件
- `-o DIR`：输出目录（默认当前目录）
- `--title`：标题（覆盖 JSON 中的 title）
- `--subtitle`：副标题（覆盖 JSON 中的 subtitle）

### 3. 输出文件

- `allocation_result.json`：分配结果（含 allocation / summary / split_persons）
- `allocation.html`：HTML 表格（如指定 --html 或 --png）
- `allocation.png`：PNG 图片（如指定 --png）

## 关键规则

- **相关人放一起**：ownership 中同一账户的人优先放在该账户
- **本人优先**：账户所有者的钱最先放入自己账户
- **最少拆分**：尽量保持每个人的钱完整不拆分
- **总资金必须等于总需求**：`sum(funds) == sum(accounts)`，否则无法精确分配

## 图片说明

- 被拆分的出资人行底色标红（`.split`），名字后带 ⚡ 标记
- 小计行蓝色底（`.subtotal`）
- 如需自定义样式，修改 `generate_html()` 中的 CSS
