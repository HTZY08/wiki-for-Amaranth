---
title: Google Workspace
---

title: "Google Workspace — 通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格"
sidebar_label: "Google Workspace"
description: "通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格"
---

--- body ---
{/* 此页面由技能（Skill）的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。编辑源文件 SKILL.md，而非此页面。*/}

# Google Workspace

通过 gws CLI 或 Python 操作 Gmail、日历、云端硬盘、文档、表格。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/productivity/google-workspace` |
| 版本 | `1.1.0` |
| 作者 | Nous Research |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Google`, `Gmail`, `Calendar`, `Drive`, `Sheets`, `Docs`, `Contacts`, `Email`, `OAuth` |
| 相关技能（Related skills） | [`himalaya`](/docs/user-guide/skills/bundled/email/email-himalaya) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理（Agent）在技能激活时看到的指令。
:::

# Google Workspace

通过 Hermes 管理的 OAuth 和轻量级 CLI 封装，操作 Gmail、日历、云端硬盘、联系人、表格和文档。当 `gws` 已安装时，技能将使用它作为执行后端，以覆盖更广泛的 Google Workspace 功能；否则回退到捆绑的 Python 客户端实现。

## 参考

- `references/gmail-search-syntax.md` — Gmail 搜索运算符（is:unread、from:、newer_than: 等）

## 脚本（Scripts）

- `scripts/setup.py` — OAuth2 设置（运行一次以授权）
- `scripts/google_api.py` — 兼容性包装 CLI。它优先使用 `gws`（如果可用）执行操作，同时保留 Hermes 现有的 JSON 输出约定。

## 首次设置

设置过程完全无需交互——你可以逐步操作，使其在 CLI、Telegram、Discord 或任何平台上都能工作。

首先定义一个简写：

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
```

### 第 0 步：检查是否已设置

```bash
$GSETUP --check
```

如果输出 `AUTHENTICATED`，则跳转到用法部分——设置已完成。

### 第 1 步：分类——询问用户需要什么

在开始 OAuth 设置之前，先问用户两个问题：

**问题 1："你需要哪些 Google 服务？仅邮件，还是也需要日历/云端硬盘/表格/文档？"**

- **仅邮件** → 用户根本不需要此技能。改用 `himalaya` 技能——它使用 Gmail 应用密码（设置 → 安全性 → 应用密码），只需 2 分钟即可设置完成，无需 Google Cloud 项目。加载 himalaya 技能并按照其设置说明操作。
- **邮件 + 日历** → 继续使用此技能，但在授权时使用 `--services email,calendar`，这样同意屏幕仅请求所需的范围（scopes）。
- **仅日历/云端硬盘/表格/文档** → 继续使用此技能，并使用更窄的 `--services` 集合，例如 `calendar,drive,sheets,docs`。
- **完整 Workspace 访问权限** → 继续使用此技能，并使用默认的 `all` 服务集合。

**问题 2："你的 Google 账号是否启用了高级保护（需要硬件安全密钥才能登录）？如果不确定，很可能没有——这是一种需要明确注册的功能。"**

- **否 / 不确定** → 正常设置。继续下面步骤。
- **是** → 管理员必须将 OAuth 客户端 ID 添加到组织允许的应用列表中，然后第 4 步才能生效。提前告知用户。

### 第 2 步：创建 OAuth 凭据（一次性，约 5 分钟）

告诉用户：

> 你需要一个 Google Cloud OAuth 客户端。这是一次性设置：
>
> 1. 创建或选择一个项目：
>    https://console.cloud.google.com/projectselector2/home/dashboard
> 2. 从 API 库启用所需的 API：
>    https://console.cloud.google.com/apis/library
>    启用：Gmail API、Google Calendar API、Google Drive API、
>    Google Sheets API、Google Docs API、People API
> 3. 在此处创建 OAuth 客户端：
>    https://console.cloud.google.com/apis/credentials
>    凭据 → 创建凭据 → OAuth 2.0 客户端 ID
> 4. 应用程序类型："桌面应用" → 创建
> 5. 如果应用仍处于测试状态，请在此处添加用户的 Google 账号作为测试用户：
>    https://console.cloud.google.com/auth/audience
>    受众 → 测试用户 → 添加用户
> 6. 下载 JSON 文件并告诉我文件路径
>
> 重要 Hermes CLI 说明：如果文件路径以 `/` 开头，请不要仅将原始路径作为单独消息发送到 CLI，因为它可能被误认为是斜杠命令。应在句子中发送，例如：
> `JSON 文件路径是：/home/user/Downloads/client_secret_....json`

当用户提供路径后：

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

如果用户粘贴的是原始的客户端 ID / 客户端密钥值而不是文件路径，请自行为他们编写一个有效的桌面 OAuth JSON 文件，将其保存到明确的位置（例如 `~/Downloads/hermes-google-client-secret.json`），然后针对该文件运行 `--client-secret`。

### 第 3 步：获取授权 URL

使用在第 1 步中选择的服务集合。示例：

```bash
$GSETUP --auth-url --services email,calendar --format json
$GSETUP --auth-url --services calendar,drive,sheets,docs --format json
$GSETUP --auth-url --services all --format json
```

这将返回一个包含 `auth_url` 字段的 JSON，并将确切的 URL 保存到 `~/.hermes/google_oauth_last_url.txt`。

此步骤的代理（Agent）规则：
- 提取 `auth_url` 字段，并将该确切 URL 作为单行发送给用户。
- 告诉用户，批准后浏览器很可能在 `http://localhost:1` 上失败，这是预期行为。
- 告诉他们从浏览器地址栏复制整个重定向后的 URL。
- 如果用户遇到 `Error 403: access_denied`，直接将其引导至 `https://console.cloud.google.com/auth/audience`，让他们将自己添加为测试用户。

