---
title: 多模型路由
description: 从 backbone 到 fallback 到 custom provider 的完整配置方案
---

Hermes 支持同时配置多个 AI 模型，按任务自动路由。目的：简单任务用便宜模型省钱，复杂任务用好模型保证质量。

## 三层路由机制

Hermes 没有显式的 `model_router` 配置节——路由通过以下三层隐式实现：

### 第一层：主模型（backbone）

```yaml
model:
  provider: deepseek
  default: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1
  vision:
    provider: custom
    model: gpt-4o-mini
    base_url: https://api.apiyi.com/v1
```

`vision` 子配置单独指定视觉模型——当 backbone 无原生视觉能力时路由到别的模型。

### 第二层：Fallback Provider（断网兜底）

```yaml
fallback_providers:
  - provider: qwen-cpt
    model: qwen3-8b-cpt
```

触发条件：429（限流）、529/503（不可用）、连接失败（DNS/超时）。本地部署的模型作为最后一层兜底。

注意：Fallback 配置修改需要新会话才能生效，不能热加载。

### 第三层：Custom Provider（额外 API）

```yaml
custom_providers:
  - name: qwen-cpt
    base_url: http://127.0.0.1:8001/v1
    api_key: not-needed
  - name: xiaomi
    base_url: https://token-plan-cn.xiaomimimo.com/v1
    api_key_env: XIAOMI_API_KEY
    models:
      - mimo-v2.5-pro
      - mimo-v2.5
      - mimo-v2-omni
```

`custom_providers` 可以注册任意 OpenAI 兼容的 API。注册后可在 skill 或代码中通过 `model: xiaomi/mimo-v2.5` 引用。

## 各模型定位

| 模型 | 角色 | 调用占比 | 用途 |
|------|------|---------|------|
| DeepSeek V4 Flash | backbone | ~80% | 日常对话、中文、轻量编码 |
| Claude Opus 4.x | 攻坚 | ~10% | 复杂架构、高难度调试 |
| Gemini 3 Pro / GPT 5.x | 多模态 | ~10% | 数学、长文档、图片理解 |

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

## 手动指定模型

临时切换，仅当前对话生效：

```bash
hermes --model claude-sonnet-4 "帮我分析这个架构的缺陷"
```

## API 中转配置

直连海外 API 不稳定时：

```yaml
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
    base_url: "https://你的中转地址/v1"
    models:
      - name: gpt-5.4
```

中转服务常见选项：API Yi、PackyAPI、OpenRouter。中转地址不带 `/v1` 会导致 404。
