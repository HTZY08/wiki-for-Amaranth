---
title: Discord
---

sidebar_position: 3
title: "Discord"
description: "将 Hermes Agent 设置为 Discord 机器人"
---

--- body ---
# Discord 设置

Hermes Agent 以机器人（bot）的形式与 Discord 集成，让您可以通过私信或服务器频道与您的 AI 助手聊天。该机器人接收您的消息，通过 Hermes Agent 处理管道（包括工具使用、记忆和推理），并实时响应。它支持文本、语音消息、文件附件和斜杠命令。

在设置之前，以下是大多数人最想了解的部分：Hermes 进入您的服务器后的行为方式。

## Hermes 的行为方式

| 上下文 | 行为 |
|---------|----------|
| **私信** | Hermes 回复每一条消息。无需 `@提及`。每条私信都有独立的会话（session）。 |
| **服务器频道** | 默认情况下，Hermes 仅在您 `@提及` 它时才会回复。如果您在没有提及它的情况下在频道中发帖，Hermes 会忽略该消息。 |
| **自由响应频道** | 您可以使用 `DISCORD_FREE_RESPONSE_CHANNELS` 让特定频道免于提及，或通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及。这些频道中的消息会被内联回复——跳过自动线程，以保持频道轻量化的聊天体验。 |
| **线程（Threads）** | Hermes 在同一线程中回复。提及规则仍然适用，除非该线程或其父频道被配置为自由响应。线程与父频道的会话历史相互隔离。 |
| **多个用户共享的频道** | 默认情况下，Hermes 会在频道内按用户隔离会话历史，以确保安全和清晰。两个人在同一频道中说话不会共享同一份记录，除非您明确禁用此功能。 |
| **提及了其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 为 `true`（默认值）时，如果一条消息 @提及了其他用户但**未**提及机器人，Hermes 保持沉默。这可以防止机器人参与针对其他人的对话。如果您希望机器人回应所有消息（无论提及了谁），请设置为 `false`。此设置仅适用于服务器频道，不适用于私信。 |

:::tip
如果您想要一个普通的机器人帮助频道，用户可以在其中与 Hermes 交流而无需每次都标记它，请将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中。
:::

### Discord 网关模型

Discord 上的 Hermes 并非无状态回复的 Webhook。它通过完整的消息网关运行，这意味着每条传入消息都会经历：

1. 授权（`DISCORD_ALLOWED_USERS`）
2. 提及/自由响应检查
3. 会话查找
4. 会话记录加载
5. 正常的 Hermes 代理执行，包括工具、记忆和斜杠命令
6. 将响应发送回 Discord

这很重要，因为在繁忙的服务器中，行为取决于 Discord 路由和 Hermes 会话策略。

### Discord 中的会话模型

默认情况下：

- 每个私信拥有自己的会话
- 每个服务器线程拥有自己的会话命名空间
- 共享频道中的每个用户在该频道内拥有自己的会话

因此，如果 Alice 和 Bob 都在 `#research` 频道中与 Hermes 交谈，Hermes 默认会将它们视为独立的会话，即使它们使用的是同一个可见的 Discord 频道。

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当您明确希望整个房间共享一个对话时，才设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

- 用户共享上下文增长和 token 成本
- 一个人的长时间工具密集型任务可能会膨胀所有人的上下文
- 一个人正在进行的操作可能会中断同个房间中另一个人的后续操作

### 中断与并发

Hermes 通过会话键跟踪正在运行的代理。

使用默认的 `group_sessions_per_user: true`：

- Alice 打断自己正在进行的请求只影响 Alice 在该频道的会话
- Bob 可以在同一频道继续交谈，而不会继承 Alice 的历史或中断 Alice 的运行

使用 `group_sessions_per_user: false`：

- 整个房间共享一个正在运行的代理槽位（用于该频道/线程）
- 不同人的后续消息可能相互打断或排队

本指南将带您完成完整的设置过程——从在 Discord 开发者门户创建机器人到发送第一条消息。

## 第一步：创建 Discord 应用

