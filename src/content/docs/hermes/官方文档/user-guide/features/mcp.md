---
title: Mcp
---

sidebar_position: 4
title: "MCP (模型上下文协议)"
description: "通过 MCP 将 Hermes Agent 连接到外部工具服务器，并精确控制 Hermes 加载哪些 MCP 工具"
---

--- body ---
# MCP (模型上下文协议) (Model Context Protocol)

MCP 让 Hermes Agent 连接到外部工具服务器，从而使智能体能够使用 Hermes 本身之外的工具 —— GitHub、数据库、文件系统、浏览器堆栈、内部 API 等等。

如果你曾希望 Hermes 使用某个已经存在于其他地方的工具，MCP 通常是最简洁的实现方式。

## MCP 为你带来的好处

- 无需先编写原生 Hermes 工具，即可访问外部工具生态
- 在同一配置中支持本地 stdio 服务器和远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，为 MCP 资源和提示（prompts）提供实用工具包装器（wrappers）
- 支持每个服务器的过滤功能，以便仅暴露你希望 Hermes 看到的 MCP 工具

## 快速开始

1. MCP 支持随标准安装一起提供 —— 无需额外步骤。

2. 将 MCP 服务器添加到 `~/.hermes/config.yaml`：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3. 启动 Hermes：

```bash
hermes chat
```

4. 要求 Hermes 使用 MCP 支持的功能。

例如：

```text
列出 /home/user/projects 中的文件并总结仓库结构。
```

Hermes 会发现 MCP 服务器的工具，并像使用其他任何工具一样使用它们。

## 目录：一键安装 Nous 认可的 MCP

Hermes 附带一个精选的 MCP 服务器目录，这些服务器已经过 Nous 员工审查并合并。它们默认被禁用 —— 只安装你实际需要的。

```bash
hermes mcp                # 交互式选择器（默认）
hermes mcp catalog        # 纯文本列表，可脚本化
hermes mcp install n8n    # 按名称安装目录条目
```

选择器会显示每个条目的当前状态：

```
n8n          available              Manage and inspect n8n workflows from Hermes
linear       enabled                Linear issue/project management (remote OAuth)
github       installed (disabled)   GitHub repo + PR tools
```

在行上按 `Enter` 键可安装（并走完所需的凭据流程）、启用、禁用或卸载。目录条目存储在 hermes-agent 仓库的 `optional-mcps/` 目录下 —— 存在于该目录意味着 Nous 批准。没有社区提交层级；条目通过合并 PR 添加。

目录条目可能需要：

- **API 密钥** —— Hermes 在安装时提示，并将值写入 `~/.hermes/.env` 文件。非秘密值（如基本 URL）也写入同一文件。
- **OAuth**（远程 MCP）—— 在配置中写为 `auth: oauth`；MCP 客户端在首次连接时打开浏览器。
- **OAuth**（第三方提供商，如 Google/GitHub）—— 如果你尚未认证，Hermes 会提示你执行 `hermes auth <provider>`。

### 安装时的工具选择

配置凭据后，Hermes 会探测 MCP 服务器以列出其暴露的所有工具，并显示一个复选框列表：

```
Select tools for 'linear' (SPACE toggle, ENTER confirm)
  [x] find_issues       Find issues matching a query
  [x] get_issue         Get a single issue
  [x] create_issue      Create a new issue
  [ ] delete_workspace  Delete a Linear workspace
  ...
```

预选的行来自：

1. **你之前的选择**，如果你之前安装过此条目（重新安装会保留你已有的选择 —— 清单的默认值不会覆盖它）
2. **清单的 `tools.default_enabled`**，如果条目声明了该字段（某些目录条目会预排除可变性或很少使用的工具）
3. **全部**，如果两者都不适用

按 ENTER 提交复选框列表。只有选中的工具会出现在 `mcp_servers.<name>.tools.include` 中。如果你选择了全部，则不会写入过滤器（最干净的配置形状，行为相同）。

