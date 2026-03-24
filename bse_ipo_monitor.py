#!/usr/bin/env python3
"""
北交所新股监控
数据源: 东财 RPTA_APP_IPOAPPLY（原 bse.cn 被代理屏蔽，切换至东财）
触发: cron 每天 08:30 / 12:00 / 18:00 执行
逻辑:
  1. 拉「未来14天内」待申购新股，发现新股（未推送过的）立刻推送大象
  2. 发现上市日期更新的，推送上市提醒
  3. 附带发行价、PE、顶格资金等分析
"""

import requests
import json
import datetime
import os
import subprocess

# ── 配置 ────────────────────────────────────────────
DAXIANG_UID   = "2369102735"
STATE_FILE    = os.path.expanduser("~/.openclaw/workspace/bse_ipo_state.json")
EASTMONEY_API = "https://datacenter-web.eastmoney.com/api/data/v1/get"
TENCENT_QUOTE = "https://qt.gtimg.cn/q=bj{code}"
# ────────────────────────────────────────────────────

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://data.eastmoney.com/xg/",
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


def parse_date(dt_str):
    """'2026-03-25 00:00:00' → '2026-03-25'，None → None"""
    if not dt_str:
        return None
    return str(dt_str)[:10]


def fetch_bj_ipo_list():
    """
    从东财拉北交所近期新股（最近30条，按申购日倒序）
    返回 list of dict
    """
    params = {
        "reportName": "RPTA_APP_IPOAPPLY",
        "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,APPLY_CODE,APPLY_DATE,LISTING_DATE,SELECT_LISTING_DATE,ISSUE_PRICE,AFTER_ISSUE_PE,ONLINE_APPLY_UPPER,ONLINE_ISSUE_NUM,TOTAL_ISSUE_NUM,PRICE_WAY,RESULT_NOTICE_DATE,INDUSTRY_NAME",
        "filter": '(IS_BEIJING="1")',
        "pageNumber": 1,
        "pageSize": 30,
        "sortTypes": -1,
        "sortColumns": "APPLY_DATE",
        "source": "WEB",
        "client": "WEB",
    }
    r = session.get(EASTMONEY_API, params=params, timeout=12, verify=False)
    r.raise_for_status()
    d = r.json()
    if not d.get("success"):
        raise RuntimeError(f"东财接口返回失败: {d.get('message')}")
    return d["result"]["data"] or []


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
            "name":     parts[1],
            "price":    parts[3],
            "industry": parts[47] if len(parts) > 47 else "—",
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


def top_capital(issue_price, online_apply_upper):
    """顶格申购所需资金（万元）"""
    if not issue_price or not online_apply_upper:
        return "待定"
    cap = float(issue_price) * int(online_apply_upper) / 10000
    return f"{cap:.1f}万元"


def build_new_ipo_msg(s):
    """新股申购推送消息"""
    code         = s.get("APPLY_CODE", "")
    name         = s.get("SECURITY_NAME_ABBR", "")
    issue_price  = s.get("ISSUE_PRICE")
    pe           = s.get("AFTER_ISSUE_PE")
    price_way    = s.get("PRICE_WAY") or "未知"
    online_upper = s.get("ONLINE_APPLY_UPPER")
    total_issue  = s.get("TOTAL_ISSUE_NUM")
    industry     = s.get("INDUSTRY_NAME") or "—"

    apply_date   = parse_date(s.get("APPLY_DATE"))   or "待定"
    result_date  = parse_date(s.get("RESULT_NOTICE_DATE")) or "待定"
    listing_date = parse_date(s.get("LISTING_DATE") or s.get("SELECT_LISTING_DATE")) or "待定"

    issue_str    = f"{float(issue_price):.2f}" if issue_price else "待定"
    total_str    = f"{float(total_issue)/10000:.2f}万股" if total_issue else "待定"
    top_cap      = top_capital(issue_price, online_upper)
    upper_str    = f"{int(online_upper):,}股" if online_upper else "待定"

    msg = f"""🔔 **北交所新股申购提醒**

**{name}**（{code}）开始申购

---
📋 **基本信息**
| 项目 | 内容 |
|------|------|
| 申购代码 | {code} |
| 发行价格 | **{issue_str} 元** |
| 定价方式 | {price_way} |
| 申购上限 | {upper_str} |
| 顶格资金 | **{top_cap}** |
| 拟发行量 | {total_str} |
| 所属行业 | {industry} |

📅 **关键日期**
| 节点 | 日期 |
|------|------|
| 申购日 | **{apply_date}** |
| 发行结果公告日 | {result_date} |
| 上市日 | {listing_date} |

📊 **估值快评**
{pe_comment(pe)}

⚠️ 北交所新股波动大，申购金额请根据自身判断决定"""
    return msg


