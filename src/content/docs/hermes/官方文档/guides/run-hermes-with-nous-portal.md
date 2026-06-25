---
sidebar_position: 1
title: "使用 Nous Portal 运行 Hermes Agent"
description: "从头到尾的指导：订阅、设置、切换模型、启用网关工具和验证路由"
---

# 使用 Nous Portal 运行 Hermes Agent

本指南将引导你从头到尾在 [Nous Portal](https://portal.nousresearch.com) 订阅上运行 Hermes Agent——从注册到验证每个工具正确路由。如果你只想了解 Portal 的概览和订阅内容，请参阅 [Nous Portal 集成页面](/integrations/nous-portal)。本页是操作脚本。

## 前置条件

- 已安装 Hermes Agent（[快速入门](/getting-started/quickstart)）
- 在配置机器上有一个浏览器（或 SSH 端口转发——参见 [通过 SSH 使用 OAuth](/guides/oauth-over-ssh)）
- 大约 5 分钟

你**不需要**：OpenAI 密钥、Anthropic 密钥、Firecrawl 账户、FAL 账户、Browser Use 账户或任何其他按厂商的凭据。这正是关键所在。

## 1. 获取订阅

打开 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)，注册并选择一个套餐。

已经订阅了？跳至第 2 步。

## 2. 运行一键设置

```bash
hermes setup --portal
```

这个单一命令完成五件事：

1. 打开浏览器到 portal.nousresearch.com 进行 OAuth 登录
2. 将刷新令牌存储到 `~/.hermes/auth.json`
3. 在 `~/.hermes/config.yaml` 中将 `model.provider` 设置为 `nous`
4. 选择一个默认的代理模型（`anthropic/claude-sonnet-4.6` 或类似的）
5. 为网页搜索、图像生成、TTS 和浏览器自动化启用工具网关（Tool Gateway）

完成后，你会回到终端，准备好聊天。

### 如果我通过 SSH 连接到服务器怎么办？

OAuth 需要浏览器，但回环回调在运行 Hermes 的机器上执行。有两个选项：

```bash
# 选项 A：SSH 端口转发（推荐）
ssh -N -L 8642:127.0.0.1:8642 user@remote-host    # 在本地终端中运行
hermes setup --portal                              # 在远程端，在本地浏览器中打开打印的 URL

# 选项 B：手动粘贴（适用于 Cloud Shell、Codespaces、EC2 Instance Connect）
hermes auth add nous --type oauth --manual-paste
# 然后重新运行 `hermes setup --portal` 来配置提供者和网关
```

完整操作步骤（包括 ProxyJump 链、mosh/tmux 和 ControlMaster 陷阱）请参阅 [通过 SSH / 远程主机使用 OAuth](/guides/oauth-over-ssh)。

## 3. 验证是否成功

```bash
hermes portal info
```

你应该看到：

```
  Nous Portal
  ───────────
  认证:    ✓ 已登录
  Portal:  https://portal.nousresearch.com
  模型:    ✓ 使用 Nous 作为推理提供者

  工具网关
  ────────────
  网页搜索与提取  通过 Nous Portal
  图像生成        通过 Nous Portal
  文本转语音      通过 Nous Portal
  浏览器自动化    通过 Nous Portal
```

