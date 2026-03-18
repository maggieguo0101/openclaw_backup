#!/usr/bin/env python3
"""
资金转账差额计算：对比两次申购的分配结果，计算转账明细。

原则：上一次已有的钱在哪个账户就不动，新一次在此基础上只调整差额。

输入：JSON 文件，包含 prev_allocation（上次分配）和 new_funds（新一次出资）等
输出：
  1. 新一次基于"不动原则"的分配结果
  2. 转账明细（补充/新增/退款，无账户间调拨）
  3. 可选 HTML/PNG 图片（含上次分配 + 新分配 + 转账明细三合一）
"""

import argparse
import json
import sys
import os


def allocate_no_move(prev_alloc: dict, new_funds: dict, accounts: dict, ownership: dict) -> dict:
    """
    不动原则分配：保留上次分配位置，只分配差额。

    Args:
        prev_alloc: 上次分配结果 {"账户名": {"出资人": 金额, ...}, ...}
        new_funds: 新一次出资 {"出资人": 金额, ...}
        accounts: 账户目标 {"账户名": 目标金额, ...}
        ownership: 归属关系 {"出资人": "所属账户名", ...}

    Returns:
        {"账户名": {"出资人": 金额, ...}, ...}
    """
    accs = list(accounts.keys())
    allocation = {acc: {} for acc in accs}

    # 第一步：保留上次分配（但不超过新出资额）
    for p in new_funds:
        new_amt = new_funds[p]
        # 上次在各账户的金额
        prev_total = sum(prev_alloc.get(acc, {}).get(p, 0) for acc in accs)

        if prev_total <= new_amt:
            # 上次全部保留
            for acc in accs:
                v = prev_alloc.get(acc, {}).get(p, 0)
                if v > 0:
                    allocation[acc][p] = v
        else:
            # 上次超过新出资，按顺序缩减
            remaining = new_amt
            for acc in accs:
                v = prev_alloc.get(acc, {}).get(p, 0)
                if v > 0 and remaining > 0:
                    put = min(v, remaining)
                    allocation[acc][p] = put
                    remaining -= put

    # 第二步：计算每人剩余未分配资金
    person_remaining = {}
    for p in new_funds:
        placed = sum(allocation[acc].get(p, 0) for acc in accs)
        remaining = round(new_funds[p] - placed, 2)
        if remaining > 0:
            person_remaining[p] = remaining

    # 计算账户缺口
    gaps = {acc: round(accounts[acc] - sum(allocation[acc].values()), 2) for acc in accs}

    # 第三步：按归属分配剩余资金
    for p in list(person_remaining.keys()):
        amt = person_remaining[p]
        own_acc = ownership.get(p)
        if own_acc and gaps.get(own_acc, 0) > 0:
            put = min(amt, gaps[own_acc])
            allocation[own_acc][p] = round(allocation[own_acc].get(p, 0) + put, 2)
            gaps[own_acc] = round(gaps[own_acc] - put, 2)
            person_remaining[p] = round(amt - put, 2)
            if person_remaining[p] <= 0:
                del person_remaining[p]

    # 第四步：完整匹配（不拆分）
    sorted_funds = sorted(person_remaining.items(), key=lambda x: x[1], reverse=True)
    used = set()
    for p, amt in sorted_funds:
        if p in used or amt <= 0:
            continue
        best_acc = None
        best_remain = float('inf')
        for acc, gap in gaps.items():
            if gap >= amt and gap - amt < best_remain:
                best_remain = gap - amt
                best_acc = acc
        if best_acc:
            allocation[best_acc][p] = round(allocation[best_acc].get(p, 0) + amt, 2)
            gaps[best_acc] = round(gaps[best_acc] - amt, 2)
            used.add(p)

    # 第五步：不得已拆分
    for p in list(person_remaining.keys()):
        if p in used:
            continue
        amt = person_remaining[p]
        while amt > 0.001:
            items = [(k, v) for k, v in gaps.items() if v > 0.001]
            if not items:
                break
            acc = max(items, key=lambda x: x[1])[0]
            put = min(amt, gaps[acc])
            allocation[acc][p] = round(allocation[acc].get(p, 0) + put, 2)
            gaps[acc] = round(gaps[acc] - put, 2)
            amt = round(amt - put, 2)

    return allocation


