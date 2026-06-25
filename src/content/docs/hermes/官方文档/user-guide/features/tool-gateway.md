---
title: Tool Gateway
---

--- body ---
## 配置参考

大多数用户无需接触此部分——`hermes model` 和 `hermes tools` 已交互式覆盖所有工作流程。此部分适用于直接编写 config.yaml 或脚本化设置。

### 按工具设置 `use_gateway` 标志

每个工具的配置块接受一个 `use_gateway` 布尔值：

```yaml
web:
  backend: firecrawl
  use_gateway: true

image_gen:
  use_gateway: true

tts:
  provider: openai
  use_gateway: true

browser:
  cloud_provider: browser-use
  use_gateway: true
```

优先级：`use_gateway: true` 会通过 Nous 路由，无论 `.env` 中是否有直接密钥。`use_gateway: false`（或缺失）则优先使用直接密钥（如果存在），仅在无密钥时回退到网关。

### 禁用网关

```yaml
web:
  use_gateway: false   # Hermes 现在使用 .env 中的 FIRECRAWL_API_KEY
```

`hermes tools` 在您选择非网关提供商时会自动清除该标志，因此通常这对您自动生效。

### 自托管网关（高级）

运行您自己的兼容 Nous 的网关？在 `~/.hermes/.env` 中覆盖端点：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # 通常从门户登录自动填充
FIRECRAWL_GATEWAY_URL=https://...         # 单独覆盖一个端点
```

这些设置项用于自定义基础设施环境（企业部署、开发环境）。普通订阅者无需设置。

## 常见问题

### 它与 Telegram / Discord / 其他消息网关兼容吗？

是的。工具网关在工具执行层运行，而非 CLI。任何能够调用工具的接口——CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器等——都能透明地受益。

### 如果我的订阅过期会怎样？

通过网关路由的工具将停止工作，直到您续费或通过 `hermes tools` 替换为直接 API 密钥。Hermes 会显示一个明确的错误，指向门户。

### 我可以查看每个工具的使用量或成本吗？

可以——[Nous 门户仪表盘](https://portal.nousresearch.com) 按工具细分使用情况，让您了解驱动账单的因素。

### Modal（无服务器终端）包含在内吗？

Modal 作为**可选附加组件**通过 Nous 订阅提供，不属于默认工具网关包的一部分。当您需要用于 shell 执行的远程沙箱时，可通过 `hermes setup terminal` 或直接在 `config.yaml` 中配置。

### 启用网关后，我需要删除现有的 API 密钥吗？

不需要——将它们保留在 `.env` 中。当 `use_gateway: true` 时，Hermes 会跳过直接密钥并使用网关。将标志改回 `false`，您的密钥将再次成为来源。网关不是锁定。