### 第 4 步：交换代码

用户将粘贴回一个 URL（例如 `http://localhost:1/?code=4/0A...&scope=...`）或仅粘贴代码字符串。两者均可。`--auth-url` 步骤会临时存储一个待处理的 OAuth 会话状态到本地，以便 `--auth-code` 稍后完成 PKCE 交换，即使在无头系统上也能工作：

```bash
$GSETUP --auth-code "用户粘贴的URL或代码" --format json
```

如果 `--auth-code` 因代码过期、已被使用或来自较旧的浏览器标签页而失败，它将返回一个新的 `fresh_auth_url`。在这种情况下，立即将新的 URL 发送给用户，让他们仅使用最新的浏览器重定向重试。

### 第 5 步：验证

```bash
$GSETUP --check
```

应输出 `AUTHENTICATED`。设置完成——令牌从此会自动刷新。

### 备注

- 令牌存储在 `~/.hermes/google_token.json` 并自动刷新。
- 待处理的 OAuth 会话状态/验证器临时存储在 `~/.hermes/google_oauth_pending.json`，直到交换完成。
- 如果 `gws` 已安装，`google_api.py` 会将其指向相同的 `~/.hermes/google_token.json` 凭据文件。用户无需单独运行 `gws auth login` 流程。
- 撤销：`$GSETUP --revoke`

## 用法

所有命令都通过 API 脚本执行。将 `GAPI` 设置为简写：

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

### Gmail

```bash
# 搜索（返回包含 id、from、subject、date、snippet 的 JSON 数组）
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# 阅读完整邮件（返回包含正文文本的 JSON）
$GAPI gmail get MESSAGE_ID

# 发送
$GAPI gmail send --to user@example.com --subject "Hello" --body "消息文本"
$GAPI gmail send --to user@example.com --subject "报告" --body "<h1>Q4</h1><p>详情...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "消息文本"

# 回复（自动创建线程并设置 In-Reply-To）
$GAPI gmail reply MESSAGE_ID --body "谢谢，这个时间可以。"
$GAPI gmail reply MESSAGE_ID --from '"支持机器人" <user@example.com>' --body "谢谢"

# 标签
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### 日历

```bash
# 列出事件（默认为未来 7 天）
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# 创建事件（需要 ISO 8601 带时区）
$GAPI calendar create --summary "团队站会" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "午餐" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "咖啡厅"
$GAPI calendar create --summary "审查" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# 删除事件
$GAPI calendar delete EVENT_ID
```

### 云端硬盘

```bash
# 搜索已有文件
$GAPI drive search "季度报告" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# 获取单个文件的元数据
$GAPI drive get FILE_ID