**如果探测失败**（服务器不可达、OAuth 未完成、后端服务未运行），安装仍然成功：清单的 `tools.default_enabled` 会直接应用（如果声明了），否则不写入过滤器。稍后当服务器可达时，重新运行 `hermes mcp configure <name>` 以细化。

### 信任模型

安装目录条目会执行清单指定的任何操作 —— `git clone`、条目的 `bootstrap` 命令（`pip install`、`npm install` 等），以及最终的 MCP 服务器自身代码。清单通过 PR 审查进入 hermes-agent 仓库，因此 Nous 在发布前已审查每个条目 —— **但你仍应在安装前阅读清单**，特别是 `source:` 字段的仓库、`install.bootstrap:` 命令以及任何 `transport.command:` 调用。

清单位于 GitHub 上的 [`optional-mcps/<name>/manifest.yaml`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps)。选择器在安装时也会打印清单的 `source:` URL，以便你快速验证上游仓库。Web 仪表板的 MCP 页面会为每个目录条目显示相同的详细信息 —— 传输方式、认证类型、端点 URL（HTTP）或命令 + 参数（stdio）、git 安装源/引用和引导命令、设置说明 —— 其中 `source:` 渲染为可点击链接，因此你可以点击安装前准确检查条目连接或运行的内容。

### 清单版本兼容性

清单会固定一个 `manifest_version`。目录是向前兼容的：如果某个 PR 添加了一个具有比你已安装的 Hermes 所能理解的更新 `manifest_version` 的条目，选择器会针对该条目显示警告（`⚠ '<name>' requires a newer Hermes`），而不是静默隐藏。看到此警告时，运行 `hermes update` 安装最新版 Hermes。

### 运行时 `${ENV_VAR}` 替换

在条目的 `transport.command`、`transport.args`、`transport.url` 和 `headers` 中，`${VAR}` 占位符会在服务器连接时从环境变量（包括 `~/.hermes/.env` 中的所有内容）解析。当目录条目想要引用用户在其他地方配置的值时很有用 —— 例如 `${HOME}/foo` 或 `${MY_PROVIDER_TOKEN}`。

注意，这与目录清单中的 `${INSTALL_DIR}` 不同，后者在安装时会被替换为目录克隆条目仓库的路径。

### 稍后更新工具选择

```bash
hermes mcp configure linear
```

重新打开相同的复选框列表，并预选你当前的选择。当你想要启用更多工具，或者当服务器添加了你想选择的新工具时使用此命令。

### 更新目录清单

MCP 永远不会自动更新。如果清单版本发生变化，请在 Hermes 更新后重新运行 `hermes mcp install <name>` 以刷新。

要向目录添加 MCP，请针对 [`optional-mcps/`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps) 提交 PR。

## 两种 MCP 服务器

### Stdio 服务器

Stdio 服务器作为本地子进程运行，通过 stdin/stdout 通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况下使用 stdio 服务器：
- 服务器已本地安装
- 你想要低延迟地访问本地资源
- 你遵循的 MCP 服务器文档显示了 `command`、`args` 和 `env`

### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

在以下情况下使用 HTTP 服务器：
- MCP 服务器托管在其他地方
- 你的组织暴露了内部 MCP 端点
- 你不想让 Hermes 为该集成生成本地子进程

### OAuth 认证的 HTTP 服务器

大多数托管 MCP 服务器（Linear、Sentry、Atlassian、Asana、Figma、Stripe 等）需要 OAuth 2.1 而不是静态的 Bearer 令牌。设置 `auth: oauth`，Hermes 会通过 MCP Python SDK 处理发现、动态客户端注册、PKCE、令牌交换、刷新和升级认证。

```yaml
mcp_servers:
  linear:
    url: "https://mcp.linear.app/mcp"
    auth: oauth
```

首次连接时，Hermes 会打印一个授权 URL，尽可能打开你的浏览器，并等待本地环回端口上的 OAuth 回调。令牌以 0o600 权限缓存到 `~/.hermes/mcp-tokens/<server>.json`；后续运行会静默重用它们，直到刷新失败。

