#!/usr/bin/env python3
"""
可转债折价套利监控系统
功能：
1. 每日下午2点扫描折价转债
2. 折价>1%时立即推送
3. 模拟组合跟踪

数据源：东方财富/腾讯财经
推送：大象消息
"""

import json
import requests
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置 ============
DAXIANG_TARGET = "single_2369102735"
DISCOUNT_THRESHOLD = -1.0  # 折价阈值（溢价率<-1%触发）
LOW_PREMIUM_THRESHOLD = 5.0  # 低溢价阈值
DOUBLE_LOW_MAX = 130  # 双低值上限

# 模拟组合文件
PORTFOLIO_FILE = Path("/root/.openclaw/workspace/data/cb_portfolio.json")
HISTORY_FILE = Path("/root/.openclaw/workspace/data/cb_history.json")

# ============ 数据获取 ============
def fetch_cb_data_akshare():
    """通过 akshare 获取可转债数据"""
    try:
        import akshare as ak
        # 获取可转债实时行情
        df = ak.bond_zh_cov_realtime()
        return df
    except Exception as e:
        print(f"akshare获取失败: {e}")
        return None

def fetch_cb_data_eastmoney():
    """东方财富API获取可转债数据"""
    url = 'https://push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': 1, 'pz': 500, 'po': 1,
        'np': 1, 'fltt': 2, 'invt': 2,
        'fid': 'f237',
        'fs': 'b:MK0354',
        'fields': 'f2,f3,f12,f14,f232,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://quote.eastmoney.com/'
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        items = data.get('data', {}).get('diff', [])
        
        result = []
        for item in items:
            price = item.get('f2')
            if price == '-' or price is None:
                continue
                
            cb = {
                'code': item.get('f12', ''),
                'name': item.get('f14', ''),
                'price': float(price) if price else 0,
                'change_pct': item.get('f3', 0),
                'stock_code': item.get('f232', ''),
                'stock_name': item.get('f234', ''),
                'conv_price': item.get('f235', 0),  # 转股价
                'conv_value': item.get('f236', 0),  # 转股价值
                'premium_rate': item.get('f237', 0),  # 溢价率
                'ytm': item.get('f239', 0),  # 到期收益率
                'remain_year': item.get('f240', 0),  # 剩余年限
            }
            
            # 计算双低值
            if cb['price'] and cb['premium_rate'] is not None:
                try:
                    cb['double_low'] = cb['price'] + float(cb['premium_rate'])
                except:
                    cb['double_low'] = 999
            else:
                cb['double_low'] = 999
                
            result.append(cb)
        
        return result
    except Exception as e:
        print(f"东方财富API获取失败: {e}")
        return None

def fetch_cb_data_tencent():
    """腾讯财经API获取可转债数据（备用）"""
    # 可转债列表代码
    codes = []  # 需要预置代码列表
    # TODO: 实现腾讯财经接口
    pass

# ============ 筛选策略 ============
def filter_discount_cb(data, threshold=DISCOUNT_THRESHOLD):
    """筛选折价转债（负溢价）"""
    if not data:
        return []
    
    discount = []
    for cb in data:
        prem = cb.get('premium_rate')
        if prem is not None and prem < threshold:
            discount.append(cb)
    
    # 按溢价率升序（折价幅度大的排前面）
    discount.sort(key=lambda x: x.get('premium_rate', 0))
    return discount

def filter_low_premium_cb(data, threshold=LOW_PREMIUM_THRESHOLD):
    """筛选低溢价转债"""
    if not data:
        return []
    
    low_prem = []
    for cb in data:
        prem = cb.get('premium_rate')
        if prem is not None and 0 <= prem <= threshold:
            low_prem.append(cb)
    
    low_prem.sort(key=lambda x: x.get('premium_rate', 0))
    return low_prem

def filter_double_low_cb(data, threshold=DOUBLE_LOW_MAX):
    """筛选双低转债"""
    if not data:
        return []
    
    double_low = []
    for cb in data:
        dl = cb.get('double_low', 999)
        if dl < threshold:
            double_low.append(cb)
    
    double_low.sort(key=lambda x: x.get('double_low', 999))
    return double_low

