---
title: Fallback Providers
---

## 定时任务（Cron Job）提供者

定时任务在创建代理（Agent）时，会继承您配置的 `fallback_providers` 链（或传统的 `fallback_model`）。若要为定时任务使用不同的主要提供者，请在定时任务本身上配置 `provider` 和 `model` 覆盖：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="检查服务器状态",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

完整的配置详情请参阅[计划任务（Cron）](/user-guide/features/cron)。

---

--- body ---
--- body ---
## 总结

| 特性 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主代理模型 | `fallback_providers` 位于 config.yaml — 每次对话出错时故障转移（每次对话恢复主模型） | `fallback_providers:`（顶级列表） |
| 辅助任务（任意）— 自动用户 | 容量错误时自动检测链（先主代理模型，再提供者链） | `auxiliary.<task>.provider: auto` |
| 辅助任务（任意）— 显式提供者 | `fallback_chain`（若设置）→ 主代理模型 → 警告并抛出异常，仅在容量错误时 | `auxiliary.<task>.fallback_chain` |
| 视觉（Vision） | 分层（见上）+ 内部 OpenRouter 重试 | `auxiliary.vision` |
| 网页提取 | 分层（见上）+ 内部 OpenRouter 重试 | `auxiliary.web_extract` |
| 上下文压缩 | 分层（见上）；若所有层均不可用，降级为无摘要 | `auxiliary.compression` |
| 技能中心 | 分层（见上） | `auxiliary.skills_hub` |
| MCP 辅助 | 分层（见上） | `auxiliary.mcp` |
| 审批分类 | 分层（见上） | `auxiliary.approval` |
| 标题生成 | 分层（见上） | `auxiliary.title_generation` |
| 分诊指定器 | 分层（见上） | `auxiliary.triage_specifier` |
| 委派 | 仅提供者覆盖（无自动回退） | `delegation.provider` / `delegation.model` |
| 定时任务 | 仅每个任务的提供者覆盖（无自动回退） | 每个任务的 `provider` / `model` |