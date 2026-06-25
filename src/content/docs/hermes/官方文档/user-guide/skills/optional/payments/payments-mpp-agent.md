---
title: "Mpp Agent — 通过机器支付协议（MPP）支付 HTTP 402 API"
sidebar_label: "Mpp Agent"
description: "通过机器支付协议（MPP）支付 HTTP 402 API"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。编辑源文件 SKILL.md，而不是此页面。 */}

# Mpp Agent

通过机器支付协议（MPP）支付 HTTP 402 API。

## 技能元数据

| 来源 | 路径 | 版本 | 作者 | 许可证 | 平台 | 标签 | 相关技能 |
|---|---|---|---|---|---|---|---|
| 可选 — 使用 `hermes skills install official/payments/mpp-agent` 安装 | `optional-skills/payments/mpp-agent` | `0.1.0` | Teknium (teknium1), Hermes Agent | MIT | linux, macos | `Payments`, `MPP`, `HTTP-402`, `Tempo`, `Stripe` | [`stripe-link-cli`](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli), [`stripe-projects`](/docs/user-guide/skills/optional/payments/payments-stripe-projects) |

## 参考：完整 SKILL.md

:::info
以下为当此技能（Skill）被触发时 Hermes 加载的完整技能定义。这是代理（Agent）在技能激活时所看到的指令。
:::

# MPP 代理技能

封装机器支付协议（MPP, https://mpp.dev）客户端，使得 Hermes 能够针对那些响应 `HTTP 402 Payment Required` 的服务器支付按请求计费的 API 访问。

提供三个客户端选项，均通过 npm 分发。选择最轻量且满足用户需求的一个。在更广泛的支付工具在 Windows 上成熟之前，限定于 `[linux, macos]`。

## 何时使用

- 某个商家 API 返回了带有 `www-authenticate` 头的 `HTTP 402` 响应，且用户希望实际支付它，而不仅仅是记录该响应。
- 用户要求“按请求付费”、“设置代理钱包”、“使用 Tempo / Privy / AgentCash”，或希望发现 MPP 定价的服务。
- Stripe Link 支付已生成共享支付令牌（Shared Payment Token, SPT），代理需要将其附加到 402 挑战中——在此流程中，优先使用 `link-cli mpp pay`（参见 `stripe-link-cli` 技能）。

## 选择客户端

| 工具 | 使用时机 | 设置 |
|---|---|---|
| `link-cli` | 用户已设置 Stripe Link，或 402 挑战中声明了 `method="stripe"` | 参见 `stripe-link-cli` 技能 |
| Tempo 钱包 | 具有支付控制的 MPP 服务、服务发现 | `tempo wallet login` |
| Privy 代理 CLI | 多链钱包、基于浏览器的充值 | `privy-agent-wallets login` |
| AgentCash | 通过一个 USDC.e 余额访问 300+ 预定价 API | `npx agentcash onboard` |
| `mppx` | 开发 + 调试，最小依赖面 | `npm install -g mppx` 然后 `mppx account create` |

默认：如果用户已经配置了 Stripe Link 或 402 挑战指定了 `method="stripe"`，则使用 `link-cli mpp pay`（`stripe-link-cli` 技能）。否则，对于一次性付费调用和调试使用 `mppx`，当用户希望持久的支付控制时使用 Tempo 钱包。

## 前提条件

- Node.js 20+ 在 `PATH` 中
- 一个已充值的钱包（Tempo / Privy / AgentCash）或一个 `mppx` 账户
- 对于 Tempo / Privy / AgentCash：按照各自的入门技能操作：
  - `https://tempo.xyz/SKILL.md`
  - `https://agents.privy.io/skill.md`
  - `https://agentcash.dev/skill.md`

如果用户选择了其中一个，请使用 `web_extract` 获取相应的 SKILL.md 文件。

## 操作步骤（mppx，最快路径）

通过 `terminal` 工具运行所有命令。

### 1. 安装并创建账户

```
npm install -g mppx
mppx account create
```

将生成的账户凭据存储在 CLI 指示的位置（CLI 会将其写入自己的配置目录下——不要将它们粘贴到代理转录中）。

### 2. 检查商家的 402 挑战

如果用户提供了一个 URL，首先探测它以确认它确实支持 MPP：

```
curl -i <url>
```

一个真正的 MPP 402 响应看起来像：

```
HTTP/1.1 402 Payment Required
www-authenticate: tempo amount=0.1 currency=...
```

### 3. 支付请求

```
mppx <url>
```

对于非 GET 方法或请求体：

```
mppx <url> --method POST --data '<json>'
```

`mppx` 会自动处理 402 挑战/凭证交互，并在成功时输出商家的实际响应。

### 4. 验证收据

`mppx` 会自动附加收据头。要检查：

```
mppx <url> -v
```

## 操作步骤（Tempo 钱包）

Tempo 钱包技能（位于 https://tempo.xyz/SKILL.md）是权威参考；使用 `web_extract` 获取它并按照其说明操作。概要：

```
tempo wallet login
tempo wallet pay <url>
```

支付控制和服务发现在钱包 UI（https://wallet.tempo.xyz）中。

## 注意事项

- **没有 `method="stripe"` 的 `HTTP 402` 响应无法通过 Stripe Link 支付。** 如果挑战中仅声明了 Tempo / 其他方法，则使用 `mppx`（或匹配的钱包）——Link 会拒绝它。反之，如果声明了 `method="stripe"`，则优先通过 `stripe-link-cli` 技能使用 Link，以便支出通过用户批准的卡进行。
- **一个头部中的多个挑战。** `www-authenticate` 可能列出多个方法（例如 `tempo, stripe`）。Link CLI 的 `mpp decode` 会选择 Stripe 的方法；`mppx` 会选择 Tempo 的方法。没有单一的“正确”客户端——根据用户已充值哪个钱包来选择。
- **零金额挑战。** 某些 MPP 端点收取 `$0.00` 并仅需要证明凭据。这些无需已充值钱包即可工作。不要将其拒绝为“损坏的”。
- **钱包密钥绝不会进入代理上下文。** 所有四个客户端都将密钥存储在自己的配置目录下（或生成会话特定的临时密钥对，如 Privy 的情况）。不要使用 `cat`/`read_file` 读取它们。
- **服务端 MPP 是不同的技能。** 如果用户想为自己的 API 添加 402 支持，则此技能不适用——请引导他们访问 https://mpp.dev/quickstart/server 以及 `mppx/nextjs` / `mppx/hono` / `mppx/express` / `mppx/elysia` 中间件。专用的 `mpp-server` 技能可能会在后续推出。

## 验证

```
mppx --version && mppx account list
```

退出代码 0 表示已安装且存在账户。