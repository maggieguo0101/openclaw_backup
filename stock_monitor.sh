#!/bin/bash
# 股票价格监控脚本
# 港股 02692 兆威机电 → 到 75 提醒
# A股 920036 觅睿科技 → 到 50 提醒

WORKSPACE="/root/.openclaw/workspace"
STATE_FILE="$WORKSPACE/stock_monitor_state.json"

# 初始化状态文件
if [ ! -f "$STATE_FILE" ]; then
  echo '{"hk02692_alerted":false,"bj920036_alerted":false}' > "$STATE_FILE"
fi

# 获取行情
DATA=$(curl -s "https://qt.gtimg.cn/q=hk02692,bj920036" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "$(date): 获取行情失败"
  exit 1
fi

# 解析价格
HK_PRICE=$(echo "$DATA" | grep "v_hk02692" | awk -F'~' '{print $4}')
BJ_PRICE=$(echo "$DATA" | grep "v_bj920036" | awk -F'~' '{print $4}')

echo "$(date): 02692=$HK_PRICE, 920036=$BJ_PRICE"

# 读取状态
HK_ALERTED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('hk02692_alerted', False))")
BJ_ALERTED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('bj920036_alerted', False))")

ALERT_MSG=""

# 检查港股 02692 >= 75
if [ -n "$HK_PRICE" ]; then
  HK_HIT=$(python3 -c "print('YES' if float('$HK_PRICE') >= 75 else 'NO')")
  if [ "$HK_HIT" = "YES" ] && [ "$HK_ALERTED" != "True" ]; then
    ALERT_MSG="🔔 **港股 02692 兆威机电** 到达 **${HK_PRICE} HKD**，已触达 75 目标价！"
    python3 -c "import json; d=json.load(open('$STATE_FILE')); d['hk02692_alerted']=True; json.dump(d, open('$STATE_FILE','w'))"
  fi
fi

# 检查A股 920036 >= 50
if [ -n "$BJ_PRICE" ]; then
  BJ_HIT=$(python3 -c "print('YES' if float('$BJ_PRICE') >= 50 else 'NO')")
  if [ "$BJ_HIT" = "YES" ] && [ "$BJ_ALERTED" != "True" ]; then
    if [ -n "$ALERT_MSG" ]; then
      ALERT_MSG="$ALERT_MSG\n\n🔔 **A股 920036 觅睿科技** 到达 **${BJ_PRICE} CNY**，已触达 50 目标价！"
    else
      ALERT_MSG="🔔 **A股 920036 觅睿科技** 到达 **${BJ_PRICE} CNY**，已触达 50 目标价！"
    fi
    python3 -c "import json; d=json.load(open('$STATE_FILE')); d['bj920036_alerted']=True; json.dump(d, open('$STATE_FILE','w'))"
  fi
fi

# 有提醒则发消息
if [ -n "$ALERT_MSG" ]; then
  echo "触发提醒: $ALERT_MSG"
  # 输出提醒内容供 cron 任务使用
  echo "$ALERT_MSG" > "$WORKSPACE/stock_alert.txt"
fi
