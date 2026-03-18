#!/usr/bin/env python3
"""
北交所新股监控
数据源: 北交所官网 bse.cn/newshare/listofissues.html
触发: cron 每天 08:30 / 12:00 / 18:00 执行
逻辑:
  1. 拉「发行中」列表，发现新股（未推送过的）立刻推送大象
  2. 拉「发行中」列表，发现有上市日期更新的，推送上市提醒
  3. 附带股票分析（发行价、PE、行业、募资用途简析）
"""

import requests
import json
import re
import datetime
import os
import sys
import subprocess

# ── 配置 ────────────────────────────────────────────
DAXIANG_UID   = "2369102735"
STATE_FILE    = os.path.expanduser("~/.openclaw/workspace/bse_ipo_state.json")
BSE_API       = "https://www.bse.cn/newShareController/infoResult.do"
TENCENT_QUOTE = "https://qt.gtimg.cn/q=bj{code}"
FIELDS        = ["id","fxCode","stockCode","stockName","initialIssueAmount",
                 "enquiryType","issuePrice","peRatio","purchaseDate",
                 "issueResultDate","enterPremiumDate"]
ENQUIRY_MAP   = {1: "询价", 2: "竞价", 3: "直接定价"}
# ────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bse.cn/newshare/listofissues.html",
})


# ── 工具函数 ─────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pushed_new": {}, "pushed_listing": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def ts_to_date(ts_ms):
    """毫秒时间戳 → YYYY-MM-DD"""
    if not ts_ms:
        return None
    return datetime.datetime.fromtimestamp(int(ts_ms) / 1000).strftime("%Y-%m-%d")


def fetch_bse_list(state_type="1"):
    """
    state_type: "1"=发行中  "2"=已完成  ""=全部
    返回 list of dict
    """
    data = {
        "statetypes": state_type,
        "page": 0,
        "companyCode": "",
        "isNewThree": 1,
        "sortfield": "purchaseDate",
        "sorttype": "desc",
        "startTime": "",
        "endTime": "",
        "keyword": "",
        "needFields": json.dumps(FIELDS),
        "callback": "cb",
    }
    r = session.post(BSE_API, data=data, timeout=12, verify=False)
    r.raise_for_status()
    m = re.search(r"\((.+)\)", r.text, re.DOTALL)
    raw = m.group(1) if m else r.text
    obj = json.loads(raw)
    return obj[0]["listInfo"]["content"]


def fetch_stock_quote(code):
    """腾讯行情 → 返回基础信息 dict"""
    try:
        r = session.get(TENCENT_QUOTE.format(code=code), timeout=6, verify=False)
        raw = r.content.decode("gbk", errors="replace")
        if "~" not in raw:
            return {}
        parts = raw.split('"')[1].split("~")
        if len(parts) < 45:
            return {}
        return {
            "name":       parts[1],
            "price":      parts[3],
            "change_pct": parts[32] if len(parts) > 32 else "N/A",
            "pe":         parts[39] if len(parts) > 39 else "N/A",
            "market_cap": parts[45] if len(parts) > 45 else "N/A",
            "industry":   parts[47] if len(parts) > 47 else "N/A",
        }
    except Exception:
        return {}


def pe_comment(pe):
    """PE 解读"""
    if pe is None:
        return "PE数据缺失"
    try:
        v = float(pe)
    except Exception:
        return "PE数据异常"
    if v <= 15:
        return f"PE {v:.1f}x，估值偏低，安全边际较高 ✅"
    elif v <= 25:
        return f"PE {v:.1f}x，估值合理，符合北交所均值水平"
    elif v <= 40:
        return f"PE {v:.1f}x，估值偏高，需关注成长性支撑"
    else:
        return f"PE {v:.1f}x，估值较贵 ⚠️，建议谨慎申购"


def enquiry_comment(t):
    name = ENQUIRY_MAP.get(t, "未知")
    if t == 3:
        return f"{name} — 价格固定，申购确定性高"
    elif t == 1:
        return f"{name} — 机构定价，波动相对可控"
    else:
        return f"{name}"


def build_new_ipo_msg(s):
    """新股发行推送消息"""
    code         = s.get("fxCode", "")
    name         = s.get("stockName", "")
    issue_price  = s.get("issuePrice")
    pe           = s.get("peRatio")
    enquiry      = s.get("enquiryType")
    amount       = s.get("initialIssueAmount")
    purchase_ts  = (s.get("purchaseDate") or {}).get("time")
    result_ts    = (s.get("issueResultDate") or {}).get("time")
    listing_ts   = (s.get("enterPremiumDate") or {}).get("time")

    purchase_date = ts_to_date(purchase_ts) or "待定"
    result_date   = ts_to_date(result_ts)   or "待定"
    listing_date  = ts_to_date(listing_ts)  or "待定"

    issue_str  = f"{issue_price:.2f}" if issue_price else "待定"
    amount_str = f"{float(amount)/10000:.2f}万股" if amount else "待定"

    quote = fetch_stock_quote(code)
    industry = quote.get("industry", "—")

    msg = f"""🔔 **北交所新股申购提醒**

**{name}**（{code}）开始申购

---
📋 **基本信息**
| 项目 | 内容 |
|------|------|
| 申购代码 | {code} |
| 发行价格 | **{issue_str} 元** |
| 定价方式 | {enquiry_comment(enquiry)} |
| 拟发行量 | {amount_str} |
| 所属行业 | {industry} |

📅 **关键日期**
| 节点 | 日期 |
|------|------|
| 申购日 | **{purchase_date}** |
| 发行结果公告日 | {result_date} |
| 上市日 | {listing_date} |

📊 **估值快评**
{pe_comment(pe)}

🔗 **官方公告**
https://www.bse.cn/newshare/listofissues_detail.html?id={s.get("id","")}

---
⚠️ 北交所新股波动大，申购金额请根据自身判断决定"""
    return msg


