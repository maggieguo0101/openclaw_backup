#!/usr/bin/env python3
"""
北交所上市提醒卡片生成器
输入：股票代码（如 920055）
输出：HTML 渲染图片，上传 S3Plus，返回链接
"""
import sys, os, json, subprocess, requests, re, datetime, warnings, tempfile
warnings.filterwarnings("ignore")

CATCLAW = "/app/skills/catclaw-search/scripts/catclaw_search.py"
S3_UPLOAD = "/root/.openclaw-init/skills/s3plus-upload/scripts/upload_to_s3plus.py"

def search(query, count=6):
    r = subprocess.run(["python3", CATCLAW, "search", query, f"--count={count}"],
                       capture_output=True, text=True, timeout=30)
    try:
        return json.loads(r.stdout).get("results", [])
    except:
        return []

def get_quote(code):
    try:
        r = requests.get(f"https://qt.gtimg.cn/q=bj{code}", timeout=8, verify=False)
        parts = r.text.split("~")
        if len(parts) < 10 or not parts[3]:
            return {}
        yest = float(parts[4]) if parts[4] else None
        cur = float(parts[3])
        return {
            "name": parts[1], "cur": cur, "yest": yest,
            "open": float(parts[5]) if parts[5] else None,
            "high": float(parts[33]) if len(parts) > 33 and parts[33] else None,
            "turnover": parts[38] if len(parts) > 38 else "—",
            "vol_wan": round(float(parts[36]) / 100, 1) if len(parts) > 36 and parts[36] else None,
            "pct": round((cur - yest) / yest * 100, 2) if yest else None,
        }
    except:
        return {}

def get_eastmoney_info(code):
    """从东财获取发行价、上市日期等基础数据"""
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://data.eastmoney.com/"})
        params = {
            "reportName": "RPTA_APP_IPOAPPLY", "columns": "ALL",
            "pageNumber": 1, "pageSize": 50,
            "sortTypes": -1, "sortColumns": "APPLY_DATE",
            "source": "WEB", "client": "WEB",
        }
        r = session.get("https://datacenter-web.eastmoney.com/api/data/v1/get",
                        params=params, timeout=12, verify=False)
        items = (r.json().get("result") or {}).get("data") or []
        for item in items:
            if item.get("SECURITY_CODE") == code:
                return {
                    "name": item.get("SECURITY_NAME_ABBR", ""),
                    "issue_price": float(item.get("ISSUE_PRICE") or 0),
                    "apply_date": (item.get("APPLY_DATE") or "")[:10],
                    "listing_date": (item.get("LISTING_DATE") or "")[:10],
                    "pe": item.get("AFTER_ISSUE_PE"),
                    "online_apply_upper": item.get("ONLINE_APPLY_UPPER"),
                    "issue_num": item.get("TOTAL_ISSUE_NUM"),
                    "online_issue_num": item.get("ONLINE_ISSUE_NUM"),
                }
    except:
        pass
    return {}

def get_fundamentals(code, name):
    """搜索基本面：行业、营收、净利润"""
    results = search(f"北交所 {name} {code} 基本面 营收 净利润 行业 主营业务 2024 2025", count=6)
    text = " ".join([r.get("snippet", "") + r.get("title", "") for r in results])

    industry = "—"
    revenue = "—"
    net_profit = "—"
    biz = "—"

    # 行业
    m = re.search(r'(?:所属行业|行业)[：:\s]*([^\s，,。]{2,12})', text)
    if m: industry = m.group(1).strip()

    # 营收
    m = re.search(r'(?:营业收入|总营收)[约为是：:\s]*(\d+\.?\d*)\s*(亿|万)', text)
    if m: revenue = m.group(1) + m.group(2) + "元"

    # 净利润
    m = re.search(r'(?:净利润|归母净利润)[约为是：:\s]*(\d+\.?\d*)\s*(亿|万)', text)
    if m: net_profit = m.group(1) + m.group(2) + "元"

    # 主营
    m = re.search(r'(?:主营业务|主要从事)[：:\s]*([^。，\n]{5,40})', text)
    if m: biz = m.group(1).strip()

    return {"industry": industry, "revenue": revenue, "net_profit": net_profit, "biz": biz}

