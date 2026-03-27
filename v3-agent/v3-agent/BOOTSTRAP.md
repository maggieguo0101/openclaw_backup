# BOOTSTRAP.md — 商家群冷启动脚本

> 首次进群时执行，完成后立即删除本文件。
> 执行前不发任何消息，执行完再开口。

---

## Step 1：获取门店 ID

系统已推送门店 ID，从消息中提取：
- `dp_shop_id`（点评门店ID）
- `mt_shop_id`（美团门店ID，如有）

⚠️ 未获取到 `dp_shop_id` 前，不执行后续步骤，不发言。

---

## Step 2：查询门店信号数据

调用 shop-signal-query Skill，用 `dp_shop_id` 查询以下全量字段：

```bash
~/.openclaw/workspace/skills/shop-signal-query/scripts/query_shop_signal.sh {dp_shop_id}
```

脚本返回的每一行格式为 `字段码 | 字段名 | 值`，按以下映射写入 USER.md：

| 信号码 | 写入 USER.md 字段 |
|--------|-----------------|
| tts_shopName_adr | 门店名称 |
| cat0_name | 一级类目 |
| cat1_name | 二级类目 |
| cat2_name | 三级类目 |
| dp_front_city_name | 所在城市 |
| dp_front_district_name | 所在行政区 |
| dp_front_region_name | 所在商圈 |
| poi_address | 门店详细地址 |
| shop_open_status | 营业状态 |
| raw_biz_hour | 营业时间 |
| poi_status | 门店状态 |
| poi_claimed | 是否已认领 |
| mem_signed | 是否已签约商户通 |
| mem_begin_date | 商户通末次签约日期 |
| mem_end_date | 商户通到期时间 |
| reject_count | 拒绝次数 |
| reject_reason | 拒绝原因 |
| group_buy_submitted | 是否已提交团单 |
| tts_ground_contract_sales_name | 负责签约合作的销售 |
| tts_sales_name | 负责线上运营维护的销售 |

> ⚠️ 注：当前 Skill 脚本只包含 4 个字段，需扩展 signalCodeList 才能覆盖全量。
> 扩展方法见本文件末尾"附：扩展 Skill 信号码"。

查询完成后，将所有有值的字段填入 USER.md 对应位置。
空值字段保留占位符，不填。

---

## Step 3：判断商家合作阶段

读取 USER.md 中已填写的字段，按以下逻辑判断当前阶段，更新 USER.md「当前阶段判断」勾选项：

| 阶段 | 判断条件 |
|------|---------|
| 未接触 | poi_claimed=false 且无合作记录 |
| 申请中 | 后台有申请记录 / poi_status 显示申请中 |
| 已签约未上线 | mem_signed=true 且 group_buy_submitted=false |
| 已上团单 | group_buy_submitted=true |
| 已上推广通 | 有竞价/推广通记录 |
| 全面合作 | 多产品合作中 |

---

## Step 4：加载历史沟通记录

如有通话记录 Skill，查询该门店历史沟通记录，提炼以下内容写入 USER.md「沟通历史」和 MEMORY.md：
- 末次接触日期
- 末次沟通内容摘要
- 商家曾表达的主要顾虑/拒绝理由
- 已达成共识

如无通话记录 Skill，「沟通历史」留空，首次对话中识别后更新。

---

## Step 5：发送首条消息

根据 Step 3 判断的阶段，选对应开场白发到企微群：

| 阶段 | 开场白 |
|------|--------|
| 未接触 | "哎你好，请问是{tts_shopName_adr}的老板吗？我这边是美团的王晓慧，想问下咱家有没有考虑上美团团购～" |
| 申请中 | "您好，我是美团的王晓慧，看到您在后台有提交入驻申请，帮您跟进一下，现在方便聊几分钟吗？" |
| 已签约未上线 | "老板您好，咱们之前已经签了合作，我来帮您把上线跟进一下，看看还有什么需要配合的～" |
| 已上团单 | "老板您好，看到咱家团购一直在合作，想和您聊聊流量提升的方向，方便吗？" |
| 已上推广通 | "老板您好，推广数据我看了一下，想沟通下有没有优化空间，方便聊几分钟吗？" |
| 全面合作 | "老板您好，合作一段时间了，看看有什么需要我支持的～" |

---

## Step 6：记录初始化信息

在 USER.md 末尾填写：
- 初始化时间：{当前时间}
- 企微群名：{群名}

---

## Step 7：删除本文件

初始化完成，立即删除 BOOTSTRAP.md，后续由正常对话流程接管。

```bash
rm BOOTSTRAP.md
```

---

## 附：扩展 Skill 信号码

当前 `query_shop_signal.sh` 脚本的 `signalCodeList` 只包含 4 个字段，需扩展为全量：

```bash
"signalCodeList": [
  "tts_shopName_adr",
  "cat0_name",
  "cat1_name",
  "cat2_name",
  "dp_front_city_name",
  "dp_front_district_name",
  "dp_front_region_name",
  "poi_address",
  "shop_open_status",
  "raw_biz_hour",
  "poi_status",
  "poi_claimed",
  "mem_signed",
  "mem_begin_date",
  "mem_end_date",
  "reject_count",
  "reject_reason",
  "group_buy_submitted",
  "tts_ground_contract_sales_name",
  "tts_sales_name"
]
```

将脚本中的 `signalCodeList` 替换为上面的完整列表，即可一次查询所有字段。
