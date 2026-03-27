#!/usr/bin/env python3
"""
北交所打新全流程工具 bse-ipo-full v2
用法:
  python3 bse_pipeline.py calendar     # 【流程2】申购/上市提醒（含申购提前预警）
  python3 bse_pipeline.py analyze CODE # 【流程3】申购分析（资金策略+三档收益）
  python3 bse_pipeline.py listing CODE # 【流程4】上市提醒+收益预测
  python3 bse_pipeline.py review CODE  # 【流程5】卖出复盘记录
  python3 bse_pipeline.py quote CODE   # 实时行情
  python3 bse_pipeline.py pipeline     # 排队/注册批文预估
"""

import subprocess, requests, json, datetime, sys, os, re, warnings
warnings.filterwarnings("ignore")

CATCLAW = "/app/skills/catclaw-search/scripts/catclaw_search.py"
STRATEGY_FILE = "/root/.openclaw/workspace/memory/ipo-strategy.md"

# 历史均值（2025年）
PIPELINE_DAYS = {
    "注册生效→上市": 31,
    "注册生效→申购": 7,
    "过会→注册生效": 63,
    "全程受理→上市": 339,
}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
})


# ============================================================
# 基础工具
# ============================================================

def search(query, count=6):
    result = subprocess.run(
        ["python3", CATCLAW, "search", query],
        capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception:
        return []


def get_quote(code):
    """腾讯API实时行情，bj前缀"""
    try:
        r = session.get(f"https://qt.gtimg.cn/q=bj{code}", timeout=10, verify=False)
        parts = r.text.split("~")
        if len(parts) < 10 or not parts[3]:
            return None
        昨收 = float(parts[4]) if parts[4] else None
        现价 = float(parts[3])
        开盘 = float(parts[5]) if parts[5] else None
        最高 = float(parts[33]) if len(parts) > 33 and parts[33] else None
        换手 = parts[38] if len(parts) > 38 else None
        成交量 = round(float(parts[36]) / 100, 2) if len(parts) > 36 and parts[36] else None
        涨幅 = round((现价 - 昨收) / 昨收 * 100, 2) if 昨收 else None
        return {
            "名称": parts[1], "代码": parts[2],
            "现价": 现价, "涨幅%": 涨幅,
            "开盘": 开盘, "最高": 最高, "昨收": 昨收,
            "换手率%": 换手, "成交量(万股)": 成交量,
            "更新": parts[30] if len(parts) > 30 else None,
        }
    except Exception as e:
        return {"error": str(e)}


def extract_code(text):
    m = re.search(r'(9200\d\d)', text)
    return m.group(1) if m else None


def extract_price(text):
    # 多种格式兼容
    patterns = [
        r'发行价格?[为是：:]\s*(\d+\.?\d*)\s*元',
        r'发行价格?[：:]\s*(\d+\.?\d*)',
        r'本次发行价格?(\d+\.?\d*)元',
        r'发行价[为是]?(\d+\.?\d*)元',
        r'[价格][为是：:\s]+(\d+\.\d+)\s*元',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            try:
                v = float(m.group(1))
                if 0.5 < v < 5000:  # 合理价格范围
                    return v
            except ValueError:
                pass
    return None


def extract_shares(text):
    """提取发行量（万股）"""
    m = re.search(r'(?:网上)?发行(?:数量|股份)?[为是：:]\s*(\d+\.?\d*)\s*万股', text)
    return float(m.group(1)) if m else None


def extract_total_sub(text):
    """提取总申购资金（亿/万亿）"""
    m = re.search(r'(?:申购资金|有效申购总量)[约大概为是：:]*\s*(\d+\.?\d*)\s*(万亿|亿|千亿)', text)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        if unit == "万亿": return val * 10000
        if unit == "千亿": return val * 1000
        return val
    # 试匹配"XXXX亿"格式
    m = re.search(r'(\d{3,5})\s*亿', text)
    if m:
        return float(m.group(1))
    return None


# ============================================================
# 核心：资金策略计算（鑫爷方法论）
# ============================================================

def calc_allocation(issue_price, net_issue_shares_wan, total_sub_billion=None):
    """
    计算最优资金分配策略
    - net_issue_shares_wan: 网上发行量（万股）
    - total_sub_billion: 总申购资金（亿元），用于估算中签率
    返回：正股门槛、碎股门槛、1+1门槛、2+1门槛、各档资金建议
    """
    net_issue = net_issue_shares_wan * 10000  # 股

    # 中签率
    if total_sub_billion and total_sub_billion > 0:
        total_sub_yuan = total_sub_billion * 1e8
        # 中签率 = 网上发行量×发行价 / 总申购金额
        cr = (net_issue * issue_price) / total_sub_yuan
    else:
        # 无数据时用2025年典型中签率0.05%
        cr = 0.0005
        total_sub_billion = net_issue * issue_price / cr / 1e8

    # 正股门槛：中100股所需资金
    # 获配股数 = 申购股数 × 中签率 ≥ 100
    # 申购股数 = 申购金额 / 发行价
    # 所以：(金额/发行价) × cr ≥ 100 → 金额 ≥ 100×发行价/cr
    zhenggu_threshold = 100 * issue_price / cr

    # 碎股门槛：约排名前1万名（行业经验值），门槛约=正股门槛×1.0~1.5
    # 近期市场数据：碎股门槛 ≈ 正股门槛 × 1.1~1.3（热门股更高）
    suigu_threshold = zhenggu_threshold * 1.15  # 保守估算

    # 1+1门槛（100股正股+100股碎股）≈ 碎股门槛附近
    one_plus_one = suigu_threshold

    # 2+1门槛（200股正股+100碎股）
    two_plus_one = zhenggu_threshold * 2 * 1.05  # 正股2手+碎股

    # 顶格（单账户上限5%网上发行量）
    top_shares = min(net_issue * 0.05, 5000000)  # 不超过500万股
    top_shares = int(top_shares / 100) * 100
    top_amount = top_shares * issue_price

    return {
        "中签率%": round(cr * 100, 4),
        "总申购资金(亿)": round(total_sub_billion, 0),
        "正股门槛(万元)": round(zhenggu_threshold / 10000, 1),
        "碎股门槛(万元)": round(suigu_threshold / 10000, 1),
        "1+1门槛(万元)": round(one_plus_one / 10000, 1),
        "2+1门槛(万元)": round(two_plus_one / 10000, 1),
        "顶格股数": int(top_shares),
        "顶格资金(万元)": round(top_amount / 10000, 1),
        "1签缴款(元)": round(issue_price * 100, 2),
    }


def print_allocation_strategy(issue_price, alloc, user_budgets=None):
    """输出资金策略建议（鑫爷风格）"""
    print(f"\n{'='*55}")
    print(f"💰 资金策略（基于鑫爷方法论）")
    print(f"{'='*55}")
    print(f"  中签率预估：{alloc['中签率%']}%  |  总申购资金：{alloc['总申购资金(亿)']}亿")
    print()
    print(f"  ⬛ 关键资金门槛：")
    print(f"  {'门槛':<15} {'资金量':<12} {'获配结果'}")
    print(f"  {'-'*45}")
    print(f"  {'正股门槛':<15} {alloc['正股门槛(万元)']}万      中100股（1手正股）")
    print(f"  {'碎股门槛':<15} {alloc['碎股门槛(万元)']}万      额外+100碎股（共200股）")
    print(f"  {'1+1门槛':<15} {alloc['1+1门槛(万元)']}万      100正股+100碎股=200股")
    print(f"  {'2+1门槛':<15} {alloc['2+1门槛(万元)']}万      200正股+100碎股=300股")
    print(f"  {'顶格':<15} {alloc['顶格资金(万元)']}万      {alloc['顶格股数']:,}股（发行量5%上限）")

    print(f"\n  📊 不同资金量建议：")
    budgets = user_budgets or [50, 100, 200, 300, 500, alloc['正股门槛(万元)'],
                                alloc['碎股门槛(万元)'], alloc['1+1门槛(万元)'],
                                alloc['2+1门槛(万元)']]
    budgets = sorted(set(budgets))

    print(f"  {'资金(万)':<10} {'申购股数':<10} {'预计获配':<15} {'建议'}")
    print(f"  {'-'*55}")
    zheng = alloc['正股门槛(万元)']
    sui = alloc['碎股门槛(万元)']
    one1 = alloc['1+1门槛(万元)']
    two1 = alloc['2+1门槛(万元)']

    for b in budgets:
        shares = int(b * 10000 / issue_price / 100) * 100
        expected_zheng = int(shares * alloc['中签率%'] / 100 / 100) * 100
        # 判断档位
        if b < 50:
            advice = "❌ 资金不足，凑分母，不建议"
            result = "大概率0股"
        elif b < zheng * 0.8:
            advice = "⚠️ 低于正股门槛，仅博碎股"
            result = f"碎股100股（不稳定）"
        elif b < zheng:
            advice = "⚠️ 接近正股门槛，可能碎股"
            result = "碎股100股"
        elif b < sui:
            advice = "✅ 超过正股门槛，稳拿1手"
            result = "100股正股"
        elif b < one1:
            advice = "✅ 碎股门槛附近，1正+碎股"
            result = "100~200股"
        elif b < two1:
            advice = "✅✅ 1+1门槛，稳拿200股"
            result = "200股（1正+1碎）"
        elif b < alloc['顶格资金(万元)']:
            advice = "✅✅ 2+1以上，优质配置"
            result = "300股+"
        else:
            advice = "🏆 顶格，最大化获配"
            result = f"{alloc['顶格股数']}股"
        print(f"  {b:<10.0f} {shares:<10,} {result:<15} {advice}")

    print(f"\n  💡 核心策略（鑫爷逻辑）：")
    print(f"  - 资金 < {zheng:.0f}万 → 只博碎股，性价比低，慎重")
    print(f"  - 资金 {zheng:.0f}~{sui:.0f}万 → 稳拿1手正股（100股）")
    print(f"  - 资金 ≈ {one1:.0f}万 → 1+1黄金档（200股），性价比最高")
    print(f"  - 分户逻辑：单账户400万 → 分2户各200万可能从200股→400股（效率翻倍）")
    print(f"  - 碎股靠时间：同档资金，8:30前越早提交碎股优先级越高")


def print_earnings_forecast(issue_price, alloc, stock_name="", pe=None, industry_pe=None):
    """三档收益预测"""
    one_lot = issue_price * 100
    print(f"\n{'='*55}")
    print(f"📐 首日收益预测（三档）")
    print(f"{'='*55}")

    # 如果有PE数据，计算理论估值
    if pe and industry_pe:
        fair_mult = industry_pe / pe
        print(f"  行业PE：{industry_pe}倍 ÷ 发行PE：{pe}倍 = 理论倍数 {fair_mult:.1f}x")
    else:
        fair_mult = 2.0

    scenarios = [
        ("悲观", max(1.3, fair_mult * 0.7), "市场情绪冷，低于理论估值"),
        ("中性", fair_mult, "达到行业PE合理估值"),
        ("乐观", fair_mult * 1.4, "高景气/资金追捧"),
    ]

    print(f"\n  {'情景':<6} {'开盘倍数':<8} {'开盘价':<10} {'1签(100股)收益':<16} {'收益率':<8} {'年化'}")
    print(f"  {'-'*60}")
    for name, mult, note in scenarios:
        open_p = round(issue_price * mult, 2)
        profit = (open_p - issue_price) * 100
        roi = profit / one_lot * 100
        ann = roi * 365 / 30
        print(f"  {name:<6} {mult:<8.1f}x {open_p:<10.2f}元 +{profit:<14.0f}元 {roi:<8.1f}% {ann:.0f}%/年")
        print(f"         ({note})")

    print(f"\n  💡 200股（1+1）收益 = 上表 ×2")
    print(f"     300股（2+1）收益 = 上表 ×3")


# ============================================================
# 流程2: 申购/上市日历（提前预警）
# ============================================================
def cmd_calendar():
    print("=== 【流程2】北交所打新日历 ===\n")
    today = datetime.date.today()
    date_str = today.strftime("%Y年%m月")
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).strftime("%Y年%m月")

    # 同时搜本月和下月，解决滞后问题
    results = search(f"北交所新股申购 920 {date_str} OR {next_month} 发行公告 上市日期", count=10)

    print(f"📅 近期北交所打新事件：\n")
    seen = set()
    for r in results:
        title = r['title']
        pub = r.get('publish_time', '')[:10]
        snippet = r.get('snippet', '')
        key = title[:20]
        if key in seen:
            continue
        seen.add(key)

        # 提取代码
        code = extract_code(title + snippet)
        # 提取申购日/上市日
        dates = re.findall(r'(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})', snippet)

        print(f"  [{pub}] {title[:60]}")
        if code:
            print(f"    代码：{code}")
        if snippet:
            print(f"    {snippet[:150]}")
        print()

    print(f"⚡ 提前获取信息技巧：")
    print(f"  - 注册批文下来后约7天公告申购 → 运行 pipeline 监控")
    print(f"  - 鑫爷/雪球实时推送比搜索更快 → 建议关注：鑫爷低风险投资（雪球）")
    print(f"  - 申购日前运行：python3 bse_pipeline.py analyze <代码>")


# ============================================================
# 流程3: 申购分析（完整版）
# ============================================================
def cmd_analyze(keyword):
    print(f"=== 【流程3】申购分析：{keyword} ===\n")

    # 搜索发行公告
    results = search(f"北交所 {keyword} 发行公告 发行价 申购 网上发行数量 2025 2026", count=8)

    issue_price = None
    issue_shares_wan = None  # 总发行量万股
    net_shares_wan = None    # 网上发行量万股
    total_sub_billion = None # 总申购资金亿
    stock_name = keyword
    stock_code = keyword if re.match(r'^9200\d\d$', keyword) else None
    pe_ratio = None
    industry_pe = None

    print("🔍 发行公告摘要：\n")
    for r in results[:4]:
        text = r.get('snippet', '') + r.get('content', '')
        title = r.get('title', '')
        pub = r.get('publish_time', '')[:10]

        # 提取数据
        if not issue_price:
            issue_price = extract_price(text)
        if not stock_code:
            stock_code = extract_code(text + title)
        if not issue_shares_wan:
            issue_shares_wan = extract_shares(text)
        # 网上发行量
        m = re.search(r'网上.*?发行.*?(\d+\.?\d*)\s*万股', text)
        if m and not net_shares_wan:
            net_shares_wan = float(m.group(1))
        # PE
        m = re.search(r'(?:发行)?[Pp][Ee][：:\s]*(\d+\.?\d*)\s*倍', text)
        if m and not pe_ratio:
            pe_ratio = float(m.group(1))
        # 总申购资金（通常在结果公告里）
        if not total_sub_billion:
            total_sub_billion = extract_total_sub(text)

        # 显示摘要
        if r.get('snippet'):
            print(f"  [{pub}] {title[:50]}")
            print(f"    {r['snippet'][:120]}")
            print()

    # 如果没有网上发行量，估算（通常网上约占总量10-20%）
    if not net_shares_wan and issue_shares_wan:
        net_shares_wan = issue_shares_wan * 0.15

    # 基本参数汇总
    print(f"\n{'='*55}")
    print(f"📊 发行参数")
    print(f"{'='*55}")
    print(f"  股票：{stock_name}  代码：{stock_code or '未确认'}")
    print(f"  发行价：{issue_price or '⚠️未找到'} 元")
    print(f"  发行PE：{pe_ratio or '未知'} 倍")
    print(f"  总发行量：{issue_shares_wan or '未知'} 万股")
    print(f"  网上发行量：{net_shares_wan or '未知'} 万股（估算）")

    if not issue_price:
        print(f"\n⚠️ 未找到发行价，请搜索确认：{keyword} 北交所发行公告")
        return

    # 如果没有总申购资金，尝试再搜一次
    if not total_sub_billion and stock_code:
        r2 = search(f"北交所 {stock_code} {stock_name} 申购资金 亿 结果公告", count=5)
        for rr in r2:
            t = rr.get('snippet', '') + rr.get('content', '')
            total_sub_billion = extract_total_sub(t)
            if total_sub_billion:
                break

    if not net_shares_wan:
        print(f"\n⚠️ 未找到网上发行量，资金门槛计算将用典型中签率(0.05%)估算")
        net_shares_wan = 200  # 默认200万股

    # 计算资金策略
    alloc = calc_allocation(issue_price, net_shares_wan, total_sub_billion)

    # 如果有总申购数据，显示说明
    if total_sub_billion:
        print(f"  总申购资金：{total_sub_billion:.0f} 亿（来自结果公告）")
    else:
        print(f"  总申购资金：未知（用典型市场均值估算，误差较大）")

    # 输出资金策略
    print_allocation_strategy(issue_price, alloc)

    # 收益预测
    print_earnings_forecast(issue_price, alloc, stock_name, pe_ratio, industry_pe)

    print(f"\n⚡ 申购建议：")
    print(f"  - 银河/中银证券 8:30 最早提交（碎股时间优先）")
    print(f"  - 国金 8:35，招商/华泰/东方/平安 8:45")
    print(f"  - 北交所全额预缴资金，冻结至中签结果（约T+2解冻）")
    print(f"  - ⚠️ 门槛数据均为估算，以官方发行结果公告为准")


# ============================================================
# 流程4: 上市提醒 + 收益预测
# ============================================================
def cmd_listing(keyword):
    print(f"=== 【流程4】上市提醒+收益预测：{keyword} ===\n")

    code = keyword if re.match(r'^9200\d\d$', keyword) else None
    issue_price = None
    stock_name = keyword
    pe_ratio = None

    # 搜索基本信息
    results = search(f"北交所 {keyword} 发行价 上市 920 申购结果", count=5)
    for r in results:
        text = r.get('snippet', '') + r.get('content', '')
        if not issue_price:
            issue_price = extract_price(text)
        if not code:
            code = extract_code(text + r.get('title', ''))
        m = re.search(r'(?:发行)?PE[：:\s]*(\d+\.?\d*)\s*倍', text)
        if m and not pe_ratio:
            pe_ratio = float(m.group(1))

    # 实时行情
    quote = None
    if code:
        quote = get_quote(code)

    print(f"📋 基本信息：")
    print(f"  股票：{stock_name}  代码：{code or '未确认'}")
    print(f"  发行价：{issue_price or '未知'} 元  |  发行PE：{pe_ratio or '未知'} 倍")

    if quote and not quote.get("error"):
        print(f"\n📈 实时行情（{quote.get('更新', '')}）：")
        现价 = quote['现价']
        开盘 = quote.get('开盘')
        最高 = quote.get('最高')
        换手 = quote.get('换手率%')
        成交量 = quote.get('成交量(万股)')

        print(f"  现价：{现价}元  涨幅：{quote.get('涨幅%')}%")
        if 开盘:
            print(f"  开盘：{开盘}元", end="")
            if issue_price:
                print(f"  开盘涨幅：+{(开盘-issue_price)/issue_price*100:.1f}%")
            else:
                print()
        if 最高:
            print(f"  最高：{最高}元", end="")
            if issue_price:
                print(f"  最高涨幅：+{(最高-issue_price)/issue_price*100:.1f}%")
            else:
                print()
        print(f"  换手率：{换手}%  成交量：{成交量}万股")

        # SOP判断
        print(f"\n🎯 SOP判断：")
        try:
            t = float(换手)
            if t < 20:
                print(f"  换手率 {t}% < 20% → 开盘即高点型 → 立刻全卖")
            elif t < 40:
                if 最高 and 现价 and 最高 > 现价 * 1.05:
                    print(f"  换手率 {t}%，价格已从高点回落 → 出货信号，考虑卖出")
                else:
                    print(f"  换手率 {t}%，20-40%区间 → 观察量价关系，暂持")
            elif t < 60:
                print(f"  换手率 {t}%，高换手区间 → 重点观察价格是否还在涨")
                print(f"  量增价升 → 持有；量增价滞/价跌 → 立刻卖！")
            else:
                print(f"  换手率 {t}% > 60%，极高换手 → 需量价配合判断")
        except (TypeError, ValueError):
            print(f"  换手率数据获取失败，请手动判断")

    elif quote and quote.get("error"):
        print(f"\n  ⚠️ 行情获取失败：{quote['error']}")
    else:
        print(f"\n  暂无实时行情（可能未开盘或代码有误）")

    # 收益预测（上市前使用）
    if issue_price:
        print_earnings_forecast(issue_price, {}, stock_name, pe_ratio)
    
    print(f"\n📋 首日SOP完整版：")
    print(f"  换手<20% → 全卖")
    print(f"  换手20-40% + 价格涨 → 观察，不急")
    print(f"  量增价升（换手飙+价格新高）→ 持有")
    print(f"  量增价滞/价跌（量价背离）→ ⚡立刻卖")
    print(f"  换手>50%+价格停涨 → 分批卖")


# ============================================================
# 流程5: 复盘记录
# ============================================================
def cmd_review(keyword):
    print(f"=== 【流程5】复盘记录：{keyword} ===\n")

    code = keyword if re.match(r'^9200\d\d$', keyword) else None
    stock_name = keyword
    issue_price = None

    results = search(f"北交所 {keyword} 发行价 上市 首日", count=3)
    for r in results:
        text = r.get('snippet', '') + r.get('content', '')
        if not issue_price:
            issue_price = extract_price(text)
        if not code:
            code = extract_code(text + r.get('title', ''))

    # 实时行情
    quote = get_quote(code) if code else None

    if quote and not quote.get("error"):
        print("📈 当前行情快照：")
        for k, v in quote.items():
            print(f"  {k}: {v}")

    today = datetime.date.today().strftime("%Y-%m-%d")
    template = f"""
---
### {stock_name}（{code or '代码未知'}）上市日复盘

- **发行价**：{issue_price or '_待填_'} 元
- **上市日**：{today}
- **开盘价**：_待填_ 元（涨幅：_待填_%）
- **最高价**：_待填_ 元（涨幅：_待填_%，时间：_待填_）
- **实际卖出均价**：_待填_ 元
- **开盘换手率**：_待填_%
- **卖出时换手率**：_待填_%
- **走势形态**：□ 开盘即高点  □ 开盘后持续拉升  □ 震荡  □ 高开低走

**操作方式**：□ 开盘全卖  □ 持有等高点  □ 分批卖

**SOP执行情况**：□ 完全按SOP  □ 有偏差（原因：_待填_）

**每签实际收益**：_待填_ 元/签 × _待填_ 签 = **_待填_ 元**

**最优收益（如果按最高点卖）**：_待填_ 元

**错失收益**：_待填_ 元

**复盘结论**：
_待填_

**下次改进点**：
_待填_
"""
    print("📝 复盘模板：")
    print(template)

    ans = input("自动写入 ipo-strategy.md？(y/N): ").strip().lower()
    if ans == 'y':
        with open(STRATEGY_FILE, 'a', encoding='utf-8') as f:
            f.write(template)
        print(f"✅ 已写入 {STRATEGY_FILE}")


# ============================================================
# 实时行情
# ============================================================
def cmd_quote(keyword):
    code = keyword if re.match(r'^\d+$', keyword) else None
    if not code:
        results = search(f"北交所 {keyword} 920 证券代码", count=3)
        for r in results:
            code = extract_code(r.get('snippet', '') + r.get('title', ''))
            if code:
                break
    if not code:
        print(f"未找到代码：{keyword}")
        return
    q = get_quote(code)
    if not q:
        print("暂无数据")
    elif q.get("error"):
        print(f"错误：{q['error']}")
    else:
        print(f"📈 bj{code} 实时行情：")
        for k, v in q.items():
            print(f"  {k}: {v}")


# ============================================================
# 流程1: 排队预估
# ============================================================
def cmd_pipeline():
    print("=== 【流程1】北交所IPO排队 & 注册批文预估 ===\n")
    results = search("北交所新股 注册生效 过会 2025 2026 申购 上市时间", count=8)
    print("📋 近期注册/过会动态：\n")
    for r in results[:6]:
        print(f"  [{r.get('publish_time','')[:10]}] {r['title']}")
        if r.get('snippet'):
            print(f"    {r['snippet'][:120]}")
        print()
    print("📊 时间线均值（2025年）：")
    for k, v in PIPELINE_DAYS.items():
        print(f"  {k}：{v}天")
    print("\n  注册生效 → 预计7天后申购，31天后上市")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    dispatch = {
        "pipeline": lambda: cmd_pipeline(),
        "calendar": lambda: cmd_calendar(),
        "analyze":  lambda: cmd_analyze(arg) if arg else print("用法: analyze <代码/名称>"),
        "listing":  lambda: cmd_listing(arg) if arg else print("用法: listing <代码>"),
        "review":   lambda: cmd_review(arg) if arg else print("用法: review <代码>"),
        "quote":    lambda: cmd_quote(arg) if arg else print("用法: quote <代码>"),
    }

    if cmd in dispatch:
        dispatch[cmd]()
    else:
        print(f"未知命令：{cmd}")
        print(__doc__)
        sys.exit(1)