def calc_earnings(issue_price, scenarios=None):
    """计算三档收益预测（100股/200股）"""
    if not scenarios:
        scenarios = [
            ("😐 悲观", 1.3, "市场冷淡，低开"),
            ("📊 中性", 2.0, "正常估值回归"),
            ("🚀 乐观", 3.0, "资金热捧"),
        ]
    result = []
    for label, mult, note in scenarios:
        open_p = round(issue_price * mult, 2)
        p100 = round((open_p - issue_price) * 100, 0)
        p200 = p100 * 2
        roi = round(p100 / (issue_price * 100) * 100, 1)
        result.append({
            "label": label, "mult": mult, "open_p": open_p,
            "p100": int(p100), "p200": int(p200), "roi": roi, "note": note
        })
    return result

def gen_sop_tips(issue_price):
    return [
        "开盘换手率 <5% → 全卖，不留仓",
        "开盘换手率 5~20% → 先卖50%，观察量价",
        "量增价升持续 → 等换手率到峰值再出",
        "量增价滞 / 价回落 → 立刻清仓",
        f"止损线：跌回发行价 {issue_price} 元以下立刻卖",
    ]

def render_html(data):
    code = data["code"]
    name = data["name"]
    issue_price = data["issue_price"]
    listing_date = data["listing_date"]
    apply_date = data["apply_date"]
    pe = data.get("pe") or "—"
    fund = data["fund"]
    earnings = data["earnings"]
    sop = data["sop"]
    today = datetime.date.today().strftime("%m/%d")

    # 颜色方案
    BG = "#0d1117"
    CARD = "#161b22"
    ACCENT = "#f0883e"
    GREEN = "#3fb950"
    RED = "#f85149"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    BORDER = "#30363d"

    earnings_rows = ""
    for e in earnings:
        color = RED if e["mult"] <= 1.5 else (GREEN if e["mult"] >= 2.5 else "#d2a679")
        earnings_rows += f"""
        <tr>
          <td style="color:{color};font-weight:600">{e['label']}</td>
          <td>{e['mult']}x</td>
          <td style="font-weight:700">{e['open_p']:.2f}元</td>
          <td style="color:{GREEN};font-weight:700">+{e['p100']:,}元</td>
          <td style="color:{GREEN}">+{e['p200']:,}元</td>
          <td style="color:{MUTED}">{e['roi']}%</td>
        </tr>"""

    sop_items = "".join([f"<li>{s}</li>" for s in sop])

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:{BG}; color:{TEXT}; font-family:'PingFang SC','Helvetica Neue',Arial,sans-serif;
         padding:24px; width:680px; }}
  .header {{ background:linear-gradient(135deg,#1a2332,#0d1117);
             border:1px solid {BORDER}; border-radius:12px; padding:20px 24px; margin-bottom:16px; }}
  .badge {{ display:inline-block; background:{ACCENT}; color:#000; font-size:11px;
            font-weight:700; padding:2px 8px; border-radius:4px; margin-bottom:8px; }}
  .title {{ font-size:26px; font-weight:700; color:{TEXT}; }}
  .subtitle {{ color:{MUTED}; font-size:13px; margin-top:4px; }}
  .card {{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
           padding:16px 20px; margin-bottom:12px; }}
  .card-title {{ font-size:12px; color:{MUTED}; text-transform:uppercase;
                 letter-spacing:0.5px; margin-bottom:12px; font-weight:600; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
  .info-item label {{ font-size:11px; color:{MUTED}; display:block; margin-bottom:2px; }}
  .info-item value {{ font-size:15px; font-weight:600; color:{TEXT}; }}
  .info-item .big {{ font-size:20px; color:{ACCENT}; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ color:{MUTED}; font-size:11px; text-align:left; padding:4px 8px;
        border-bottom:1px solid {BORDER}; }}
  td {{ padding:7px 8px; border-bottom:1px solid {BORDER}; color:{TEXT}; }}
  tr:last-child td {{ border-bottom:none; }}
  .sop-list {{ list-style:none; }}
  .sop-list li {{ font-size:13px; color:{TEXT}; padding:5px 0;
                  border-bottom:1px solid {BORDER}; padding-left:16px; position:relative; }}
  .sop-list li:before {{ content:"▶"; color:{ACCENT}; position:absolute; left:0; font-size:10px; top:6px; }}
  .sop-list li:last-child {{ border-bottom:none; }}
  .footer {{ text-align:center; color:{MUTED}; font-size:11px; margin-top:8px; }}
</style></head><body>

<div class="header">
  <div class="badge">🔔 北交所上市提醒</div>
  <div class="title">{name} <span style="font-size:16px;color:{MUTED}">({code})</span></div>
  <div class="subtitle">申购日 {apply_date} &nbsp;→&nbsp; <span style="color:{ACCENT};font-weight:600">上市日 {listing_date}</span> &nbsp;|&nbsp; 生成于 {today}</div>
</div>

<div class="card">
  <div class="card-title">📊 发行基本参数</div>
  <div class="info-grid">
    <div class="info-item"><label>发行价</label><value class="big">{issue_price:.2f}<span style="font-size:14px;color:{MUTED}">元</span></value></div>
    <div class="info-item"><label>发行PE</label><value>{pe}倍</value></div>
    <div class="info-item"><label>行业</label><value>{fund['industry']}</value></div>
    <div class="info-item"><label>主营业务</label><value style="font-size:13px">{fund['biz'][:20]}</value></div>
    <div class="info-item"><label>营收（近期）</label><value>{fund['revenue']}</value></div>
    <div class="info-item"><label>净利润（近期）</label><value>{fund['net_profit']}</value></div>
  </div>
</div>

<div class="card">
  <div class="card-title">💰 首日收益预测</div>
  <table>
    <thead><tr>
      <th>情景</th><th>开盘倍数</th><th>预估开盘价</th>
      <th>100股收益</th><th>200股收益</th><th>收益率</th>
    </tr></thead>
    <tbody>{earnings_rows}</tbody>
  </table>
  <div style="font-size:11px;color:{MUTED};margin-top:8px">* 倍数 = 开盘价÷发行价，仅供参考</div>
</div>

<div class="card">
  <div class="card-title">⚡ 上市日卖出 SOP</div>
  <ul class="sop-list">{sop_items}</ul>
</div>

<div class="footer">小爪 · 北交所打新系统 · 数据来源：东财/腾讯行情 · 仅供参考，不构成投资建议</div>
</body></html>"""
    return html

def upload_to_s3(filepath):
    r = subprocess.run(
        ["python3", S3_UPLOAD, "--env", "prod-corp", "--file", filepath],
        capture_output=True, text=True, timeout=30
    )
    # 提取 URL
    m = re.search(r'https://[^\s"\']+', r.stdout)
    return m.group(0) if m else None

def main(code):
    print(f"[1/5] 获取东财基础数据: {code}")
    em = get_eastmoney_info(code)

    name = em.get("name") or code
    issue_price = em.get("issue_price") or 0
    listing_date = em.get("listing_date") or "待确认"
    apply_date = em.get("apply_date") or "—"
    pe = em.get("pe")

    if not issue_price:
        print(f"⚠️ 东财未找到发行价，尝试搜索...")
        results = search(f"北交所 {code} 发行价 申购公告", count=5)
        for r in results:
            text = r.get("snippet","") + r.get("title","")
            m = re.search(r'发行价[格]?[为是：:\s]*(\d+\.?\d*)\s*元', text)
            if m:
                issue_price = float(m.group(1))
                break

    if not issue_price:
        print(f"❌ 无法获取发行价，退出")
        sys.exit(1)

    print(f"[2/5] 搜索基本面: {name}")
    fund = get_fundamentals(code, name)

    print(f"[3/5] 计算收益预测: 发行价={issue_price}")
    earnings = calc_earnings(issue_price)
    sop = gen_sop_tips(issue_price)

    print(f"[4/5] 渲染卡片...")
    data = {
        "code": code, "name": name,
        "issue_price": issue_price, "listing_date": listing_date,
        "apply_date": apply_date, "pe": pe,
        "fund": fund, "earnings": earnings, "sop": sop,
    }
    html = render_html(data)

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html)
        html_path = f.name

    # 用 playwright 截图
    img_path = html_path.replace(".html", ".png")
    r = subprocess.run(
        ["python3", "-c", f"""
import asyncio
from playwright.async_api import async_playwright
async def shot():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={{'width':680,'height':900}})
        await page.goto('file://{html_path}')
        await page.wait_for_timeout(500)
        await page.screenshot(path='{img_path}', full_page=True)
        await b.close()
asyncio.run(shot())
"""],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0:
        print(f"截图失败: {r.stderr[:200]}")
        sys.exit(1)

    print(f"[5/5] 上传 S3Plus...")
    url = upload_to_s3(img_path)

    # 清理
    os.unlink(html_path)
    os.unlink(img_path)

    if url:
        print(f"✅ 卡片已生成：{url}")
        # 同时输出结构化摘要供 AI 使用
        print(f"SUMMARY:{name}({code}) 发行价{issue_price}元 上市日{listing_date} 行业:{fund['industry']}")
    else:
        print("❌ S3上传失败")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 gen_listing_card.py <股票代码>")
        sys.exit(1)
    main(sys.argv[1])