def calc_transfers(prev_alloc: dict, new_alloc: dict, prev_funds: dict, new_funds: dict, accounts: dict) -> list:
    """
    计算转账明细。

    Returns:
        [{"person": str, "amount": float, "to": str, "note": str, "type": str}, ...]
    """
    accs = list(accounts.keys())
    transfers = []

    all_persons = list(dict.fromkeys(list(new_funds.keys()) + list(prev_funds.keys())))

    for p in all_persons:
        prev_total = sum(prev_alloc.get(acc, {}).get(p, 0) for acc in accs)
        new_total = sum(new_alloc.get(acc, {}).get(p, 0) for acc in accs)

        diff = round(new_total - prev_total, 2)

        if diff > 0:
            # 需要补钱
            if prev_total == 0:
                tf_type = "新增"
            else:
                tf_type = "补充"

            # 找出补到了哪些账户
            for acc in accs:
                prev_v = prev_alloc.get(acc, {}).get(p, 0)
                new_v = new_alloc.get(acc, {}).get(p, 0)
                acc_diff = round(new_v - prev_v, 2)
                if acc_diff > 0:
                    acc_short = acc.replace("账户", "")
                    note = f"本次{tf_type}" if len([a for a in accs if round(new_alloc.get(a, {}).get(p, 0) - prev_alloc.get(a, {}).get(p, 0), 2) > 0]) == 1 else f"本次{tf_type}（拆分）"
                    if tf_type == "补充":
                        note = f"补差额（{new_funds.get(p,0)}−{prev_funds.get(p,0)}）"
                    transfers.append({
                        "person": p,
                        "amount": acc_diff,
                        "to": acc_short,
                        "note": note,
                        "type": tf_type,
                    })

        elif diff < 0:
            # 需要退钱
            transfers.append({
                "person": p,
                "amount": abs(diff),
                "to": f"退{p}",
                "note": f"退{abs(diff)}（上次{prev_total}→本次{new_total}）",
                "type": "退款",
            })

    return transfers


def fmt(v):
    if v == 0:
        return ""
    if v == int(v):
        return str(int(v))
    return f"{v:.2f}"


def generate_html(prev_alloc, new_alloc, prev_funds, new_funds, accounts, transfers,
                  prev_title="", new_title="", main_title="资金去向汇总", note="") -> str:
    accs = list(accounts.keys())
    all_persons_prev = list(prev_funds.keys())
    all_persons_new = list(new_funds.keys())

    def build_alloc_table(alloc, funds, persons):
        rows = ""
        for p in persons:
            if funds.get(p, 0) == 0:
                continue
            # 检查是否被拆分
            count = sum(1 for acc in accs if alloc.get(acc, {}).get(p, 0) > 0)
            is_split = count > 1
            cls = ' class="split"' if is_split else ''
            label = f"{p} ⚡" if is_split else p
            cells = f'<td>{fmt(funds[p])}</td>'
            for acc in accs:
                cells += f'<td>{fmt(alloc.get(acc, {}).get(p, 0))}</td>'
            rows += f'<tr{cls}><td>{label}</td>{cells}</tr>\n'

        # 小计
        total_amt = sum(funds.get(p, 0) for p in persons if funds.get(p, 0) > 0)
        sub_cells = f'<td>{fmt(total_amt)}</td>'
        for acc in accs:
            st = sum(alloc.get(acc, {}).get(p, 0) for p in persons)
            sub_cells += f'<td>{fmt(round(st, 2))}</td>'
        rows += f'<tr class="subtotal-row"><td>账户汇总</td>{sub_cells}</tr>\n'
        return rows

    headers = '<th>出资人</th><th>金额</th>' + ''.join(f'<th>{acc}</th>' for acc in accs)

    prev_rows = build_alloc_table(prev_alloc, prev_funds, all_persons_prev)
    new_rows = build_alloc_table(new_alloc, new_funds, all_persons_new)

    # 转账明细
    tf_rows = ""
    supplements = [t for t in transfers if t["type"] in ("补充", "新增")]
    refunds = [t for t in transfers if t["type"] == "退款"]

    if supplements:
        tf_rows += '<tr class="section-header"><td colspan="4">资金补充 / 新增</td></tr>\n'
        for t in supplements:
            tf_rows += f'<tr><td>{t["person"]}</td><td>{fmt(t["amount"])}</td><td>{t["to"]}</td><td class="note">{t["note"]}</td></tr>\n'

    if refunds:
        tf_rows += '<tr class="section-header"><td colspan="4">退款</td></tr>\n'
        for t in refunds:
            tf_rows += f'<tr class="refund"><td>{t["person"]}</td><td>{fmt(t["amount"])}</td><td>{t["to"]}</td><td class="note">{t["note"]}</td></tr>\n'

    note_html = f'<div class="note-box">{note}</div>' if note else ""

    html = f'''<html><head><style>
body {{ font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif; padding: 20px; background: white; }}
h1 {{ text-align: center; font-size: 20px; margin-bottom: 8px; }}
.note-box {{ text-align: center; font-size: 12px; color: #E53935; margin-bottom: 25px; padding: 6px; background: #FFF3E0; border-radius: 4px; max-width: 640px; margin-left: auto; margin-right: auto; }}
.section {{ max-width: 640px; margin: 0 auto 35px; }}
.title {{ font-size: 14px; font-weight: bold; margin-bottom: 8px; padding: 6px 10px; background: #E8F0FE; border-left: 4px solid #4472C4; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #B8D4F0; color: #333; padding: 8px; text-align: center; font-size: 12px; border: 1px solid #999; }}
td {{ border: 1px solid #ccc; padding: 7px 10px; text-align: right; font-size: 12px; }}
td:first-child {{ text-align: center; font-weight: 500; }}
.subtotal-row td {{ border-top: 2px solid #666; font-weight: bold; }}
.split {{ background: #FCE4EC; }}
.section-header td {{ background: #E8F0FE; font-weight: bold; text-align: left !important; padding: 8px 10px; border-left: 4px solid #4472C4; font-size: 12px; }}
.refund {{ background: #FFF3E0; }}
.note {{ text-align: left !important; font-size: 11px; color: #666; }}
.tf-table td {{ text-align: center; }}
.tf-table td:nth-child(2) {{ text-align: right; }}
.tf-table td:nth-child(4) {{ text-align: left; }}
</style></head><body>

<h1>{main_title}</h1>
{note_html}

<div class="section">
<div class="title">① {prev_title}</div>
<table><tr>{headers}</tr>{prev_rows}</table>
</div>

<div class="section">
<div class="title">② {new_title}</div>
<table><tr>{headers}</tr>{new_rows}</table>
</div>

<div class="section">
<div class="title">③ 转账明细 · 仅差额操作，无账户间调拨</div>
<table class="tf-table">
<tr><th>出资人</th><th>金额</th><th>收款人/方向</th><th>备注</th></tr>
{tf_rows}
</table>
</div>

</body></html>'''
    return html