def build_listing_msg(s):
    """上市日期确认推送"""
    code         = s.get("APPLY_CODE", "")
    name         = s.get("SECURITY_NAME_ABBR", "")
    issue_price  = s.get("ISSUE_PRICE")
    listing_date = parse_date(s.get("LISTING_DATE") or s.get("SELECT_LISTING_DATE")) or "待定"
    issue_str    = f"{float(issue_price):.2f}" if issue_price else "—"

    days_str = ""
    ld = s.get("LISTING_DATE") or s.get("SELECT_LISTING_DATE")
    if ld:
        try:
            delta = datetime.date.fromisoformat(ld[:10]) - datetime.date.today()
            if delta.days > 0:
                days_str = f"（还有 **{delta.days}** 天）"
            elif delta.days == 0:
                days_str = "（**今日上市！**）"
        except Exception:
            pass

    quote = fetch_stock_quote(s.get("SECURITY_CODE", ""))

    msg = f"""📅 **北交所新股上市提醒**

**{name}**（{code}）上市日期已确认

---
🗓️ **上市日期：{listing_date}** {days_str}
💰 **发行价格：{issue_str} 元**"""

    if quote.get("price"):
        msg += f"\n📈 **当前参考价：{quote['price']} 元**"

    msg += """

📋 **上市首日操作提醒**
- 9:15~9:25 观察集合竞价换手率
- 换手 > 40% → 可以格局等冲高
- 换手 20~40% → 分批卖，先走一半
- 换手 < 20% → **立刻全部卖出，不犹豫**
- 下午流动性极差，原则上上午解决"""
    return msg


def send_daxiang(msg):
    """通过 openclaw CLI 发大象消息"""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "daxiang",
        "--target", DAXIANG_UID,
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

    # fallback: 写入待发文件，由 heartbeat 拾取
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
    print(f"[{now}] 北交所新股监控启动（数据源: 东财）")

    state = load_state()
    pushed_new     = state.get("pushed_new", {})
    pushed_listing = state.get("pushed_listing", {})

    try:
        stocks = fetch_bj_ipo_list()
        print(f"[OK] 北交所新股: {len(stocks)} 条")
    except Exception as e:
        print(f"[ERR] 拉取失败: {e}")
        return

    # 只关注最近14天内有申购日期的新股（或申购日在未来）
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=14)

    notified = 0

    for s in stocks:
        # 用 APPLY_CODE 作为唯一键（更稳定）
        sid          = str(s.get("APPLY_CODE", "") or s.get("SECUCODE", ""))
        code         = s.get("APPLY_CODE", "")
        name         = s.get("SECURITY_NAME_ABBR", "")
        apply_date   = parse_date(s.get("APPLY_DATE"))
        listing_date = parse_date(s.get("LISTING_DATE") or s.get("SELECT_LISTING_DATE"))

        # 过滤：只处理申购日在14天内的（包括未来）
        if apply_date:
            try:
                ad = datetime.date.fromisoformat(apply_date)
                if ad < cutoff:
                    continue  # 太老了跳过
            except Exception:
                pass

        # ① 新股申购推送（从未推送过）
        if sid not in pushed_new:
            print(f"[NEW] {code} {name} 申购日={apply_date} → 发送申购提醒")
            msg = build_new_ipo_msg(s)
            send_daxiang(msg)
            pushed_new[sid] = now
            notified += 1

        # ② 上市日期确认推送（之前没有 or 日期变更）
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
