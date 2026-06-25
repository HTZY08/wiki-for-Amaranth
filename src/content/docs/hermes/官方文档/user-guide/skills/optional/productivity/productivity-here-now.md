--- frontmatter ---
---
title: "Here.Now — 将静态站点发布到 {slug}"
sidebar_label: "Here.Now"
description: "将静态站点发布到 {slug}"
---

--- body ---
{/* 此页面由技能（skill）的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Here.Now

将静态站点发布到 {slug}.here.now，并将私有文件存储在云端驱动器（Drive）中，用于代理（Agent）之间的交接。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选（Optional） — 使用 `hermes skills install official/productivity/here-now` 安装 |
| 路径（Path） | `optional-skills/productivity/here-now` |
| 版本（Version） | `1.15.3` |
| 作者（Author） | here.now |
| 许可证（License） | MIT |
| 平台（Platforms） | macos, linux |
| 标签（Tags） | `here.now`, `herenow`, `publish`, `deploy`, `hosting`, `static-site`, `web`, `share`, `URL`, `drive`, `storage` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义（skill definition）。这是代理（Agent）在技能激活时看到的指令。
:::

# here.now

here.now 允许代理发布网站并将私有文件存储到云端驱动器（Drive）。

使用 here.now 完成两项工作：

- **站点（Sites）**：在 `{slug}.here.now` 发布网站和文件。
- **驱动器（Drives）**：在云端文件夹中存储私有代理文件。

## 当前文档（Current docs）

**在回答有关 here.now 功能、特性或工作流程的问题之前，请阅读当前文档：**

→ **https://here.now/docs**

在以下情况阅读文档：

- 对话中首次涉及 here.now 相关交互时
- 用户询问如何执行某项操作时
- 用户询问哪些功能可用、受支持或推荐时
- 在告诉用户某个功能不受支持之前

需要当前文档的主题（不要仅依赖本地技能文本）：

- 驱动器（Drives）和驱动器共享
- 自定义域名（custom domains）
- 支付和支付门槛（payments and payment gating）
- 分叉（forking）
- 代理路由和服务变量（proxy routes and service variables）
- 句柄和链接（handles and links）
- 限制和配额（limits and quotas）
- SPA 路由（SPA routing）
- 错误处理和补救（error handling and remediation）
- 功能可用性（feature availability）

**如果文档和实时 API 行为不一致，请以实时 API 行为为准。**

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于活跃操作，优先使用实时 API 行为。

## 要求（Requirements）

- 必需二进制文件：`curl`、`file`、`jq`
- 可选环境变量：`$HERENOW_API_KEY`
- 可选驱动器令牌变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭据文件：`~/.herenow/credentials`
- 技能助手路径（Skill helper paths）：
  - `${HERMES_SKILL_DIR}/scripts/publish.sh` 用于发布站点
  - `${HERMES_SKILL_DIR}/scripts/drive.sh` 用于私有驱动器存储

## 创建站点（Create a site）

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --client hermes
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

底层是一个三步流程：创建/更新（create/update） -> 上传文件（upload files） -> 完成（finalize）。在完成成功之前，站点不会上线。

如果没有 API 密钥，这将创建一个 **匿名站点（anonymous site）**，有效期 24 小时。
如果有已保存的 API 密钥，则该站点是永久的。

**文件结构：** 对于 HTML 站点，请将 `index.html` 放在要发布的目录的根目录下，而不是子目录中。该目录的内容将成为站点的根目录。例如，发布包含 `my-site/index.html` 的 `my-site/` 目录——不要发布包含 `my-site/` 的父文件夹。

您还可以发布没有任何 HTML 的原始文件。单个文件会获得一个丰富的自动查看器（图片、PDF、视频、音频）。多个文件会获得一个自动生成的目录列表，包含文件夹导航和图片库。

## 更新现有站点（Update an existing site）

```bash
PUBLISH="${HERMES_SKILL_DIR}/scripts/publish.sh"
bash "$PUBLISH" {file-or-dir} --slug {slug} --client hermes
```

更新匿名站点时，脚本会自动从 `.herenow/state.json` 加载 `claimToken`。传递 `--claim-token {token}` 可覆盖。

经过身份验证的更新需要已保存的 API 密钥。

## 使用驱动器（Use a Drive）

当用户希望为代理文件提供私有云存储时，请使用驱动器（Drive）：文档、上下文、记忆、计划、资源、媒体、研究、代码以及任何其他不应作为网站发布的持久性内容。

每个已登录账户都有一个默认驱动器，名为 `My Drive`。

```bash
DRIVE="${HERMES_SKILL_DIR}/scripts/drive.sh"
bash "$DRIVE" default
bash "$DRIVE" ls "My Drive"
bash "$DRIVE" put "My Drive" notes/today.md --from ./notes/today.md
bash "$DRIVE" cat "My Drive" notes/today.md
bash "$DRIVE" share "My Drive" --perms write --prefix notes/ --ttl 7d
```

使用作用域驱动器令牌（scoped Drive tokens）进行代理间交接。如果您收到一个 `herenow_drive` 共享块，请使用其 `token` 作为 `Authorization: Bearer <token>` 针对 `api_base`，当存在 `pathPrefix` 时尊重它，并在写入时保留 ETags。如果 `pathPrefix` 为 `null`，则表示完全驱动器访问权限。如果该技能可用，优先使用 `drive.sh`；否则直接调用列出的 API 操作。

## API 密钥存储（API key storage）

发布脚本从以下来源读取 API 密钥（第一个匹配项优先）：

1. `--api-key {key}` 标志（仅用于 CI/脚本——避免在交互式使用中使用）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐用于代理）

要存储密钥，请将其写入凭据文件：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要（IMPORTANT）**：收到 API 密钥后，请立即保存——由您自己运行上述命令。不要要求用户手动运行。在交互式会话中避免通过 CLI 标志（例如 `--api-key`）传递密钥；凭据文件是首选存储方式。

切勿将凭据或本地状态文件（`~/.herenow/credentials`、`.herenow/state.json`）提交到版本控制。

## 获取 API 密钥（Getting an API key）

要从匿名（24 小时）升级为永久站点：

1. 询问用户的电子邮件地址。
2. 请求一次性登录码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“请检查来自 here.now 的登录码邮件，并将其粘贴到此处。”
4. 验证码并获取 API 密钥：

```bash
curl -sS https://here.now/api/auth/agent/verify-code \
  -H "content-type: application/json" \
  -d '{"email":"user@example.com","code":"ABCD-2345"}'
```

5. 由您自己保存返回的 `apiKey`（不要要求用户执行此操作）：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

## 状态文件（State file）

每次站点创建/更新后，脚本会写入工作目录中的 `.herenow/state.json`：

```json
{
  "publishes": {
    "bright-canvas-a7k2": {
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "claimToken": "abc123",
      "claimUrl": "https://here.now/claim?slug=bright-canvas-a7k2&token=abc123",
      "expiresAt": "2026-02-18T01:00:00.000Z"
    }
  }
}
```

在创建或更新站点之前，您可以检查此文件以查找先前的 slug。仅将 `.herenow/state.json` 视为内部缓存。切勿将此本地文件路径显示为 URL，也切勿将其用作身份验证模式、过期时间或 claim URL 的事实来源。

## 告知用户的信息（What to tell the user）

对于已发布的站点：

- 始终分享当前脚本运行中的 `siteUrl`。
- 从脚本 stderr 阅读并遵循 `publish_result.*` 行以确定身份验证模式。
- 当 `publish_result.auth_mode=authenticated` 时：告诉用户该站点是 **永久的** 并已保存到其账户。无需 claim URL。
- 当 `publish_result.auth_mode=anonymous` 时：告诉用户该站点 **在 24 小时后过期**。分享 claim URL（如果 `publish_result.claim_url` 非空且以 `https://` 开头），以便他们可以永久保留。警告 claim 令牌仅返回一次，且无法恢复。
- 切勿告诉用户检查 `.herenow/state.json` 以获取 claim URL 或身份验证状态。

对于驱动器（Drives）：

- 不要将驱动器文件描述为公共 URL。
- 告诉用户驱动器内容为私有，除非使用作用域令牌共享。
- 与另一个代理共享访问权限时，优先使用具有窄 `pathPrefix` 和短 TTL 的作用域令牌。

## publish.sh 选项（publish.sh options）

| 标志（Flag）                   | 描述（Description）                                  |
| ---------------------- | -------------------------------------------- |
| `--slug {slug}`        | 更新现有站点而非创建 |
| `--claim-token {token}`| 覆盖匿名更新的 claim 令牌    |
| `--title {text}`       | 查看器标题（非 HTML 站点）             |
| `--description {text}` | 查看器描述                            |
| `--ttl {seconds}`      | 设置过期时间（仅限已认证模式）               |
| `--client {name}`      | 用于归因的代理名称（例如 `hermes`）    |
| `--base-url {url}`     | API 基础 URL（默认：`https://here.now`）    |
| `--allow-nonherenow-base-url` | 允许将身份验证发送到非默认的 `--base-url` |
| `--api-key {key}`      | API 密钥覆盖（优先使用凭据文件）    |
| `--spa`                | 启用 SPA 路由（为未知路径提供 index.html） |
| `--forkable`           | 允许其他人分叉此站点                           |

## 超越 publish.sh（Beyond publish.sh）

对于驱动器操作，请使用 `drive.sh` 或驱动器 API。对于更广泛的账户和站点管理——删除、元数据、密码、支付、域名、句柄、链接、变量、代理路由、分叉、复制等——请参阅当前文档：

→ **https://here.now/docs**

完整文档：https://here.now/docs