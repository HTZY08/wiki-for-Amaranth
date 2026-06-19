---
title: 配置指南
description: 从 API Key 到完整生产配置，覆盖新手入门和老手参考
---

## 配置文件位置

主配置位于 `~/.hermes/config.yaml`。Docker 部署时映射自宿主机。

```bash
nano ~/.hermes/config.yaml
```

如文件不存在，复制示例：`cp config.example.yaml ~/.hermes/config.yaml`

## 配置 AI 模型

### 获取 API Key

注册服务商 → 控制台 → API Keys → 创建 Key（通常以 `sk-` 开头）。

### 单模型配置

```yaml
providers:
  deepseek:
    api_key: "sk-你...的key"
    models:
      - name: deepseek-chat
        type: chat
```

### 多模型配置

```yaml
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    models:
      - name: deepseek-v4-flash
        type: chat
  openai:
    api_key: ${OPENAI_API_KEY}
    models:
      - name: gpt-5.4
        type: chat
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    models:
      - name: claude-sonnet-4
        type: chat
```

### 使用环境变量（推荐）

API Key 写在配置文件里容易误提交到 Git：

```yaml
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
```

在 `.env` 文件中设置：

```bash
# ~/.hermes/.env
DEEPSEEK_API_KEY=sk-<your-key>
OPENAI_API_KEY=sk-<your-key>
ANTHROPIC_API_KEY=sk-ant-<your-key>
```

### 基础参数

```yaml
agent:
  name: "hermes"
  instructions: "你是一个 AI 助手"
```

## Docker Compose 模板

```yaml
version: "3.8"
services:
  hermes:
    image: ghcr.io/nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    volumes:
      - /opt/data:/opt/data
      - /opt/data/home:/home
    environment:
      - TZ=Asia/Shanghai
    env_file:
      - /opt/data/.env
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## .env 完整模板

```bash
# ── AI 模型 API ──
DEEPSEEK_API_KEY=sk-<your-key>
OPENAI_API_KEY=sk-<your-key>
ANTHROPIC_API_KEY=sk-ant-<your-key>

# ── 国内 API 中转 ──
APIYI_API_KEY=sk-<your-key>
SILICONFLOW_API_KEY=sk-<your-key>

# ── 微信 iLink Bot ──
WEIXIN_ACCOUNT_ID=<your_bot_id>@im.bot
WEIXIN_TOKEN=<your_token>
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com
WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c
WEIXIN_DM_POLICY=pairing
WEIXIN_ALLOW_ALL_USERS=true

# ── 其他 ──
CLOUDFLARE_API_TOKEN=<your-token>
TZ=Asia/Shanghai
```
