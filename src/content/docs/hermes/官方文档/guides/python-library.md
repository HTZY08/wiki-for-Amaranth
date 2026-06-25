---
title: Python Library
---

## 关键构造参数（Key Constructor Parameters）

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `model` | `str` | `""` | OpenRouter 格式的模型（默认为空；运行时从你的 Hermes 配置中解析） |
| `quiet_mode` | `bool` | `False` | 抑制 CLI 输出 |
| `enabled_toolsets` | `List[str]` | `None` | 白名单特定工具集 |
| `disabled_toolsets` | `List[str]` | `None` | 黑名单特定工具集 |
| `save_trajectories` | `bool` | `False` | 将对话保存为 JSONL |
| `ephemeral_system_prompt` | `str` | `None` | 自定义系统提示（不会保存到轨迹中） |
| `max_iterations` | `int` | `90` | 每次对话的最大工具调用迭代次数 |
| `skip_context_files` | `bool` | `False` | 跳过加载 `AGENTS.md` 文件 |
| `skip_memory` | `bool` | `False` | 禁用持久化内存读写 |
| `api_key` | `str` | `None` | API 密钥（回退到环境变量） |
| `base_url` | `str` | `None` | 自定义 API 端点 URL |
| `platform` | `str` | `None` | 平台提示（`"discord"`、`"telegram"` 等） |

---

--- body ---
--- body ---
## 重要说明

:::tip
- 如果不想将工作目录中的 `AGENTS.md` 文件加载到系统提示中，请设置 **`skip_context_files=True`**。
- 设置 **`skip_memory=True`** 可阻止代理（Agent）读取或写入持久化内存 —— 推荐用于无状态 API 端点。
- `platform` 参数（例如 `"discord"`、`"telegram"`）会注入特定于平台的格式化提示，使代理能够调整其输出风格。
:::

:::warning
- **线程安全性**：每个线程或任务创建一个 `AIAgent`。切勿在并发调用之间共享实例。
- **资源清理**：对话结束时，代理会自动清理资源（终端会话、浏览器实例）。如果在长时间运行的进程中运行，请确保每次对话正常完成。
- **迭代限制**：默认 `max_iterations=90` 是一个较为宽裕的值。对于简单的问答场景，可考虑降低此值（例如 `max_iterations=10`），以防止工具调用循环失控并控制成本。
:::