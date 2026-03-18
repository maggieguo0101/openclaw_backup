# HEARTBEAT.md

## 任务
1. **Review待办清单**：检查 memory/2026-MM-DD.md 中未完成的任务，空闲时主动推进
2. **翻译进度**：如果没有其他紧急任务，继续翻译Steve Pavlina 2025文章
3. **定期检查**：轮换检查邮件、日历、消息（2-4次/天）

## 定期任务

### GitHub 备份（每天23:00左右自动执行）
```bash
cd /root/.openclaw/workspace && git add -A && git diff --cached --quiet || (git commit -m "auto backup $(date +%Y-%m-%d)" && git push)
```
- 检查是否有新文件/变更，有则 commit + push，没有则跳过
- 静默执行，不打扰老板

## 快捷指令

老板发以下关键词时，直接执行对应操作，无需确认：

| 指令 | 动作 |
|---|---|
| `/token` 或 `token看板` | 运行 `python3 /root/.openclaw/workspace/token_dashboard.py`，截图，上传 S3Plus，发链接 |
