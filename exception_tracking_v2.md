# 添加王晓慧企微及企微群 - 各种异常情况埋点梳理

> 基于《AIBD直签-添加王晓慧企微及企微群能力》方案，按流程各环节梳理异常情况及对应埋点设计。

---

## 一、整体流程 & 异常分布全览

![AIBD直签流程·各环节异常情况全览](https://s3plus-bj02.vip.sankuai.com/openclaw-bucket/aibd-exception-flow.png)

---

## 二、各环节异常情况 & 埋点设计

### 环节1：AI外呼阶段

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 1.1 | 外呼无人接听 | 多次拨打商家无人接听，无法触达 | `aibd_call_no_answer` | merchantId, callCount, lastCallTime |
| 1.2 | 外呼被拒绝/挂断 | 商家接通后主动挂断或明确拒绝 | `aibd_call_rejected` | merchantId, callDuration, rejectReason |
| 1.3 | 外呼意向判断失败 | AI无法判断商家意向，无法推进 | `aibd_call_intent_unknown` | merchantId, callId |
| 1.4 | 外呼号码无效 | 号码停机/空号/错误 | `aibd_call_invalid_number` | merchantId, phoneNumber |

---

### 环节2：添加王晓慧企微

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 2.1 | **好友申请发出，商家未通过** | 王晓慧发出好友申请，商家超时未接受（超过N天） | `weixiao_friend_req_timeout` | merchantId, assistantId, reqSentTime, timeoutHours |
| 2.2 | **好友申请被拒绝** | 商家主动拒绝王晓慧的好友申请 | `weixiao_friend_req_rejected` | merchantId, assistantId |
| 2.3 | **小助手添加限频触发** | 当天添加好友数达到上限（被动100个/日） | `weixiao_add_limit_reached` | assistantId, date, dailyAddCount |
| 2.4 | **小助手账号被封禁** | 因投诉或违规导致小助手账号被封 | `weixiao_account_banned` | assistantId, banTime, affectedFriendCount, affectedGroupCount |
| 2.5 | **深海托管异常** | 深海平台未能成功托管/消息下发失败 | `shensea_hosting_error` | assistantId, errorCode, errorMsg |
| 2.6 | **好友数量达上限** | 单个小助手好友数达20000上限 | `weixiao_friend_limit_reached` | assistantId, currentFriendCount |

---

### 环节3：企微好友已加，但企微群未新建

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 3.1 | **好友通过后超时未建群** | 商家已通过好友申请，但超过N小时/天未触发建群 | `group_create_timeout_after_friend` | merchantId, assistantId, friendAddedTime, timeoutHours |
| 3.2 | **建群失败-系统错误** | 调用深海建群接口返回失败 | `group_create_api_failed` | merchantId, assistantId, errorCode, errorMsg |
| 3.3 | **建群失败-小助手当日建群数达上限** | 单个小助手当日已建60个群，触发上限 | `group_create_daily_limit` | assistantId, date, dailyGroupCount |
| 3.4 | **建群失败-小助手总群数达上限** | 小助手手动建群总数达500上限 | `group_create_total_limit` | assistantId, totalGroupCount |
| 3.5 | **建群成功但商家不在群内** | 群创建成功，但商家未被成功拉入 | `group_create_merchant_missing` | merchantId, groupId, assistantId |
| 3.6 | **建群成功但销售未入群** | 群创建成功，但对应销售未被拉入 | `group_create_sales_missing` | groupId, salesId, assistantId |
| 3.7 | **群和门店关联失败** | 建群后群ID与门店ID绑定关系写入失败 | `group_store_bind_failed` | groupId, storeId, errorCode |

---

### 环节4：企微群已建，但未发起企微问答

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 4.1 | **建群后超时未发起问答** | 群创建后超过N小时，AI未发出第一条开场消息 | `qa_init_timeout_after_group` | groupId, merchantId, groupCreatedTime, timeoutHours |
| 4.2 | **问答消息发送失败** | AI尝试发消息但深海平台下发失败 | `qa_msg_send_failed` | groupId, assistantId, errorCode, errorMsg |
| 4.3 | **消息发出但商家未回复-超时** | AI发出问答消息，商家超过3小时无回复 | `qa_merchant_no_reply_timeout` | groupId, merchantId, msgSentTime, timeoutHours |
| 4.4 | **单日群内消息量超限** | 小助手单日消息总量达7200条上限 | `qa_daily_msg_limit` | groupId, assistantId, date, msgCount |
| 4.5 | **群内消息丢失** | 群数量超过1000时出现消息拉取丢失 | `qa_msg_loss_detected` | groupId, assistantId, lostMsgCount |
| 4.6 | **商家退群** | 商家主动退出企微群，问答流程中断 | `qa_merchant_left_group` | groupId, merchantId, leaveTime |
| 4.7 | **AI回复内容异常** | 商家发消息但AI无法给出有效回复 | `qa_ai_response_failed` | groupId, merchantId, userMsg, errorType |

---

### 环节5：问答完成，但签约未完成

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 5.1 | **签约链接发出，商家超时未点击** | 签约小程序链接发出后超3小时无操作 | `sign_link_click_timeout` | groupId, merchantId, linkSentTime, timeoutHours |
| 5.2 | **签约小程序打开失败** | 商家点击后小程序加载异常 | `sign_miniapp_load_failed` | merchantId, errorCode |
| 5.3 | **签约流程中途放弃** | 商家进入签约小程序但未提交 | `sign_process_abandoned` | merchantId, lastStep |
| 5.4 | **已认领商家-材料提交超时** | 请材料后超3小时商家未提供材料 | `sign_material_submit_timeout` | groupId, merchantId, reqTime, timeoutHours |
| 5.5 | **已认领商家-材料不完整** | 商家提供的材料缺少营业执照或身份证 | `sign_material_incomplete` | groupId, merchantId, missingItems |
| 5.6 | **签约审批超时** | 签约提交后超3小时未审批完成 | `sign_approval_timeout` | merchantId, submitTime, timeoutHours |
| 5.7 | **签约审批被拒绝** | 签约审批不通过，需重新处理 | `sign_approval_rejected` | merchantId, rejectReason |

---

### 环节6：签约完成，但上团单未完成

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 6.1 | **签约完成后超时未触发上团单** | 签约回调后超3小时未发起上团单 | `order_init_timeout_after_sign` | merchantId, signedTime, timeoutHours |
| 6.2 | **团单字段收集不完整** | 必填字段（团单名称/门市价/团购价）未收集完整 | `order_field_incomplete` | groupId, merchantId, missingFields |
| 6.3 | **上团单接口调用失败** | 调用上团单 Skill 时接口返回错误 | `order_submit_api_failed` | merchantId, errorCode, errorMsg |
| 6.4 | **团单行业字段模板缺失** | 该商家行业的字段模板未配置 | `order_template_missing` | merchantId, industryType |
| 6.5 | **团单提交后审核超时** | 团单提交后超时未完成平台审核 | `order_review_timeout` | merchantId, submitTime, timeoutHours |
| 6.6 | **团单审核被拒绝** | 团单信息不符合平台要求，审核不通过 | `order_review_rejected` | merchantId, rejectReason |

---

### 环节7：通知真人销售跟进的异常

| # | 异常场景 | 异常描述 | 建议埋点事件名 | 关键字段 |
|---|----------|----------|----------------|----------|
| 7.1 | **大象通知发送失败** | 通知真人销售的大象消息发送失败 | `sales_notify_daxiang_failed` | merchantId, salesMisId, errorCode |
| 7.2 | **真人销售超时未跟进** | 大象通知发出后超3小时，销售未处理 | `sales_followup_timeout` | merchantId, salesMisId, notifyTime, timeoutHours |
| 7.3 | **销售misId映射缺失** | 无法找到该商家对应的责任销售 | `sales_mis_mapping_missing` | merchantId, groupId |

---

## 三、小助手账号层面的异常

| # | 异常场景 | 建议埋点事件名 | 关键字段 |
|---|----------|----------------|----------|
| 8.1 | 单账号群数量超过建议上限（300群） | `assistant_group_overload` | assistantId, currentGroupCount, threshold |
| 8.2 | 单账号好友数超过建议上限（3000） | `assistant_friend_overload` | assistantId, currentFriendCount, threshold |
| 8.3 | 单日消息量超过7200条上限 | `assistant_daily_msg_overload` | assistantId, date, msgCount |
| 8.4 | 账号被封禁（无法做继承转移） | `assistant_account_banned` | assistantId, banReason, affectedGroups |
| 8.5 | 深海平台流量超限（>150MB/min） | `shensea_traffic_overload` | assistantId, trafficMbPerMin |
| 8.6 | 深海仅支持iOS托管 | `shensea_android_unsupported` | assistantId, deviceType |

---

## 四、埋点优先级汇总

| 优先级 | 埋点事件名 | 所属环节 | 说明 |
|--------|-----------|---------|------|
| 🔴 P0 | `weixiao_account_banned` | 账号层 | 封号影响所有群，最严重 |
| 🔴 P0 | `group_create_timeout_after_friend` | 环节3 | 好友加了但群未建，典型断链 |
| 🔴 P0 | `qa_init_timeout_after_group` | 环节4 | 群建了但未发问答，典型断链 |
| 🔴 P0 | `qa_merchant_left_group` | 环节4 | 商家退群，流程彻底中断 |
| 🔴 P0 | `sign_approval_rejected` | 环节5 | 签约被拒，需立即人工介入 |
| 🔴 P0 | `order_submit_api_failed` | 环节6 | 上团单失败，直接影响转化 |
| 🟡 P1 | `weixiao_friend_req_timeout` | 环节2 | 好友申请无响应 |
| 🟡 P1 | `qa_merchant_no_reply_timeout` | 环节4 | 商家沉默，需提醒 |
| 🟡 P1 | `sign_link_click_timeout` | 环节5 | 签约链接无人点击 |
| 🟡 P1 | `sales_followup_timeout` | 环节7 | 真人销售未跟进 |
| 🟡 P1 | `assistant_group_overload` | 账号层 | 账号负载预警 |
| 🟢 P2 | `aibd_call_no_answer` | 环节1 | 外呼无人接 |
| 🟢 P2 | `group_store_bind_failed` | 环节3 | 群和门店绑定失败 |
| 🟢 P2 | `order_template_missing` | 环节6 | 行业模板缺失 |
| 🟢 P2 | `sales_mis_mapping_missing` | 环节7 | 销售映射缺失 |

---

## 五、异常处理建议

| 异常类型 | 处理策略 |
|----------|---------|
| 超时类（好友未通过/群未建/问答无回复） | 按3小时窗口自动补发提醒，22:00~08:00 夜间静默，超最大重试次数后转人工 |
| 系统错误类（接口失败/托管异常） | 自动重试3次，失败后告警通知技术负责人 |
| 账号风控类（封号/限频） | 立即切换备用小助手账号，同时触发紧急告警 |
| 商家主动拒绝类（退群/拒绝好友） | 标记商家状态，通知销售人工跟进，不再自动触达 |
| 人工介入类（材料不完整/审批被拒） | 通过大象通知对应销售，附带详细信息和操作指引 |

---

## 六、监控告警配置表

> 告警级别说明：**P0** = 核心链路中断，需立即响应（5min内）；**P1** = 影响转化效率，需当日处理（1h内）；**P2** = 潜在风险，需关注（24h内）

| 监控环节 | 指标项 | 监控描述 | 触发条件 | 告警级别 |
|----------|--------|----------|----------|----------|
| **接入层** | 深海平台消息下发成功率 | 王晓慧账号通过深海发送消息的成功率 | 成功率 < 95%（5min 窗口） | P0 |
| **接入层** | 深海平台消息接收成功率 | 深海接收企微群消息并回调 OpenClaw 的成功率 | 成功率 < 95%（5min 窗口） | P0 |
| **接入层** | 企微群消息丢失率 | 单群消息拉取丢失情况（群数量超 1000 时高发） | 丢失率 > 1%（10min 窗口） | P1 |
| **账号层** | 小助手账号封禁数 | 当前被封禁的小助手账号数量 | 封禁数 ≥ 1 | P0 |
| **账号层** | 单账号日消息量 | 单个小助手账号当日累计发送消息总量 | 单账号 > 6000 条/日（预警）；> 7200 条/日（触发上限） | P1 |
| **账号层** | 单账号群负载 | 单个小助手账号当前承载群数量 | > 300 群（预警）；> 500 群（触发上限） | P1 |
| **账号层** | 单账号好友数 | 单个小助手账号当前好友总量 | > 3000（预警）；> 18000（接近上限） | P1 |
| **账号层** | 深海流量超限 | 单账号下发信息流量速率 | > 120MB/min（预警）；> 150MB/min（红线） | P0 |
| **添加企微** | 好友申请通过率 | 每日王晓慧发出好友申请中商家通过的比例 | 通过率 < 30%（当日，较基线下降 20%+） | P1 |
| **添加企微** | 好友申请积压量 | 发出后超 24h 仍未通过/拒绝的申请数 | 积压数 > 100 | P2 |
| **企微群** | 建群成功率 | 触发建群动作后实际建群成功的比例 | 成功率 < 95%（1h 窗口） | P0 |
| **企微群** | 好友加成功→建群耗时 | 从好友通过到建群完成的时间 | 平均耗时 > 30min | P1 |
| **企微群** | 建群后成员完整率 | 建群后商家+销售均在群内的比例 | 完整率 < 98% | P1 |
| **企微群** | 群与门店绑定失败数 | 建群后 groupId↔storeId 绑定写入失败的数量 | 失败数 > 0（任意出现即告警） | P1 |
| **企微问答** | 建群→首条消息发送耗时 | 从建群完成到 AI 发出第一条开场消息的时间 | 平均耗时 > 10min | P1 |
| **企微问答** | AI 回复超时率 | AI 响应商家消息耗时 > 15s 的比例 | 超时比例 > 5%（10min 窗口） | P1 |
| **企微问答** | 商家无回复率 | 发出问答消息后 3h 内商家无任何回复的群比例 | 无回复率 > 60%（当日） | P2 |
| **企微问答** | 商家退群数 | 当日商家主动退群的数量 | 退群数 > 10（当日） | P1 |
| **签约** | 签约链接点击率 | 发出签约小程序链接后商家点击的比例 | 点击率 < 20%（当日，较基线下降 30%+） | P2 |
| **签约** | 签约提交接口异常数 | "提交签约"接口 5xx 报错次数 | 1min 内 5xx 报错 > 5 次 | P0 |
| **签约** | 签约审批通过率 | 提交签约后审批通过的比例 | 通过率 < 80%（当日） | P1 |
| **签约** | 签约审批耗时 | 从提交签约到审批完成的平均时间 | 平均耗时 > 4h | P2 |
| **上团单** | 上团单接口成功率 | 调用上团单接口的成功率 | 成功率 < 95%（5min 窗口） | P0 |
| **上团单** | 上团单接口异常数 | 上团单接口 5xx 报错次数 | 1min 内 5xx 报错 > 5 次 | P0 |
| **上团单** | 签约完成→上团单触发耗时 | 从签约审批通过到触发上团单流程的时间 | 平均耗时 > 30min | P1 |
| **上团单** | 团单审核通过率 | 提交团单后平台审核通过的比例 | 通过率 < 85%（当日） | P1 |
| **下游依赖** | 资质审核接口（OCR/风控）成功率 | 调用营业执照/身份证 OCR 识别及风控接口的成功率 | 连续 3 次调用失败或超时 | P1 |
| **下游依赖** | 大象通知接口成功率 | 向真人销售发送大象通知消息的成功率 | 成功率 < 99%（5min 窗口） | P1 |
| **业务漏斗** | 外呼→加企微转化率 | AI 外呼成功后商家实际添加王晓慧的比例 | 转化率较过去 7 日均值下降 > 30% | P2 |
| **业务漏斗** | 加企微→建群转化率 | 好友通过后成功建群的比例 | 转化率较过去 7 日均值下降 > 30% | P2 |
| **业务漏斗** | 建群→签约完成转化率 | 建群后最终完成签约的比例 | 转化率较过去 7 日均值下降 > 30% | P1 |
| **业务漏斗** | 签约→上团单完成转化率 | 签约完成后最终完成上团单的比例 | 转化率较过去 7 日均值下降 > 30% | P1 |

---

## 七、告警响应 SLA

| 告警级别 | 响应时间 | 处理时间 | 通知方式 |
|----------|----------|----------|----------|
| **P0** | 5min 内响应 | 30min 内恢复或降级 | 大象即时消息 + 电话 |
| **P1** | 30min 内响应 | 2h 内处理完毕 | 大象即时消息 |
| **P2** | 2h 内响应 | 24h 内处理完毕 | 大象日报汇总 |