def main():
    parser = argparse.ArgumentParser(description="资金转账差额计算")
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", help="输出目录 (默认当前目录)", default=".")
    parser.add_argument("--png", action="store_true", help="生成 PNG 图片")
    parser.add_argument("--html", action="store_true", help="生成 HTML 文件")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    accounts = data["accounts"]
    prev_funds = data["prev_funds"]
    prev_alloc = data["prev_allocation"]
    new_funds = data["new_funds"]
    ownership = data.get("ownership", {})
    prev_title = data.get("prev_title", "上次申购")
    new_title = data.get("new_title", "本次申购")
    main_title = data.get("title", "资金去向汇总")
    note = data.get("note", "⚡ 原则：上次已有的钱在哪个账户就不动，本次在此基础上只调整差额")

    # 执行不动原则分配
    new_alloc = allocate_no_move(prev_alloc, new_funds, accounts, ownership)

    # 计算转账明细
    transfers = calc_transfers(prev_alloc, new_alloc, prev_funds, new_funds, accounts)

    os.makedirs(args.output, exist_ok=True)

    # 输出结果 JSON
    result = {
        "new_allocation": new_alloc,
        "transfers": transfers,
        "summary": {}
    }
    for acc in accounts:
        total = round(sum(new_alloc[acc].values()), 2)
        result["summary"][acc] = {"total": total, "target": accounts[acc], "match": total == accounts[acc]}

    result_path = os.path.join(args.output, "transfer_result.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"结果已保存: {result_path}")

    # 打印摘要
    accs = list(accounts.keys())
    print("\n=== 新分配（不动原则）===")
    for acc in accs:
        total = round(sum(new_alloc[acc].values()), 2)
        print(f"\n{acc} (目标{accounts[acc]}):")
        for k, v in new_alloc[acc].items():
            print(f"  {k}: {fmt(v)}")
        print(f"  小计: {fmt(total)}")

    print("\n=== 转账明细 ===")
    for t in transfers:
        print(f"  {t['person']}: {fmt(t['amount'])} → {t['to']} ({t['note']})")

    # 生成 HTML / PNG
    if args.html or args.png:
        html_content = generate_html(
            prev_alloc, new_alloc, prev_funds, new_funds, accounts, transfers,
            prev_title, new_title, main_title, note
        )
        html_path = os.path.join(args.output, "transfer.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML 已保存: {html_path}")

    if args.png:
        try:
            from playwright.sync_api import sync_playwright
            png_path = os.path.join(args.output, "transfer.png")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 720, "height": 800})
                page.goto(f"file://{os.path.abspath(html_path)}")
                page.wait_for_timeout(500)
                page.screenshot(path=png_path, full_page=True)
                browser.close()
            print(f"PNG 已保存: {png_path}")
        except Exception as e:
            print(f"PNG 生成失败: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