如果任何一行显示的不是“通过 Nous Portal”，或者认证行显示“未登录”，请跳至下面的[故障排除](#故障排除)。

## 4. 运行你的第一次对话

```bash
hermes chat
```

尝试一些同时调用模型和工具网关的问题：

```
嘿，搜索网页查找“Hermes Agent release notes”并总结前 3 条结果。
```

你应该看到 Hermes 调用 `web_search`（基于 Firecrawl，通过网关）并用摘要回复。如果搜索运行并且回复合理，你就完成了——Portal 已端到端连接。

## 5. 选择你真正想要的模型

`hermes setup --portal` 允许你在设置期间选择模型，但订阅的关键在于可以使用完整目录——随时在会话中使用 `/model` 切换：

```bash
/model anthropic/claude-sonnet-4.6     # 最佳通用代理模型
/model openai/gpt-5.4                  # 强推理 + 工具调用
/model google/gemini-2.5-pro           # 大上下文窗口
/model deepseek/deepseek-v3.2          # 高性价比编码模型
/model anthropic/claude-opus-4.6       # 专为复杂问题设计的重量级模型
```

或者打开选择器浏览：

```bash
/model
```

永久更改默认模型：

```bash
# 在终端中，任何会话之外
hermes config set model.default anthropic/claude-sonnet-4.6
```

### 不要为代理工作选择 Hermes-4

Hermes-4-70B 和 Hermes-4-405B 可在 Portal 上以大幅折扣获得，但它们是**聊天/推理模型**，而非针对工具调用调整的模型。它们在多步骤代理循环中会表现不佳。通过 [Nous Chat](https://chat.nousresearch.com) 将它们用于对话/研究工作，或通过[订阅代理](/user-guide/features/subscription-proxy) 从非代理工具中使用它们。对于 Hermes Agent 本身，请坚持使用上面的前沿代理模型。

Portal 自己的[信息页面](https://portal.nousresearch.com/info)也包含此警告——这是官方的 Nous 指导，而不仅仅是 Hermes 侧的意见。

## 6.（可选）自定义工具网关路由

网关是按工具选择性加入的，而非全有或全无。如果你已经拥有 Browserbase 账户并希望继续使用它，同时通过 Nous 路由网页搜索和图像生成，这是支持的：

```bash
hermes tools
# → 网页搜索        → "Nous Subscription"     （推荐）
# → 图像生成        → "Nous Subscription"     （推荐）
# → 浏览器          → "Browserbase"           （你现有的密钥）
# → TTS             → "Nous Subscription"     （推荐）
```

即使在你登录 Nous Portal 之前，这些行也会出现在 `hermes tools` 中 —— 如果你选择“Nous Subscription”但没有活动会话，Hermes 会内联运行 Portal 登录（不会更改你的推理提供者或其他工具）。

使用以下命令验证你的混合配置：

```bash
hermes portal tools
```

你将看到每个工具的路由 —— 对于通过订阅路由的工具显示“通过 Nous Portal”，对于使用你自己密钥的工具显示合作伙伴名称（`browserbase`、`firecrawl` 等）。

## 7.（可选）启用语音模式

由于工具网关包含 OpenAI TTS，[语音模式](/user-guide/features/voice-mode)无需单独的 OpenAI 密钥即可工作：

```bash
hermes setup voice
# → 选择 "Nous Subscription" 作为 TTS
# → 选择一个语音转文本后端（本地 faster-whisper 免费，无需设置）
```

然后在任何消息平台（Telegram、Discord、Signal 等）会话中，发送语音消息，Hermes 将转录它、回复，并用合成语音回复 —— 全部通过你的 Portal 订阅完成。

## 8.（可选）定时任务 + 常开工作流

Portal 订阅适用于[定时任务](/user-guide/features/cron)和[批处理](/user-guide/features/batch-processing)，其工作方式与交互式聊天相同 —— OAuth 刷新令牌会自动重用。无需额外设置；只需安排定时任务，它们将计入你的订阅。

```bash
hermes cron create "every day at 9am" \
  "Search the web for top AI news and summarize the 5 most important stories" \
  --name "Daily AI news"
```

定时任务将在无人值守的情况下运行，通过你的 Portal 订阅调用模型 + 网页搜索 + 摘要。

## 配置文件和多人设置

如果你使用 [Hermes 配置文件](/user-guide/profiles)（例如每个项目一个单独的配置），Portal 刷新令牌将通过共享令牌存储自动在所有配置文件之间共享。在任何配置文件上登录一次，其他配置文件会自动获取。

对于多个人共享一台机器的团队设置，每个人都有自己的 Portal 账户 → 每个主目录拥有自己的 `~/.hermes/auth.json` → 用户之间不共享令牌。这是正确的边界。

## 故障排除

### 运行 `hermes setup --portal` 后 `hermes portal info` 显示“未登录”

OAuth 流程未完成。重新运行它：

```bash
hermes portal
```

如果浏览器没有打开或回调失败，你很可能在远程/无头主机上——请参阅[通过 SSH 使用 OAuth](/guides/oauth-over-ssh) 了解端口转发和手动粘贴的变通方法。

### “Model: currently openrouter”（或其他提供者）而不是“using Nous as inference provider”

你的本地配置发生了偏离。OAuth 已成功但 `model.provider` 仍指向其他提供者。修复：

```bash
hermes config set model.provider nous
```

或以交互方式：

```bash
hermes model
# 选择 Nous Portal
```

使用 `hermes portal info` 重新验证。

### 工具网关工具显示合作伙伴名称而不是“通过 Nous Portal”

每个工具配置覆盖了网关。运行：

```bash
hermes tools
# 为任何你想通过网关路由的工具选择 "Nous Subscription"
```

一些用户有意混合使用——例如通过 Nous 路由网页搜索但使用自己的 Browserbase 密钥进行浏览器路由。如果这是有意的，则保持不变。如果不是，此命令可修复它。

### 会话中显示“需要重新认证”

你的 Portal 刷新令牌已失效（密码更改、手动撤销、会话过期）。该令牌现在本地隔离，因此 Hermes 不会无限重放它。只需重新登录：

```bash
hermes auth add nous
```

成功重新登录后，隔离会自动清除。

### 我想要的模型不在 `/model` 选择器中

Portal 目录镜像了 OpenRouter 的模型列表（超过 300 个）。如果某个模型缺失，尝试直接输入 OpenRouter 风格的 slug：

```bash
/model anthropic/claude-opus-4.6
/model openai/o1-2025-12-17
```

如果某个模型确实不可用，请[提交 issue](https://github.com/NousResearch/hermes-agent/issues) —— 大多数缺失是由于我们可以更新的路由配置。

### 账单未显示在我的 Portal 账户中

`hermes portal info` 会告诉你实际是否通过 Portal 或其他提供者路由。常见原因：

- `model.provider` 设置为 `openrouter` / `anthropic` 等，而非 `nous`
- OAuth 刷新失败，回退到其他已配置的提供者
- 多个 Hermes 配置文件，你使用了错误的配置（检查 `hermes profile list`）

### 想要撤销并重新开始

```bash
hermes auth logout nous       # 清除本地刷新令牌
# 然后重新运行设置或从 Portal Web 界面移除订阅
```

## 简而言之，你能得到什么

| 没有 Portal | 有 Portal |
|-------------|-----------|
| `.env` 中有 1 个 OpenRouter / Anthropic / OpenAI 密钥 | 1 个 OAuth 刷新令牌，无需 `.env` 密钥 |
| 1 个 Firecrawl 密钥用于网页搜索 | 网页通过网关路由 |
| 1 个 FAL 密钥用于图像生成 | 图像生成通过网关路由 |
| 1 个 Browser Use / Browserbase 密钥用于浏览器 | 浏览器通过网关路由 |
| 1 个 OpenAI 密钥用于 TTS / 语音模式 | TTS 通过网关路由 |
| 5 个单独的控制台、充值、发票 | 1 个订阅，1 张发票 |
| 跨机器：复制全部 5 个密钥 | 跨机器：重新 OAuth 一次 |

这就是交易。如果你无论如何已经在使用这些后端中的两个以上，订阅就物超所值。

## 参见

- **[Nous Portal 集成页面](/integrations/nous-portal)** —— 订阅内容概述
- **[工具网关](/user-guide/features/tool-gateway)** —— 每个通过网关路由的工具的完整详情
- **[订阅代理](/user-guide/features/subscription-proxy)** —— 从非 Hermes 工具使用你的 Portal 订阅
- **[语音模式](/user-guide/features/voice-mode)** —— 在 Portal 订阅上设置语音对话
- **[通过 SSH 使用 OAuth](/guides/oauth-over-ssh)** —— 远程/无头登录模式
- **[配置文件](/user-guide/profiles)** —— 在多个 Hermes 配置之间共享一个 Portal 登录