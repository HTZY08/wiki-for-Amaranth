--- frontmatter ---
---
sidebar_position: 2
sidebar_label: "Google Workspace"
title: "Google Workspace — Gmail、日历、云端硬盘、表格和文档"
description: "通过 OAuth2 认证的 Google API 发送邮件、管理日历事件、搜索云端硬盘、读写表格和访问文档"
---

--- body ---
--- body ---
# Google Workspace 技能（Skill）

针对 Hermes 集成的 Gmail、日历、云端硬盘、联系人、表格和文档。使用 OAuth2 并自动刷新令牌。当可用时，优先使用 [Google Workspace CLI (`gws`)](https://github.com/googleworkspace/cli) 以获得更广泛的覆盖范围，否则回退到 Google 的 Python 客户端库。

**技能路径：** `skills/productivity/google-workspace/`

## 设置

设置完全由代理驱动——让 Hermes 设置 Google Workspace，它会引导你完成每一步。流程如下：

1. **创建 Google Cloud 项目**并启用所需 API（Gmail、日历、云端硬盘、表格、文档、People）
2. **创建 OAuth 2.0 凭据**（桌面应用类型）并下载客户端密钥 JSON
3. **授权**——Hermes 生成一个授权 URL，你在浏览器中批准，然后粘贴回重定向 URL
4. **完成**——从那时起令牌自动刷新

:::tip 仅限电子邮件用户
如果你只需要电子邮件（不需要日历/云端硬盘/表格），请改用 **himalaya** 技能——它使用 Gmail 应用密码，只需 2 分钟，无需 Google Cloud 项目。
:::

## Gmail

### 搜索

```bash
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"
```

返回 JSON，包含每条消息的 `id`、`from`、`subject`、`date`、`snippet` 和 `labels`。

### 读取

```bash
$GAPI gmail get MESSAGE_ID
```

以文本形式返回完整消息正文（优先纯文本，回退到 HTML）。

### 发送

```bash
# 基本发送
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"

# HTML 邮件
$GAPI gmail send --to user@example.com --subject "Report" \
  --body "<h1>Q4 Results</h1><p>Details here</p>" --html

# 自定义发件人标头（显示名称 + 电子邮件）
$GAPI gmail send --to user@example.com --subject "Hello" \
  --from '"Research Agent" <user@example.com>' --body "Message text"

# 带抄送
$GAPI gmail send --to user@example.com --cc "team@example.com" \
  --subject "Update" --body "FYI"
```

### 自定义发件人标头

`--from` 标志允许你在外发邮件中自定义发件人显示名称。当多个代理共享同一个 Gmail 账户但希望收件人看到不同的名称时，这非常有用：

```bash
# 代理 1
$GAPI gmail send --to client@co.com --subject "Research Summary" \
  --from '"Research Agent" <shared@company.com>' --body "..."

# 代理 2  
$GAPI gmail send --to client@co.com --subject "Code Review" \
  --from '"Code Assistant" <shared@company.com>' --body "..."
```

**工作原理：** `--from` 的值被设置为 MIME 消息上的 RFC 5322 `From` 标头。Gmail 允许在你自己的已认证电子邮件地址上自定义显示名称，无需额外配置。收件人看到自定义显示名称（例如“Research Agent”），而电子邮件地址保持不变。

**重要提示：** 如果你在 `--from` 中使用了*不同的电子邮件地址*（不是已认证的账户），Gmail 要求该地址已在 Gmail 设置 → 账户 → 以…身份发送邮件中配置为[以其他地址发送邮件别名](https://support.google.com/mail/answer/22370)。

`--from` 标志同时适用于 `send` 和 `reply`：

```bash
$GAPI gmail reply MESSAGE_ID \
  --from '"Support Bot" <shared@company.com>' --body "We're on it"
```

### 回复

```bash
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
```

自动将回复加入线程（设置 `In-Reply-To` 和 `References` 标头），并使用原始消息的线程 ID。

### 标签

```bash
# 列出所有标签
$GAPI gmail labels

# 添加/移除标签
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

## 日历

```bash
# 列出事件（默认未来7天）
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# 创建事件（需要时区）
$GAPI calendar create --summary "Team Standup" \
  --start 2026-03-01T10:00:00-07:00 --end 2026-03-01T10:30:00-07:00

# 带地点和参与人
$GAPI calendar create --summary "Lunch" \
  --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z \
  --location "Cafe" --attendees "alice@co.com,bob@co.com"

# 删除事件
$GAPI calendar delete EVENT_ID
```

:::warning
日历时间**必须**包含时区偏移（例如 `-07:00`）或使用 UTC（`Z`）。像 `2026-03-01T10:00:00` 这样的裸日期时间会产生歧义，将被视为 UTC。
:::

## 云端硬盘

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

## 表格

```bash
# 读取范围
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# 写入范围
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# 追加行
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

## 文档

```bash
$GAPI docs get DOC_ID
```

返回文档标题和完整文本内容。

## 联系人

```bash
$GAPI contacts list --max 20
```

## 输出格式

所有命令返回 JSON。每个服务的关键字段：

| 命令 | 字段 |
|---------|--------|
| `gmail search` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `snippet`, `labels` |
| `gmail get` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `labels`, `body` |
| `gmail send/reply` | `status`, `id`, `threadId` |
| `calendar list` | `id`, `summary`, `start`, `end`, `location`, `description`, `htmlLink` |
| `calendar create` | `status`, `id`, `summary`, `htmlLink` |
| `drive search` | `id`, `name`, `mimeType`, `modifiedTime`, `webViewLink` |
| `contacts list` | `name`, `emails`, `phones` |
| `sheets get` | 单元格值的二维数组 |

## 问题排查

| 问题 | 解决方案 |
|---------|-----|
| `NOT_AUTHENTICATED` | 运行设置（让 Hermes 设置 Google Workspace） |
| `REFRESH_FAILED` | 令牌已撤销——重新运行授权步骤 |
| `HttpError 403: Insufficient Permission` | 缺少作用域——撤销并使用正确的服务重新授权 |
| `HttpError 403: Access Not Configured` | 在 Google Cloud 控制台中未启用 API |
| `ModuleNotFoundError` | 使用 `--install-deps` 运行设置脚本 |