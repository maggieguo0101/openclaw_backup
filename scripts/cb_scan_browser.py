#!/usr/bin/env python3
"""
可转债折价/双低扫描 - 通过搜索引擎获取实时数据
适用于无法直接访问东方财富API的沙箱环境
"""

import subprocess
import json
import re
import sys
from datetime import datetime

def search_cb_data(query, engine="bing", limit=5):
    """通过catclaw搜索获取可转债数据"""
    cmd = [
        "python3", "/app/skills/catclaw-search/scripts/catclaw_search.py",
        "search", query,
        "-s", engine,
        "-n", str(limit),
        "--no-fast", "--timeout", "20"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"搜索失败: {e}")
        return None

def scan_discount():
    """扫描折价转债信息"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 搜索最新折价/负溢价数据
    queries = [
        f"可转债 负溢价 折价 套利 {datetime.now().strftime('%Y年%m月')}",
        f"转股溢价率为负 可转债 {datetime.now().strftime('%Y年%m月')} 机会",
        f"可转债 双低排名 低溢价 前十 {datetime.now().strftime('%Y年%m月')}"
    ]
    
    all_snippets = []
    for q in queries:
        data = search_cb_data(q)
        if data and 'results' in data:
            for r in data['results']:
                content = r.get('content', r.get('snippet', ''))
                title = r.get('title', '')
                all_snippets.append(f"【{title}】\n{content[:500]}")
    
    return all_snippets

def generate_report():
    """生成完整报告"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    snippets = scan_discount()
    
    report = f"""📊 可转债折价套利日报 {now}

⚠️ 注意：以下数据来自网络搜索，仅供参考，实际操作请以集思录(jisilu.cn)实时数据为准。

"""
    
    if snippets:
        for s in snippets[:5]:
            report += s + "\n\n---\n\n"
    
    report += """
💡 **每日操作清单**：
1. 登录集思录 → 可转债 → 按溢价率排序
2. 筛选：溢价率<0% + 已进入转股期 + 非强赎
3. 折价>1%的 → 考虑买入转股套利
4. 折价0.5%-1% → 关注观察
5. 双低值<115的 → 加入摊大饼组合

📌 实操数据源：
• 集思录：https://www.jisilu.cn/data/cbnew/
• 宁稳网：https://www.ninwin.cn/
"""
    return report

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(generate_report())
    else:
        print(generate_report())
