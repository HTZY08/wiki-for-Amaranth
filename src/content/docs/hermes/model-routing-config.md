---
title: "多模型路由实战：MoE 方案的 config.yaml 配置"
description: "从 backbone 到攻坚到兜底，Heremes 实际配置全记录"
---

# 多模型路由实战配置

本文记录 Hermes Agent 中实现 MoE（Mixture of Experts）多模型策略的完整配置。不是理论——是本站正在运行的配置。

---

## 一、MoE 策略回顾

```
80% 调用 → DeepSeek V4 Flash（日常：问答、中文、轻量编码）
10% 调用 → Claude Opus 4.7/4.8（攻坚：复杂架构、高难度调试）
10% 调用 → Gemini 3 Pro / GPT-5.4（多模态、数学、长文档）
```

这个策略的前提是：**Hermes 原生支持多 Provider 路由**，不需要第三方代理。

---

## 二、Hermes 的路由机制

Hermes 的路由是**隐式**的。它没有 `model_router` 配置节——而是通过以下三层机制实现的：

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

这是 Hermes 本身使用的模型。大多数对话和工具调用走这里。

`vision` 子配置单独指定视觉模型——因为 DeepSeek V4 Flash 没有原生视觉能力，需要路由到别的模型。

### 第二层：Fallback Provider（断网兜底）

```yaml
fallback_providers:
  - provider: qwen-cpt
    model: qwen3-8b-cpt
```

Hermes 在以下情况自动触发 fallback：
- **429** — Rate Limit
- **529** / **503** — 服务不可用
- **连接失败** — DNS 解析失败、Connection timeout

本地部署的 Qwen3-8B CPT（LoRA 微调版）作为最后一层兜底。

**注意：** Fallback 配置修改需要**新会话**才能生效，不能热加载。

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

`custom_providers` 定义的 Provider 可以在对话中手动切换，或者在 Fallback 时自动选用。

---

## 三、实际配置

### 3.1 主模型

```
DeepSeek V4 Flash（backbone）
→ 通过 deepseek 官方 API
→ 所有日常对话、简单编码、中文问答
→ 成本：$0.14 输入 / $0.28 输出（每百万 token）
```

### 3.2 攻坚模型

通过用户切换（手动 / 对话指令）使用：

- Claude Opus 4.7/4.8 → PackyAPI 代理
- GPT-5.4 → OpenRouter 或 Codex

Hermes 的 `model-switcher` 插件支持在对话中直接切换模型，无需重启。

### 3.3 多模态/视觉

```
主模型 vision 配置 → API Yi（qwen-vl-plus / gemini-2.5-flash-image）
→ 不走 Hermes 原生 vision_analyze（API key 历史问题已修复）
→ Python requests 直调 SiliconFlow
```

### 3.4 本地兜底

```
Watchdog cron（每 3 分钟）→ 检测主 API 可达性
  ├─ 可达 → 什么都不做（0 token）
  └─ 不可达 → 拉起本地推理服务器（端口 8001）
              → Fallback 自动切到 qwen-cpt
              → 网络恢复后切回主模型
```

---

## 四、完整配置清单

```yaml
# ========== 主模型 ==========
model:
  provider: deepseek
  default: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1
  vision:
    provider: custom
    model: gpt-4o-mini
    base_url: https://api.apiyi.com/v1

# ========== Fallback ==========
fallback_providers:
  - provider: qwen-cpt
    model: qwen3-8b-cpt

# ========== 自定义 Provider ==========
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

---

## 五、路由决策流

```
用户输入
  ↓
Hermes 主模型（DeepSeek V4 Flash）处理
  ├─ 正常 → 响应
  ├─ 需要视觉 → 自动路由到 vision provider
  ├─ 429/503/断网 → 触发 Fallback
  │    └─ 本地 Qwen3-8B CPT 处理
  └─ 用户手动切换模型 → 使用指定 Provider
```

这个三层的核心思想：**日常用最便宜的，攻坚用最好的，断网用本地的**。

---

## 六、注意事项

| 事项 | 说明 |
|------|------|
| Fallback 配置不能热加载 | 修改 config.yaml 后需 `/new` 新会话 |
| Vision 不走原生 tool | 因历史遗留问题，视觉理解走 Python 直调 SiliconFlow |
| 本地服务器的加载时间 | Qwen3-8B 4bit 加载约 2 分钟，+ watchdog 延迟约 3-5 分钟 |
| 同容器内用 127.0.0.1 | 不需要 `host.docker.internal` |
| 不同 Provider 的模型不可混用 | 需在各自的 config 段中声明 |
