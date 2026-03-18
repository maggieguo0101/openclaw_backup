import requests
import json

# 尝试获取可转债列表数据
url = 'https://datacenter.eastmoney.com/api/data/v1/get'
params = {
    'reportName': 'RPT_BOND_CB_LIST',
    'columns': 'ALL',
    'filter': '(TRADE_DATE>="2026-03-11")',
    'pageNumber': 1,
    'pageSize': 50,
    'source': 'WEB'
}

try:
    r = requests.get(url, params=params, timeout=10)
    print(r.text[:3000])
except Exception as e:
    print(f'Error: {e}')