# 上传本地文件（自动检测 MIME 类型）
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# 下载（二进制文件原样下载；Google 原生文件导出为合理的默认格式：
# 文档→pdf、表格→csv、幻灯片→pdf、绘图→png）
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# 创建文件夹
$GAPI drive create-folder "报告"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# 共享
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # 任何人拥有链接
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# 删除——默认为垃圾箱（可恢复）。使用 --permanent 可跳过垃圾箱。
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent
```

### 联系人

```bash
$GAPI contacts list --max 20
```

### 表格

```bash
# 创建新电子表格
$GAPI sheets create --title "Q4 预算"
$GAPI sheets create --title "库存" --sheet-name "存货"

# 读取
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# 写入
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["姓名","分数"],["Alice","95"]]'

# 追加行
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["新","行","数据"]]'
```

### 文档

```bash
# 读取
$GAPI docs get DOC_ID

# 创建新文档（可选地添加初始正文文本）
$GAPI docs create --title "会议记录"
$GAPI docs create --title "草稿" --body "第一段..."

# 在已有文档末尾追加文本
$GAPI docs append DOC_ID --text "要追加的附加内容"
```

## 输出格式

所有命令返回 JSON。使用 `jq` 解析或直接读取。关键字段：

- **Gmail search**：`[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**：`{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**：`{status: "sent", id, threadId}`
- **Calendar list**：`[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**：`{status: "created", id, summary, htmlLink}`
- **Drive search**：`[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive get**：`{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive upload**：`{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive download**：`{status: "downloaded", id, name, path, mimeType}`
- **Drive create-folder**：`{status: "created", id, name, webViewLink}`
- **Drive share**：`{status: "shared", permissionId, fileId, role, type}`
- **Drive delete**：`{status: "trashed" | "deleted", fileId, permanent}`
- **Contacts list**：`[{name, emails: [...], phones: [...]}]`
- **Sheets get**：`[[单元格, 单元格, ...], ...]`
- **Sheets create**：`{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs create**：`{status: "created", documentId, title, url}`
- **Docs append**：`{status: "appended", documentId, inserted_at, characters}`

## 规则

1. **未经用户确认，不得发送邮件、创建/删除日历事件、删除云端硬盘文件、共享文件或修改文档/表格。** 显示将要执行的操作（收件人、文件 ID、内容、共享角色）并请求批准。对于 `drive delete`，优先使用默认的垃圾箱（可恢复）而不是 `--permanent`。
2. **首次使用前检查身份验证**——运行 `setup.py --check`。如果失败，引导用户完成设置。
3. **对于复杂查询，使用 Gmail 搜索语法参考**——通过 `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")` 加载。
4. **日历时间必须包含时区**——始终使用带偏移量的 ISO 8601（例如 `2026-03-01T10:00:00-06:00`）或 UTC（`Z`）。
5. **遵守速率限制**——避免快速连续调用 API。尽可能批量读取。

## 故障排除

| 问题 | 解决方法 |
|------|----------|
| `NOT_AUTHENTICATED` | 运行上述设置步骤 2-5 |
| `REFRESH_FAILED` | 令牌被撤销或过期——重新执行步骤 3-5 |
| `HttpError 403: Insufficient Permission` | 缺少 API 范围——`$GSETUP --revoke` 然后重新执行步骤 3-5 |
| `AUTHENTICATED (partial)` 或 "Token missing scopes" | 新的写入能力（Drive 写入/删除、Docs 创建/编辑）需要重新授权。`$GSETUP --revoke` 然后重新执行步骤 3-5 以授予升级后的范围。 |
| `HttpError 403: Access Not Configured` | API 未启用——用户需要在 Google Cloud Console 中启用它 |
| `ModuleNotFoundError` | 运行 `$GSETUP --install-deps` |
| 高级保护阻止授权 | Workspace 管理员必须将 OAuth 客户端 ID 加入白名单 |

## 撤销访问权限

```bash
$GSETUP --revoke
```