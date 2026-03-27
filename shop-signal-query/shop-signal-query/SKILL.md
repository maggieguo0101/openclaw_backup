---
name: shop-signal-query
description: "Query merchant info by shop ID (dp_shop_id), including category (cat0/cat1), shop name, and city. Trigger keywords: 查门店信号、门店信息、商户类目、门店类目、门店城市、shop signal、dp_shop_id."
---

# Shop Signal Query

## Usage

```bash
~/.openclaw/workspace/skills/shop-signal-query/scripts/query_shop_signal.sh <dp_shop_id>
```

Example:
```bash
~/.openclaw/workspace/skills/shop-signal-query/scripts/query_shop_signal.sh 999999117
```

## Output Format

```
code | name | value
```

Example:
```
cat0_name | 商户后台一级类目 | 丽人
cat1_name | 商户后台二级类目 | 美发
shop_name | 门店名称 | XX美容院
city_name | 门店所在城市名称 | 上海
```

## Requirements

- `sr-crm-oc` CLI available (replaces mtcurl, works in non-interactive environments)