**远程 / 无头主机。** 当 Hermes 在与你的浏览器不同的机器上运行时，环回回调无法到达你的笔记本电脑。有两种方式完成流程：

- **粘贴回（无需设置）：** 在交互式终端上，Hermes 会在授权 URL 旁边打印 "Or paste the redirect URL here…"。在你的浏览器中打开该 URL，批准，复制浏览器最终重定向到的完整 URL（重定向会显示连接错误 —— 这在意料之中），粘贴到提示符处。裸的 `?code=…&state=…` 查询字符串也可以。
- **SSH 端口转发：** `ssh -N -L <port>:127.0.0.1:<port> user@host` 在另一个终端中，然后让重定向正常进行。

请参阅 [OAuth over SSH / Remote Hosts](../../guides/oauth-over-ssh.md#mcp-servers) 了解完整指南，包括无 DCR 的服务器（例如 Slack）、预注册的 `client_id`/`client_secret`、作用域自定义以及通过 `hermes mcp login <server>` 重新认证。

**陷阱 —— 不支持自动注册的提供商（Google Drive、Atlassian）。** 某些服务器拒绝裸 `auth: oauth` 所依赖的动态客户端注册步骤（RFC 7591）—— Google 官方的 Drive 服务器（`https://drivemcp.googleapis.com/mcp/v1`）返回 `400 Bad Request`，因此不会创建 OAuth 客户端，也不会获取令牌。症状很微妙：这些服务器也提供 *无需* 认证的 `tools/list`，因此 `hermes mcp login` 可以列出工具并看起来正常工作，但每个真正的工具调用稍后都会超时。`hermes mcp login` 现在会检测到这一点（它检查令牌是否实际落盘），并告诉你提供自己的 OAuth 客户端。在提供商的控制台中创建一个，并将其添加到配置中：

```yaml
mcp_servers:
  googledrive:
    url: "https://drivemcp.googleapis.com/mcp/v1"
    auth: oauth
    oauth:
      client_id: "<your-oauth-client-id>"
      client_secret: "<your-oauth-client-secret>"
```

然后运行 `hermes mcp login googledrive` —— 使用预注册的客户端，Hermes 会跳过注册并运行正常的浏览器授权流程。

**陷阱 —— 配置自动重载竞争。** 当你从正在运行的 Hermes 会话中编辑 `~/.hermes/config.yaml` 时，CLI 会在 30 秒超时后自动重载 MCP 连接。这对于交互式 OAuth 流程来说不够。添加条目后，从新的终端运行 `hermes mcp login <server>` —— 它会等待整整 5 分钟让你完成认证。

## mTLS / 客户端证书

支持需要双向 TLS（mutual TLS，客户端证书认证）的远程 HTTP MCP 服务器，通过 `client_cert` / `client_key` 实现。Hermes 会将解析后的证书传递给底层 HTTP 客户端用于 TLS 握手。

`client_cert` 接受三种形式：

- **单个组合 PEM 路径** —— 同时包含证书和私钥的文件：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/.certs/mcp-client.pem"
```

- **`[cert, key]` 二元组** —— 证书和私钥分别位于不同文件中（等效于同时设置 `client_cert` + `client_key`）：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key"]
```

- **`[cert, key, password]` 三元组** —— 当私钥加密时，第三个元素是密钥密码：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key", "${MCP_KEY_PASSWORD}"]
```

你也可以通过 `client_cert`（组合 PEM）加上显式的 `client_key` 来完全分开设置证书和密钥。路径支持 `~` 扩展；文件缺失会引发清晰的、针对服务器的错误，而不是不透明的 TLS 握手失败。

## 基本配置参考

Hermes 从 `~/.hermes/config.yaml` 的 `mcp_servers` 键下读取 MCP 配置。

### 通用键

| 键 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行文件 |
| `args` | 列表 | stdio 服务器的参数 |
| `env` | 映射 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 端点 |
| `headers` | 映射 | 远程服务器的 HTTP 头 |
| `client_cert` | 字符串 \| 列表 | mTLS 的客户端证书 —— 组合 PEM 路径，或 `[cert, key]` / `[cert, key, password]` |
| `client_key` | 字符串 | 客户端私钥 PEM 路径（当与 `client_cert` 分开时） |
| `timeout` | 数字 | 工具调用超时 |
| `connect_timeout` | 数字 | 初始连接超时 |
| `enabled` | 布尔值 | 如果为 `false`，Hermes 完全跳过此服务器 |
| `supports_parallel_tool_calls` | 布尔值 | 如果为 `true`，此服务器的工具可能并发运行 |
| `tools` | 映射 | 每个服务器的工具过滤和实用工具策略 |

### 最小 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 最小 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## 内置预设

对于知名的 MCP 服务器，`hermes mcp add` 接受一个 `--preset` 标志，该标志会填充传输细节，这样你就不必查找命令和参数。预设仅提供默认值 —— 你在同一命令行传递的其他任何内容（环境变量、头、过滤）仍然优先。

| 预设 | 它配置的内容 |
|---|---|
| `codex` | Codex CLI 的 MCP 服务器（`codex mcp-server` over stdio）。需要 `codex` CLI 在 PATH 中。 |

```bash
# 一行命令添加 Codex CLI 作为 MCP 服务器
hermes mcp add codex --preset codex
```

这会写入等效于以下内容：

```yaml
mcp_servers:
  codex:
    command: "codex"
    args: ["mcp-server"]
```

你可以选择任何本地名称（`hermes mcp add my-codex --preset codex` 没问题）；预设仅提供 `command`/`args` 默认值。

## Hermes 如何注册 MCP 工具

Hermes 会为 MCP 工具添加前缀，以避免与内置名称冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

在实践中，你通常不需要手动调用带前缀的名称 —— Hermes 会看到工具并在正常推理过程中选择它。

## MCP 实用工具

当支持时，Hermes 还会围绕 MCP 资源和提示注册实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些实用工具按每个服务器注册，使用相同的前缀模式，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要说明

这些实用工具现在具有能力感知功能：
- 仅当 MCP 会话实际支持资源操作时，Hermes 才会注册资源实用工具
- 仅当 MCP 会话实际支持提示操作时，Hermes 才会注册提示实用工具

因此，暴露了可调用工具但没有资源/提示的服务器将不会获得这些额外的包装器。

## 每个服务器的过滤

你可以控制每个 MCP 服务器向 Hermes 贡献哪些工具，从而实现对工具命名空间的精细管理。

### 完全禁用服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果 `enabled: false`，Hermes 会完全跳过该服务器，甚至不会尝试连接。

### 白名单服务器工具

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues]
```

仅注册这些 MCP 服务器工具。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

注册除排除项之外的所有服务器工具。

### 优先级规则

如果两者都存在：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 获胜。

### 也过滤实用工具

你也可以单独禁用 Hermes 添加的实用包装器：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 禁用了 `list_resources` 和 `read_resource`
- `tools.prompts: false` 禁用了 `list_prompts` 和 `get_prompt`

### 完整示例

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues, search_code]
      prompts: false

  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer]
      resources: false

  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

