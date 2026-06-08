---
title: 微信接入
description: 通过微信 iLink Bot（ClawBot）与 Hermes 对话
---

配置微信网关后，你可以用微信给 Hermes 发消息，就像跟朋友聊天一样。

---

## 原理

```
你（手机微信） → 微信 iLink 服务器 → Hermes Gateway → Hermes Agent
```

使用的是微信官方的 **iLink Bot** 接口（ClawBot），通过二维码绑定你的个人微信号，无需公众号。

## 前提条件

- ✅ Hermes 已正常运行
- ✅ 网络能直接访问 `ilinkai.weixin.qq.com`（**不能走代理**，国内服务器）
- ✅ 手机微信（个人号即可，无需公众号）

## 第一步：获取凭证

Hermes 微信网关通过二维码扫码绑定你的微信号。

### 生成二维码

在 Hermes 容器内运行：

```bash
# 去掉代理（微信要求直连）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 调用接口获取二维码
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
```

返回的 JSON 中：
- `qrcode` — 二维码 ID（用于查询状态）
- `qrcode_img_content` — 二维码内容（生成图片用）

### 扫码与确认

1. 用手机微信扫描二维码
2. 在手机上点击"确认登录"
3. 等待返回凭证

```bash
# 查询扫码状态（长轮询接口，会阻塞等待）
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_qrcode_status?qrcode=<上一步返回的qrcode>"
```

状态流转：`wait` → `scaned` → `confirmed`

扫码确认后，返回的凭证包含：

| 字段 | 说明 |
|------|------|
| `ilink_bot_id` | Bot ID，类似 `xxx@im.bot` |
| `bot_token` | Token，格式为 `bot_id:hex字符串` |
| `baseurl` | 服务器地址，固定为 `https://ilinkai.weixin.qq.com` |
| `ilink_user_id` | 你的微信用户 ID |

> ⚠️ `get_qrcode_status` 是长轮询接口，会阻塞 ~30 秒直到状态变化或超时。不是秒回查询。

## 第二步：配置环境变量

将凭证写入 `~/.hermes/.env`：

```bash
# 追加到 .env
cat >> ~/.hermes/.env << 'EOF'

# WeChat iLink Bot
WEIXIN_ACCOUNT_ID=xxx@im.bot
WEIXIN_TOKEN=xxx@im.bot:hex字符串
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com
WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c
WEIXIN_DM_POLICY=pairing
WEIXIN_ALLOW_ALL_USERS=true
EOF
```

> ⚠️ `WEIXIN_TOKEN` 包含 `@` 和 `:`，用 `cat >>` 追加时不会被截断，但用 `export $(cat .env | xargs)` 会出问题。建议用 Python 加载 `.env`。

## 第三步：启动微信网关

### 手动测试

```bash
# 去掉代理
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 启动网关
HERMES_ALLOW_ROOT_GATEWAY=1 hermes gateway run --replace
```

### 持久运行

正式使用需要让网关开机自启。推荐修改 s6 run 脚本：

1. 找到网关 run 脚本路径：
   ```bash
   find /run /opt/data -name "run" -path "*/gateway*/run" 2>/dev/null
   ```

2. 在 `exec s6-setuidgid hermes hermes gateway run` 前插入：
   ```bash
   # WeChat iLink 需要直连（代理无法到达 weixin.qq.com）
   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
   ```

3. 重启网关：
   ```bash
   pkill -f "hermes gateway run"
   ```

## 第四步：确认连接

```bash
# 查看网关状态
cat /opt/data/gateway_state.json | python3 -m json.tool

# 应该看到 "weixin": {"state": "connected"}

# 查看进程
ps aux | grep "hermes gateway run"

# 查看日志
tail -20 /opt/data/logs/gateway.log
```

## 功能说明

### 支持的消息类型

- **文本消息** — 直接对话
- **图片消息** — 自动识别图片内容（需配置视觉模型）
- **语音消息** — 转文字后处理

### 长任务处理

耗时任务会自动转后台执行，你可以在微信上继续发别的消息，任务完成后收到通知。

## 故障排查

### 连不上 iLink 服务器

**症状**：日志频繁出现 `Cannot connect to host ilinkai.weixin.qq.com:443`

**原因**：代理冲突。微信是国内服务器，走美国代理连不上。

**诊断**：
```bash
# 直连测试
curl -s --noproxy '*' --connect-timeout 10 \
  https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3 \
  -o /dev/null -w "直连: HTTP %{http_code}, %{time_total}s\\n"

# 走代理测试
curl -s --proxy http://127.0.0.1:7890 --connect-timeout 10 \
  https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3 \
  -o /dev/null -w "走代理: HTTP %{http_code}, %{time_total}s\\n"
```

- 直连 200 + 走代理 000 → **代理冲突**，启动网关前去代理
- 都 000 → 网络不通

**修复**：修改 s6 run 脚本，启动前 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`

### Token 验证失败

**症状**：gateway log 报 token 相关错误

**检查**：
```bash
# 确认 Token 完整（长 hex 不应被截断）
cat ~/.hermes/.env | grep WEIXIN_TOKEN

# 确认格式为 bot_id:完整hex
```

### 消息发出去没回复

```bash
# 查 agent 日志
tail -20 /opt/data/logs/agent.log

# 查 gateway 日志
tail -20 /opt/data/logs/gateway.log

# 确认 gateway 进程存活
ps aux | grep "hermes gateway run"
```

### 限流

微信 iLink 有频率限制。症状：日志出现 `rate limited`，消息发不出去。

**修复**：重启 gateway 断开限流循环：
```bash
pkill -f "hermes gateway run"
rm -f /opt/data/gateway.lock /opt/data/gateway_state.json
HERMES_ALLOW_ROOT_GATEWAY=1 hermes gateway run --replace
```

等待 1-2 分钟让计数器复位。
