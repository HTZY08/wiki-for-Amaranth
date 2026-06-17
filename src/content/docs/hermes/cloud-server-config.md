---
title: 云服务器配置快照
description: 腾讯云轻量服务器上 Hermes + mihomo + 微信网关的完整配置快照
---

> 给朋友配置的云服务器，作为 24h 在线的微信助手主机。

## 服务器规格

| 项目 | 值 |
|:----|:---:|
| 规格 | 4核 4G 3Mbps |
| 磁盘 | 40GB SSD |
| OS | Ubuntu 24.04 LTS |
| Docker | yes |
| 费用 | ¥99/年（首单优惠） |

## 服务组件

| 组件 | 版本/配置 | 状态 |
|:----|:---------|:----:|
| **mihomo** | 最新，http://172.17.0.2:7890 | ✅ |
| **Hermes** | v0.16.0，venv 隔离 | ✅ |
| **主模型** | mimo-v2.5-pro（小米 MiMo） | ✅ |
| **Hindsight Lite** | v0.5.6，port 8888 | ✅ |
| **Playwright** | v1.60.0 + Chromium | ✅ |
| **微信网关** | iLink Bot 协议 | ✅ |
| **Skills** | 354 个（31 分类） | ✅ |
| **Memory** | 24K / 12K chars | ✅ |

## 部署时间线

| 日期 | 事件 |
|:----|:-----|
| 2026-06-15 | 购买腾讯云轻量服务器（首单 ¥99/年） |
| 2026-06-16 | SSH 基础环境搭建：Docker、Python、Git |
| 2026-06-16 | mihomo 代理容器部署，花云订阅接入 |
| 2026-06-16 | Hermes v0.16.0 安装（venv + pip） |
| 2026-06-16 | Playwright + Chromium 浏览器安装 |
| 2026-06-16 | 微信 iLink 网关扫码上线 |
| 2026-06-16 | Skills 全量推送（SCP 354 个） |
| 2026-06-16 | Token Plan key 替换修复 |
| 2026-06-16 | XIAOMI_BASE_URL 配置修复（tp-key 必须配专属 endpoint） |

## 微信网关配置

### 字段映射

| iLink API 字段 | .env 变量 | 说明 |
|:--------------|:---------|:-----|
| `ilink_bot_id` | `WEIXIN_ACCOUNT_ID` | 完整值如 xxx@im.bot |
| `bot_token` | `WEIXIN_TOKEN` | 完整字符串，不分拆 |
| 固定值 | `WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com` | 必填 |
| 固定值 | `WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c` | 建议加 |
| 固定值 | `WEIXIN_DM_POLICY=pairing` | 建议加 |
| 固定值 | `GATEWAY_ALLOW_ALL_USERS=true` | 不加拒收 |

**不要写旧版字段**：`WEIXIN_APP_ID`、`WEIXIN_APP_SECRET`、`WEIXIN_AES_KEY`

### 扫码流程

二维码有效期仅 ~120 秒。推荐流程：

1. 用户在微信准备好
2. 出码：发 iLink URL 或生成二维码图片
3. 立即转发给用户扫码
4. 后台轮询 `get_qrcode_status`（2s 间隔），自动读取凭证写入 `.env`

### 常见 Token Plan key 坑

`tp-` 开头的 key 必须显式设置环境变量：

```bash
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

`config.yaml` 里的 `base_url` 对 xiaomi provider **不生效**——auth.py 只读 `XIAOMI_BASE_URL` 环境变量。不加则走到默认 endpoint，Token Plan key 被拒 → 401。

## 代理配置

### 容器拓扑

```
┌──────────────────────────┐     ┌──────────────────────┐
│  Hermes 容器              │     │  mihomo 容器          │
│  http_proxy ──────────────┼──►  │  172.17.0.2:7890     │
│  no_proxy: .cn, .qq.com  │     │  API: 172.17.0.2:9090│
└──────────────────────────┘     └──────────────────────┘
```

### 订阅更新脚本

```bash
# /opt/data/update_sub.sh
# 每周日凌晨 3 点自动执行（cron）
bash /opt/data/update_sub.sh "<新订阅URL>"
```

### 节点切换

```bash
# 切到美国出口（流式大 payload 更稳定）
curl -X PUT http://172.17.0.2:9090/proxies/Proxies \
  -H "Content-Type: application/json" \
  -d '{"name":"US"}'
curl -X PUT http://172.17.0.2:9090/proxies/US \
  -H "Content-Type: application/json" \
  -d '{"name":"🇺🇸 美国实验性 IEPL 专线 1"}'
```

## 已知缺陷

### mihomo 二进制名问题

Docker 内 mihomo 的二进制路径不是 `/usr/bin/mihomo` 而是 `/clash`，配置目录在 `/root/.config/clash/`。Docker bind mount 时需要注意路径映射。
修复方式：改用 Docker volume `mihomo-config-vol`，通过 `docker exec -i` 的 stdin 管道写入配置。

### 内存限制

单个 Hermes 实例占用 ~1.5-2GB RAM。4G 服务器同时跑 Hermes + mihomo + Hindsight 已接近满载，不建议在同一台服务器上再跑双微信实例或其他重型服务。

## 状态检查

```bash
# 一键全览
docker ps && \
  curl -sf http://localhost:8888/health && \
  df -h / && \
  free -h && \
  ps aux | grep -c "hermes" | tail -1
```

## 故障排查

| 现象 | 原因 | 解决 |
|:----|:-----|:-----|
| 微信消息无响应 | 代理环境污染 | `unset http_proxy https_proxy` 后重启 gateway |
| 模型返回 401 | Token Plan key 过期 | 小米平台重新生成，更新 `.env` |
| mihomo 配置丢失 | Docker 重启后 bind mount 失效 | 改用 `mihomo-config-vol` volume |
| 扫码后 Session expired | 旧会话已死 | 重新出码 → 扫码 → 启网关 |
| Chromium 下载慢 | 服务器带宽仅 3Mbps | 或跳过浏览器功能（不影响基础对话） |
