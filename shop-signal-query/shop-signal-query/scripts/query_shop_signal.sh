#!/bin/bash

dp_shop_id="${1:?Usage: $0 <dp_shop_id>}"
partition_date=$(date -v-1d +%Y%m%d 2>/dev/null || date -d yesterday +%Y%m%d)

response=$(sr-crm-oc curl -X POST -H "Content-Type: application/json" \
    -d "{\"request\":{\"tenantId\":3,\"signalCodeList\":[\"tts_shopName_adr\",\"cat0_name\",\"cat1_name\",\"cat2_name\",\"dp_front_city_name\",\"dp_front_district_name\",\"dp_front_region_name\",\"poi_address\",\"shop_open_status\",\"raw_biz_hour\",\"poi_status\",\"poi_claimed\",\"mem_signed\",\"mem_begin_date\",\"mem_end_date\",\"reject_count\",\"reject_reason\",\"group_buy_submitted\",\"tts_ground_contract_sales_name\",\"tts_sales_name\"],\"inputParams\":{\"dp_shop_id\":\"$dp_shop_id\",\"partition_date\":\"$partition_date\"}}}" \
    "https://xiaozhi.sankuai.com/gw/sk/signal/querySignalsValue")

echo "$response" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f"Failed to parse response: {e}", file=sys.stderr)
    sys.exit(1)
if data.get("code") != 200:
    print("API error:", data.get("message"), file=sys.stderr)
    sys.exit(1)
for item in data.get("data") or []:
    if item.get("value"):
        print(item["code"], "|", item["name"], "|", item["value"])
'