## 如果所有内容都被过滤掉会发生什么？

如果你的配置过滤掉了所有可调用的工具，并禁用或省略了所有支持的实用工具，Hermes 不会为该服务器创建一个空的运行时 MCP 工具集。

这保持了工具列表的整洁。

## 运行时行为

### 发现时间

Hermes 在启动时发现 MCP 服务器，并将其工具注册到常规工具注册表中。

### 动态工具发现

MCP 服务器可以通过发送 `notifications/tools/list_changed` 通知来通知 Hermes 其可用工具的运行时变化。当 Hermes 收到此通知时，它会自动重新获取服务器的工具列表并更新注册表 —— 无需手动执行 `/reload-mcp`。

这对于能力动态变化的 MCP 服务器非常有用（例如，当加载新的数据库模式时添加工具，或当服务离线时移除工具的服务器）。

刷新受锁保护，因此来自同一服务器的快速连续通知不会导致重叠刷新。提示和资源更改通知（`prompts/list_changed`、`resources/list_changed`）会被接收，但尚未处理。

### 重载

如果你更改了 MCP 配置，请使用：

```text
/reload-mcp
```

这会从配置重新加载 MCP 服务器并刷新可用工具列表。对于服务器本身推送的运行时工具更改，请参阅上面的 [动态工具发现](#dynamic-tool-discovery)。

### 工具集

每个配置的 MCP 服务器在贡献至少一个注册工具时，也会创建一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集级别更容易理解 MCP 服务器。

## 安全模型

### Stdio 环境变量过滤

对于 stdio 服务器，Hermes 不会盲目传递你的完整 shell 环境。

只会传递明确配置的 `env` 加上一个安全的基线。这减少了意外的秘密泄露。

### 配置级别的暴露控制

新的过滤支持也是一种安全控制：
- 禁用你不希望模型看到的危险工具
- 对于敏感的服务器，仅暴露最小的白名单
- 当你不希望暴露该表面时，禁用资源/提示包装器

## 示例用例

### 具有最小问题管理表面的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue]
      prompts: false
      resources: false
```

像这样使用：

```text
显示标记为 bug 的开放问题，然后草拟一个新的问题，关于不稳定的 MCP 重连行为。
```

### 移除了危险操作的 Stripe 服务器

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

像这样使用：

```text
查找最近 10 次失败付款，并总结常见失败原因。
```

### 针对单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

像这样使用：

```text
检查项目根目录并解释目录布局。
```

## 故障排除

### MCP 服务器无法连接

检查：

```bash
# 验证 MCP 依赖是否已安装（已包含在标准安装中）
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

然后验证你的配置并重启 Hermes。

### 工具未出现

可能的原因：
- 服务器连接失败
- 发现失败
- 你的过滤配置排除了这些工具
- 该服务器上不存在该实用工具能力
- 服务器通过 `enabled: false` 被禁用

如果你有意进行了过滤，这是预期行为。

### 为什么资源或提示实用工具没有出现？

因为 Hermes 现在仅当以下两个条件都为真时才注册这些包装器：
1. 你的配置允许它们
2. 服务器会话实际支持该能力

这是有意为之，以保持工具列表的诚实性。

## 并行工具调用

默认情况下，MCP 工具顺序执行 —— 一次一个。如果你的 MCP 服务器暴露了可以安全并发运行的工具（例如只读查询、独立的 API 调用），你可以选择并行执行：

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

当 `supports_parallel_tool_calls` 为 `true` 时，Hermes 可能会在单个工具调用批次中同时执行来自该服务器的多个工具，就像它处理内置只读工具（web_search、read_file 等）一样。

:::caution
仅对工具可以安全同时运行的 MCP 服务器启用并行调用。如果工具读取和写入共享状态、文件、数据库或外部资源，请在启用此设置之前检查读/写竞争条件。
:::

## MCP 采样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求 LLM 推理。这让 MCP 服务器可以要求 Hermes 代其生成文本 —— 对于需要 LLM 能力但没有自己模型访问权限的服务器很有用。

采样对于所有 MCP 服务器 **默认启用**（当 MCP SDK 支持时）。在 `sampling` 键下按服务器进行配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # 启用采样（默认：true）
      model: "openai/gpt-4o"  # 覆盖采样请求的模型（可选）
      max_tokens_cap: 4096     # 每个采样响应的最大令牌数（默认：4096）
      timeout: 30              # 每个请求的超时秒数（默认：30）
      max_rpm: 10              # 速率限制：每分钟最大请求数（默认：10）
      max_tool_rounds: 5       # 采样循环中的最大工具使用轮数（默认：5）
      allowed_models: []       # 服务器可请求的模型名称白名单（空 = 任意）
      log_level: "info"        # 审计日志级别：debug、info 或 warning（默认：info）
```

采样处理器包括滑动窗口速率限制器、每个请求超时和工具循环深度限制，以防止失控使用。指标（请求计数、错误、使用的令牌数）按服务器实例跟踪。

要禁用特定服务器的采样：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## 将 Hermes 作为 MCP 服务器运行

除了连接 **到** MCP 服务器之外，Hermes 也可以 **成为** 一个 MCP 服务器。这让其他支持 MCP 的智能体（Claude Code、Cursor、Codex 或任何 MCP 客户端）可以使用 Hermes 的消息传递能力 —— 列出对话、读取消息历史、以及跨所有已连接平台发送消息。

### 何时使用

- 你想要 Claude Code、Cursor 或其他编码智能体通过 Hermes 发送和读取 Telegram/Discord/Slack 消息
- 你想要一个单一的 MCP 服务器，同时桥接到 Hermes 的所有已连接消息平台
- 你已经有一个运行中的 Hermes 网关，并且已连接平台

### 快速开始

```bash
hermes mcp serve
```

这会启动一个 stdio MCP 服务器。MCP 客户端（而不是你）管理进程生命周期。

### MCP 客户端配置

将 Hermes 添加到你的 MCP 客户端配置中。例如，在 Claude Code 的 `~/.claude/claude_desktop_config.json` 中：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

或者如果你在特定位置安装了 Hermes：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "/home/user/.hermes/hermes-agent/venv/bin/hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 可用工具

MCP 服务器暴露了 10 个工具，匹配 OpenClaw 的通道桥接表面，加上一个 Hermes 特定的通道浏览器：

| 工具 | 描述 |
|------|-------------|
| `conversations_list` | 列出活跃的消息对话。可按平台过滤或按名称搜索。 |
| `conversation_get` | 通过会话键获取一个对话的详细信息。 |
| `messages_read` | 读取对话的近期消息历史。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图片、媒体）。 |
| `events_poll` | 从某个游标位置轮询新对话事件。 |
| `events_wait` | 长轮询 / 阻塞直到下一个事件到达（近乎实时）。 |
| `messages_send` | 通过平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上的可用消息目标。 |
| `permissions_list_open` | 列出在此桥接会话期间观察到的待处理审批请求。 |
| `permissions_respond` | 允许或拒绝待处理的审批请求。 |

### 事件系统

MCP 服务器包含一个实时事件桥，轮询 Hermes 的会话数据库以获取新消息。这使 MCP 客户端能够近乎实时地感知传入的对话：

```
# 轮询新事件（非阻塞）
events_poll(after_cursor=0)

# 等待下一个事件（最多阻塞至超时）
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`

事件队列在内存中，并在桥接连接时启动。旧消息可通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # 正常模式
hermes mcp serve --verbose    # 在 stderr 上输出调试日志
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储（`~/.hermes/sessions/sessions.json` 和 SQLite 数据库）读取对话数据。一个后台线程轮询数据库以获取新消息，并维护一个内存中的事件队列。对于发送消息，它使用与 Hermes 智能体本身相同的 `send_message` 基础设施。

网关不需要为读取操作（列出对话、读取历史、轮询事件）运行。但对于发送操作，它需要运行，因为平台适配器需要活动连接。

### 当前限制

- 嵌入式 `hermes mcp serve` 目前仅暴露 **stdio-only** 的 MCP 服务器。如果你需要 HTTP MCP 服务器，请运行单独的适配器 —— 或者更常见的是，使用 Hermes 的 MCP **客户端** 端，它已经支持 stdio 和 HTTP（`mcp_servers.yaml` / `config.yaml` 中的 `url` + `headers`；请参阅上面的 [HTTP 服务器](#http-servers)）。
- 事件轮询间隔约 200ms，通过 mtime 优化的数据库轮询（当文件未更改时跳过工作）
- 尚无 `claude/channel` 推送通知协议
- 仅文本发送（无法通过 `messages_send` 发送媒体/附件）

## 相关文档

- [Use MCP with Hermes](/guides/use-mcp-with-hermes)
- [CLI Commands](/reference/cli-commands)
- [Slash Commands](/reference/slash-commands)
- [FAQ](/reference/faq)