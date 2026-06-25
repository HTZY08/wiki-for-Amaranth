--- frontmatter ---
---
title: "Stripe Projects — 通过 Stripe Projects 配置 SaaS 服务并同步凭据"
sidebar_label: "Stripe Projects"
description: "通过 Stripe Projects 配置 SaaS 服务并同步凭据"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Stripe Projects

通过 Stripe Projects 配置 SaaS 服务并同步凭据。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选 — 使用 `hermes skills install official/payments/stripe-projects` 安装 |
| 路径（Path） | `optional-skills/payments/stripe-projects` |
| 版本（Version） | `0.1.0` |
| 作者（Author） | Teknium (teknium1), Hermes Agent |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos |
| 标签（Tags） | `Payments`, `Stripe`, `Projects`, `Provisioning`, `Infrastructure` |
| 相关技能（Related skills） | [`stripe-link-cli`](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli), [`mpp-agent`](/docs/user-guide/skills/optional/payments/payments-mpp-agent) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）会将其作为指令使用。
:::

# Stripe Projects 技能

封装了 [Stripe Projects](https://projects.dev) CLI 插件，使 Hermes 能够配置 SaaS 服务（如 Neon、Twilio、Vercel 等），生成凭据并将其同步到用户的 `.env` 文件中，同时在一个地方管理多个提供商的计费。

在 Windows 上更广泛的支付集群成熟之前，暂限定为 `[linux, macos]`。Stripe CLI 本身是跨平台的；此限定是集群的策略，而非硬性限制。

## 使用时机

触发短语：

- "设置 &lt;provider>"、"配置 &lt;Neon|Twilio|Vercel|...>"、"创建一个数据库"
- "为这个项目提供一个 &lt;Postgres|Redis|Twilio number|...>"
- "管理我的堆栈凭据"、"轮换此密钥"、"升级我的套餐"
- "我可以添加哪些提供商？"

如果用户已有提供商账户，此技能仍可通过 `stripe projects link <provider>` 进行连接。如果用户想使用已有的提供商资源（例如现有的数据库或 Vercel 项目），请先检查提供商支持情况；目前许多提供商支持配置新资源，但不支持导入现有资源。

## 前提条件（Prerequisites）

- 已安装 Stripe CLI（macOS 上使用 Homebrew，Linux 上使用包管理器，或从 https://docs.stripe.com/stripe-cli/install 下载）
- 已安装 Stripe Projects 插件
- 拥有一个 Stripe 账户。如果用户还没有账户，CLI 可以在设置过程中通过浏览器引导他们登录或创建账户。

## 安装

macOS：

```
brew install stripe/stripe-cli/stripe
stripe plugin install projects
```

Linux：按照 https://docs.stripe.com/stripe-cli/install 上的平台特定安装说明进行操作，然后：

```
stripe plugin install projects
```

## 运行方式

所有命令均通过 `terminal` 工具从用户的项目目录内运行（CLI 会将 `.env` 和 `.projects/vault/vault.json` 写入当前工作目录）。

## 流程（Procedure）

### 1. 初始化项目

```
cd <project-root>
stripe projects init
```

这会创建 `.projects/vault/vault.json`（加密的凭据存储）并准备好项目以接收提供商。

### 2. 发现可用提供商

```
stripe projects catalog
```

列出 Stripe Projects 支持的所有提供商 — 数据库、托管、认证、AI、分析、消息等。

### 3. 添加服务

```
stripe projects add <provider>/<service>
```

示例：

- `stripe projects add neon/postgres`
- `stripe projects add twilio/sms`
- `stripe projects add runloop/sandbox`

CLI 会在用户自己的提供商账户中配置该服务，生成凭据，将其同步到 `.env` 文件中，并将资源记录在存储库中。用户可能需要确认层级选择或定价提示。

### 4. 验证

```
stripe projects list
```

应显示新添加的提供商及其 `.env` 密钥。

### 5. 管理/升级/移除

```
stripe projects upgrade <provider>     # 更改层级
stripe projects remove <provider>      # 取消配置
stripe projects rotate <provider>      # 轮换凭据
```

## 注意事项（Pitfalls）

- **`.env` 写入是真实的写入。** CLI 会附加到项目根目录中的任何 `.env` 文件。如果用户的 `.env` 已被 .gitignore 忽略（通常如此），密钥将安全保存；否则，此技能可能成为凭据泄露的途径。务必先检查 `.gitignore`。
- **按项目状态。** `.projects/vault/vault.json` 是按项目存储的。在两个不同项目中配置相同服务将创建两个独立的资源——以及两张账单。
- **计费发生在 Stripe 端。** 在 `add`/`upgrade` 过程中出现的层级提示会触发实际收费；在确认前应向用户展示这些信息。
- **提供商可用性会变化。** 目录会不断增长；如果用户指定的提供商不在列表中，请先运行 `stripe projects catalog | grep <name>` 再调用 `add`，而不是直接失败。
- **存储库中的凭据已加密，但 `.env` 是明文。** 遵循标准的 `.env` 卫生习惯——切勿提交它。
- **移除服务并不总是销毁底层资源。** 某些提供商可能会留下一个暂停或休眠的资源。对于高成本服务（尤其是托管数据库），请在 `remove` 后检查提供商的独立仪表板。

## 验证（Verification）

```
stripe projects --version && stripe projects list
```

在已初始化的项目中退出码为 0 表示插件运行正常。