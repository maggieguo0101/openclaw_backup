#!/usr/bin/env python3
"""
Token 消耗看板
从 OpenClaw session 日志中提取 token 使用数据，生成可视化看板图片
"""

import json
import glob
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

# ----------- 数据提取 -----------

def load_token_data():
    """从所有 session jsonl 文件中提取 token 数据"""
    files = glob.glob('/root/.openclaw/agents/main/sessions/*.jsonl')
    
    daily = defaultdict(lambda: {
        'input': 0, 'output': 0, 'cache_read': 0, 'cache_write': 0, 'total': 0, 'turns': 0
    })
    
    for f in files:
        try:
            with open(f) as fp:
                for line in fp:
                    try:
                        d = json.loads(line)
                        if d.get('type') != 'message':
                            continue
                        msg = d.get('message', {})
                        if msg.get('role') != 'assistant':
                            continue
                        usage = msg.get('usage', {})
                        if not usage:
                            continue
                        
                        ts = d.get('timestamp', '')
                        if not ts:
                            continue
                        # 转北京时间
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        date_key = (dt.astimezone(timezone.utc).strftime('%Y-%m-%d'))
                        # 换算为北京时间日期（+8h）
                        from datetime import timedelta
                        bj_dt = dt + timedelta(hours=8)
                        date_key = bj_dt.strftime('%Y-%m-%d')
                        
                        inp = usage.get('input', 0) or 0
                        out = usage.get('output', 0) or 0
                        cache_r = usage.get('cacheRead', 0) or 0
                        cache_w = usage.get('cacheWrite', 0) or 0
                        total = usage.get('totalTokens', 0) or (inp + out + cache_r + cache_w)
                        
                        daily[date_key]['input'] += inp
                        daily[date_key]['output'] += out
                        daily[date_key]['cache_read'] += cache_r
                        daily[date_key]['cache_write'] += cache_w
                        daily[date_key]['total'] += total
                        daily[date_key]['turns'] += 1
                        
                    except Exception:
                        pass
        except Exception:
            pass
    
    return dict(sorted(daily.items()))


