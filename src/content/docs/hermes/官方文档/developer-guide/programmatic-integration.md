---
title: "Programmatic Integration"
---

## 模型热切换（Model hot-swapping）

会话中的模型切换适用于所有界面 —— 其底层是通过 `/model` 斜杠命令实现的。

- **CLI / TUI:** `/model claude-sonnet-4` 或 `/model openrouter:anthropic/claude-sonnet-4.6`
- **TUI 网关 RPC:** 使用 `command.dispatch`，参数为 `{"command": "/model claude-sonnet-4"}`
- **ACP:** IDE 将斜杠命令作为提示（prompt）发送；代理（agent）进行分发
- **API 服务器:** 在请求体中包含 `model` 字段，或设置 `X-Hermes-Model`

内置了提供商感知的解析功能（相同的模型名称会根据当前提供商自动选择正确的格式）。参见 `hermes_cli/model_switch.py`。

---

## 关于 `--mode rpc` 的说明

Hermes 没有 `--mode rpc` 标志。上述三种协议已涵盖所有用例 —— ACP 用于 IDE 协议客户端，TUI 网关用于 stdio JSON-RPC 主机，API 服务器用于 HTTP。如果你发现存在实际缺口且无协议可填补，请提出 issue，并注明你正在构建的具体消费者（consumer）。