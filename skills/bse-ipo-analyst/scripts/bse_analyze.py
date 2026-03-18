#!/usr/bin/env python3
"""
北交所新股申购分析工具
用法:
  python3 bse_analyze.py list          # 列出当前所有发行中新股
  python3 bse_analyze.py analyze CODE  # 分析指定股票（如 920069）
  python3 bse_analyze.py pending       # 显示近期待申购新股

输出格式：结构化 JSON 或可读文本，供 Claude 组织为最终分析报告
"""

import requests
import json
import re
import datetime
import sys
import warnings
warnings.filterwarnings("ignore")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bse.cn/newshare/listofissues.html",
})

BSE_API = "https://www.bse.cn/newShareController/infoResult.do"
TENCENT_QUOTE = "https://qt.gtimg.cn/q=bj{code}"

FIELDS = ["id", "fxCode", "stockCode", "stockName", "initialIssueAmount",
          "enquiryType", "issuePrice", "peRatio", "purchaseDate",
          "issueResultDate", "enterPremiumDate", "planDate"]
ENQUIRY_MAP = {1: "询价", 2: "竞价", 3: "直接定价"}


def ts_to_date(ts_obj):
    if not ts_obj:
        return None
    ts = ts_obj.get("time") if isinstance(ts_obj, dict) else ts_obj
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d")


def fetch_bse_list(state_type="1", keyword=""):
    data = {
        "statetypes": state_type,
        "page": 0,
        "isNewThree": 1,
        "sortfield": "purchaseDate",
        "sorttype": "desc",
        "keyword": keyword,
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
    try:
        r = session.get(TENCENT_QUOTE.format(code=code), timeout=6, verify=False)
        raw = r.content.decode("gbk", errors="replace")
        if "~" not in raw:
            return {}
        parts = raw.split('"')[1].split("~")
        if len(parts) < 45:
            return {}
        return {
            "price": parts[3],
            "industry": parts[47] if len(parts) > 47 else "",
        }
    except Exception:
        return {}


def calc_yield(issue_price, open_price, top_capital_wan, freeze_days=4):
    """计算打新年化收益率（顶格100股正股）"""
    gain_per_sign = (open_price - issue_price) * 100
    annual_yield = gain_per_sign / (top_capital_wan * 10000) * (365 / freeze_days) * 100
    return round(gain_per_sign, 2), round(annual_yield, 2)


def days_until(date_str):
    if not date_str:
        return None
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - datetime.date.today()).days


def format_stock(s, verbose=False):
    code = s.get("fxCode", "")
    name = s.get("stockName", "")
    issue_price = s.get("issuePrice") or 0
    pe = s.get("peRatio") or 0
    enquiry = s.get("enquiryType", 3)
    amount = s.get("initialIssueAmount") or 0
    purchase_date = ts_to_date(s.get("purchaseDate"))
    result_date = ts_to_date(s.get("issueResultDate"))
    listing_date = ts_to_date(s.get("enterPremiumDate"))

    purchase_days = days_until(purchase_date)
    listing_days = days_until(listing_date)

    # 北交所申购上限规则：
    # 网上发行量 = 总发行量 × 90%（战略配售10%）
    # 单账户顶格上限 ≈ 网上发行量 × 5%（经验值，实际以招股书为准）
    net_issue = amount * 0.9
    top_shares = round(net_issue * 0.05, 0)
    top_capital_wan = round(top_shares * issue_price / 10000, 2)

    # 正股门槛估算：经验值约顶格的48%（基于历史数据）
    est_threshold_wan = round(top_capital_wan * 0.48, 0)

    quote = fetch_stock_quote(code)
    industry = quote.get("industry", "—")

    result = {
        "code": code,
        "name": name,
        "issue_price": issue_price,
        "pe": pe,
        "pricing_type": ENQUIRY_MAP.get(int(enquiry) if enquiry else 0, "未知"),
        "issue_shares_wan": round(amount / 10000, 2),
        "top_shares_wan": round(top_shares / 10000, 2),
        "top_capital_wan": top_capital_wan,
        "est_threshold_wan": est_threshold_wan,
        "purchase_date": purchase_date,
        "purchase_days": purchase_days,
        "result_date": result_date,
        "listing_date": listing_date,
        "listing_days": listing_days,
        "industry": industry,
        "sign_capital_yuan": round(issue_price * 100, 2),  # 1签100股缴款
    }

    if verbose:
        # 预计开盘价区间（基于行业PE折价还原）
        # 发行PE通常14~15x，行业PE一般20~40x，取2~2.5倍发行价作为中性估计
        open_pessimistic = round(issue_price * 1.5, 2)
        open_neutral = round(issue_price * 2.0, 2)
        open_optimistic = round(issue_price * 2.5, 2)

        scenarios = []
        for label, op in [("悲观", open_pessimistic), ("中性", open_neutral), ("乐观", open_optimistic)]:
            gain, yr = calc_yield(issue_price, op, top_capital_wan)
            scenarios.append({
                "scenario": label,
                "open_price": op,
                "gain_per_sign": gain,
                "annual_yield_pct": yr,
            })
        result["yield_scenarios"] = scenarios

    return result


