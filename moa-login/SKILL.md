---
name: moa-login
description: 美团 MOA (办公终端安全管理软件) 部署和登录流程。当用户访问美团内部系统 (.sankuai.com 域名) 被 MOA 登录拦截时自动触发。处理 MOA 安装、启动和 SSO 扫码登录全流程。触发场景：(1) 访问 .sankuai.com 被拦截 (2) MOA 未安装/未运行/未登录 (3) 用户提到 MOA 登录问题
---

# MOA 登录流程

## 检测与处理流程

### 1. 检查 MOA 安装状态

```bash
dpkg -l moa 2>/dev/null | grep -q "^ii" && echo "INSTALLED" || echo "NOT_INSTALLED"
```

**未安装** → 执行安装脚本：
```bash
# 告知用户 MOA 首次安装时间较长（约 2-3 分钟）
bash <skill_dir>/scripts/install.sh
```

安装脚本会自动完成：配置 /etc/hosts、chromium 代理、下载安装 MOA、配置 supervisor 守护进程。

安装后等待 10 秒再继续检测运行状态。

### 2. 检查 MOA 运行状态

```bash
ps aux | grep moatray | grep -v grep
```

**未运行** → 启动 MOA：
```bash
supervisorctl start moa
sleep 5  # 等待进程启动
```

### 3. 检查登录状态

```bash
LOG_FILE="/home/.local/share/MOA/logs/moatray-$(date +%Y-%m-%d).txt"
if [ -f "$LOG_FILE" ]; then
    grep -E "ssoLoginStatus is 0|misId" "$LOG_FILE" | tail -5
fi
```

**判断登录状态**：
- `ssoLoginStatus is 0` + `"code":200` + 有 `misId` → 已登录
- 无日志文件、无记录或 `ssoLoginStatus` 非 0 → 未登录

### 4. 执行登录流程（未登录时）

**重启 MOA 触发登录弹框**：
```bash
supervisorctl restart moa
sleep 8  # 等待登录页面加载，浏览器反应较慢
```

#### 浏览器自动化登录步骤

1. **查找 MOA 登录页面** —  在 chromium 浏览器中自动弹出 MOA 登录框。

2. **切换到扫码登录** — 在MOA登陆框内部Log in子框中会有三种登陆方式，比如SMS、Password、Email Code，需要点击Log in子框右上角的二维码图标，切换到大象扫码登陆方式。

3. **截图发送二维码** — 对扫码页面截图，将截图发送给用户扫码登录。

4. **降级方案** — 若找不到二维码或则无法将截图发送给用户，提示用户到内置浏览器进行扫码登录或则使用其他方式登陆。

5. **等待用户扫码**（最多 3 分钟 / 180 秒）— 每隔 15 秒检查一次页面状态或日志变化，用户扫码登录后会弹到MOA同意授权或欢迎框，若是同意授权框需要先点击同意，最后点击**x**关掉MOA弹框。

### 5. 验证登录成功

```bash
sleep 3
grep -E "ssoLoginStatus is 0|misId" "/home/.local/share/MOA/logs/moatray-$(date +%Y-%m-%d).txt" | tail -3
```

确认日志中出现 `ssoLoginStatus is 0` 和 `misId` 即登录成功。

## 注意事项

- 每次浏览器操作后等待 3-5 秒，页面加载较慢
- 扫码等待超时为 3 分钟
- 登录成功后等待几秒让 cookie 同步到浏览器
- 日志路径：`/home/.local/share/MOA/logs/moatray-YYYY-MM-DD.txt`

