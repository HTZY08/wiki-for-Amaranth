---
title: 多模型路由
description: MoE 式多模型调度架构
---

Hermes Agent 采用 MoE（Mixture of Experts）式多模型架构，按任务类型自动分配最合适的 LLM 后端。

## 模型栈

| 模型 | 角色 | 调用量 | 用途 |
|------|------|--------|------|
| **DeepSeek V4 Flash** | 常驻 backbone | ~80-90% | 日常对话、常规任务、CLI 交互 |
| **GPT-5.5** (via Codex) | 代码专家 | 按需 | 代码重构、复杂编程 |
| **Claude Opus** (via PackyAPI) | 推理专家 | 按需 | 架构决策、深度分析 |
| **Gemini Pro** (via APIYi) | 备选推理 | 按需 | 长上下文、特定场景 |
| **Grok/Mistral** (via OpenRouter) | 实验性 | 偶尔 | 测试、对比、特定需求 |

## 路由策略

```
任务请求
    │
    ├── 日常对话/简单查询 → DeepSeek V4 Flash
    ├── 复杂代码/编程     → Codex → GPT-5.5
    ├── 深度分析/架构     → Claude Opus
    ├── 长文档处理        → Gemini Pro
    └── 实验/对比         → OpenRouter (Grok/Mistral)
```

## 配置方式

在 `config.yaml` 中配置多个 provider：

```yaml
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    models:
      - name: deepseek-v4-flash
        type: chat

  openrouter:
    api_key: ${OPENROUTER_API_KEY}
    models:
      - name: openai/gpt-5.5
      - name: x-ai/grok-3
```

通过 CLI 或 Gateway 请求时指定模型：

```bash
hermes --model claude-opus "分析这个架构的缺陷"
```

## 优势

- **成本优化**：80% 调用走便宜的 DeepSeek，硬骨头才调高价模型
- **能力互补**：各取所长——DeepSeek 快，Claude 深，GPT 编码稳
- **容灾**：某个 provider 挂掉时自动 fallback
