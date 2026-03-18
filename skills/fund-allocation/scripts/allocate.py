#!/usr/bin/env python3
"""
资金分配算法：将总资金按目标金额分配到多个账户。

规则：
  第一阶段：本人+相关人资金优先放对应账户（相关人放一起）
  第二阶段：公共资金完整匹配（尽量不拆分）
  第三阶段：不得已的拆分（大额填大坑）

输入：JSON 文件，格式见下方 --help
输出：分配结果 JSON + 可选 HTML/PNG 图片
"""

import argparse
import json
import sys
import os


def allocate(accounts: dict, funds: dict, ownership: dict) -> dict:
    """
    核心分配算法。

    Args:
        accounts: {"账户名": 目标金额, ...}
        funds: {"出资人": 金额, ...}
        ownership: {"出资人": "所属账户名", ...}
            - 无归属的人不在此 dict 中，视为公共资金

    Returns:
        {"账户名": {"出资人": 金额, ...}, ...}
    """
    allocation = {acc: {} for acc in accounts}

    # === 第一阶段：本人+相关人优先放对应账户 ===
    for acc_name, demand in accounts.items():
        related = [p for p, owner in ownership.items() if owner == acc_name and p in funds]
        related_total = sum(funds[p] for p in related)

        if related_total <= demand:
            # 全部放入
            for p in related:
                allocation[acc_name][p] = funds[p]
        else:
            # 超出需求：先放本人，再放其他相关人直到填满（不拆分个人）
            remaining = demand
            # 本人优先
            if acc_name in funds and acc_name in related:
                put = min(funds[acc_name], remaining)
                allocation[acc_name][acc_name] = put
                remaining -= put

            for p in related:
                if p == acc_name:
                    continue
                if remaining <= 0:
                    break
                p_money = funds[p]
                if p_money <= remaining:
                    allocation[acc_name][p] = p_money
                    remaining -= p_money
                # 放不下整笔的跳过（不拆分），进公共池

    # 统计已分配
    person_placed = {}
    for acc_name in accounts:
        for p, v in allocation[acc_name].items():
            person_placed[p] = person_placed.get(p, 0) + v

    # 公共资金池
    public_funds = {}
    for p, m in funds.items():
        placed = person_placed.get(p, 0)
        if placed < m:
            public_funds[p] = m - placed

    # 计算缺口
    account_gaps = {}
    for acc_name in accounts:
        total_in = sum(allocation[acc_name].values())
        account_gaps[acc_name] = accounts[acc_name] - total_in

    # === 第二阶段：完整资金优先匹配 ===
    sorted_funds = sorted(public_funds.items(), key=lambda x: x[1], reverse=True)
    used = set()

    # 完美匹配
    for fund_name, fund_money in sorted_funds:
        if fund_name in used:
            continue
        for acc_name, gap in account_gaps.items():
            if gap > 0 and fund_money == gap:
                allocation[acc_name][fund_name] = fund_money
                account_gaps[acc_name] = 0
                used.add(fund_name)
                break

    # 最优容纳匹配
    remaining_list = [(k, v) for k, v in public_funds.items() if k not in used]
    remaining_list.sort(key=lambda x: x[1], reverse=True)

    for fund_name, fund_money in remaining_list:
        if fund_name in used:
            continue
        best_acc = None
        best_remain = float('inf')

        for acc_name, gap in account_gaps.items():
            if gap > 0 and gap >= fund_money:
                remain = gap - fund_money
                if remain < best_remain:
                    best_remain = remain
                    best_acc = acc_name

        if best_acc:
            allocation[best_acc][fund_name] = fund_money
            account_gaps[best_acc] -= fund_money
            used.add(fund_name)

    # === 第三阶段：不得已拆分 ===
    remaining_pool = {k: v for k, v in public_funds.items() if k not in used}
    final_funds = sorted(remaining_pool.items(), key=lambda x: x[1], reverse=True)

    for fund_name, fund_money in final_funds:
        remaining = fund_money
        while remaining > 0:
            items = [(k, v) for k, v in account_gaps.items() if v > 0]
            if not items:
                break
            acc_name = max(items, key=lambda x: x[1])[0]
            gap = account_gaps[acc_name]

            put = min(remaining, gap)
            allocation[acc_name][fund_name] = allocation[acc_name].get(fund_name, 0) + put
            account_gaps[acc_name] -= put
            remaining -= put

    return allocation


