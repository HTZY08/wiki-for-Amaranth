---
title: 配置模板参考
description: Docker/环境变量/CI/代理等配置模板，隐去敏感信息
---

> 所有 `<占位符>` 需要替换为实际值。敏感信息已隐去。

---

## Docker Compose

```yaml
version: "3.8"

services:
  hermes:
    image: ghcr.io/nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /opt/data:/opt/data          # 宿主目录映射
      - /opt/data/home:/home         # home 目录
    environment:
      - TZ=Asia/Shanghai
      - HERMES_HOME=/opt/data        # Hermes 配置目录
    env_file:
      - /opt/data/.env               # API Key 等敏感信息
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]     # GPU 透传（按需）
    network_mode: bridge
```

---

## 环境变量 (.env)

```bash
# ── AI 模型 API ──
DEEPSEEK_API_KEY=sk-<your_deepseek_key>
OPENAI_API_KEY=sk-<your_openai_key>
ANTHROPIC_API_KEY=sk-ant-<your_anthropic_key>

# ── 国内 API 中转 ──
APIYI_API_KEY=sk-<your_apyyi_key>
SILICONFLOW_API_KEY=sk-<your_siliconflow_key>

# ── 微信 iLink Bot ──
WEIXIN_ACCOUNT_ID=<your_bot_id>@im.bot
WEIXIN_TOKEN=<your_bot_id>@im.bot:<hex_token>
WEIXIN_BASE_URL=https://ilinkai.weixin.qq.com
WEIXIN_CDN_BASE_URL=https://novac2c.cdn.weixin.qq.com/c2c
WEIXIN_DM_POLICY=pairing
WEIXIN_ALLOW_ALL_USERS=true

# ── Cloudflare ──
CLOUDFLARE_API_TOKEN=<your_cf_token>

# ── 其他 ──
TZ=Asia/Shanghai
```

---

## Hermes 配置 (config.yaml)

```yaml
# ~/.hermes/config.yaml 或 /opt/data/config.yaml

gateway:
  enabled: true
  platforms:
    weixin:
      enabled: true

cron:
  enabled: true
  max_concurrent: 3

# 视觉模型配置
model:
  vision: provider=custom, model=qwen-vl-plus, base_url=<中转地址>/v1, api_key=$APIYI_API_KEY
auxiliary:
  vision: provider=custom, model=qwen-vl-plus, base_url=<中转地址>/v1, api_key=$APIYI_API_KEY
```

---

## GitHub Actions CI/CD

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      deployments: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy dist --project-name <项目名> --branch main
```

---

## 代理配置 (mihomo / Clash Meta)

```yaml
# /opt/data/mihomo-config/config.yaml

proxies:
  - name: "US-出口"
    type: <协议>
    server: <服务器地址>
    port: <端口>
    cipher: chacha20-ietf-poly1305
    password: "<密码>"
    udp: true

proxy-groups:
  - name: "AI出口"
    type: select
    proxies:
      - "US-出口"
      - DIRECT

rules:
  # 国内 API 直连
  - DOMAIN-SUFFIX,siliconflow.cn,DIRECT
  - DOMAIN-SUFFIX,weixin.qq.com,DIRECT
  
  # AI API 走代理
  - DOMAIN-SUFFIX,openai.com,AI出口
  - DOMAIN-SUFFIX,anthropic.com,AI出口
  - DOMAIN-SUFFIX,deepseek.com,AI出口
  
  # 默认直连
  - MATCH,DIRECT
```

---

## NVIDIA Container Toolkit

GPU 透传安装步骤：

```bash
# WSL2 / Linux
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 验证
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

## s6 Gateway Run 脚本

```bash
#!/bin/command/execlinecd -P

# /run/service/gateway-default/run

# ⚠️ WeChat iLink 必须直连（代理连不上 weixin.qq.com）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

exec s6-setuidgid hermes hermes gateway run
```

---

## Astro + Starlight 配置

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://<你的域名>.pages.dev',
  integrations: [starlight({
    title: '<站点名>',
    defaultLocale: 'root',
    locales: {
      root: { label: '简体中文', lang: 'zh-cn' },
    },
    sidebar: [
      { label: '🏠 首页', link: '/' },
      // 你的导航项
    ],
  })],
});
```