# ============ 报告生成 ============
def generate_discount_report(discount_list, low_prem_list, double_low_list):
    """生成监控报告"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    lines = [
        f"📊 **可转债套利监控** {now}",
        ""
    ]
    
    # 折价转债（最重要）
    if discount_list:
        lines.append("🔴 **折价转债（套利机会）**")
        lines.append("```")
        for cb in discount_list[:10]:
            lines.append(
                f"{cb['name']}({cb['code']}) "
                f"价格:{cb['price']:.2f} "
                f"转股价值:{cb.get('conv_value', '-')} "
                f"溢价率:{cb['premium_rate']:.2f}%"
            )
        lines.append("```")
        lines.append("")
    else:
        lines.append("🟢 当前无折价转债")
        lines.append("")
    
    # 低溢价转债
    if low_prem_list:
        lines.append(f"🟡 **低溢价转债 TOP10**（溢价率<{LOW_PREMIUM_THRESHOLD}%）")
        lines.append("```")
        for cb in low_prem_list[:10]:
            lines.append(
                f"{cb['name']} "
                f"价格:{cb['price']:.2f} "
                f"溢价率:{cb['premium_rate']:.2f}%"
            )
        lines.append("```")
        lines.append("")
    
    # 双低转债
    if double_low_list:
        lines.append(f"📉 **双低转债 TOP10**（双低值<{DOUBLE_LOW_MAX}）")
        lines.append("```")
        for cb in double_low_list[:10]:
            lines.append(
                f"{cb['name']} "
                f"价格:{cb['price']:.2f} "
                f"溢价率:{cb.get('premium_rate', 0):.2f}% "
                f"双低:{cb['double_low']:.1f}"
            )
        lines.append("```")
        lines.append("")
    
    # 统计
    lines.append("📈 **统计**")
    lines.append(f"• 折价转债: {len(discount_list)}只")
    lines.append(f"• 低溢价转债: {len(low_prem_list)}只")
    lines.append(f"• 双低转债: {len(double_low_list)}只")
    
    return "\n".join(lines)

def generate_alert_report(cb):
    """生成单只转债折价提醒"""
    return f"""⚠️ **折价套利提醒**

**{cb['name']}**({cb['code']})
• 现价: {cb['price']:.2f}
• 转股价值: {cb.get('conv_value', '-')}
• 溢价率: **{cb['premium_rate']:.2f}%** 🔴
• 正股: {cb['stock_name']}({cb['stock_code']})

💡 操作建议：
1. T日买入转债 → 当日转股
2. T+1日卖出股票
3. 预期收益: {abs(cb['premium_rate']):.2f}%（扣费后约{abs(cb['premium_rate'])-0.2:.2f}%）

⚠️ 风险：T+1日正股可能下跌，需评估隔夜风险。
"""

# ============ 模拟组合 ============
def load_portfolio():
    """加载模拟组合"""
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return {"holdings": [], "cash": 100000, "history": []}

def save_portfolio(portfolio):
    """保存模拟组合"""
    PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

def update_portfolio_values(portfolio, cb_data):
    """更新持仓市值"""
    cb_dict = {cb['code']: cb for cb in cb_data}
    total_value = portfolio['cash']
    
    for holding in portfolio['holdings']:
        code = holding['code']
        if code in cb_dict:
            holding['current_price'] = cb_dict[code]['price']
            holding['market_value'] = holding['shares'] * cb_dict[code]['price']
            holding['profit'] = holding['market_value'] - holding['cost']
            holding['profit_pct'] = (holding['profit'] / holding['cost']) * 100
            total_value += holding['market_value']
    
    portfolio['total_value'] = total_value
    portfolio['total_profit'] = total_value - 100000
    portfolio['total_profit_pct'] = (portfolio['total_profit'] / 100000) * 100
    return portfolio

# ============ 主函数 ============
def run_daily_scan():
    """每日扫描（下午2点执行）"""
    print(f"[{datetime.now()}] 开始扫描...")
    
    # 获取数据
    data = fetch_cb_data_eastmoney()
    if not data:
        print("获取数据失败")
        return None
    
    print(f"获取到 {len(data)} 只可转债")
    
    # 筛选
    discount = filter_discount_cb(data)
    low_prem = filter_low_premium_cb(data)
    double_low = filter_double_low_cb(data)
    
    # 生成报告
    report = generate_discount_report(discount, low_prem, double_low)
    
    # 更新模拟组合
    portfolio = load_portfolio()
    portfolio = update_portfolio_values(portfolio, data)
    save_portfolio(portfolio)
    
    return {
        'report': report,
        'discount': discount,
        'low_premium': low_prem,
        'double_low': double_low,
        'portfolio': portfolio
    }

def run_realtime_alert():
    """实时折价提醒（折价>1%时触发）"""
    data = fetch_cb_data_eastmoney()
    if not data:
        return None
    
    discount = filter_discount_cb(data, threshold=-1.0)
    if discount:
        alerts = []
        for cb in discount:
            alerts.append(generate_alert_report(cb))
        return alerts
    return None

# ============ CLI ============
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cb_discount_monitor.py [daily|alert|test]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "daily":
        result = run_daily_scan()
        if result:
            print(result['report'])
    
    elif cmd == "alert":
        alerts = run_realtime_alert()
        if alerts:
            for a in alerts:
                print(a)
                print("---")
        else:
            print("当前无折价套利机会")
    
    elif cmd == "test":
        # 测试数据获取
        data = fetch_cb_data_eastmoney()
        if data:
            print(f"获取到 {len(data)} 只可转债")
            # 打印前5只
            for cb in data[:5]:
                print(f"{cb['name']}({cb['code']}) 价格:{cb['price']} 溢价率:{cb.get('premium_rate')}%")
        else:
            print("获取数据失败")
