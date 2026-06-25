---
sidebar_position: 11
title: "飞书 / Lark"
description: "将 Hermes Agent 设置为飞书或 Lark 机器人"
---

# 飞书 / Lark 设置

Hermes Agent 作为全功能机器人集成于飞书和 Lark。连接后，您可以在私聊或群聊中与代理（Agent）对话，在家庭聊天中接收定时任务结果，并通过普通网关流程发送文本、图片、音频和文件附件。

该集成支持两种连接模式：

- `websocket` — 推荐；Hermes 发起出站连接，无需公共 Webhook 端点
- `webhook` — 当您希望飞书/Lark 通过 HTTP 向网关推送事件时有用

## Hermes 的行为

| 上下文 | 行为 |
|--------|------|
| 私聊 | Hermes 对每条消息都响应。 |
| 群聊 | 仅在群聊中 @提及机器人时，Hermes 才响应。 |
| 共享群聊 | 默认情况下，在共享聊天中，会话历史按用户隔离。 |

此共享聊天行为由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当您明确希望每个聊天共享一个会话时，才将其设置为 `false`。

## 第一步：创建飞书 / Lark 应用

### 推荐：扫码创建（一条命令）

```bash
hermes gateway setup
```

选择 **飞书 / Lark**，然后使用飞书或 Lark 手机应用扫描二维码。Hermes 将自动创建一个具有正确权限的机器人应用，并保存凭据。

### 备选：手动设置

如果扫码创建不可用，向导将回退到手动输入：