def generate_html(allocation: dict, accounts: dict, funds: dict, title: str = "", subtitle: str = "") -> str:
    """生成 HTML 表格。"""
    all_persons = list(funds.keys())
    acc_names = list(accounts.keys())

    # 检测被拆分的人
    split_persons = set()
    for p in all_persons:
        count = sum(1 for acc in acc_names if allocation[acc].get(p, 0) > 0)
        if count > 1:
            split_persons.add(p)

    rows_html = ""
    for p in all_persons:
        is_split = p in split_persons
        cls = ' class="split"' if is_split else ''
        name_display = f"{p} ⚡" if is_split else p
        cells = ""
        for acc in acc_names:
            val = allocation[acc].get(p, 0)
            cells += f"<td>{val if val > 0 else '-'}</td>"
        cells += f"<td>{funds[p]}</td>"
        rows_html += f'<tr{cls}><td>{name_display}</td>{cells}</tr>\n'

    # 小计行
    subtotal_cells = ""
    grand_total = 0
    for acc in acc_names:
        t = sum(allocation[acc].values())
        subtotal_cells += f"<td>{t}</td>"
        grand_total += t
    subtotal_cells += f"<td>{grand_total}</td>"

    header_cells = "".join(f"<th>{acc}账户</th>" for acc in acc_names)

    title_html = f"<h2>{title}</h2>" if title else ""
    subtitle_html = f'<h3>{subtitle}</h3>' if subtitle else ""

    html = f'''<html><head><style>
body {{ font-family: Arial, sans-serif; padding: 20px; background: white; }}
h2 {{ text-align: center; margin-bottom: 5px; }}
h3 {{ text-align: center; margin-top: 0; color: #666; font-weight: normal; }}
table {{ border-collapse: collapse; width: 100%; max-width: 620px; margin: 0 auto; }}
th, td {{ border: 1px solid #333; padding: 8px; text-align: center; font-size: 12px; }}
th {{ background: #4472C4; color: white; }}
.subtotal {{ background: #D9E1F2; font-weight: bold; }}
.split {{ background: #FCE4EC; }}
</style></head><body>
{title_html}
{subtitle_html}
<table>
<tr><th>出资人</th>{header_cells}<th>合计</th></tr>
{rows_html}
<tr class="subtotal"><td>各账户小计</td>{subtotal_cells}</tr>
</table>
</body></html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description="资金分配算法")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", help="输出目录 (默认当前目录)", default=".")
    parser.add_argument("--png", action="store_true", help="生成 PNG 图片")
    parser.add_argument("--html", action="store_true", help="生成 HTML 文件")
    parser.add_argument("--title", default="资金分配方案", help="标题")
    parser.add_argument("--subtitle", default="", help="副标题")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    accounts = data["accounts"]  # {"账户名": 目标金额}
    funds = data["funds"]        # {"出资人": 金额}
    ownership = data.get("ownership", {})  # {"出资人": "所属账户名"}
    title = args.title or data.get("title", "资金分配方案")
    subtitle = args.subtitle or data.get("subtitle", "")

    # 执行分配
    allocation = allocate(accounts, funds, ownership)

    # 输出 JSON 结果
    result = {
        "allocation": allocation,
        "summary": {}
    }
    split_persons = []
    for acc_name in accounts:
        total = sum(allocation[acc_name].values())
        result["summary"][acc_name] = {"total": total, "target": accounts[acc_name], "match": total == accounts[acc_name]}

    for p in funds:
        count = sum(1 for acc in accounts if allocation[acc].get(p, 0) > 0)
        if count > 1:
            parts = {acc: allocation[acc][p] for acc in accounts if allocation[acc].get(p, 0) > 0}
            split_persons.append({"name": p, "parts": parts})
    result["split_persons"] = split_persons

    os.makedirs(args.output, exist_ok=True)

    result_path = os.path.join(args.output, "allocation_result.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"结果已保存: {result_path}")

    # 打印摘要
    print("\n=== 分配结果 ===")
    for acc_name in accounts:
        total = sum(allocation[acc_name].values())
        print(f"\n{acc_name}账户 (目标{accounts[acc_name]}):")
        for k, v in allocation[acc_name].items():
            print(f"  {k}: {v}")
        print(f"  小计: {total}")

    if split_persons:
        print(f"\n被拆分: {', '.join(s['name'] for s in split_persons)}")

    # 生成 HTML
    if args.html or args.png:
        html_content = generate_html(allocation, accounts, funds, title, subtitle)
        html_path = os.path.join(args.output, "allocation.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML 已保存: {html_path}")

    # 生成 PNG
    if args.png:
        try:
            from playwright.sync_api import sync_playwright
            png_path = os.path.join(args.output, "allocation.png")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 700, "height": 600})
                page.goto(f"file://{os.path.abspath(html_path)}")
                page.wait_for_timeout(500)
                page.screenshot(path=png_path, full_page=True)
                browser.close()
            print(f"PNG 已保存: {png_path}")
        except Exception as e:
            print(f"PNG 生成失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
