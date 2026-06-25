--- frontmatter ---
---
title: "Stripe Link Cli — 通过Stripe Link进行代理支付 — 信用卡、SPT、审批"
sidebar_label: "Stripe Link Cli"
description: "通过Stripe Link进行代理支付 — 信用卡、SPT、审批"
---

--- body ---
{/* 此页面由网站/scripts/generate-skill-docs.py根据技能的SKILL.md自动生成。请编辑原始SKILL.md，而非此页面。 */}

# Stripe Link Cli

通过Stripe Link进行代理（Agent）支付 — 信用卡、SPT、审批。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/payments/stripe-link-cli` 安装 |
| 路径 | `optional-skills/payments/stripe-link-cli` |
| 版本 | `0.1.0` |
| 作者 | Teknium (teknium1), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `Payments`, `Stripe`, `Link`, `Checkout`, `MPP` |
| 相关技能（Skill） | [`mpp-agent`](/docs/user-guide/skills/optional/payments/payments-mpp-agent), [`stripe-projects`](/docs/user-guide/skills/optional/payments/payments-stripe-projects) |

## 参考：完整 SKILL.md

:::info
以下是此技能（Skill）被触发时Hermes加载的完整技能定义。这是技能（Skill）处于活动状态时代理所看到的指令。
:::

# Stripe Link CLI 技能（Skill）

包装 [@stripe/link-cli](https://github.com/stripe/link-cli)，使Hermes能够代表用户使用一次性虚拟信用卡或共享支付令牌（Shared Payment Token，SPT）完成购买。每笔支出均需在Link移动/Web应用内进行审批 — Hermes无法自行批准。

目前仅限美国（需要Link账户）。上游CLI不支持Windows — 此技能（Skill）限制为 `[linux, macos]`。

## 何时使用

触发短语：

- "购买X", "支付X", "进行购买", "完成结账"
- "给我一张卡", "我需要一种支付方式"
- "登录到Link", "连接我的Link钱包"
- 商家API返回HTTP 402，并带有 `www-authenticate: ... method="stripe"`

如果用户需要进行付费API调用（HTTP 402，无结账表单），则 `card` 路径是错误的 — 应通过此技能（Skill）使用SPT，或切换到 `mpp-agent` 技能（Skill）。

## 前置条件

- Node.js 20+ 在 `PATH` 中可用（`node --version`）
- 美国地区（需要Link账户）

在Hermes尝试支付之前，Link账户、支付方式和支出审批应用**不需要**预先设置 — CLI在首次运行时将引导用户完成设置：

- 在 https://app.link.com 注册Link账户 — 在首次 `link-cli` 认证时创建/关联
- 至少一种支付方式 — 在首次运行 https://app.link.com/wallet 时添加
- Link移动/Web应用 — 在收到首次支出请求时打开以批准

无需设置环境变量 — 认证状态由CLI在其自己的配置目录下本地存储。

## 安装

全局安装一次：

```
npm install -g @stripe/link-cli
```

或通过 `npx @stripe/link-cli` 临时调用。以下技能（Skill）使用已安装的 `link-cli` 形式。

## 运行方式

所有命令通过 `terminal` 工具执行。CLI会自动检测非TTY调用者，默认输出紧凑的 `toon` 格式 — 对模型来说没问题。如果某个步骤需要结构化字段，请传递 `--format json`。

发现命令：`link-cli --llms-full`。
在调用前获取命令的架构：`link-cli <command> --schema`。

## 流程

### 1. 检查/建立认证

```
link-cli auth status
```

如果未认证，请使用清晰的客户端名称登录（此标签会显示在用户的Link应用中）：

```
link-cli auth login --client-name "Hermes" --interval 5 --timeout 300
```

`--interval`/`--timeout` 形式会内联轮询，因此代理无需管理 `_next` 步骤。向用户打印验证URL+短语，并等待CLI返回。

**在 `auth status` 确认登录之前，不要继续执行此步骤。**

### 2. 在创建支出请求前评估商家

决定凭证类型：

| 商家界面 | `--credential-type` |
|---|---|
| 标准Web结账表单 / Stripe Elements | `card`（默认） |
| 返回HTTP 402，并带有 `www-authenticate` 中的 `method="stripe"` | `shared_payment_token` |
| 返回HTTP 402，但 `method` 不是 `"stripe"` | 不支持 — 停止 |

对于402响应，不要手动解码挑战。直接传递原始头信息：

```
link-cli mpp decode --challenge '<完整的WWW-Authenticate头>'
```

这将验证挑战并提取网络ID和解码后的请求体。

### 3. 列出支付方式及配送地址

```
link-cli payment-methods list
link-cli shipping-address list
```

除非用户另行指定，否则使用第一个条目。`payment-methods list` 中的 `id` 即为下一步中的 `--payment-method-id`。

### 4. 创建支出请求

在发出此命令前，与用户确认最终总金额。金额单位为分。

```
link-cli spend-request create \
  --payment-method-id <pm_id> \
  --merchant-name "<名称>" \
  --merchant-url "<URL>" \
  --context "<一句话：购买什么以及原因>" \
  --amount <分> \
  --line-item "name:<项目>,unit_amount:<分>,quantity:1" \
  --total "type:total,display_text:总计,amount:<分>" \
  --request-approval
