---
title: 代理配置
description: 配置网络代理——让 Hermes 能访问海外 AI API
---

Hermes Agent 需要调用海外 AI 服务（如 OpenAI、Anthropic），在国内网络环境下需要配置代理。

> **⚠️ 2026-07-23 更新**：mihomo 已停用，机场暂停。VPS 自建代理（HostDare 100.117.231.9:8888）也未运行。本机当前**无可用出墙代理**。以下内容为历史配置记录，恢复代理时参考。

> 如果你在海外服务器部署，或使用国内可直连的 AI 服务商（如 DeepSeek 硅基流动），可以跳过本配置。

---

## 原理

```
Hermes 容器 → HTTP 代理 → 海外出口 → AI API 服务
```

代理是一个中间服务，负责把网络请求转发到海外。Hermes 使用 mihomo（Clash Meta 内核）作为代理服务。

## 第一步：准备代理订阅

你需要一个代理服务商的订阅链接（通常在购买代理服务后，服务商会提供一个 URL，以 `https://` 开头）。

> 本手册不推荐具体服务商。自行搜索"Clash 订阅"、"机场订阅"了解。

## 第二步：配置代理文件

创建代理配置文件 `mihomo-config.yaml`：

```yaml
# mihomo-config.yaml
port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: info

# 代理节点（从订阅 URL 获取）
proxies:
  # 这里的内容通常由订阅自动生成

# 代理组
proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - 你的节点名称

# 规则 —— 哪些走代理，哪些直连
rules:
  - DOMAIN-SUFFIX,openai.com,Proxy
  - DOMAIN-SUFFIX,anthropic.com,Proxy
  - DOMAIN-SUFFIX,api.github.com,Proxy
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
```

### 使用订阅自动生成

大多数代理服务商提供"Clash 配置文件下载"。可以直接保存为 `mihomo-config.yaml` 使用。

```bash
# 用订阅 URL 下载配置
curl -o mihomo-config.yaml "你的订阅链接"
```

## 第三步：配置 Docker Compose

在 `docker-compose.yml` 中添加代理容器：

```yaml
services:
  hermes:
    # ... 其他配置 ...
    environment:
      - http_proxy=http://mihomo:7890
      - https_proxy=http://mihomo:7890
    depends_on:
      - mihomo

  mihomo:
    image: ghcr.io/metacubex/mihomo:latest
    container_name: mihomo
    volumes:
      - ./mihomo-config.yaml:/root/.config/mihomo/config.yaml
    ports:
      - "7890:7890"
      - "9090:9090"  # 控制面板端口
    cap_add:
      - NET_ADMIN
```

## 第四步：启动并验证

```bash
# 重新创建容器（加上了 mihomo 服务）
docker compose up -d
```

```bash
# 验证代理连通性
docker exec hermes-agent curl -x http://mihomo:7890 -I https://api.openai.com
```

应该返回 `HTTP/2 200` 或类似的状态码。

### 配置校验清单

配置完成后逐项检查：

| 检查项 | 命令 | 通过标志 |
|--------|------|---------|
| mihomo 进程运行 | `docker compose ps mihomo` | 状态为 `Up` |
| 代理端口监听 | `curl -x http://127.0.0.1:7890 -I https://www.google.com` | 返回 `200` 或 `3xx` |
| AI API 可达 | `docker exec hermes-agent curl -x http://mihomo:7890 -I https://api.openai.com` | 返回 `200` 或 `401`（401 说明通到了，是 key 问题） |
| 规则生效 | `curl -x http://127.0.0.1:7890 -I https://www.baidu.com` | 返回 `200`（国内网站不走代理） |

## 锁定出口地区（可选）

AI 服务商可能有地域限制。可以在配置中指定出口地区：

```yaml
proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - 美国节点  # 选择美国节点以确保兼容性
```

## 调试代理

### 查看代理状态

```bash
# 查看 mihomo 日志
docker compose logs mihomo

# 查看连接的节点
curl http://localhost:9090/proxies
```

### 测试延迟

```bash
# 测试代理延迟
curl -x http://127.0.0.1:7890 -o /dev/null -s -w "%{time_total}s\n" https://www.google.com
```

### 常见问题

**问题：代理无法连接**
> 检查订阅是否过期。
> `docker compose logs mihomo` 看具体错误。

**问题：部分网站能上，AI API 连不上**
> 检查规则配置，确保 AI 服务商的域名走代理。
> 试试把 `MATCH,Proxy` 改为全部走代理。

**问题：国内网站打不开**
> 检查 GEOIP 规则是否生效。
> 可以在规则中添加：`DOMAIN-SUFFIX,baidu.com,DIRECT`

---

## 下一步

配置完成后，进入 **[配置指南](/hermes/配置/configuration/)** 设置 API Key。
