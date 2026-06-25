---
title: 密钥管理
description: Hermes Agent 官方文档汉化版
---

> 本文档基于 [Hermes Agent 官方文档](https://hermes-agent.nousresearch.com/docs/) 汉化
> 原文地址: [`user-guide/secrets/index.md`](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/secrets/index.md)
> 本版本为自用学习用途，非官方翻译。

# Secrets

Hermes can pull API keys from external secret managers at process startup instead of storing them in `~/.hermes/.env`. The bootstrap token for the secret manager lives in `.env`; every other provider key (OpenAI, Anthropic, OpenRouter, etc.) can stay in the manager and rotate centrally.

Supported:

- [Bitwarden Secrets Manager](./bitwarden) — `bws` CLI, lazy-installed, free tier works.

More backends (Vault, AWS Secrets Manager, 1Password CLI) are easy to add behind the same interface — the lift is one module in `agent/secret_sources/` and one CLI handler. File a request if you have a specific one in mind.
