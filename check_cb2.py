import requests
import json

# 尝试不同的API
urls_to_try = [
    # 东方财富可转债行情
    ("https://push2.eastmoney.com/api/qt/clist/get", {
        'pn': 1, 'pz': 100, 'po': 1, 'np': 1, 'fltt': 2, 'invt': 2,
        'fid': 'f3', 'fs': 'm:1+t:23', 'fields': 'f1,f2,f3,f4,f12,f13,f14'
    }),
    # 网易财经可转债
    ("https://quotes.money.163.com/service/chddata.html", {
        'code': '013010',  # 示例可转债代码
        'start': '20260301',
        'end': '20260312',
        'fields': 'TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER'
    })
]

for url, params in urls_to_try:
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"=== {url} ===")
        print(r.text[:2000])
        print()
    except Exception as e:
        print(f"Error {url}: {e}")
