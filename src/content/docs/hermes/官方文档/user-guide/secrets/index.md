--- frontmatter ---
---
title: 密钥管理
description: Hermes Agent 官方文档汉化版
---

--- body ---
# 密钥（Secrets）

Hermes 可以在进程启动时从外部密钥管理器（secret managers）拉取 API 密钥，而不是将其存储在 `~/.hermes/.env` 中。密钥管理器的引导令牌（bootstrap token）位于 `.env` 中；所有其他提供商密钥（如 OpenAI、Anthropic、OpenRouter 等）可以保留在密钥管理器中并集中轮换。

支持：

- [Bitwarden 密钥管理器](./bitwarden) — `bws` CLI，惰性安装，免费版即可使用。

更多后端（Vault、AWS Secrets Manager、1Password CLI）可以轻松通过同一接口添加——只需在 `agent/secret_sources/` 中添加一个模块和一个 CLI 处理器即可。如果您有特定的需求，请提交请求。