1. 打开飞书或 Lark 开发者控制台：
   - 飞书：[https://open.feishu.cn/](https://open.feishu.cn/)
   - Lark：[https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在 **凭证与基础信息** 中，复制 **App ID** 和 **App Secret**。
4. 为应用启用 **机器人** 能力。
5. 运行 `hermes gateway setup`，选择 **飞书 / Lark**，然后根据提示输入凭据。

:::warning
请保密 App Secret。任何拥有它的人都可以冒充您的应用。
:::

### 配置权限

在飞书开发者控制台中，转到 **权限管理** 并添加以下范围。您可以在权限页面中批量导入它们。

**必需权限：**

| 范围 | 用途 |
|------|------|
| `im:message` | 接收和读取消息 |
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:resource` | 访问用户发送的图片、文件和音频 |
| `im:chat` | 访问聊天/群组元数据 |
| `im:chat:readonly` | 读取聊天列表和成员身份 |

**推荐权限（用于完整功能）：**

| 范围 | 用途 |
|------|------|
| `im:message.reactions:readonly` | 接收表情反应事件 |
| `admin:app.info:readonly` | 自动检测机器人身份以进行 @提及门控 |
| `contact:user.id:readonly` | 解析用户 ID 以进行白名单匹配 |

### 配置事件

在 **事件与回调** 中：

1. 将连接模式设置为 **长连接（WebSocket）**（推荐）或配置 Webhook URL
2. 在 **事件配置** 部分，订阅：
   - `im.message.receive_v1` — 接收消息必需

### 发布应用

配置权限和事件后，转到 **版本管理** 并发布一个新版本的应用。权限在版本发布并获得批准（对于企业应用，可能需要管理员批准）之前不会生效。

## 第二步：选择连接模式

### 推荐：WebSocket 模式

当 Hermes 在您的笔记本电脑、工作站或私有服务器上运行时，使用 WebSocket 模式。无需公共 URL。官方的 Lark SDK 会打开并维护一个持久的出站 WebSocket 连接，并自动重连。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 必须安装 `websockets` Python 包。SDK 在内部处理连接生命周期、心跳和自动重连。

**工作原理：** 适配器在后台执行器线程中运行 Lark SDK 的 WebSocket 客户端。入站事件（消息、反应、卡片操作）被分派到主 asyncio 循环。断开连接时，SDK 将尝试自动重连。

### 可选：Webhook 模式

仅当您已经在一个可达的 HTTP 端点后面运行 Hermes 时，才使用 Webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 Webhook 模式下，Hermes 启动一个 HTTP 服务器（通过 `aiohttp`），并在以下地址提供飞书端点：

```text
/feishu/webhook
```

**要求：** 必须安装 `aiohttp` Python 包。

您可以自定义 Webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # 默认：127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # 默认：8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # 默认：/feishu/webhook
```

当飞书发送 URL 验证挑战（`type: url_verification`）时，Webhook 会自动响应，以便您可以在飞书开发者控制台中完成订阅设置。当设置了 `FEISHU_VERIFICATION_TOKEN` 时，挑战响应会受到其门控——令牌缺失或不匹配的挑战请求将被拒绝，这样未经验证的远程方无法通过回显攻击者控制的挑战数据来证明端点控制权。

## 第三步：配置 Hermes

### 选项 A：交互式设置

```bash
hermes gateway setup
```

选择 **飞书 / Lark** 并填写提示。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# 可选但强烈推荐
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 接受：

- `feishu` 用于飞书中国版
- `lark` 用于 Lark 国际版

## 第四步：启动网关

```bash
hermes gateway
```

然后在飞书/Lark 中给机器人发消息以确认连接已生效。

## 家庭聊天

在飞书/Lark 聊天中使用 `/set-home` 将其标记为定时任务结果和跨平台通知的家庭渠道。

您也可以预先配置：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全

### 用户白名单

在生产环境中，设置飞书 Open ID 的白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果您将白名单留空，任何能接触到机器人的人都可能使用它。在群聊中，消息处理前会检查发送者的 `open_id` 是否在白名单中。

### Webhook 加密密钥

在 Webhook 模式下运行时，设置加密密钥以启用入站 Webhook 负载的签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

此密钥可在飞书应用配置的 **事件订阅** 部分找到。设置后，适配器会使用签名算法验证每个 Webhook 请求：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

计算出的哈希值会与 `x-lark-signature` 标头进行时间安全比较。签名无效或缺失的请求将被拒绝，并返回 HTTP 401。

:::tip
在 WebSocket 模式下，签名验证由 SDK 自身处理，因此 `FEISHU_ENCRYPT_KEY` 是可选的。在 Webhook 模式下，强烈建议生产环境中使用。
:::

### 验证令牌

额外的身份验证层，检查 Webhook 负载中的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

此令牌也可在飞书应用的 **事件订阅** 部分找到。设置后，每个入站 Webhook 负载的 `header` 对象中必须包含匹配的 `token`。令牌不匹配的请求将被拒绝，并返回 HTTP 401。

可以同时使用 `FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 实现深度防御。

## 群消息策略

`FEISHU_GROUP_POLICY` 环境变量控制 Hermes 在群聊中是否以及如何响应：

```bash
FEISHU_GROUP_POLICY=allowlist   # 默认
```

| 值 | 行为 |
|----|------|
| `open` | Hermes 响应任何群组中任何用户的 @提及。 |
| `allowlist` | Hermes 仅响应 `FEISHU_ALLOWED_USERS` 中列出的用户的 @提及。 |
| `disabled` | Hermes 完全忽略所有群消息。 |

在所有模式下，机器人必须被显式 @提及（或 @all）后才会处理消息。私聊始终绕过此门控。

设置 `FEISHU_REQUIRE_MENTION=false` 让 Hermes 读取所有群流量，而不需要 @提及：

```bash
FEISHU_REQUIRE_MENTION=false
```

对于每个聊天的控制，在 `group_rules` 条目上设置 `require_mention`——请参阅下面的 [每个群组的访问控制](#每个群组的访问控制-per-group-access-control)。

### 机器人身份

Hermes 在启动时自动检测机器人的 `open_id` 和显示名称。仅当自动检测无法访问飞书 API，或者您的应用使用租户范围的用户 ID 时，才需要手动设置：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx     # 仅在自动检测失败时
FEISHU_BOT_USER_ID=xxx        # 如果您的应用使用 sender_id_type=user_id 则需要
FEISHU_BOT_NAME=MyBot         # 仅在自动检测失败时
```

## 机器人间消息

默认情况下，Hermes 忽略其他机器人发送的消息。当您希望 Hermes 参与 A2A 编排或从同一群组中的其他机器人接收通知时，启用机器人间消息。

```bash
FEISHU_ALLOW_BOTS=mentions   # 默认：none
```

| 值 | 行为 |
|----|------|
| `none` | 忽略所有来自其他机器人的消息（默认）。 |
| `mentions` | 仅当对方机器人 @提及 Hermes 时接受。 |
| `all` | 接受所有对方机器人的消息。 |

也可在 `config.yaml` 中配置为 `feishu.allow_bots`（两者都设置时环境变量优先）。

对方机器人无需添加到 `FEISHU_ALLOWED_USERS`——该白名单仅适用于人类发送者。

授予 `application:bot.basic_info:read` 范围以显示对方机器人名称；不授予时，对方机器人仍然正常路由，但显示为它们的 `open_id`。

## 交互式卡片操作

当用户点击由机器人发送的交互式卡片上的按钮或与之交互时，适配器将其路由为合成的 `/card` 命令事件：

- 按钮点击变为：`/card button {"key": "value", ...}`
- 卡片定义中的 `value` 负载作为 JSON 包含在内。
- 卡片操作在 15 分钟窗口内进行去重，以防止双重处理。

网关驱动的更新提示使用原生的飞书 `是` / `否` 卡片，而不是回退到纯文本回复。当 `hermes update --gateway` 需要确认时，适配器将选定的答案记录在 Hermes 的 `.update_response` 文件中，并以内联方式将卡片替换为已解决状态。

卡片操作事件以 `MessageType.COMMAND` 分派，因此它们流经正常的命令处理管道。

这也是 **命令批准** 的工作方式——当代理需要运行危险命令时，它会发送一个包含“允许一次/会话/始终/拒绝”按钮的交互式卡片。用户点击按钮，卡片操作回调将批准决定送回代理。

### 必需的飞书应用配置

交互式卡片需要在飞书开发者控制台中进行 **三个** 配置步骤。缺少任何一个都会导致用户点击卡片按钮时出现错误 **200340**。

1. **订阅卡片操作事件：**
   在 **事件订阅** 中，将 `card.action.trigger` 添加到您订阅的事件中。

2. **启用交互式卡片能力：**
   在 **应用功能 > 机器人** 中，确保 **交互式卡片** 开关已启用。这将告诉飞书您的应用可以接收卡片操作回调。

3. **配置卡片请求 URL（仅限 Webhook 模式）：**
   在 **应用功能 > 机器人 > 消息卡片请求网址** 中，将 URL 设置为与事件 Webhook 相同的端点（例如 `https://your-server:8765/feishu/webhook`）。在 WebSocket 模式下，SDK 会自动处理此设置。

:::warning
如果没有完成所有三个步骤，飞书将成功 *发送* 交互式卡片（发送仅需 `im:message:send` 权限），但点击任何按钮都会返回错误 200340。卡片看起来正常工作——只有当用户与之交互时才会出现错误。
:::

## 文档评论智能回复

除了聊天之外，适配器还可以回答飞书/Lark 文档上的 `@` 提及。当用户在文档上留下评论（本地文本选择或整文档评论）并 @提及机器人时，Hermes 会读取文档以及周围的评论线程，并在该线程内内联发布 LLM 回复。

由 `drive.notice.comment_add_v1` 事件驱动，处理程序：

- 并行获取文档内容和评论时间线（整文档线程 20 条消息，本地选择线程 12 条）。
- 使用范围限定在该单一评论会话的 `feishu_doc` + `feishu_drive` 工具集运行代理。
- 将回复分块为 4000 字符，并以线程回复形式发回。
- 每个文档的会话缓存 1 小时，最多 50 条消息，以便对同一文档的后续评论保持上下文。

### 3 层访问控制

文档评论回复是 **仅显式授权** 模式——没有隐式的全部允许模式。权限按以下顺序解析（每个字段第一个匹配项获胜）：

1. **精确文档** — 规则限定到特定文档 token。
2. **通配符** — 匹配一组文档模式的规则。
3. **顶层** — 工作空间的默认规则。

每条规则有两种策略：

- **`allowlist`** — 一个静态的用户/租户列表。
- **`pairing`** — 静态列表 ∪ 运行时批准的存储。适用于推出期间审核员可以实时授予访问权限的场景。

规则位于 `~/.hermes/feishu_comment_rules.json`（配对授权位于 `~/.hermes/feishu_comment_pairing.json`），具有 mtime 缓存的热重载——编辑后无需重启网关，在下一个评论事件时生效。

CLI：

```bash
# 检查当前规则和配对状态
python -m gateway.platforms.feishu_comment_rules status

# 模拟特定文档和用户的访问检查
python -m gateway.platforms.feishu_comment_rules check <fileType:fileToken> <user_open_id>

# 运行时管理配对授权
python -m gateway.platforms.feishu_comment_rules pairing list
python -m gateway.platforms.feishu_comment_rules pairing add <user_open_id>
python -m gateway.platforms.feishu_comment_rules pairing remove <user_open_id>
```

### 必需的飞书应用配置

在已授予的聊天/卡片权限基础上，添加云端文档评论事件：

- 在 **事件订阅** 中订阅 `drive.notice.comment_add_v1`。
- 授予 `docs:doc:readonly` 和 `drive:drive:readonly` 范围，以便处理程序可以读取文档内容。

## 会议邀请事件

您可以像邀请人类参与者一样，将 Hermes 飞书/Lark 机器人邀请到视频会议中。当机器人收到会议邀请事件时，Hermes 可以自动启动一个代理回合，尝试加入会议。

由 `vc.bot.meeting_invited_v1` 事件驱动，流程如下：

- 用户邀请机器人加入飞书/Lark 视频会议。
- 飞书/Lark 向 Hermes 发送会议邀请事件。
- Hermes 提取邀请者、会议主题和会议号。
- 如果邀请者通过网关白名单或配对策略授权，代理会收到会议号并尝试自动加入。
- 如果邀请格式错误，或者代理无法加入，Hermes 将丢弃该事件或向邀请者回复简洁的解释。

格式错误的邀请（不包含邀请者和 `meeting_no`）将被忽略。

### 必需的飞书应用配置

在已授予的聊天/卡片权限基础上，添加视频会议邀请事件：

- 在 **事件订阅** 中订阅 `vc.bot.meeting_invited_v1`。
- 启用飞书/Lark 开发者控制台为该事件提示的视频会议权限范围。
- 保持 `im:message` 和 `im:message:send_as_bot` 启用，以便 Hermes 可以回复邀请者。
- 确保网关用户白名单或配对策略已授权邀请者。会议邀请不会绕过正常的网关访问检查。

## 媒体支持

### 入站（接收）

适配器接收并缓存来自用户的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|--------|---------|
| **图片** | .jpg, .jpeg, .png, .gif, .webp, .bmp | 通过飞书 API 下载并本地缓存 |
| **音频** | .ogg, .mp3, .wav, .m4a, .aac, .flac, .opus, .webm | 下载并缓存；小型文本文件自动提取内容 |
| **视频** | .mp4, .mov, .avi, .mkv, .webm, .m4v, .3gp | 下载并作为文档缓存 |
| **文件** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx 等 | 下载并作为文档缓存 |

来自富文本（post）消息的媒体，包括内嵌图片和文件附件，也会被提取并缓存。

对于基于文本的小型文档（.txt, .md），文件内容会自动注入到消息文本中，以便代理无需工具即可直接读取。

### 出站（发送）

| 方法 | 发送内容 |
|------|---------|
| `send` | 文本或富文本 post 消息（根据 markdown 内容自动检测） |
| `send_image` / `send_image_file` | 将图片上传到飞书，然后作为原生图片气泡发送（可选带标题） |
| `send_document` | 将文件上传到飞书 API，然后作为文件附件发送 |
| `send_voice` | 将音频文件作为飞书文件附件上传 |
| `send_video` | 上传视频并作为原生媒体消息发送 |
| `send_animation` | GIF 降级为文件附件（飞书没有原生 GIF 气泡） |

文件上传路由根据扩展名自动进行：

- `.ogg`, `.opus` → 作为 `opus` 音频上传
- `.mp4`, `.mov`, `.avi`, `.m4v` → 作为 `mp4` 媒体上传
- `.pdf`, `.doc(x)`, `.xls(x)`, `.ppt(x)` → 以其文档类型上传
- 其他所有文件 → 作为通用流文件上传

## Markdown 渲染和 Post 回退

当出站文本包含 markdown 格式（标题、粗体、列表、代码块、链接等）时，适配器会自动将其作为飞书 **post** 消息发送，其中嵌入了 `md` 标签，而非纯文本。这可以在飞书客户端中实现富文本渲染。

如果飞书 API 拒绝 post 负载（例如，由于不支持的 markdown 结构），适配器会自动回退为纯文本发送（去除 markdown）。这种两阶段回退确保消息始终能够送达。

纯文本消息（未检测到 markdown）会作为简单的 `text` 消息类型发送。

## 处理状态反应

在代理工作时，机器人会在您的消息上显示一个 `正在输入` 反应。当回复到达时，该反应会被清除；如果处理失败，则会被替换为 `叉号`。

设置 `FEISHU_REACTIONS=false` 可关闭此功能。

## 突发保护和批处理

适配器包含针对快速消息突发的防抖处理，以避免压垮代理：

### 文本批处理

当用户连续快速发送多条文本消息时，它们会在分派前合并为单个事件：

| 设置 | 环境变量 | 默认值 |
|------|---------|--------|
| 静默期 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6s |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000 |

### 媒体批处理

连续快速发送的多个媒体附件（例如，同时拖放多张图片）会合并为单个事件：

| 设置 | 环境变量 | 默认值 |
|------|---------|--------|
| 静默期 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8s |

### 每个聊天的序列化

同一聊天中的消息会串行处理（一次一个），以保持对话连贯性。每个聊天都有自己单独的锁，因此不同聊天中的消息可以并发处理。

## 速率限制（Webhook 模式）

在 Webhook 模式下，适配器会实施基于 IP 的速率限制，以防止滥用：

- **窗口：** 60 秒滑动窗口
- **限制：** 每个（app_id，路径，IP）三元组在每个窗口内最多 120 个请求
- **跟踪上限：** 最多跟踪 4096 个唯一键（防止无限制的内存增长）

超过限制的请求会收到 HTTP 429（请求过多）。

### Webhook 异常跟踪

适配器会跟踪每个 IP 地址的连续错误响应。如果在 6 小时窗口内同一 IP 出现 25 次连续错误，则会记录警告。这有助于检测配置错误的客户端或探测尝试。

其他 Webhook 保护措施：
- **请求体大小限制：** 1 MB 最大值
- **请求体读取超时：** 30 秒
- **Content-Type 强制：** 仅接受 `application/json`

## WebSocket 调优

使用 `websocket` 模式时，您可以自定义重连和心跳行为：

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_interval: 120   # 重连尝试之间的秒数（默认：120）
      ws_ping_interval: 30         # WebSocket 心跳间隔（可选；未设置时使用 SDK 默认）
```

| 设置 | 配置键 | 默认值 | 描述 |
|------|--------|-------|------|
| 重连间隔 | `ws_reconnect_interval` | 120s | 重连尝试之间的等待时间 |
| 心跳间隔 | `ws_ping_interval` | _(SDK 默认)_ | WebSocket 保活心跳频率 |

## 每个群组的访问控制 (Per-Group Access Control)

除了全局的 `FEISHU_GROUP_POLICY` 之外，您还可以使用 `config.yaml` 中的 `group_rules` 为每个群聊设置精细规则：

```yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"     # 未在 group_rules 中列出的群组的默认策略
      admins:                          # 可以管理机器人设置的用户
        - "ou_admin_open_id"
      group_rules:
        "oc_group_chat_id_1":
          policy: "allowlist"          # open | allowlist | blacklist | admin_only | disabled
          allowlist:
            - "ou_user_open_id_1"
            - "ou_user_open_id_2"
        "oc_group_chat_id_2":
          policy: "admin_only"
        "oc_group_chat_id_3":
          policy: "blacklist"
          blacklist:
            - "ou_blocked_user"
        "oc_free_chat":
          policy: "open"
          require_mention: false       # 为此聊天覆盖 FEISHU_REQUIRE_MENTION
```

| 策略 | 描述 |
|------|------|
| `open` | 群组中的任何人都可以使用机器人 |
| `allowlist` | 只有群组 `allowlist` 中的用户才能使用机器人 |
| `blacklist` | 除了群组 `blacklist` 中的用户外，其他人都可以使用机器人 |
| `admin_only` | 只有全局 `admins` 列表中的用户才能在此群组中使用机器人 |
| `disabled` | 机器人忽略此群组中的所有消息 |

在 `group_rules` 条目上设置 `require_mention: false`，以跳过该特定聊天的 @提及要求。省略时，聊天将继承全局的 `FEISHU_REQUIRE_MENTION` 值。

未在 `group_rules` 中列出的群组将回退到 `default_group_policy`（默认为 `FEISHU_GROUP_POLICY` 的值）。

## 去重

入站消息使用消息 ID 进行去重，TTL 为 24 小时。去重状态会在重启后持久化到 `~/.hermes/feishu_seen_message_ids.json`。

| 设置 | 环境变量 | 默认值 |
|------|---------|--------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048 条 |

## 所有环境变量

| 变量 | 必需 | 默认值 | 描述 |
|------|------|--------|------|
| `FEISHU_APP_ID` | ✅ | — | 飞书/Lark App ID |
| `FEISHU_APP_SECRET` | ✅ | — | 飞书/Lark App Secret |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（中国版）或 `lark`（国际版） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 用户白名单，逗号分隔的 open_id 列表 |
| `FEISHU_ALLOW_BOTS` | — | `none` | 接受来自其他机器人的消息：`none`，`mentions`，或 `all` |
| `FEISHU_REQUIRE_MENTION` | — | `true` | 群消息是否必须 @提及机器人 |
| `FEISHU_HOME_CHANNEL` | — | — | 定时任务/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | Webhook 签名验证的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | Webhook 负载身份验证的验证令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群消息策略：`open`，`allowlist`，`disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | 机器人的 open_id（用于 @提及检测） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | 机器人的 user_id（用于 @提及检测） |
| `FEISHU_BOT_NAME` | — | _(空)_ | 机器人的显示名称（用于 @提及检测） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook 端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 跟踪的去重消息 ID 最大数量 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本突发防抖静默期 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每个文本批次合并的最大消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每个文本批次合并的最大字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体突发防抖静默期 |

WebSocket 和每个群组的 ACL 设置通过 `config.yaml` 中的 `platforms.feishu.extra` 配置（请参阅上面的 [WebSocket 调优](#websocket-调优-websocket-tuning) 和 [每个群组的访问控制](#每个群组的访问控制-per-group-access-control)）。

## 故障排除

| 问题 | 解决方法 |
|------|---------|
| `lark-oapi not installed` | 安装 SDK：`pip install lark-oapi` |
| `websockets not installed; websocket mode unavailable` | 安装 websockets：`pip install websockets` |
| `aiohttp not installed; webhook mode unavailable` | 安装 aiohttp：`pip install aiohttp` |
| `FEISHU_APP_ID or FEISHU_APP_SECRET not set` | 设置两个环境变量，或通过 `hermes gateway setup` 配置 |
| `Another local Hermes gateway is already using this Feishu app_id` | 同一时间只有一个 Hermes 实例可以使用相同的 app_id。先停止另一个网关。 |
| 机器人在群组中无响应 | 确保机器人被 @提及，检查 `FEISHU_GROUP_POLICY`，如果策略是 `allowlist`，确认发送者在 `FEISHU_ALLOWED_USERS` 中 |
| `Webhook rejected: invalid verification token` | 确保 `FEISHU_VERIFICATION_TOKEN` 与飞书应用事件订阅配置中的令牌匹配 |
| `Webhook rejected: invalid signature` | 确保 `FEISHU_ENCRYPT_KEY` 与飞书应用配置中的加密密钥匹配 |
| Post 消息显示为纯文本 | 飞书 API 拒绝了 post 负载；这是正常的回退行为。查看日志了解详情。 |
| 机器人未收到图片/文件 | 为飞书应用授予 `im:message` 和 `im:resource` 权限范围 |
| 机器人身份未自动检测 | 通常是访问飞书机器人信息端点的临时网络问题。手动设置 `FEISHU_BOT_OPEN_ID` 和 `FEISHU_BOT_NAME` 作为临时解决方法。 |
| 启用 `FEISHU_ALLOW_BOTS` 后，对方机器人的消息仍被忽略 | Hermes 尚无法识别自己的身份——设置 `FEISHU_BOT_OPEN_ID`（如果您的应用使用 `sender_id_type=user_id`，还需设置 `FEISHU_BOT_USER_ID`）。 |
| 对方机器人显示为 `ou_xxxxxx` 而非名称 | 授予 `application:bot.basic_info:read` 范围。 |
| 点击批准按钮时出现错误 200340 | 在飞书开发者控制台中启用 **交互式卡片** 能力并配置 **卡片请求 URL**。请参阅上面的 [必需的飞书应用配置](#必需的飞书应用配置-required-feishu-app-configuration)。 |
| `Webhook rate limit exceeded` | 同一 IP 每分钟超过 120 个请求。通常是配置错误或循环。 |

## 工具集 (Toolset)

飞书 / Lark 使用 `hermes-feishu` 平台预设，其中包含与 Telegram 和其他基于网关的消息平台相同的核心工具。