# SMB商家企微群运营方案 v2（重构版）

## 一、背景与目标

50万SMB商家体量大、销售产能有限，商家遇到改价/上下架/活动报名等问题无人快速响应，影响留存和活跃。**目标：** 在企微群内引入 OpenClaw（王晓慧账号）作为第一响应，替代人工完成标准化维护，降低人力成本、提升商家响应效率。

---

## 二、核心服务能力：OpenClaw Skill 清单

> 以下场景覆盖商户主动发起会话的 **约70%**，是 OpenClaw 在群内的核心价值载体。

| 优先级 | 沟通场景 | 商户核心问题（来自听音） | 频率 | Skill 名称 | 现状 | 已有 Skill / MCP 链接 |
|---|---|---|---|---|---|---|
| P0 | **团单管理** | 帮我上团单/改价格/改库存/改时间/下架；团单太复杂；报名活动团单不符合条件 | 商户发起 #1，占23.1% | `deal-group-assistant` | ✅ 已有 | [服务零售商品助手](https://friday.sankuai.com/mcp/skill-detail?activeTab=overview&id=4283) · [经营宝APP外链生成](https://friday.sankuai.com/mcp/skill-detail?activeTab=overview&id=5320) |
| P0 | **营销活动报名** | 有什么活动？我的团单符合条件吗？报名失败（提交3次未通过） | 全周期 Top2，占12-26% | `marketing-activity-assistant` | ⚠️ 需封装 | [营销优惠提报 RPC 接口文档](https://km.sankuai.com/collabpage/2724108004)（已做AI友好适配） |
| P0 | **推广产品咨询** | 推广余额不够；推广消耗是否异常；推广方案怎么选；推广通设置 | LE新手期 #1，占13-16% | `promotion-assistant` | ⚠️ 需建 | [广告合作 Skill](https://friday.sankuai.com/skills/skill-detail?activeTab=overview&id=8212)（可参考，推广数据查询接口需确认） |
| P1 | **评价管理** | 如何删差评？申诉评价与实际不符；差评审核进度 | 中频，占5-8% | `merchant-review-cli` | ✅ 已有 | [merchant-review-cli](https://friday.sankuai.com/mcp/skill-detail?activeTab=overview&id=4926) |
| P1 | **店铺装修** | 头图怎么修改？图片能否用于装修？审核不通过原因 | 中频，占8% | `vg-decoration` | ✅ 已有 | [经营宝店铺装修 Skill](https://friday.sankuai.com/mcp/skill-detail?activeTab=overview&id=5456) |
| P1 | **经营评分诊断** | 浏览量为什么上不去？怎么提升转化率？热榜规则？线索质量差 | CKA #1，占10-14% | `store-performance-advisor` | ❌ 待建 | —（经营评分 API 需确认） |
| P1 | **续约咨询** | 续费多少钱？合同什么时候到期？连锁门店员工无法推动老板付款 | 续约期 #1，占9-24% | `renewal-assistant` | ❌ 待建 | —（续约接口需确认） |
| P1 | **财务管理** | 为什么不能提现？银行卡绑定问题；账单对账 | 中频 | `financial-assistant` | ❌ 待建 | — |
| P2 | **资质审核** | 审核进度；营业执照要求；连锁门店证明函怎么开 | 低中频 | `qualification-checker` | ⚠️ 需封装 | [merchant shopinfo CLI](https://dev.sankuai.com/code/repo-detail/nib/merchant-skills/file/list?path=meituan-merchant-cli) |
| P2 | **退款查询** | 退款到哪了？催退款；走到哪一步了 | 低频 | `refund-tracker` | ❌ 待建 | — |
| P2 | **连锁门店管理** | 统一管理证明；POI变更；门店合并/分拆 | 低频，教母行业集中 | `chain-store-manager` | ⚠️ 需封装 | [dzbizsupply 命令组](https://dev.sankuai.com/code/repo-detail/nib/spt-cli/file/list) |

**数据来源：** [【到综】商户与销售企微沟通行为分析](https://km.sankuai.com/collabpage/1519578113) · [【新LE】商户与销售沟通行为分析](https://km.sankuai.com/collabpage/2752162228) · [服务零售 CLI & MCP 全家桶](https://km.sankuai.com/collabpage/2751560754)

### Skill 现状汇总

| 状态 | 数量 | 场景 | 行动 |
|---|---|---|---|
| ✅ 已有，直接接入 | 3个 | 团单管理、评价管理、店铺装修 | 配置到群即可 |
| ⚠️ 需封装 | 4个 | 营销活动报名、推广咨询、资质审核、连锁门店 | 底层接口已有，包装成对话式 Skill |
| ❌ 需新建 | 4个 | 经营评分、续约咨询、财务管理、退款查询 | 确认后端接口 → 从零建 |

### 关键底层依赖（所有 Skill 共用）

| 依赖模块 | 作用 | 现有资源 | 优先级 |
|---|---|---|---|
| **商户身份识别** | 企微群成员 → 绑定门店ID | 需定制开发 | 🔴 必须先做 |
| **门店基础数据** | 门店名称/城市/品类查询 | [shop_common_data MCP](https://friday.sankuai.com/mcp/mcp-server-detail?activeTab=overview&id=3529) | 🔴 P0 |
| **销售私海门店** | 根据门店名检索私海 | [get_privatesea_shops MCP](https://friday.sankuai.com/mcp/mcp-server-detail?activeTab=overview&id=2929) | 🔴 P0 |
| **操作鉴权** | 确认商户本人/授权运营身份 | 需定制开发 | 🔴 P0 |

---

## 三、分工机制：销售 vs OpenClaw

| 事项 | 销售负责 | OpenClaw 负责 | 兜底方式 |
|---|---|---|---|
| 建立关系 | ✅ 加好友、拉群、破冰 | — | — |
| 入群介绍 | — | ✅ 自动发开场白 | — |
| 日常标准化答疑 | 兜底（复杂/情感类） | ✅ 第一响应 | 无法处理时 @销售 转人工 |
| 活动推送 | — | ✅ 定时批量群发 | — |
| 商品操作（上/改/下） | — | ✅ 调用 Skill 直接执行 | 失败时通知销售跟进 |
| 签约跟进 | ✅ 强意向商家深度跟进 | ✅ 标准化流程引导 | — |

---

## 四、群结构与运营机制

### 4.1 群结构

- **群成员：** 商家（1个）+ 责任销售 + 王晓慧（OpenClaw 账号）
- **群规模：** 1群1商家（精准服务，避免串消息）
- **覆盖目标：** 50万SMB商家，初期试点存量群（~100个）

### 4.2 触发机制

| 触发方式 | 说明 |
|---|---|
| **@王晓慧** | 商家主动提问，OpenClaw 识别意图 → 调用对应 Skill |
| **关键词监听** | 检测到"怎么改价"/"活动怎么报名"等触发词时主动响应 |
| **定时推送** | 活动招商、经营报告、余额提醒等按 cron 定期发出 |

### 4.3 入群开场白模板

> 大家好，我是王晓慧 🤖，美团智能服务助手。
>
> 有任何门店经营问题，可以直接 **@我** 或发关键词，我来帮您处理：
> - 📦 团单上架/改价/下架
> - 🎯 营销活动报名
> - 📊 经营数据查询
> - ⭐ 评价申诉
>
> 复杂问题我会及时转给您的责任销售跟进，请放心使用～

---

## 五、建群方案

| 来源 | 规模 | 现状 | 所需操作 | 优先级 |
|---|---|---|---|---|
| **存量群**（王晓慧已是群主） | ~100个 | 已在群 ✅ | 直接接入 OpenClaw，配置 Skill | 🔴 P0 最快落地 |
| **已加好友**（系统建群） | <60个/天（API限制） | 销售已加好友 | 系统 Job 批量建群 + 拉王晓慧 | 🟡 P1 |
| **未加好友**（销售拉群） | 大规模扩张 | 需先加好友 | 销售手动加好友 → 拉群 | 🟡 P1 |
| **AIBD外呼建联** | 待评估 | 不依赖销售 | AI 外呼引导商家加王晓慧 → 自动建群 | 🟢 P2 |

### 王晓慧账号关键限制（风控红线）

| 类别 | 限制 | 应对 |
|---|---|---|
| 每日 API 建群 | <60个/天 | Job 均速建群，监控当日计数 |
| 加入群总数 | ~2000个/账号 | 多账号负载均衡 |
| 消息发送 | 15条/min，7200条/日 | 定时推送按限速队列 |
| 主动加好友 | 老账号 <60人/天 | 超阈值停止当日添加 |

---

## 六、账号采买测算

（待补充）