1. 前往 [Discord 开发者门户](https://discord.com/developers/applications) 并使用您的 Discord 账户登录。
2. 点击右上角的 **New Application**。
3. 输入您的应用名称（例如 "Hermes Agent"），并接受开发者服务条款。
4. 点击 **Create**。

您将进入 **General Information** 页面。记下 **Application ID**——稍后您将需要它来构建邀请 URL。

## 第二步：创建机器人

1. 在左侧边栏中，点击 **Bot**。
2. Discord 会自动为您的应用创建一个机器人用户。您将看到机器人的用户名，您可以自定义它。
3. 在 **Authorization Flow** 下：
   - 将 **Public Bot** 设置为 **ON**——需要使用 Discord 提供的邀请链接（推荐）。这允许“安装”选项卡生成默认的授权 URL。
   - 将 **Require OAuth2 Code Grant** 保持为 **OFF**。

:::tip
您可以在此页面为您的机器人设置自定义头像和横幅。这将是用户在 Discord 中看到的样子。
:::

:::info[私有机器人替代方案]
如果您希望保持机器人私有（Public Bot = OFF），您**必须**使用第五步中的 **Manual URL** 方法，而不是“安装”选项卡。Discord 提供的链接要求启用 Public Bot。
:::

## 第三步：启用特权网关意图

这是整个设置中最关键的一步。如果没有启用正确的意图，您的机器人将连接到 Discord，但**无法读取消息内容**。

在 **Bot** 页面，向下滚动到 **Privileged Gateway Intents**。您将看到三个开关：

| 意图 | 用途 | 是否需要？ |
|--------|---------|-----------| 
| **Presence Intent** | 查看用户在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表，解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |

**同时启用 Server Members Intent 和 Message Content Intent**：将它们切换到 **ON**。

- 没有 **Message Content Intent**，您的机器人会收到消息事件，但消息文本是空的——机器人实际上看不到您输入了什么。
- 没有 **Server Members Intent**，机器人无法解析允许用户列表中的用户名，可能无法识别谁在发送消息。

:::warning[这是 Discord 机器人不工作的首要原因]
如果您的机器人处于在线状态但从不回复消息，那么 **Message Content Intent** 几乎肯定被禁用了。返回 [开发者门户](https://discord.com/developers/applications)，选择您的应用 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已打开。点击 **Save Changes**。
:::

**关于服务器数量：**
- 如果您的机器人在 **少于 100 个服务器** 中，您可以自由切换意图。
- 如果您的机器人在 **100 个或更多服务器** 中，Discord 要求您提交验证申请才能使用特权意图。对于个人使用，这无需担心。

点击页面底部的 **Save Changes**。

## 第四步：获取机器人令牌

机器人令牌是 Hermes Agent 用来登录为您机器人的凭证。仍在 **Bot** 页面：

1. 在 **Token** 部分下，点击 **Reset Token**。
2. 如果您的 Discord 账户启用了双因素认证，请输入您的 2FA 代码。
3. Discord 将显示您的新令牌。**立即复制它。**

:::warning[令牌只显示一次]
令牌只显示一次。如果您丢失了它，您需要重置并生成一个新的。切勿公开分享您的令牌或将其提交到 Git——拥有此令牌的任何人可以完全控制您的机器人。
:::

将令牌安全地存储在某处（例如密码管理器）。您将在第八步中用到它。

## 第五步：生成邀请 URL

您需要一个 OAuth2 URL 来邀请机器人到您的服务器。有两种方法：

### 选项 A：使用安装选项卡（推荐）

:::note[需要 Public Bot]
此方法要求第二步中 **Public Bot** 设置为 **ON**。如果您将 Public Bot 设置为 OFF，请改用下面的 Manual URL 方法。
:::

1. 在左侧边栏中，点击 **Installation**。
2. 在 **Installation Contexts** 下，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 **Default Install Settings** 的 Guild Install 下：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下面列出的权限。

### 选项 B：手动 URL

您可以直接使用以下格式构建邀请 URL：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

将 `YOUR_APP_ID` 替换为第一步中的 Application ID。

### 必需权限

这些是机器人所需的最低权限：

- **View Channels** — 查看它可以访问的频道
- **Send Messages** — 回复您的消息
- **Embed Links** — 格式化丰富的响应
- **Attach Files** — 发送图像、音频和文件输出
- **Read Message History** — 维护对话上下文

### 推荐附加权限

- **Send Messages in Threads** — 在线程对话中回复
- **Add Reactions** — 添加表情反应以确认

### 权限整数

| 级别 | 权限整数 | 包含内容 |
|-------|-------------------|-----------------|
| 最小 | `117760` | 查看频道、发送消息、阅读消息历史、附加文件 |
| 推荐 | `274878286912` | 以上所有权限加上嵌入链接、在线程中发送消息、添加反应 |

## 第六步：邀请到您的服务器

1. 在浏览器中打开邀请 URL（来自安装选项卡或您构建的手动 URL）。
2. 在 **添加至服务器** 下拉菜单中，选择您的服务器。
3. 点击 **继续**，然后 **授权**。
4. 如果提示，完成验证码。

:::info
您需要在 Discord 服务器上拥有 **管理服务器** 权限才能邀请机器人。如果您在下拉菜单中看不到您的服务器，请让服务器管理员使用邀请链接。
:::

授权后，机器人会出现在您服务器的成员列表中（在您启动 Hermes 网关之前，它会显示为离线状态）。

## 第七步：找到您的 Discord 用户 ID

Hermes Agent 使用您的 Discord 用户 ID 来控制谁可以与机器人交互。查找方法：

1. 打开 Discord（桌面应用或网页版）。
2. 前往 **设置** → **高级** → 将 **开发者模式** 切换为 **ON**。
3. 关闭设置。
4. 右键点击您自己的用户名（在消息中、成员列表或您的个人资料上）→ **复制用户 ID**。

您的用户 ID 是一个长数字，例如 `284102345871466496`。

:::tip
开发者模式还允许您以相同的方式复制 **频道 ID** 和 **服务器 ID**——右键点击频道或服务器名称，选择“复制 ID”。如果您想手动设置一个主频道，您将需要频道 ID。
:::

## 第八步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Discord**，然后粘贴您的机器人令牌和用户 ID。

### 选项 B：手动配置

将以下内容添加到您的 `~/.hermes/.env` 文件中：

```bash
# 必需
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# 多个允许用户（逗号分隔）
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

然后启动网关：

```bash
hermes gateway
```

几秒钟内，机器人应该在 Discord 中上线。给它发一条消息——无论是私信还是它可以看到的频道——来测试。

:::tip
您可以在后台运行 `hermes gateway`，或将其作为 systemd 服务以实现持久运行。详情请参阅部署文档。
:::

## 配置参考

Discord 行为通过两个文件控制：**`~/.hermes/.env`** 用于凭证和环境级别开关，以及 **`~/.hermes/config.yaml`** 用于结构化设置。当两者都设置时，环境变量始终优先于 config.yaml 中的值。

### 环境变量 (`.env`)

| 变量 | 必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord 开发者门户](https://discord.com/developers/applications) 的机器人令牌。 |
| `DISCORD_ALLOWED_USERS` | **是** | — | 允许与机器人交互的 Discord 用户 ID，逗号分隔。没有这个或 `DISCORD_ALLOWED_ROLES`，网关会拒绝所有用户。 |
| `DISCORD_ALLOWED_ROLES` | 否 | — | 逗号分隔的 Discord 角色 ID。拥有这些角色之一的成员即被授权——与 `DISCORD_ALLOWED_USERS` 是 OR 语义。连接时会自动启用 **Server Members Intent**。当审核团队变动时很有用：新版主获得角色后立即拥有访问权限，无需推送配置。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | 机器人发送主动消息（cron 输出、提醒、通知）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 主频道在日志和状态输出中的显示名称。 |
| `DISCORD_COMMAND_SYNC_POLICY` | 否 | `"safe"` | 控制原生斜杠命令启动同步。`"safe"` 对现有全局命令进行 diff，仅更新变化的内容，当 Discord 元数据更改无法通过补丁应用时重新创建命令。`"bulk"` 保留旧的 `tree.sync()` 行为。`"off"` 完全跳过启动同步。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 当为 `true` 时，机器人仅在服务器频道中被 `@提及` 时才会回复。设置为 `false` 以响应所有频道中的所有消息。 |
| `DISCORD_THREAD_REQUIRE_MENTION` | 否 | `false` | 当为 `true` 时，线程内的提及快捷方式被禁用——线程与频道一样受到限制，即使机器人已经参与其中，也需要 `@提及`。当多个机器人共享一个线程，您希望每个机器人仅通过显式 `@提及` 触发时使用此设置。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人无需 `@提及` 即可响应，即使 `DISCORD_REQUIRE_MENTION` 为 `true`。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 当为 `true` 时，如果一条消息 `@提及` 了其他用户但**未**提及机器人，机器人保持沉默。防止机器人跳入针对其他人的对话。仅适用于服务器频道，不适用于私信。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 当为 `true` 时，自动为文本频道中的每个 `@提及` 创建一个新线程，以便每个对话都是隔离的（类似于 Slack 行为）。已经在线程或私信中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制机器人如何处理来自其他 Discord 机器人的消息。`"none"` — 忽略所有其他机器人。`"mentions"` — 仅接受 `@提及` Hermes 的机器人消息。`"all"` — 接受所有机器人消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 当为 `true` 时，机器人在处理消息时添加表情反应（开始处理时 👀，成功时 ✅，错误时 ❌）。设置为 `false` 以完全禁用反应。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人**从不**响应，即使被 `@提及`。优先级高于所有其他频道设置。 |
| `DISCORD_ALLOWED_CHANNELS` | 否 | — | 逗号分隔的频道 ID。设置后，机器人**仅**在这些频道中响应（以及允许的私信）。覆盖 `config.yaml` 中的 `discord.allowed_channels`。与 `DISCORD_IGNORED_CHANNELS` 结合使用以表达允许/拒绝规则。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 逗号分隔的频道 ID，在这些频道中机器人直接在该频道中响应，而不是创建线程。仅在 `DISCORD_AUTO_THREAD` 为 `true` 时相关。 |
| `DISCORD_HISTORY_BACKFILL` | 否 | `true` | 当为 `true` 时，在机器人被提及后，会在用户消息前附加最近的频道回滚消息（自上次机器人响应以来）。恢复机器人因 `require_mention` 而可能错过的上下文。在私信和自由响应频道中跳过。设置为 `false` 以禁用。 |
| `DISCORD_HISTORY_BACKFILL_LIMIT` | 否 | `50` | 向后扫描以构建回滚块的最大消息数量。实际上，扫描通常更早停止——在机器人自己在频道中的最后一条消息处。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` — 从不回复原始消息，`"first"` — 仅对第一条消息块进行回复引用（默认），`"all"` — 对每个块进行回复引用。 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 否 | `false` | 当为 `false`（默认）时，机器人无法 @提及 `@everyone` 或 `@here`，即使其响应中包含这些令牌。设置为 `true` 以重新启用。请参阅下面的提及控制。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 否 | `false` | 当为 `false`（默认）时，机器人无法 @提及 `@role`。设置为 `true` 以允许。 |
| `DISCORD_ALLOW_MENTION_USERS` | 否 | `true` | 当为 `true`（默认）时，机器人可以通过 ID @提及单个用户。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 否 | `true` | 当为 `true`（默认）时，回复消息会 @提及原始作者。 |
| `DISCORD_PROXY` | 否 | — | Discord 连接的代理 URL（HTTP、WebSocket、REST）。覆盖 `HTTPS_PROXY`/`ALL_PROXY`。支持 `http://`、`https://` 和 `socks5://` 协议。 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 否 | `false` | 当为 `true` 时，机器人接受任何文件类型的附件（不仅限于内置的 PDF/文本/zip/办公文档白名单）。未知类型会被缓存到磁盘，并以本地路径和 `application/octet-stream` MIME 类型呈现给代理，以便其可以使用 `terminal` / `read_file` / `ffprobe` 等进行检查。 |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 否 | `33554432` | 网关将下载和缓存的每个附件的最大字节数。默认 32 MiB。设置为 `0` 表示无上限（附件在写入时保存在内存中，因此无上限会带来实际的内存成本）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 否 | `0.6` | 适配器在刷新排队文本块之前等待的宽限窗口。用于平滑流式输出。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 否 | `2.0` | 当单条消息超过 Discord 长度限制时，拆分块之间的延迟。 |

### 配置文件 (`config.yaml`)

`~/.hermes/config.yaml` 中的 `discord` 部分镜像了上述环境变量。Config.yaml 中的设置作为默认值应用——如果等效的环境变量已设置，则环境变量优先。

```yaml
# Discord-specific settings
discord:
  require_mention: true           # 在服务器频道中需要 @提及
  thread_require_mention: false   # 如果为 true，在线程中也要求 @提及（多机器人线程）
  free_response_channels: ""      # 逗号分隔的频道 ID（或 YAML 列表）
  auto_thread: true               # 在 @提及 时自动创建线程
  reactions: true                 # 在处理期间添加表情反应
  ignored_channels: []            # 机器人从不响应的频道 ID
  no_thread_channels: []          # 机器人直接响应而不创建线程的频道 ID
  history_backfill: true          # 在提及后附加最近的频道回滚（默认：true）
  history_backfill_limit: 50      # 向后扫描的最大消息数（默认：50）
  channel_prompts: {}             # 每个频道的临时系统提示
  allow_mentions:                 # 允许机器人提及的内容（安全默认值）
    everyone: false               # @everyone / @here 提及（默认：false）
    roles: false                  # @role 提及（默认：false）
    users: true                   # @user 提及（默认：true）
    replied_user: true            # 回复引用提及作者（默认：true）

# 会话隔离（适用于所有网关平台，不仅限于 Discord）
group_sessions_per_user: true     # 在共享频道中按用户隔离会话
```

#### `discord.require_mention`

**类型：** 布尔值 — **默认：** `true`

启用时，机器人仅在服务器频道中被直接 `@提及` 时才会响应。无论此设置如何，私信始终响应。

#### `discord.thread_require_mention`

**类型：** 布尔值 — **默认：** `false`

默认情况下，一旦机器人参与了一个线程（在 `@提及` 时自动创建或回复过一次），它会在该线程中继续响应后续每条消息，而无需再次 `@提及`。这是一对一对话的正确默认行为。

在**多机器人线程**中，用户每次转向一个机器人，这个默认值可能成为问题——线程中的每个其他机器人也会对每条消息触发，消耗 token 并刷屏频道。设置 `thread_require_mention: true` 来禁用线程内快捷方式，并使线程与频道一样受到限制。显式的 `@提及` 仍然有效。

```yaml
discord:
  require_mention: true
  thread_require_mention: true    # 多机器人设置
```

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认：** `""`

机器人在这些频道中无需 `@提及` 即可响应所有消息的频道 ID。接受逗号分隔的字符串或 YAML 列表：

```yaml
# 字符串格式
discord:
  free_response_channels: "1234567890,9876543210"

# 列表格式
discord:
  free_response_channels:
    - 1234567890
    - 9876543210
```

如果某个线程的父频道在此列表中，该线程也成为免提及频道。

自由响应频道也**跳过自动创建线程**——机器人内联回复，而不是为每条消息创建新线程。这使频道可以作为轻量级聊天界面使用。如果您想要线程行为，请不要将频道列为自由响应（改用正常的 `@提及` 流程）。

#### `discord.auto_thread`

**类型：** 布尔值 — **默认：** `true`

启用时，常规文本频道中的每个 `@提及` 都会自动为对话创建一个新线程。这保持主频道整洁，并为每个对话提供自己隔离的会话历史。创建线程后，该线程中的后续消息不需要 `@提及`——机器人知道它已经参与其中。设置 [`thread_require_mention`](#discordthread_require_mention) 为 `true` 以禁用此线程内快捷方式（用于多机器人设置）。

发送到现有线程或私信的消息不受此设置影响。列在 `discord.free_response_channels` 或 `discord.no_thread_channels` 中的频道也会绕过自动线程化，而是进行内联回复。

#### `discord.reactions`

**类型：** 布尔值 — **默认：** `true`

控制机器人是否添加表情反应作为视觉反馈：
- 👀 当机器人开始处理您的消息时添加
- ✅ 当响应成功发送时添加
- ❌ 如果处理过程中发生错误时添加

如果您觉得反应分散注意力，或者机器人的角色没有“添加反应”权限，请禁用它。

#### `discord.ignored_channels`

**类型：** 字符串或列表 — **默认：** `[]`

机器人**从不**响应的频道 ID，即使被直接 `@提及`。这具有最高优先级——如果某个频道在此列表中，机器人会默默地忽略该处的所有消息，无论 `require_mention`、`free_response_channels` 或其他任何设置如何。

```yaml
# 字符串格式
discord:
  ignored_channels: "1234567890,9876543210"

# 列表格式
discord:
  ignored_channels:
    - 1234567890
    - 9876543210
```

如果某个线程的父频道在此列表中，该线程中的消息也会被忽略。

#### `discord.no_thread_channels`

**类型：** 字符串或列表 — **默认：** `[]`

在这些频道中，机器人直接在该频道中响应，而不是自动创建线程。这仅在 `auto_thread` 为 `true`（默认）时有效。在这些频道中，机器人像普通消息一样内联回复，而不是生成新线程。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # 机器人在这里内联回复
```

适用于专用于机器人交互的频道，在这些频道中线程会带来不必要的噪音。

#### `discord.channel_prompts`

**类型：** 映射 — **默认：** `{}`

每个频道的临时系统提示，在每个轮次中注入到匹配的 Discord 频道或线程中，但不会持久化到记录历史中。

```yaml
discord:
  channel_prompts:
    "1234567890": |
      此频道用于研究任务。优先深度比较、引用和简洁的综合。
    "9876543210": |
      此论坛用于治疗式支持。要温暖、接地气且不评判。
```

行为：
- 精确的线程/频道 ID 匹配获胜。
- 如果消息到达线程或论坛帖子内，且该线程没有显式条目，Hermes 会回退到父频道/论坛 ID。
- 提示在运行时临时应用，因此更改它们会立即影响未来的轮次，而无需重写过去的会话历史。

#### `discord.history_backfill`

**类型：** 布尔值 — **默认：** `true`

启用后，机器人会在每次 `@提及` 时恢复遗漏的频道消息。当 `require_mention: true` 时，机器人只处理直接标记它的消息——频道中其他所有内容对会话记录都是不可见的。历史回填在触发时向后扫描最近的频道历史，收集机器人上次响应和当前提及之间的消息，并将其包含为上下文。

按表面区分的行为：

- **服务器频道**（使用 `require_mention: true`）：回填扫描自机器人上次响应以来的频道历史。当机器人未被寻址时其他参与者发帖时有用。
- **线程**：回填只扫描线程——Discord 的 `channel.history()` 在线程上只返回该线程的消息，而不是父频道。这是正确的范围，因为线程通常是自包含的对话。
- **私信**：跳过。每一条私信都会触发机器人，因此会话记录已经完整——没有提及缺口需要填补。
- **自由响应频道**和**机器人自己创建的线程**：同样跳过，因为没有提及限制意味着没有缺口。

按用户隔离的会话（`group_sessions_per_user: true`，默认）也受益：用户的会话缺少其他频道参与者发布的上下文，以及用户自己在标记机器人之前发布的消息。回填填补了这两个缺口。

```yaml
discord:
  history_backfill: true   # 默认
```

要关闭它：

```yaml
discord:
  history_backfill: false
```

> **注意：** 在机器人处理期间（触发和响应之间）到达的消息不会被捕获。这是一个可接受的简化——用户可以重新发送或再次标记。

#### `discord.history_backfill_limit`

**类型：** 整数 — **默认：** `50`

向后扫描以恢复频道上下文的最大消息数量。实际上，扫描通常更早停止——在机器人自己在频道中的最后一条消息处，这是轮次之间的自然边界。这个限制是针对冷启动和长时间间隔（近期历史中没有先前的机器人消息）的安全上限。

```yaml
discord:
  history_backfill: true
  history_backfill_limit: 50
```

#### `group_sessions_per_user`

**类型：** 布尔值 — **默认：** `true`

这是一个全局网关设置（不仅限于 Discord），控制同一频道中的用户是否获得隔离的会话历史。

当为 `true`：Alice 和 Bob 在 `#research` 中交谈各自拥有与 Hermes 的独立对话。当为 `false`：整个频道共享一个对话记录和一个正在运行的代理槽位。

```yaml
group_sessions_per_user: true
```

参见上面的 [会话模型](#discord-中的会话模型) 部分，了解每种模式的完整含义。

#### `display.tool_progress`

**类型：** 字符串 — **默认：** `"all"` — **取值：** `off`, `new`, `all`, `verbose`

控制机器人是否在处理期间在聊天中发送进度消息（例如“正在读取文件...”、“正在运行终端命令...”）。这是一个应用于所有平台的全局网关设置。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 无进度消息
- `new` — 仅显示每个轮次中第一次工具调用
- `all` — 显示所有工具调用（在网关消息中截断至 40 个字符）
- `verbose` — 显示完整的工具调用详情（可能产生长消息）

#### `display.tool_progress_command`

**类型：** 布尔值 — **默认：** `false`

启用后，会在网关中提供 `/verbose` 斜杠命令，让您可以在工具进度模式之间循环切换（`off → new → all → verbose → off`），而无需编辑 config.yaml。

```yaml
display:
  tool_progress_command: true
```

## 斜杠命令访问控制

默认情况下，每个允许的用户都可以执行所有斜杠命令。要将您的允许列表拆分为**管理员**（完全斜杠命令访问权限）和**普通用户**（仅限您显式启用的命令），请在 Discord 平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    discord:
      extra:
        # 现有用户允许列表（不变）
        allow_from:
          - "123456789012345678"  # 管理员用户 ID
          - "999888777666555444"  # 普通用户 ID

        # 新增——管理员获得所有斜杠命令（内置 + 插件）
        allow_admin_from:
          - "123456789012345678"

        # 新增——非管理员允许用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户可以看到自己的访问权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：服务器频道的单独管理员 / 命令列表
        group_allow_admin_from:
          - "123456789012345678"
        group_user_allowed_commands:
          - status
```

**行为：**

- 在某个范围（私信或服务器频道）的 `allow_admin_from` 中的用户可以运行**每个**已注册的斜杠命令——内置和插件注册的——通过实时命令注册表。
- 不在 `allow_admin_from` 中的用户只能运行 `user_allowed_commands` 中列出的命令，加上始终允许的基本命令：`/help` 和 `/whoami`。
- 普通聊天（非斜杠消息）不受影响。非管理员用户仍然可以正常与代理交谈；他们只是无法触发任意命令。
- **向后兼容：** 如果某个范围没有设置 `allow_admin_from`，则该范围的斜杠命令门控被禁用。现有安装无需更改即可继续工作。
- 私信管理员状态不代表服务器频道管理员状态。每个范围都有自己的管理员列表。

使用 `/whoami` 查看活动范围、您的级别（admin / user / unrestricted）以及您可以运行哪些斜杠命令。

## 交互式模型选择器

在 Discord 频道中发送 `/model` 且不带参数，即可打开基于下拉菜单的模型选择器：

1. **提供商选择** — 一个显示可用提供商（最多 25 个）的选择下拉菜单。
2. **模型选择** — 第二个下拉菜单，显示所选提供商的模型（最多 25 个）。

选择器在 120 秒后超时。只有授权用户（`DISCORD_ALLOWED_USERS` 中的用户）可以与其交互。如果您知道模型名称，直接输入 `/model <name>`。

## 技能的原生斜杠命令

Hermes 自动将已安装的技能注册为**原生 Discord 应用程序命令**。这意味着技能会出现在 Discord 的自动补全 `/` 菜单中，与内置命令并列。

- 每个技能成为一个 Discord 斜杠命令（例如 `/code-review`、`/ascii-art`）
- 技能接受可选的 `args` 字符串参数
- Discord 对每个机器人最多有 100 个应用程序命令的限制——如果您的技能超过可用槽位，额外的技能会被跳过并在日志中显示警告
- 技能在机器人启动时与内置命令（如 `/model`、`/reset` 和 `/background`）一起注册

无需额外配置——任何通过 `hermes skills install` 安装的技能都会在下一次网关重启时自动注册为 Discord 斜杠命令。

### 禁用斜杠命令注册

如果您针对同一个 Discord 应用运行多个 Hermes 网关（例如，staging 和生产环境），其中只有一个应该拥有全局斜杠命令注册的所有权——否则最后一次启动会获胜，注册会来回波动。在“从属”网关上关闭斜杠命令注册：

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # 默认：true
```

在“主”网关上保留 `true` 以保持正常行为——内置命令和已安装技能的全局 `/` 菜单命令。

## 发送媒体（`send_message` + `MEDIA:` 标签）

Discord 适配器支持通过 `send_message` 工具和代理发出的内联 `MEDIA:/path/to/file` 标签来原生上传所有常见媒体类型：

| 类型 | 交付方式 |
|---|---|
| 图片 (PNG/JPG/WebP) | 原生 Discord 图片附件，带内联预览 |
| 动画 GIF | `send_animation` 上传为 `animation.gif`，以便 Discord 内联播放（而不是静态缩略图） |
| 视频 (MP4/MOV) | `send_video` — 原生视频播放器 |
| 音频 / 语音 | `send_voice` — 尽可能使用原生语音消息，否则作为文件附件 |
| 文档 (PDF/ZIP/docx/等) | `send_document` — 原生附件，带下载按钮 |

Discord 的每次上传大小限制取决于服务器的 Boost 等级（免费 25 MB，最高 500 MB）。如果 Hermes 收到 HTTP 413，适配器会回退到指向本地缓存路径的链接，而不是静默失败。

## 接收任意文件类型

用户上传的任何文件类型都会被接受。授权与代理通信是门控条件——而不是文件扩展名。每次上传都会被下载，缓存到 `~/.hermes/cache/documents/` 下，并以 `DOCUMENT` 类型的消息事件呈现给代理，以便其可以使用 `terminal`（`ffprobe`、`unzip`、`file`、`strings` 等）或 `read_file` 检查文件。

- 已知类型（PDF、docx/xlsx/pptx、zip、图片/音频/视频等）保留其精确的 MIME。
- 未知类型回退到上传报告的内容类型，如果没有提供则为 `application/octet-stream`。
- 小的 UTF-8 可解码文件（文本、代码、配置、HTML、CSS、JSON、YAML 等）的内容会自动注入到提示中，最多 100 KiB。无法解码的二进制文件仅作为指向路径的上下文注释呈现（通过 `to_agent_visible_cache_path` 为 Docker/Modal 沙箱终端自动转换），以免撑爆上下文窗口。

唯一入站限制是每个文件的大小上限（默认 32 MiB）：

```yaml
discord:
  # 可选 — 提高/禁用每个文件的大小上限。默认 32 MiB。
  # 整个文件在缓存时保存在内存中，因此无限制上传会带来实际的内存开销。
  max_attachment_bytes: 33554432   # 字节；0 = 无限制
```

等效环境变量：`DISCORD_MAX_ATTACHMENT_BYTES=33554432`（或 `0` 表示无上限）。

旧版 `discord.allow_any_attachment` 标志现在是一个空操作——任何文件类型始终被接受——保留它只是为了不让现有配置报错。

:::warning 无限制的内存成本
禁用大小上限（`max_attachment_bytes: 0`）意味着用户可以上传一个多 GB 的文件给机器人，网关会在将缓存写入磁盘时努力通过内存缓冲它。仅在受信任的单用户安装中设置此选项。对于共享机器人，请保留默认的 32 MiB 或保守地提高它。
:::

## 交互式提示（澄清）

当代理调用 `clarify` 工具时——询问您喜欢哪种方法、获得任务后的反馈或在非平凡决策前检查——Discord 会为该问题渲染**每个选项一个按钮**：

> 我应该使用哪个框架来构建仪表板？
>
> [1. Next.js] [2. Remix] [3. Astro] [其他（输入答案）]

点击编号按钮回答，或点击 **其他** 输入自由格式的答案（您在该频道中发送的下一条消息将成为答案）。无预设选项的开放式 `clarify` 调用跳过按钮，仅捕获您的下一条消息。

一旦做出选择，按钮会自行禁用，这样重复点击不会双重解决提示。通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时（默认 `600` 秒）。如果您在超时内没有响应，代理会以哨兵消息解除阻塞并适应，而不是挂起。

## 主频道

您可以指定一个“主频道”，机器人会在其中发送主动消息（例如 cron 作业输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在任何机器人存在的 Discord 频道中键入 `/sethome`。该频道将成为主频道。

### 手动配置

将这些添加到您的 `~/.hermes/.env` 中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

将 ID 替换为实际的频道 ID（右键点击 → 在开发者模式下复制频道 ID）。

## 语音消息

Hermes Agent 支持 Discord 语音消息：

- **传入的语音消息**会自动使用配置的 STT 提供商进行转录：本地 `faster-whisper`（无需密钥）、Groq Whisper (`GROQ_API_KEY`) 或 OpenAI Whisper (`VOICE_TOOLS_OPENAI_KEY`)。
- **文本转语音**：使用 `/voice tts` 让机器人在发送文本回复的同时发送语音音频响应。
- **Discord 语音频道**：Hermes 也可以加入语音频道，聆听用户说话，并在频道中回话。

完整的设置和操作指南，请参见：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

### 语音频道音频效果（环境音 + 口头确认）

当机器人在语音频道中时，您可以赋予它更具对话感的感觉：在开始工作前发出简短的口头确认（“让我查一下”），以及在工具运行时播放一种微妙的背景“思考”音——语音会将环境音降低，完成后恢复，类似于 Grok 语音模式。

discord.py 每个连接只播放一个音频流，因此 Hermes 在传出流上安装了一个软件混音器，将环境循环音、确认音和 TTS 回复合并到该单个流中——它们重叠而非切断彼此。

这**默认是关闭的**。在 `config.yaml` 中启用：

```yaml
discord:
  voice_fx:
    enabled: true          # 主开关
    ambient_enabled: true  # 工具运行时的空闲“思考”背景音
    ambient_path: ""       # 自定义循环文件（任何音频格式）；"" = 内置合成垫音
    ambient_gain: 0.18     # 空闲背景音量（0.0–1.0）
    duck_gain: 0.06        # 机器人说话时的环境音量
    speech_gain: 1.0       # TTS / 确认音量
    ack_enabled: true      # 在每个轮次第一次工具调用前说一个短句
    ack_phrases:           # 随机选择；设置为 [] 以禁用口头确认
      - "让我看看。"
      - "请稍等。"
      - "正在查。"
```

注意：
- 确认最多每个轮次触发一次，仅当机器人在语音频道中且混音器激活时。它使用您配置的 TTS 提供商。
- `ambient_path` 接受任何 `ffmpeg` 可以解码的文件；它会无缝循环。留空以使用内置合成垫音（无需素材）。
- 所有设置都在 `config.yaml` 中（而非 `.env`）——它们是行为设置，而非机密。
- 当 `voice_fx.enabled` 为 `false` 时，语音播放使用原始的单次路径，一切保持不变。

## 论坛频道

Discord 论坛频道（类型 15）不接受直接消息——论坛中的每个帖子必须是一个线程。Hermes 自动检测论坛频道，并在需要发送时创建一个新的线程帖子，因此 `send_message`、TTS、图片、语音消息和文件附件无需代理特殊处理即可工作。

- **线程名称**源自消息的第一行（去掉 Markdown 标题前缀，最多 100 个字符）。当消息仅为附件时，使用文件名作为回退线程名称。
- **附件**随新线程的起始消息一起发送——没有单独的上传步骤，没有部分发送。
- **一次调用，一个线程**：每次论坛发送创建一个新线程。因此，连续发送到同一论坛会生成单独的线程。
- **检测是三层结构**：首先使用频道目录缓存，然后使用进程本地探测缓存，最后使用实时 `GET /channels/{id}` 探测作为最后手段（其结果会在进程生命周期内记忆）。

刷新目录（在暴露该功能的平台上使用 `/channels refresh`，或重启网关）会填充自机器人启动后创建的论坛频道缓存。

## 故障排除

### 机器人在线但不回复消息

**原因**：Message Content Intent 被禁用。

**修复**：前往 [开发者门户](https://discord.com/developers/applications) → 您的应用 → Bot → Privileged Gateway Intents → 启用 **Message Content Intent** → 保存更改。重启网关。

### 启动时出现 "Disallowed Intents" 错误

**原因**：您的代码请求的意图未在开发者门户中启用。

**修复**：在 Bot 设置中启用所有三个特权网关意图（Presence、Server Members、Message Content），然后重启。

### 机器人无法看到特定频道中的消息

**原因**：机器人的角色没有查看该频道的权限。

**修复**：在 Discord 中，进入频道的设置 → 权限 → 添加机器人的角色，并启用 **View Channel** 和 **Read Message History**。

### 403 Forbidden 错误

**原因**：机器人缺少必需的权限。

**修复**：使用第五步中的 URL 重新邀请机器人，并赋予正确的权限，或在服务器设置 → 角色中手动调整机器人的角色权限。

### 机器人离线

**原因**：Hermes 网关未运行，或令牌不正确。

**修复**：检查 `hermes gateway` 是否正在运行。验证 `.env` 文件中的 `DISCORD_BOT_TOKEN`。如果您最近重置了令牌，请更新它。

### "User not allowed" / 机器人忽略您

**原因**：您的用户 ID 不在 `DISCORD_ALLOWED_USERS` 中。

**修复**：将您的用户 ID 添加到 `~/.hermes/.env` 中的 `DISCORD_ALLOWED_USERS`，然后重启网关。

### 同一频道中的人意外共享上下文

**原因**：`group_sessions_per_user` 被禁用，或者该上下文中的平台无法提供用户 ID。

**修复**：在 `~/.hermes/config.yaml` 中设置此项并重启网关：

```yaml
group_sessions_per_user: true
```

如果您有意想要一个共享房间的对话，请保持禁用——但请注意共享记录历史和共享中断行为。

## 安全性

:::warning
始终设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）以限制谁可以与机器人交互。如果没有两者，网关默认拒绝所有用户作为安全措施。仅授权您信任的人——授权用户可以完全访问代理的功能，包括工具使用和系统访问。
:::

### 基于角色的访问控制

对于通过角色而不是个人用户列表（审核团队、支持人员、内部工具）进行访问管理的服务器，请使用 `DISCORD_ALLOWED_ROLES`——逗号分隔的角色 ID 列表。拥有这些角色之一的任何成员都被授权。

```bash
# ~/.hermes/.env — 可与 DISCORD_ALLOWED_USERS 一起使用或替代
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义：

- **与用户允许列表的 OR 逻辑。** 如果用户的 ID 在 `DISCORD_ALLOWED_USERS` 中**或**他们在 `DISCORD_ALLOWED_ROLES` 中有任何角色，则该用户被授权。
- **自动启用 Server Members Intent。** 当设置了 `DISCORD_ALLOWED_ROLES` 时，机器人在连接时启用 Members intent——Discord 需要它才能随成员记录发送角色信息。
- **角色 ID，而非名称。** 从 Discord 获取：**用户设置 → 高级 → 开发者模式 ON**，然后右键点击任何角色 → **复制角色 ID**。
- **私信回退。** 在私信中，角色检查会扫描共享的服务器；在任一共享服务器中具有允许角色的用户在私信中也被授权。

当审核团队人员流动时，这是首选模式——新版主在获得角色的那一刻就获得了访问权限，无需编辑 `.env` 或重启网关。

### 提及控制

默认情况下，Hermes 阻止机器人 @提及 `@everyone`、`@here` 和角色提及，即使其回复中包含这些令牌。这可以防止措辞不当的提示或回显的用户内容刷屏整个服务器。单个 `@user` 提及和回复引用提及（小的“正在回复…”标签）保持启用，因此正常对话仍然有效。

您可以通过环境变量或 `config.yaml` 放松这些默认设置：

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # 允许机器人 @提及 @everyone / @here
    roles: false         # 允许机器人 @提及 @role
    users: true          # 允许机器人 @提及 单个 @user
    replied_user: true   # 回复时提及作者
```

```bash
# ~/.hermes/.env — 环境变量优先于 config.yaml
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::tip
除非您确切知道为什么需要，否则请将 `everyone` 和 `roles` 保留为 `false`。LLM 很容易在看似正常的回复中产生字符串 `@everyone`；如果没有这种保护，那会通知您服务器上的每个成员。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅 [安全指南](../security.md)。