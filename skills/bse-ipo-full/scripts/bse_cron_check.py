#!/usr/bin/env python3
"""
北交所打新日历 Cron 检查脚本（零 token 版）
用途：每天10:00由 cron 直接调用，不经过 AI。
- 有近7天内申购/上市事件 → 写入 /tmp/bse_events.json → 调 openclaw message 发大象通知
- 无事件 → 静默退出，不发任何消息
"""

import subprocess, requests, json, datetime, sys, os, re, warnings
warnings.filterwarnings("ignore")

CATCLAW = "/app/skills/catclaw-search/scripts/catclaw_search.py"
OUTPUT_FILE = "/tmp/bse_events.json"
DAXIANG_UID = "2369102735"  # 郭蕾萍大象 UID

# ============================================================
# 搜索北交所近期打新事件
# ============================================================

def search(query, count=6):
    result = subprocess.run(
        ["python3", CATCLAW, "search", query, f"--count={count}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception:
        return []


def extract_events_from_results(results):
    """从搜索结果中提取近7天内的打新事件"""
    events = []
    today = datetime.date.today()
    window_end = today + datetime.timedelta(days=7)

    # 常见日期格式
    date_patterns = [
        r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})',
        r'(\d{2})[-/](\d{1,2})[-/](\d{1,2})',
    ]

    # 关键词
    keywords = ['申购', '认购', '上市', '发行', '打新', '新股', '920']

    for r in results:
        text = (r.get('title', '') + ' ' + r.get('snippet', '') + ' ' + r.get('description', ''))
        if not any(k in text for k in keywords):
            continue

        # 提取股票代码
        code_match = re.search(r'9[012]\d{4}', text)
        code = code_match.group() if code_match else ''

        # 提取日期
        found_date = None
        for pat in date_patterns:
            m = re.search(pat, text)
            if m:
                try:
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    if y < 100:
                        y += 2000
                    candidate = datetime.date(y, mo, d)
                    if today <= candidate <= window_end:
                        found_date = candidate
                        break
                except Exception:
                    continue

        if found_date or code:
            events.append({
                'title': r.get('title', '')[:60],
                'code': code,
                'date': found_date.isoformat() if found_date else '',
                'snippet': r.get('snippet', '')[:120],
                'url': r.get('url', ''),
            })

    # 去重（按 code+date）
    seen = set()
    deduped = []
    for e in events:
        key = (e['code'], e['date'])
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    return deduped


def check_bse_calendar():
    today = datetime.date.today()
    this_month = today.strftime("%Y年%m月")
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).strftime("%Y年%m月")

    queries = [
        f"北交所新股申购 {this_month}",
        f"北交所新股申购 {next_month}",
        f"北交所新股上市 {this_month}",
        f"北交所 920 申购日期 近期",
    ]

    all_results = []
    for q in queries:
        all_results.extend(search(q, count=5))

    events = extract_events_from_results(all_results)
    return events


# ============================================================
# 发大象通知（直接用 openclaw message CLI）
# ============================================================

def send_daxiang(msg):
    """用 openclaw message 发大象消息"""
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "daxiang",
         "--target", DAXIANG_UID, "--message", msg],
        capture_output=True, text=True, timeout=15
    )
    return result.returncode == 0


def format_events_message(events):
    today = datetime.date.today()
    lines = [f"🔔 **北交所打新提醒** ({today.strftime('%m/%d')})\n"]

    # 按日期排序
    events_with_date = [e for e in events if e['date']]
    events_no_date = [e for e in events if not e['date']]
    events_sorted = sorted(events_with_date, key=lambda x: x['date']) + events_no_date

    for e in events_sorted[:5]:  # 最多展示5条
        date_str = e['date'] or '待确认'
        code_str = f" [{e['code']}]" if e['code'] else ''
        lines.append(f"📅 {date_str}{code_str} — {e['title'][:40]}")
        if e['snippet']:
            lines.append(f"   {e['snippet'][:80]}")

    lines.append("\n发 `analyze <代码>` 获取完整申购分析")
    return '\n'.join(lines)


# ============================================================
# 主流程
# ============================================================

def main():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 开始检查北交所打新日历...")

    events = check_bse_calendar()

    if not events:
        print("✅ 近7天无北交所打新事件，静默退出")
        # 写空结果供调试
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({'checked_at': datetime.datetime.now().isoformat(), 'events': []}, f, ensure_ascii=False)
        sys.exit(0)

    # 有事件
    print(f"📢 发现 {len(events)} 个打新事件，准备发送大象通知")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            'checked_at': datetime.datetime.now().isoformat(),
            'events': events
        }, f, ensure_ascii=False, indent=2)

    msg = format_events_message(events)
    print("消息内容：")
    print(msg)

    ok = send_daxiang(msg)
    if ok:
        print("✅ 大象通知已发送")
    else:
        print("❌ 大象通知发送失败，结果已写入 /tmp/bse_events.json")
        sys.exit(1)


if __name__ == '__main__':
    main()