def cmd_list():
    stocks = fetch_bse_list("1")
    today = datetime.date.today()
    print(f"北交所发行中新股（共 {len(stocks)} 只）\n")
    for s in sorted(stocks, key=lambda x: (x.get("purchaseDate") or {}).get("time") or 0, reverse=True):
        code = s.get("fxCode", "")
        name = s.get("stockName", "")
        price = s.get("issuePrice")
        pe = s.get("peRatio")
        purchase_date = ts_to_date(s.get("purchaseDate"))
        listing_date = ts_to_date(s.get("enterPremiumDate"))

        flag = ""
        if purchase_date:
            d = datetime.datetime.strptime(purchase_date, "%Y-%m-%d").date()
            diff = (d - today).days
            if diff == 0:
                flag = " ⬅️【今日申购】"
            elif diff == 1:
                flag = " ⬅️【明日申购】"
            elif diff < 0 and not listing_date:
                flag = f" （已申购{-diff}天前，上市待定）"

        print(f"{code} {name:10} | 发行价:{price:6} | PE:{pe:5} | 申购:{purchase_date}{flag} | 上市:{listing_date or '待定'}")


def cmd_analyze(code_or_name):
    stocks = fetch_bse_list("1", keyword=code_or_name)
    if not stocks:
        # 尝试搜索全部
        stocks = fetch_bse_list("", keyword=code_or_name)
    if not stocks:
        print(f"未找到：{code_or_name}")
        return

    s = stocks[0]
    data = format_stock(s, verbose=True)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_pending():
    """显示未来7天内待申购的新股"""
    stocks = fetch_bse_list("1")
    today = datetime.date.today()
    upcoming = []
    for s in stocks:
        purchase_date = ts_to_date(s.get("purchaseDate"))
        if purchase_date:
            d = datetime.datetime.strptime(purchase_date, "%Y-%m-%d").date()
            diff = (d - today).days
            if 0 <= diff <= 7:
                upcoming.append((diff, s))

    if not upcoming:
        print("未来7天内无待申购新股")
        return

    upcoming.sort(key=lambda x: x[0])
    print(f"未来7天待申购新股（{len(upcoming)} 只）：\n")
    for diff, s in upcoming:
        data = format_stock(s, verbose=True)
        label = "今日" if diff == 0 else f"{diff}天后"
        print(f"【{label}申购】{data['name']}（{data['code']}）")
        print(f"  发行价: {data['issue_price']}元 | PE: {data['pe']}x | 定价: {data['pricing_type']}")
        print(f"  顶格资金: {data['top_capital_wan']}万元 | 正股门槛(估): {data['est_threshold_wan']}万元")
        print(f"  1签缴款: {data['sign_capital_yuan']}元")
        if data.get("yield_scenarios"):
            print("  收益预测:")
            for sc in data["yield_scenarios"]:
                print(f"    {sc['scenario']}: 开盘价{sc['open_price']}元 → 每签+{sc['gain_per_sign']}元 | 顶格年化{sc['annual_yield_pct']}%")
        print()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pending"
    if cmd == "list":
        cmd_list()
    elif cmd == "analyze" and len(sys.argv) > 2:
        cmd_analyze(sys.argv[2])
    elif cmd == "pending":
        cmd_pending()
    else:
        print("用法: bse_analyze.py [list|analyze CODE|pending]")
