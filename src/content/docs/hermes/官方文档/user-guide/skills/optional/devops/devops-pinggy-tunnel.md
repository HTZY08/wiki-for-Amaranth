--- frontmatter ---
---
title: "Pinggy Tunnel — 通过 SSH 实现零安装的 localhost 隧道（Pinggy）"
sidebar_label: "Pinggy Tunnel"
description: "通过 SSH 实现零安装的 localhost 隧道（Pinggy）"
---

--- body ---
{/* 此页面由技能目录中的 SKILL.md 文件通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Pinggy Tunnel

通过 SSH 实现零安装的 localhost 隧道（基于 Pinggy）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/devops/pinggy-tunnel` 安装 |
| 路径 | `optional-skills/devops/pinggy-tunnel` |
| 版本 | `0.1.0` |
| 作者 | Teknium (teknium1), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Pinggy`, `Tunnel`, `Networking`, `SSH`, `Webhook`, `Localhost` |
| 相关技能 | `cloudflared-quick-tunnel`, `webhook-subscriptions` |

## 参考：完整 SKILL.md

:::info
以下是当此技能被触发时，Hermes 加载的完整技能定义。这是技能激活时，代理（Agent）看到的指令。
:::

# Pinggy Tunnel 技能

使用 Pinggy SSH 反向隧道将本地服务（开发服务器、Webhook 接收端、MCP 端点、演示应用）暴露到公共互联网。无需安装守护进程——用户已有的 SSH 客户端连接到 `a.pinggy.io:443`，Pinggy 返回一个公共的 HTTP/HTTPS URL。

免费层：60 分钟隧道，随机子域名，无需注册。专业层（每月 3 美元）是可选方案，需使用令牌。

## 何时使用

- 用户要求“将此本地服务暴露”、“分享我的开发服务器”、“让此 URL 公开”、“隧道端口 N”、“为 webhook 获取公共 URL”
- 在本地任务期间需要接收 webhook 回调（Stripe、GitHub、Discord、AgentMail）
- 与远程方共享一次性的 HTTP 演示（MCP 服务器、Ollama/vLLM 端点、仪表盘）
- 主机有 SSH 但没有 `cloudflared`/`ngrok` 二进制文件，安装它们会显得过于复杂

如果主机已经配置了 `cloudflared`，则优先使用 `cloudflared-quick-tunnel` 技能——Cloudflare 快速隧道不会在 60 分钟后过期。

## 先决条件

- 系统 PATH 中包含 `ssh` 命令（可通过 `ssh -V` 检查）。Linux、macOS 和 Windows 10 及以上系统默认包含。无需其他安装。
- 在隧道启动前，本地服务已在 `127.0.0.1:<port>` 上监听。Pinggy 会返回 URL，但如果本地源未启动，将返回 502 错误。

可选：

- `PINGGY_TOKEN` 环境变量，用于付费专业层功能（持久子域名、自定义域名、多隧道、无 60 分钟限制）。免费层无需凭据。

## 快速参考

```bash
# 纯 HTTP/HTTPS 隧道，用于端口 8000（免费层）
ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R0:localhost:8000 free@a.pinggy.io

# TCP 隧道（数据库、原始 SSH 等）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:5432 tcp@a.pinggy.io

# TLS 隧道（Pinggy 无法解密——在源端自带证书）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:443 tls@a.pinggy.io

# 基本认证网关（b:user:pass）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "b:admin:secret+free@a.pinggy.io"

# Bearer 令牌网关（k:token）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "k:mysecrettoken+free@a.pinggy.io"

# IP 白名单（w:CIDR）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "w:203.0.113.0/24+free@a.pinggy.io"

# 启用 CORS + 强制 HTTPS 重定向
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "co+x:https+free@a.pinggy.io"

# 专业层（持久 URL，无 60 分钟限制）
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 "$PINGGY_TOKEN+a.pinggy.io"
```

## 流程——启动隧道并获取 URL

模型（Model）应使用 `terminal` 工具。隧道必须在共享期间保持存活，因此应作为后台进程运行，并从标准输出（stdout）中解析公共 URL。

### 1. 确认本地源已启动

```bash
curl -sI http://127.0.0.1:8000/ | head -1
# 预期结果：HTTP/1.x 200（或任何非连接拒绝的响应）
```

如果还没有任何服务在监听，请先启动它（例如 `python3 -m http.server 8000 --bind 127.0.0.1`）。Pinggy 会愉快地返回一个指向无效地址的 URL——用户将看到 502 错误，直到源服务启动。

### 2. 作为后台进程启动隧道

使用 `terminal(background=True)` 并将输出捕获到日志文件（Pinggy 将 URL 打印到 stdout，然后保持连接打开）：

```bash
LOG=/tmp/pinggy-8000.log
nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -R0:localhost:8000 free@a.pinggy.io \
    > "$LOG" 2>&1 &
echo $! > /tmp/pinggy-8000.pid
```

`StrictHostKeyChecking=no` + `UserKnownHostsFile=/dev/null` 可以跳过首次运行时的主机密钥提示。`ServerAliveInterval=30` 防止空闲 NAT 断开 SSH 会话。

### 3. 从日志中解析 URL

```bash
sleep 4
grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-8000.log | head -1
```

预期输出类似于：

```
You are not authenticated.
Your tunnel will expire in 60 minutes.
http://yqycl-98-162-69-48.a.free.pinggy.link
https://yqycl-98-162-69-48.a.free.pinggy.link
```

将 `https://...pinggy.link` URL 交给用户。

### 4. 验证

```bash
curl -sI https://<the-url>/ | head -3
# 预期结果：200/302 或本地源实际返回的任何状态码
```

如果得到 `502 Bad Gateway`，说明 SSH 会话已建立但本地源未监听——请先修复步骤 1。

### 5. 清理

```bash
kill "$(cat /tmp/pinggy-8000.pid)"
# 或者，如果 pid 文件丢失：
pkill -f 'ssh -p 443 .* free@a\.pinggy\.io'
```

如果从 `terminal(background=True)` 获取了会话 ID，优先使用 `process(action='kill', session_id=...)`。

## 通过用户名关键字进行访问控制

Pinggy 将控制标志通过 `+` 分隔堆叠在 SSH 用户名中。当 `user@host` 参数包含 `+` 时，始终使用引号括起来：

| 关键字 | 效果 |
|---------|--------|
| `b:user:pass` | HTTP 基本认证网关 |
| `k:token` | Bearer 令牌头部网关（`Authorization: Bearer <token>`） |
| `w:CIDR` | IP 白名单（单个 IP 或 CIDR，可重复） |
| `co` | 添加 `Access-Control-Allow-Origin: *`（CORS） |
| `x:https` | 强制 HTTPS——自动将 HTTP 重定向到 HTTPS |
| `a:Name:Value` | 添加请求头部 |
| `u:Name:Value` | 更新请求头部 |
| `r:Name` | 移除请求头部 |
| `qr` | 将 URL 的二维码打印到 stdout（方便移动设备分享） |

可自由组合：`"b:admin:secret+co+x:https+free@a.pinggy.io"`。

## Web 调试器（可选）

Pinggy 可以将入站流量镜像到 `localhost:4300` 以供检查。在 SSH 命令中添加本地转发：

```bash
ssh -p 443 -L4300:localhost:4300 -R0:localhost:8000 free@a.pinggy.io
```

然后在浏览器中打开 `http://localhost:4300` 查看实时的请求/响应对。

## 陷阱

- **免费层有 60 分钟硬限制。** SSH 会话在 60 分钟时终止；URL 失效。如果需要更长时间的共享，请使用 `PINGGY_TOKEN`（专业层）或通过 shell 循环自动重启（注意：免费层每次重启 URL 都会变化）。
- **免费层 URL 是随机的，重启后改变。** 不要将其加入书签，也不要粘贴到配置文件中。每次解析日志。
- **免费层并发隧道限制为每个源 IP 一个。** 从同一台机器启动第二个隧道通常会杀死第一个。专业层解除此限制。
- **用户名中的 `+` 必须用引号括起来。** 裸露的 `ssh ... b:admin:secret+free@a.pinggy.io` 在 bash 中有效，但在将 `+` 特殊处理的 shell 中或通过编程方式组装时可能失效。始终使用双引号包裹。
- **不要在没有访问控制标志的情况下隧道传输任何敏感内容。** 裸 HTTP 隧道任何拥有 URL 的人都可以访问。对于非公共服务，使用 `b:`、`k:` 或 `w:`。
- **`process(action='log')` 可能错过 SSH 横幅输出。** Pinggy 在打印 URL 后 SSH 会话进入交互模式。始终重定向到日志文件并直接使用 `grep` 文件——与 `cloudflared-quick-tunnel` 模式相同。
- **首次运行时的主机密钥提示。** 默认的 OpenSSH 配置会询问用户是否接受 Pinggy 的主机密钥。对于无人值守运行，始终传递 `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null`。
- **TCP 和 TLS 隧道返回 `<subdomain>.a.pinggy.online:<port>` 对，而不是 https URL。** 使用不同的正则表达式（`tcp://` 和端口）进行解析。不要假设每个 Pinggy 隧道都是 HTTP。
- **专业模式需要将令牌作为用户名，而不是标志。** 使用 `"$PINGGY_TOKEN+a.pinggy.io"`（不加 `free@`）。有了令牌，还可以添加 `:persistent` 以获得稳定的子域名——请参阅 `pinggy.io/docs/`。

## 配方

结合本地源和 Pinggy 隧道的复合模式。每个配方都是独立的——启动源，启动隧道，解析 URL，交给用户。

### 配方 1——接收 webhook 回调

当外部服务（Stripe、GitHub、Discord、AgentMail 等）需要在本地任务期间向一个可公开访问的 URL 发送 POST 请求时使用。

```bash
# 1. 小型捕获服务器：每个请求都追加到 /tmp/webhook-hits.log
cat >/tmp/webhook-server.py <<'PY'
import http.server, json, datetime, pathlib
LOG = pathlib.Path("/tmp/webhook-hits.log")
class H(http.server.BaseHTTPRequestHandler):
    def _capture(self):
        n = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        rec = {"t": datetime.datetime.utcnow().isoformat(), "path": self.path,
               "method": self.command, "headers": dict(self.headers), "body": body}
        with LOG.open("a") as f: f.write(json.dumps(rec) + "\n")
        self.send_response(200); self.send_header("content-type","application/json")
        self.end_headers(); self.wfile.write(b'{"ok":true}\n')
    def do_GET(self): self._capture()
    def do_POST(self): self._capture()
    def log_message(self,*a,**k): pass
http.server.HTTPServer(("127.0.0.1", 18080), H).serve_forever()
PY
nohup python3 /tmp/webhook-server.py >/tmp/webhook-server.log 2>&1 &
echo $! >/tmp/webhook-server.pid

# 2. 隧道——使用 Bearer 令牌网关，防止无关人员污染捕获日志
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:18080 "k:$(openssl rand -hex 12)+free@a.pinggy.io" \
    >/tmp/webhook-pinggy.log 2>&1 &
echo $! >/tmp/webhook-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/webhook-pinggy.log | head -1)
echo "Webhook URL: $URL"

# 3. 在代理工作期间，查看命中记录
tail -f /tmp/webhook-hits.log
```

将 `$URL` 交给需要调用您的服务。清理：`kill $(cat /tmp/webhook-server.pid) $(cat /tmp/webhook-pinggy.pid)`。

### 配方 2——通过 HTTP/SSE 暴露 MCP 服务器

当远程 MCP 客户端（另一台机器上的 Claude Desktop、队友的编辑器等）需要访问本地机器上运行的 MCP 服务器时使用。仅适用于使用 HTTP 传输的 MCP 服务器——stdio 模式的服务器无法通过隧道传输。

```bash
# 1. 以 HTTP 模式启动 MCP 服务器（示例：FastMCP 服务器，端口 8765）
nohup python3 my_mcp_server.py --transport http --port 8765 \
    >/tmp/mcp-server.log 2>&1 &
echo $! >/tmp/mcp-server.pid

# 2. 使用 Bearer 令牌进行隧道——MCP 流量不应暴露在互联网上
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:8765 "k:$TOKEN+free@a.pinggy.io" \
    >/tmp/mcp-pinggy.log 2>&1 &
echo $! >/tmp/mcp-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/mcp-pinggy.log | head -1)
echo "MCP URL: $URL"
echo "Bearer token: $TOKEN"
```

远程客户端使用 `Authorization: Bearer $TOKEN` 连接到 `$URL`。Hermes 自身的原生 MCP 客户端配置：`{"transport": "http", "url": "<URL>", "headers": {"Authorization": "Bearer <TOKEN>"}}`。

### 配方 3——暴露本地 LLM 端点（Ollama / vLLM / llama.cpp）

与远程调用者（另一个代理、手机、队友）共享本地模型。Ollama 监听 `:11434`，vLLM 和 llama.cpp 通常监听 `:8000`。

```bash
# 前置条件：模型服务器已在 127.0.0.1:11434 上运行（Ollama 默认端口）
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:11434 "k:$TOKEN+co+free@a.pinggy.io" \
    >/tmp/llm-pinggy.log 2>&1 &
echo $! >/tmp/llm-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/llm-pinggy.log | head -1)
echo "端点（Endpoint）: $URL"
echo "令牌（Token）:    $TOKEN"

# 验证
curl -s "$URL/api/tags" -H "Authorization: Bearer $TOKEN" | head
```

`co` 启用 CORS，以便浏览器调用者能够访问端点。对于仅后端调用者，可省略 `co`。对于 OpenAI 兼容的 vLLM/llama.cpp 端点，调用者使用基础 URL `$URL/v1` 并携带 `Authorization: Bearer $TOKEN`——但请注意，Pinggy 不会修改或替换请求体中的任何内容，因此模型服务器本身会看到 Pinggy 的令牌；本地服务器应配置为忽略认证（因为它已经在 `127.0.0.1` 上），让 Pinggy 负责网关控制。

### 配方 4——使用一次性密码共享开发服务器

最快的“让队友试用我运行中的应用”模式。随机密码，仅打印一次，Ctrl-C 时终止。

```bash
PASS=$(openssl rand -base64 12 | tr -d '+/=' | head -c 12)
echo "开发服务器密码：$PASS"
ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:3000 "b:dev:$PASS+co+x:https+free@a.pinggy.io"
# URL 打印到终端。分享 URL + 密码。Ctrl-C 清理。
```

`b:dev:$PASS` 使用 HTTP 基本认证对 URL 进行网关保护。`x:https` 强制使用 TLS。`co` 为 SPA 前端添加 CORS。

## 验证

```bash
# 端到端：启动一个简单的源，建立隧道，访问它，然后清理
python3 -m http.server 18000 --bind 127.0.0.1 >/tmp/origin.log 2>&1 &
ORIGIN_PID=$!

nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -R0:localhost:18000 free@a.pinggy.io >/tmp/pinggy-verify.log 2>&1 &
SSH_PID=$!

sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-verify.log | head -1)
echo "URL: $URL"
curl -sI "$URL/" | head -1

kill "$SSH_PID" "$ORIGIN_PID"
```

预期结果：一个 `pinggy.link` URL，以及 curl 头部返回 `HTTP/2 200`。