```

对于MPP商户，添加 `--credential-type shared_payment_token`。

`--request-approval` 会通知用户的Link应用并轮询，直到用户批准或拒绝。CLI在拒绝/超时时会以非零退出码退出。

### 5. 检索凭证 — 安全地

**不要将卡信息打印到标准输出。** 使用 `--output-file`，以便PAN（主账号）永远不会进入代理的转录或日志：

```
link-cli spend-request retrieve <lsrq_id> \
  --include card \
  --output-file /tmp/link-card.json \
  --format json
```

文件将以 `0600` 权限写入；标准输出仅显示脱敏字段（品牌、后四位、有效期）以及 `card_output_file` 路径。

### 6. 使用凭证

- 对于Web结账：将文件路径提供给用户，或将其传递给直接从磁盘填充表单的浏览器驱动工具。**切勿**将卡文件的 `read_file` 或 `cat` 内容带入代理的推理上下文。
- 对于MPP商户：

  ```
  link-cli mpp pay <商户URL> \
    --spend-request-id <lsrq_id> \
    --method POST \
    --data '<JSON body>'
  ```

### 7. 清理

购买完成后立即删除卡文件：

```
rm -f /tmp/link-card.json
```

## 可选：改用MCP服务器运行

`@stripe/link-cli --mcp` 将相同的命令作为MCP工具通过stdio暴露。要将其注册到Hermes的原生MCP：

```
hermes mcp add stripe-link --command "npx" --args "@stripe/link-cli --mcp"
```

然后 `hermes mcp list` 应显示 `stripe-link`。相同的审批规则适用 — MCP不会绕过Link应用的审批步骤。

## 陷阱

- **仅限美国。** 在美国以外，`auth login` 将失败。告知用户，不要反复重试。
- **卡号（PAN）绝不能进入代理上下文。** 每次都要使用 `--output-file`。如果你已经未使用它进行检索，立即执行 `link-cli auth logout` 是不够的 — 卡是一次性的，但轮换卫生很重要。
- **`--request-approval` 会阻塞直到用户操作。** 如果用户睡着了，CLI将超时。设定好预期。
- **多步骤 `_next` 命令。** 某些命令返回 `_next.command`，必须执行才能继续。如有疑问，优先使用内联轮询标志（`--interval`/`--timeout`）。
- **输出格式默认在非TTY模式下为 `toon`。** 对于文本描述没问题，但如果下游步骤需要解析特定字段，请传递 `--format json`。
- **不要默认使用 `card`。** 之所以有商家评估步骤（第2节），是因为选择错误的凭证类型会导致购买静默失败或泄露比所需更多的数据。

## 验证

```
link-cli --version && link-cli auth status
```

退出码0表示已安装并登录。