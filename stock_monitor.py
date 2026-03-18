#!/usr/bin/env python3
"""港股实时行情 - 使用腾讯appstock接口（更实时）"""
import json, sys, urllib.request

def get_hk_price(code):
    """获取港股实时价格"""
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk{code},day,,,1,qfq"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    qt = data['data'][f'hk{code}']['qt'][f'hk{code}']
    return {
        'code': code,
        'name': qt[1],
        'price': float(qt[3]),
        'prev_close': float(qt[4]),
        'open': float(qt[5]),
        'high': float(qt[34] if qt[34] else qt[33]),
        'low': float(qt[35] if qt[35] else qt[34]),
        'volume': float(qt[6]),
        'amount': float(qt[37]),
        'change_pct': float(qt[32]),
        'time': qt[30],
    }

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "02692"
    info = get_hk_price(code)
    print(f"代码: {info['code']}")
    print(f"名称: {info['name']}")
    print(f"现价: {info['price']} HKD")
    print(f"涨跌: {info['change_pct']}%")
    print(f"最高: {info['high']}")
    print(f"最低: {info['low']}")
    print(f"时间: {info['time']}")