# ----------- 看板生成 -----------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Token 消耗看板</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
    background: #0f0f1a;
    color: #e0e0e0;
    padding: 32px 28px 40px;
    min-width: 820px;
  }}
  
  /* 标题栏 */
  .header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
  }}
  .title {{
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .title .emoji {{ font-size: 26px; }}
  .subtitle {{
    font-size: 13px;
    color: #666;
    margin-top: 3px;
  }}
  .update-time {{
    font-size: 12px;
    color: #555;
  }}
  
  /* 汇总卡片 */
  .summary-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 28px;
  }}
  .card {{
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 18px 20px;
  }}
  .card-label {{
    font-size: 12px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }}
  .card-value {{
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
  }}
  .card-unit {{
    font-size: 13px;
    color: #666;
    margin-top: 4px;
  }}
  .card.accent-blue {{ border-color: #3b82f6; }}
  .card.accent-purple {{ border-color: #8b5cf6; }}
  .card.accent-green {{ border-color: #10b981; }}
  .card.accent-orange {{ border-color: #f59e0b; }}
  .card.accent-blue .card-value {{ color: #60a5fa; }}
  .card.accent-purple .card-value {{ color: #a78bfa; }}
  .card.accent-green .card-value {{ color: #34d399; }}
  .card.accent-orange .card-value {{ color: #fbbf24; }}
  
  /* 图表区 */
  .chart-section {{
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 22px 24px;
    margin-bottom: 20px;
  }}
  .section-title {{
    font-size: 14px;
    font-weight: 600;
    color: #ccc;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  
  /* 柱状图 */
  .bar-chart {{
    display: flex;
    align-items: flex-end;
    gap: 10px;
    height: 160px;
  }}
  .bar-item {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    height: 100%;
    justify-content: flex-end;
  }}
  .bar-value-label {{
    font-size: 10px;
    color: #888;
    white-space: nowrap;
  }}
  .bar-stack {{
    width: 100%;
    border-radius: 4px 4px 0 0;
    min-height: 2px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    overflow: hidden;
  }}
  .bar-seg-cache {{ background: #2d4a7a; }}
  .bar-seg-input {{ background: #3b82f6; }}
  .bar-seg-output {{ background: #8b5cf6; }}
  .bar-date {{
    font-size: 10px;
    color: #666;
    writing-mode: horizontal-tb;
    text-align: center;
    margin-top: 4px;
  }}
  .bar-date.today {{ color: #60a5fa; font-weight: 600; }}
  
  /* 图例 */
  .legend {{
    display: flex;
    gap: 16px;
    margin-top: 14px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #888;
  }}
  .legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
  }}
  
  /* 明细表 */
  .table-section {{
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    border-radius: 12px;
    padding: 22px 24px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  th {{
    text-align: left;
    color: #666;
    font-weight: 500;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 0 0 10px 0;
    border-bottom: 1px solid #2a2a45;
  }}
  th:not(:first-child), td:not(:first-child) {{
    text-align: right;
  }}
  td {{
    padding: 9px 0;
    border-bottom: 1px solid #1e1e35;
    color: #ccc;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr.today-row td {{ color: #60a5fa; font-weight: 600; }}
  .total-row td {{
    border-top: 1px solid #3a3a5a;
    padding-top: 12px;
    color: #fff;
    font-weight: 600;
  }}
  .num {{ font-variant-numeric: tabular-nums; }}
  
  /* 缓存命中率 */
  .hit-rate {{ color: #34d399 !important; font-size: 11px; }}
  .hit-rate-low {{ color: #f59e0b !important; font-size: 11px; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="title"><span class="emoji">🦞</span> Token 消耗看板</div>
    <div class="subtitle">OpenClaw · {model} · 数据从 {start_date} 起</div>
  </div>
  <div class="update-time">更新于 {update_time}</div>
</div>

<!-- 汇总卡片 -->
<div class="summary-grid">
  <div class="card accent-blue">
    <div class="card-label">累计总 Token</div>
    <div class="card-value">{total_all_fmt}</div>
    <div class="card-unit">tokens（含缓存）</div>
  </div>
  <div class="card accent-purple">
    <div class="card-label">累计 Output</div>
    <div class="card-value">{total_output_fmt}</div>
    <div class="card-unit">生成 tokens</div>
  </div>
  <div class="card accent-green">
    <div class="card-label">累计缓存命中</div>
    <div class="card-value">{cache_hit_rate}%</div>
    <div class="card-unit">缓存节省 {cache_saved_fmt} tokens</div>
  </div>
  <div class="card accent-orange">
    <div class="card-label">今日对话轮次</div>
    <div class="card-value">{today_turns}</div>
    <div class="card-unit">今日 total {today_total_fmt}</div>
  </div>
</div>

<!-- 柱状图 -->
<div class="chart-section">
  <div class="section-title">📊 每日 Token 消耗（最近10天）</div>
  <div class="bar-chart">
    {bars_html}
  </div>
  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#8b5cf6"></div>Output</div>
    <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div>Input</div>
    <div class="legend-item"><div class="legend-dot" style="background:#2d4a7a"></div>Cache Read</div>
  </div>
</div>

<!-- 明细表 -->
<div class="table-section">
  <div class="section-title">📋 每日明细</div>
  <table>
    <thead>
      <tr>
        <th>日期</th>
        <th>轮次</th>
        <th>Input</th>
        <th>Output</th>
        <th>Cache Read</th>
        <th>Total</th>
        <th>缓存命中率</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
    <tfoot>
      {total_row_html}
    </tfoot>
  </table>
</div>

</body>
</html>
"""


def fmt_num(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_num_full(n):
    return f"{n:,}"


def generate_dashboard(daily_data, output_path):
    from datetime import datetime, timedelta
    
    today = datetime.now(timezone.utc) + timedelta(hours=8)
    today_str = today.strftime('%Y-%m-%d')
    
    dates = sorted(daily_data.keys())[-10:]  # 最近10天
    
    # 汇总
    all_dates = sorted(daily_data.keys())
    total_input = sum(v['input'] for v in daily_data.values())
    total_output = sum(v['output'] for v in daily_data.values())
    total_cache_r = sum(v['cache_read'] for v in daily_data.values())
    total_cache_w = sum(v['cache_write'] for v in daily_data.values())
    total_all = sum(v['total'] for v in daily_data.values())
    total_turns = sum(v['turns'] for v in daily_data.values())
    
    cache_hit_rate = round(total_cache_r / total_all * 100) if total_all > 0 else 0
    cache_saved = total_cache_r
    
    today_data = daily_data.get(today_str, {})
    today_turns = today_data.get('turns', 0)
    today_total = today_data.get('total', 0)
    
    start_date = all_dates[0] if all_dates else today_str
    
    # 柱状图
    max_val = max((v['total'] for v in [daily_data[d] for d in dates]), default=1)
    bars = []
    for d in dates:
        v = daily_data[d]
        t = v['total'] or 1
        pct = t / max_val
        bar_h = int(pct * 130)
        
        # 按比例拆分高度
        cache_h = int(bar_h * (v['cache_read'] / t))
        input_h = int(bar_h * (v['input'] / t))
        output_h = bar_h - cache_h - input_h
        
        is_today = d == today_str
        date_label = d[5:]  # MM-DD
        
        bars.append(f"""
        <div class="bar-item">
          <div class="bar-value-label">{fmt_num(t)}</div>
          <div class="bar-stack" style="height:{bar_h}px">
            <div class="bar-seg-output" style="height:{max(output_h,1)}px"></div>
            <div class="bar-seg-input" style="height:{max(input_h,1)}px"></div>
            <div class="bar-seg-cache" style="height:{max(cache_h,1)}px"></div>
          </div>
          <div class="bar-date {'today' if is_today else ''}">{date_label}{'▲' if is_today else ''}</div>
        </div>
        """)
    
    bars_html = '\n'.join(bars)
    
    # 明细表行
    rows = []
    for d in sorted(daily_data.keys()):
        v = daily_data[d]
        t = v['total']
        cr = v['cache_read']
        hit = round(cr / t * 100) if t > 0 else 0
        hit_class = 'hit-rate' if hit >= 80 else 'hit-rate-low'
        is_today = d == today_str
        row_class = 'today-row' if is_today else ''
        today_mark = ' 🔸' if is_today else ''
        rows.append(f"""
        <tr class="{row_class}">
          <td>{d}{today_mark}</td>
          <td class="num">{v['turns']}</td>
          <td class="num">{fmt_num_full(v['input'])}</td>
          <td class="num">{fmt_num_full(v['output'])}</td>
          <td class="num">{fmt_num_full(cr)}</td>
          <td class="num">{fmt_num_full(t)}</td>
          <td class="{hit_class}">{hit}%</td>
        </tr>
        """)
    
    rows_html = '\n'.join(rows)
    
    overall_hit = round(total_cache_r / total_all * 100) if total_all > 0 else 0
    total_row_html = f"""
    <tr class="total-row">
      <td>合计</td>
      <td class="num">{total_turns}</td>
      <td class="num">{fmt_num_full(total_input)}</td>
      <td class="num">{fmt_num_full(total_output)}</td>
      <td class="num">{fmt_num_full(total_cache_r)}</td>
      <td class="num">{fmt_num_full(total_all)}</td>
      <td class="hit-rate">{overall_hit}%</td>
    </tr>
    """
    
    html = HTML_TEMPLATE.format(
        model='catclaw-proxy-model',
        start_date=start_date,
        update_time=today.strftime('%Y-%m-%d %H:%M'),
        total_all_fmt=fmt_num(total_all),
        total_output_fmt=fmt_num(total_output),
        cache_hit_rate=cache_hit_rate,
        cache_saved_fmt=fmt_num(cache_saved),
        today_turns=today_turns,
        today_total_fmt=fmt_num(today_total),
        bars_html=bars_html,
        rows_html=rows_html,
        total_row_html=total_row_html,
    )
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return html


if __name__ == '__main__':
    print("📊 正在提取 token 数据...")
    data = load_token_data()
    print(f"✅ 找到 {len(data)} 天的数据")
    for d, v in sorted(data.items()):
        print(f"  {d}: total={v['total']:,}  in={v['input']:,}  out={v['output']:,}  cache={v['cache_read']:,}  turns={v['turns']}")
    
    output = '/root/.openclaw/workspace/token_dashboard.html'
    generate_dashboard(data, output)
    print(f"\n✅ 看板已生成: {output}")