def build_listing_msg(s):
    """上市日期确认推送"""
    code         = s.get("fxCode", "")
    name         = s.get("stockName", "")
    issue_price  = s.get("issuePrice")
    listing_ts   = (s.get("enterPremiumDate") or {}).get("time")
    listing_date = ts_to_date(listing_ts) or "待定"
    issue_str    = f"{issue_price:.2f}" if issue_price else "—"

    # 距离上市天数
    days_str = ""
    if listing_ts:
        delta = datetime.datetime.fromtimestamp(int(listing_ts)/1000).date() - datetime.date.today()
        if delta.days >= 0:
            days_str = f"（还有 **{delta.days}** 天）"
        else:
            days_str = "（今日上市！）"

    quote = fetch_stock_quote(code)

    msg = f"""📅 **北交所新股上市提醒**

**{name}**（{code}）上市日期已确认

---
🗓️ **上市日期：{listing_date}** {days_str}
💰 **发行价格：{issue_str} 元**"""

    if quote.get("price"):
        msg += f"""
📈 **当前参考价：{quote['price']} 元**"""

    msg += f"""

📋 **上市首日操作提醒**
- 9:15~9:25 观察集合竞价换手率
- 换手 > 40% → 可以格局等冲高
- 换手 20~40% → 分批卖，先走一半
- 换手 < 20% → **立刻全部卖出，不犹豫**
- 下午流动性极差，原则上上午解决

🔗 https://www.bse.cn/newshare/listofissues_detail.html?id={s.get("id","")}"""
    return msg


def send_daxiang(msg):
    """通过 openclaw CLI 发大象消息"""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "daxiang",
        "--to", DAXIANG_UID,
        "--message", msg,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"[SENT] 大象消息发送成功")
            return True
        else:
            print(f"[WARN] openclaw send失败，写入pending: {result.stderr[:100]}")
    except Exception as e:
        print(f"[WARN] 发送异常: {e}")

    # fallback: 写入待发文件，由 heartbeat 拾取后通过 message 工具发送
    notify_path = os.path.expanduser("~/.openclaw/workspace/bse_ipo_notify_pending.json")
    pending = []
    if os.path.exists(notify_path):
        try:
            with open(notify_path) as f:
                pending = json.load(f)
        except Exception:
            pending = []
    pending.append({"to": DAXIANG_UID, "message": msg, "time": datetime.datetime.now().isoformat()})
    with open(notify_path, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)
    print(f"[PENDING] 消息已写入待发队列")
    return False


# ── 主逻辑 ───────────────────────────────────────────

def run():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 北交所新股监控启动")

    state = load_state()
    pushed_new     = state.get("pushed_new", {})      # {id: push_time}
    pushed_listing = state.get("pushed_listing", {})   # {id: listing_date}

    try:
        stocks = fetch_bse_list("1")   # 发行中
        print(f"[OK] 发行中: {len(stocks)} 条")
    except Exception as e:
        print(f"[ERR] 拉取失败: {e}")
        return

    notified = 0

    for s in stocks:
        sid      = str(s.get("id", ""))
        code     = s.get("fxCode", "")
        name     = s.get("stockName", "")
        listing_ts = (s.get("enterPremiumDate") or {}).get("time")
        listing_date = ts_to_date(listing_ts)

        # ① 新股申购推送（从未推送过）
        if sid not in pushed_new:
            print(f"[NEW] {code} {name} → 发送申购提醒")
            msg = build_new_ipo_msg(s)
            send_daxiang(msg)
            pushed_new[sid] = now
            notified += 1

        # ② 上市日期确认推送（之前是待定，现在有具体日期了）
        prev_listing = pushed_listing.get(sid)
        if listing_date and listing_date != prev_listing:
            print(f"[LISTING] {code} {name} 上市日期确认 → {listing_date}")
            msg = build_listing_msg(s)
            send_daxiang(msg)
            pushed_listing[sid] = listing_date
            notified += 1

    if notified == 0:
        print(f"[OK] 无新动态，本次检查完毕")

    state["pushed_new"]     = pushed_new
    state["pushed_listing"] = pushed_listing
    state["last_check"]     = now
    save_state(state)
    print(f"[DONE] 本次推送 {notified} 条，状态已保存")


if __name__ == "__main__":
    run()
