#!/bin/bash
# 会议室监控脚本 - 每次运行检查一次，找到空闲就通知

cd /root/.openclaw/workspace
RESULT=$(python3 scripts/check_meeting_room.py 2>&1)
echo "$RESULT"

# 检查是否找到空闲
if echo "$RESULT" | grep -q '"found": true'; then
    echo "🎉 找到空闲会议室！发送通知..."
    # 这里通过 openclaw 发送通知
    exit 0
else
    echo "暂无空闲，继续等待..."
    exit 1
fi
