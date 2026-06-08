---
title: 多模型路由
description: 配置多个 AI 模型，按任务自动选择最合适的模型
---

Hermes 支持同时配置多个 AI 模型，根据任务类型自动选择最合适的模型。这样既能省钱（简单任务用便宜模型），又能保证质量（复杂任务用好模型）。

---

## 为什么需要多个模型

不同 AI 模型各有专长：

| 模型 | 特点 | 适合做什么 |
|------|------|-----------|
| DeepSeek V4 Flash | 响应快、价格低 | 日常对话、简单查询、常规任务 |
| GPT-5.x | 编程能力强 | 写代码、重构、调试 |
| Claude Opus | 分析深度好 | 架构设计、复杂分析、长文本 |
| Gemini Pro | 上下文窗口大 | 处理超长文档、多模态输入 |

## 配置多模型

在 `~/.hermes/config.yaml` 中配置多个 provider：

```yaml
providers:
  # 主力模型——处理 80% 的日常任务
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    models:
      - name: deepseek-chat
        type: chat

  # 代码专家——只有写代码时才调用
  openai:
    api_key: ${OPENAI_API_KEY}
    models:
      - name: gpt-4o
        type: chat

  # 深度推理——复杂问题使用
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    models:
      - name: claude-sonnet-4
        type: chat
```

## 路由策略

配置好后，Hermes 会自动按策略选择模型：

```
你发来一个请求
    │
    ├── 日常聊天/简单问题 → DeepSeek（成本最低）
    ├── 编写代码/调试     → GPT（编程最强）
    ├── 深度分析/架构设计 → Claude（分析最深）
    ├── 处理长文档        → Gemini（上下文最大）
    └── 实验性任务        → 其他模型（按配置）
```

## 手动指定模型

你也可以在对话中临时指定用哪个模型：

```bash
# 在 CLI 中
hermes --model claude-opus "帮我分析这个架构的缺陷"

# 在对话中
使用 GPT 帮我写一段 Python 代码
```

## 配置 API 中转

如果直接连接海外 API 不稳定，可以使用中转服务：

```yaml
providers:
  openai:
    api_key: ${OPENAI_API_KEY}
    base_url: "https://你的中转地址/v1"  # 替换为你的中转 URL
    models:
      - name: gpt-4o
```

## 故障排查

### 某个模型报错

```yaml
# 临时禁用有问题的模型
providers:
  openai:
    enabled: false  # 先关掉
```

### 所有模型都超时

检查网络代理是否正常。尝试直接 ping API 地址：

```bash
curl -I https://api.openai.com
```

如果不通，检查[代理配置](/hermes/proxy-setup/)。

### 想切换主力模型

修改 `config.yaml` 中的 `default_model`：

```yaml
agent:
  default_model: gpt-4o  # 把主力模型改成 GPT
```
