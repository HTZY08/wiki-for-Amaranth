---
sidebar_position: 1
title: "Telegram"
description: "将 Hermes Agent 设置为 Telegram 机器人"
---

# Telegram 设置

Hermes Agent 与 Telegram 集成，作为一个功能完整的对话机器人。连接后，你可以从任何设备与你的代理（Agent）聊天，发送自动转写的语音备忘录，接收定时任务结果，并在群聊中使用该代理（Agent）。该集成基于 [python-telegram-bot](https://python-telegram-bot.org/)，支持文本、语音、图片和文件附件。

## 步骤 1：通过 BotFather 创建机器人

每个 Telegram 机器人都需要一个由 [@BotFather](https://t.me/BotFather)（Telegram 官方机器人管理工具）颁发的 API 令牌（token）。

1. 打开 Telegram，搜索 **@BotFather**，或访问 [t.me/BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 选择一个**显示名称**（例如 "Hermes Agent"）——可以是任何内容
4. 选择一个**用户名**——必须唯一且以 `bot` 结尾（例如 `my_hermes_bot`）
5. BotFather 会回复你的 **API 令牌（token）**。它看起来像这样：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请保密你的机器人令牌（token）。任何拥有此令牌（token）的人都可以控制你的机器人。如果泄露，请立即通过在 BotFather 中使用 `/revoke` 命令撤销它。
:::

## 步骤 2：自定义你的机器人（可选）

这些 BotFather 命令可以改善用户体验。向 @BotFather 发送消息并使用：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始聊天前显示的“这个机器人能做什么？”文本 |
| `/setabouttext` | 机器人个人资料页面的简短文本 |
| `/setuserpic` | 为你的机器人上传头像 |
| `/setcommands` | 定义命令菜单（聊天中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否查看所有群组消息（参见步骤 3） |

:::tip
对于 `/setcommands`，一个有用的起始集合：

```
help - 显示帮助信息
new - 开始新的对话
sethome - 将此聊天设置为首页频道
```
:::

### 在线/离线状态指示器（可选）

Telegram 机器人没有真正的在线/离线状态绿点——那个绿点是**用户账户**的功能，不是 Bot API 为机器人提供的。最接近的替代是机器人的**简短描述**（机器人个人资料页面中显示在名称下方的文字）。

启用 `status_indicator`，Hermes 会在网关（gateway）连接时将简短描述设置为**在线**，在正常关闭时设置为**离线**：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        status_indicator: true
        # 可选的自定义字符串（默认值："Online" / "Offline"）：
        status_online: "🟢 在线"
        status_offline: "🔴 离线"
```

注意：

- 简短描述是机器人的**全局**设置（对所有用户可见），不是每个聊天的。用户可以在机器人个人资料页面上看到它，而不是在打开的聊天中作为实时徽章。
- 只有**干净的**网关（gateway）关闭（`/stop`、`disconnect`）才会写入“离线”。硬崩溃会保留最后已知的状态——这是个人资料文本指示器固有的局限性。
- 默认关闭，因为它会修改机器人的全局个人资料。

### 命令菜单优先级与上限（可选）

当 Telegram 网关（gateway）启动时，Hermes 会自动注册其命令菜单。该菜单由中央斜杠命令注册表加上符合条件的插件/技能（Skill）命令构建，然后进行截断，以确保 Telegram 可靠地接受有效负载。默认上限是 60 个命令——足以保留所有内置命令以及常见的技能（Skill）命令。

如果你有希望在 Telegram 的 `/` 选择器中保持可见的本地或插件命令，可以在 `~/.hermes/config.yaml` 中为它们设置优先级：

```yaml
platforms:
  telegram:
    extra:
      command_menu:
        max_commands: 60
        priority_mode: prepend  # prepend | append | replace
        priority:
          - my_plugin_command
```

`priority_mode` 控制你的列表如何与 Hermes 内置的优先级列表组合：

- `prepend`：你的命令在前，然后是 Hermes 默认命令
- `append`：保持 Hermes 默认命令在前，然后是你的命令
- `replace`：仅使用你的列表进行优先级排序

Telegram 最多允许 100 个 BotCommand，但大的命令有效负载可能会失败。Hermes 默认为 60 以确保可靠性，并将配置的值限制在 `1..100` 范围内；使用 `/commands` 查看完整命令列表。

## 步骤 3：隐私模式（对群组至关重要）

Telegram 机器人有一个**默认启用的隐私模式**。这是在群组中使用机器人时最常见的困惑来源。

**开启隐私模式时**，你的机器人只能看到：
- 以 `/` 命令开头的消息
- 直接回复机器人自身消息的回复
- 服务消息（成员加入/离开、置顶消息等）
- 机器人是管理员的频道中的消息

**关闭隐私模式时**，机器人会接收群组中的每一条消息。

### 如何禁用隐私模式

1. 向 **@BotFather** 发送消息
2. 发送 `/mybots`
3. 选择你的机器人
4. 转到 **Bot Settings → Group Privacy → Turn off**

:::warning
更改隐私设置后，**你必须从群组中移除机器人并重新添加**。Telegram 会在机器人加入群组时缓存隐私状态，并且直到移除并重新添加机器人后才会更新。
:::

:::tip
禁用隐私模式的替代方案：将机器人提升为**群组管理员**。管理员机器人无论隐私设置如何，始终接收所有消息，这避免了切换全局隐私模式的需要。
:::

### 观察群组对话而不自动回复

对于 OpenClaw/Yuanbao 风格的群组行为，配置 Telegram 使机器人能够**看到**普通群组消息，但仅在直接触发时**响应**：

```yaml
telegram:
  allowed_chats:
    - "-1001234567890"
  group_allowed_chats:
    - "-1001234567890"
  require_mention: true
  observe_unmentioned_group_messages: true
```

启用此模式后，来自明确允许列表中的聊天/主题的未提及群组消息会被追加到共享的聊天/主题会话记录中作为观察到的上下文，但不会分派代理（Agent）。`allowed_chats` 控制机器人响应的范围；`group_allowed_chats` 授权用于观察上下文的共享群组会话，因此在此模式下使用相同的聊天 ID。之后在该允许列表中的聊天/主题中使用 `@botname` 提及、回复机器人或配置的提及模式可以利用该观察到的上下文。触发消息还会被标记上 `[昵称|用户ID]` 并获得每次回合的安全提示（safety prompt），以便模型将之前的观察行视为上下文，而不是针对机器人的指令。

等效的环境变量：

```bash
TELEGRAM_ALLOWED_CHATS=-1001234567890
TELEGRAM_GROUP_ALLOWED_CHATS=-1001234567890
TELEGRAM_OBSERVE_UNMENTIONED_GROUP_MESSAGES=true
```

这要求 Telegram 将普通群组消息传递给网关（gateway），因此请按上述说明禁用 BotFather 隐私模式或将机器人提升为群组管理员。

## 步骤 4：找到你的用户 ID

Hermes Agent 使用数字 Telegram 用户 ID 来控制访问。你的用户 ID **不是**你的用户名——它是一个像 `123456789` 这样的数字。

**方法 1（推荐）：** 向 [@userinfobot](https://t.me/userinfobot) 发送消息——它会立即回复你的用户 ID。

**方法 2：** 向 [@get_id_bot](https://t.me/get_id_bot) 发送消息——另一个可靠的选择。

保存这个号码；你下一步会用到它。

## 步骤 5：配置 Hermes

### 选项 A：交互式设置（推荐）

```bash
hermes gateway setup
```

在提示时选择 **Telegram**。向导会询问你的机器人令牌（token）和允许的用户 ID，然后为你写入配置。

### 选项 B：手动配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # 多个用户用逗号分隔
```

### 启动网关（Gateway）

```bash
hermes gateway
```

机器人在几秒钟内应该上线。在 Telegram 上向它发送一条消息以验证。

## 从 Docker 支持的终端发送生成的文件

如果你的终端后端是 `docker`，请记住 Telegram 附件是由**网关（gateway）进程**发送的，而不是从容器内部。这意味着最终的 `MEDIA:/...` 路径必须在网关（gateway）运行的主机上可读。

常见陷阱：

- 代理（Agent）在 Docker 内部将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- Telegram 交付失败，因为 `/workspace/report.txt` 仅存在于容器内部，不在主机上

推荐模式：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

然后：

- 在 Docker 内部将文件写入 `/output/...`
- 在 `MEDIA:` 中输出**主机可见的**路径，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果你已经有 `docker_volumes:` 部分，将新的挂载添加到同一列表中。YAML 重复键会静默覆盖较早的键。

### 支持的 `MEDIA:` 文件扩展名

网关（gateway）从代理（Agent）回复中提取 `MEDIA:/path/to/file` 标签，并将引用的文件作为平台原生附件发送。所有网关（gateway）平台支持的扩展名：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`、`jpg`、`jpeg`、`gif`、`webp`、`bmp`、`tiff`、`svg` |
| 音频 | `mp3`、`wav`、`ogg`、`m4a`、`opus`、`flac`、`aac` |
| 视频 | `mp4`、`mov`、`webm`、`mkv`、`avi` |
| **文档** | `pdf`、`txt`、`md`、`csv`、`json`、`xml`、`html`、`yaml`、`yml`、`log` |
| **办公** | `docx`、`xlsx`、`pptx`、`odt`、`ods`、`odp` |
| **归档** | `zip`、`rar`、`7z`、`tar`、`gz`、`bz2` |
| **电子书/包** | `epub`、`apk`、`ipa` |

此列表中的任何内容都会在支持它的平台上作为原生附件交付（Telegram、Discord、Signal、Slack、WhatsApp、飞书（Feishu）、Matrix 等）；在不支持原生附件的平台上，会回退为链接或纯文本指示器。**粗体**类别是在最近几个版本中添加的——如果你之前依赖模型说“这是文件：/path/to/report.docx”，请改用 `MEDIA:/path/to/report.docx` 以获得原生交付。

## Webhook 模式

默认情况下，Hermes 使用**长轮询**连接到 Telegram——网关（gateway）向 Telegram 服务器发出出站请求以获取新更新。这对于本地和始终在线的部署很有效。

对于**云部署**（Fly.io、Railway、Render 等），**webhook 模式**更具成本效益。这些平台可以在接收到入站 HTTP 流量时自动唤醒挂起的机器，但不能在出站连接上自动唤醒。由于轮询是出站的，轮询机器人永远无法休眠。Webhook 模式反转了方向——Telegram 将更新推送到你的机器人的 HTTPS URL，使部署能够在空闲时休眠。

| | 轮询（默认） | Webhook |
|---|---|---|
| 方向 | 网关（Gateway）→ Telegram（出站） | Telegram → 网关（Gateway）（入站） |
| 最适合 | 本地、始终在线的服务器 | 具有自动唤醒功能的云平台 |
| 设置 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲成本 | 机器必须保持运行 | 机器可以在消息之间休眠 |

### 配置

将以下内容添加到 `~/.hermes/.env`：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # 必需
# TELEGRAM_WEBHOOK_PORT=8443        # 可选，默认为 8443
```

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | 公共 HTTPS URL，Telegram 将向其发送更新。URL 路径会自动提取（例如，上面示例中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | 秘密令牌（secret token），Telegram 会在每个 webhook 请求中回显以进行验证。网关（gateway）在没有它的情况下拒绝启动——参见 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。使用 `openssl rand -hex 32` 生成。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | Webhook 服务器监听的本地端口（默认：`8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关（gateway）会启动一个 HTTP webhook 服务器而不是轮询。当未设置时，使用轮询模式——与以前版本的行为没有变化。

### 云部署示例（Fly.io）

1. 将环境变量添加到你的 Fly.io 应用密钥（secrets）中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在你的 `fly.toml` 中暴露 webhook 端口：

```toml
[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. 部署：

```bash
fly deploy
```

网关（gateway）日志应显示：`[telegram] Connected to Telegram (webhook mode)`。

## 代理支持

如果 Telegram 的 API 被屏蔽，或者你需要通过代理（Proxy）路由流量，请设置 Telegram 特定的代理 URL。这将优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**选项 1：config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2：环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议：`http://`、`https://`、`socks5://`。

该代理（Proxy）适用于主 Telegram 连接和后备 IP 传输。如果未设置 Telegram 特定的代理，网关（gateway）会回退到 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或 macOS 系统代理自动检测）。

## 首页频道（Home Channel）

在任何 Telegram 聊天（私聊或群组）中使用 `/sethome` 命令将其指定为**首页频道**。定时任务（cron 作业）将其结果交付到此频道。

你也可以在 `~/.hermes/.env` 中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="我的笔记"
```

:::tip
群组聊天 ID 是负数（例如 `-1001234567890`）。你的个人私聊聊天 ID 与你的用户 ID 相同。
:::

### 主题模式下的 Cron 交付

如果你在机器人私聊中启用了主题模式，交付到根聊天的 cron 消息会落入仅系统大厅——在那里回复不会打开任何会话，你会看到“主聊天保留用于系统命令”的通知。创建一个专用的论坛主题（例如 `Cron`）并设置：

```bash
TELEGRAM_CRON_THREAD_ID=<topic_thread_id>
```

`TELEGRAM_CRON_THREAD_ID` 会覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID`，仅用于 cron 交付。该主题中的回复会继续该主题的现有会话。

## 语音消息

### 传入语音（语音转文字）

你在 Telegram 上发送的语音消息会自动由 Hermes 配置的 STT 提供程序转写并作为文本注入到对话中。

- `local` 使用运行 Hermes 机器上的 `faster-whisper`——无需 API 密钥
- `groq` 使用 Groq Whisper，需要 `GROQ_API_KEY`
- `openai` 使用 OpenAI Whisper，需要 `VOICE_TOOLS_OPENAI_KEY`

#### 跳过 STT：将原始音频文件传递给代理（Agent）

如果你更希望**代理（Agent）本身**处理音频——例如用于说话人分离（diarization）、自定义转写工具，或者只是存档录音——请在 `~/.hermes/config.yaml` 中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

禁用 STT 后，网关（gateway）仍会将语音/音频附件下载到 Hermes 的音频缓存中，但**不会转写**。代理（Agent）会收到带有如下标记的消息：

```
[用户发送了一条语音消息：/home/<user>/.hermes/cache/audio/<hash>.ogg]
```

你的工具或技能（Skill）可以直接读取该路径（例如，将其传递给本地说话人分离管道、更丰富的转写模型，或上传到长期存储）。文件扩展名反映了 Telegram 提供的原始格式（语音留言为 `.ogg`，音频附件为 `.mp3`/`.m4a` 等）。

这与下面[通过本地 Bot API 服务器传输大文件（>20MB）](#large-files-20mb-via-local-bot-api-server)部分自然配合，后者将 Telegram 的 20MB getFile 上限提升至 2GB——当你想要处理的录音时长超过几分钟时非常有用。

### 传出语音（文字转语音）

当代理（Agent）通过 TTS 生成音频时，它会作为原生 Telegram **语音气泡**（圆形、可内联播放的类型）交付。

- **OpenAI 和 ElevenLabs** 原生生成 Opus——无需额外设置
- **Edge TTS**（默认的免费提供程序）输出 MP3，需要 **ffmpeg** 转换为 Opus：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

没有 ffmpeg，Edge TTS 音频会作为常规音频文件发送（仍然可播放，但使用矩形播放器而不是语音气泡）。

在 `config.yaml` 中的 `tts.provider` 键下配置 TTS 提供程序。

## 通过本地 Bot API 服务器传输大文件（>20MB）

Telegram 的**公共** Bot API 将 `getFile` 下载限制在 **20 MB**，因此任何大于此的语音留言、音频文件、视频或文档都会被 Hermes 以“太大”的回复静默拒绝。解决此问题的文档方法是运行一个**本地** [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程——与 Telegram 使用的相同服务器软件，但在你的网络上运行。本地服务器将文件上限提升至 **2 GB**，当 Hermes 看到配置了自定义 `base_url` 时，它会自动提升其内部上限。

这解锁了以下工作流程：

- 向机器人发送长语音留言（45 分钟的会议、播客）
- 上传大视频用于视觉工具处理
- 存档原始音频用于离线管道，如说话人分离（diarization）、对齐或训练数据

### 步骤 1：获取 Telegram API 凭据

本地服务器直接与 Telegram 的 MTProto 层通信（而不是公共 Bot API），因此它需要 **MTProto 凭据**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps) 并使用你的 Telegram 账户登录。
2. 创建一个新应用程序（任何名称和简短描述都可以）。
3. 复制 `api_id` 和 `api_hash`——两者都是必需的。

### 步骤 2：运行 telegram-bot-api 服务器

社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简单的路径。一个最小的 `docker-compose.yaml`（使用 `--local` 模式以启用更高的限制）：

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # 仅绑定到回环接口；请查看安全说明
    environment:
      TELEGRAM_API_ID: "12345"           # 步骤 1 中的 api_id
      TELEGRAM_API_HASH: "abcdef..."     # 步骤 1 中的 api_hash
      TELEGRAM_LOCAL: "1"                # 启用 --local 模式（将 20MB → 2GB）
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

启动它：

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

:::warning 安全
本地 Bot API 服务器在 URL 路径中接受你的机器人令牌（token）（例如 `/bot<TOKEN>/getMe`），而**没有额外认证**。任何能够访问该端口的人都可以完全控制你的机器人——读取它能看到的所有消息、以它的身份发送消息等。将容器绑定到 `127.0.0.1` 和/或在其前面放置一个反向代理在私有网络上。**切勿将端口 8081 暴露给公共互联网。**
:::

### 步骤 3：从公共 API 注销机器人（一次性）

一个机器人一次只能在一个 Bot API 服务器上处于活动状态。如果你的机器人之前已经在 `api.telegram.org` 上运行（几乎肯定是的），你必须先在那里显式注销它，然后本地服务器才能接受它：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# 预期响应：{"ok":true,"result":true}
```

这是一次性的迁移步骤——你不需要在每次重启时重复。Telegram 会将 `logOut` 后收到的消息通过新服务器交付。

验证本地服务器能够代表机器人与 Telegram 通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# 预期响应：{"ok":true,"result":{"id":...,"is_bot":true,...}}
```

### 步骤 4：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra` 下添加 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # 请参阅下面的步骤 5——仅当机器人的数据
                              # 目录对 Hermes 进程可读时才设置此项
```

:::caution 使用 `platforms.telegram.extra`，而不是 `telegram.extra`
目前只有 `platforms.<name>.extra` 形式会被深度合并到平台配置中。直接放在顶级 `telegram.extra` 块下的键会被静默丢弃。
:::

当设置了 `base_url` 时，Hermes：

- 针对本地服务器构建 python-telegram-bot 客户端
- 自动将其内部文档/音频大小上限从 20 MB 提升至 2 GB
- 在“太大”错误消息中报告活动上限（`Maximum: 2048 MB.`），以便明显知道你处于哪种模式

重启网关（gateway）并查找确认日志行：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

### 步骤 5：`local_mode`——磁盘上的文件访问

本地服务器有两种方式交付文件：

1. **不带 `--local`（默认）：** 文件通过 `/file/bot<TOKEN>/<path>` 的 HTTP 提供，与公共 Bot API 相同。20MB 的上限仍然有效。仅作为网络修复有用（例如，当 `api.telegram.org` 不可达但你可以自托管时）；不是你想要的提升大小的方法。
2. **带 `--local`（通过上面的 `TELEGRAM_LOCAL=1` 设置）：** 文件写入服务器的文件系统，`getFile` 返回一个**绝对路径**而不是 HTTP URL。20MB 的上限被解除。Hermes 必须**从磁盘**读取字节，而不是通过 HTTP。

要使磁盘读取路径有效，请将上述配置中的 `local_mode: true` 设置为 **并** 确保 Hermes 进程可以读取服务器返回的路径。两种场景：

- **同一台机器**——telegram-bot-api 和 Hermes 在同一主机上运行。将数据卷绑定挂载到 Hermes 可以读取的目录（例如 `/var/lib/telegram-bot-api`），并确保文件所有权匹配。容器会将其权限降低到内部 `telegram-bot-api` 用户（UID 因镜像而异）；最简单的修复方法是在 compose 服务中添加 `user: "<UID>:<GID>"`，使文件由 Hermes 已经以其身份运行的 uid 拥有。
- **不同机器**——机器人服务器在一台主机上运行（例如 NAS、单独的虚拟机），而 Hermes 在另一台上。服务器的数据目录必须与 Hermes 机器共享**相同的绝对路径**（服务器报告的路径，通常是 `/var/lib/telegram-bot-api`）。NFS 适用于此；如果你不想处理文件系统级别的 UID 不匹配，CIFS/SMB 配合 `uid=` 挂载重新映射会更友好。

如果设置了 `local_mode: true` 但 Hermes 无法 `stat` 返回的文件路径（权限问题或挂载错误），python-telegram-bot 会静默回退到针对本地服务器的 HTTP `getFile`——在 `--local` 模式下，它会返回 `404 Not Found`。症状会出现在 `gateway.log` 中：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果你看到这个，说明上限提升是有效的但文件共享无效。从 Hermes 主机上以网关（gateway）运行的用户身份验证 `ls -la /var/lib/telegram-bot-api/<TOKEN>/voice/`，并确认单个文件可以 `cat` 而没有权限错误。

### 步骤 6：测试

向机器人发送一个大于 20 MB 的语音留言或音频文件。跟踪网关（gateway）日志：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

你应该会看到一行 `[Telegram] Cached user voice at /home/<user>/.hermes/cache/audio/...` 并且**没有**“太大”的拒绝。结合 `stt.enabled: false`（上面），原始音频文件的路径然后会落在代理（Agent）的入站消息中，用于下游处理。

## 群聊使用

Hermes Agent 可以在 Telegram 群聊中工作，但有一些注意事项：

- **隐私模式**决定了机器人可以看到哪些消息（参见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 仍然适用——只有授权用户才能触发机器人，即使在群组中也是如此
- 你可以通过 `telegram.require_mention: true` 让机器人不响应普通的群组聊天
- 使用 `telegram.require_mention: true` 时，群组消息在以下情况下被接受：
  - 是对机器人某条消息的回复
  - 是 `@botusername` 提及
  - 是 `/command@botusername`（Telegram 的机器人菜单命令形式，包含机器人名称）
  - 匹配你配置的 `telegram.mention_patterns` 中的某个正则唤醒词
- 在有多个 Hermes 机器人的群组中，`telegram.exclusive_bot_mentions` 保持路由确定性。当一条消息显式提及一个或多个 Telegram 机器人用户名时，只有被提及的机器人配置（Profile）处理它；其他 Hermes 机器人在运行回复和唤醒词回退之前会忽略它。此功能默认启用。
- 使用 `telegram.ignored_threads` 让 Hermes 在特定的 Telegram 论坛主题中保持静默，即使该群组否则会允许自由回复或提及触发的回复。
- 如果 `telegram.require_mention` 未设置或为 false，Hermes 保持之前的开放群组行为，并响应它能看到的普通群组消息。

### 一个群组中的多个 Hermes 机器人

如果你在同一个 Telegram 群组中运行多个 Hermes 配置（Profile），请为每个配置创建一个 Telegram 机器人令牌（token），并为每个配置启动一个网关（gateway）。不要在多个正在运行的网关（gateway）中重复使用同一个机器人令牌（token）；Telegram 会拒绝同一令牌的并发轮询。

推荐的群组配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

使用此设置，像 `@research_bot @ops_bot summarize this` 这样的群组消息仅由 `research_bot` 和 `ops_bot` 处理。群组中的其他 Hermes 机器人在运行回复和唤醒词回退之前会保持静默。

仅在对旧式群组中，显式提及不应覆盖回复和唤醒词触发器的情况下，才设置 `exclusive_bot_mentions: false`。

若要操作多个配置，请为每个配置运行一次网关（gateway）命令。例如：

```bash
# 默认配置
hermes gateway start
hermes gateway status
hermes gateway stop

# 命名配置
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

对于小型固定机群，请使用 shell 循环或脚本，为默认配置调用 `hermes gateway <action>`，为每个命名配置调用 `hermes -p <profile> gateway <action>`。这比假设一个单一的进程级命令可以在每个服务管理器上控制每个命名配置更可靠。

### 故障排除：在私聊中有效，但在群组中无效

如果机器人在私人聊天中响应，但在群组中保持沉默，请按顺序检查这些关卡：

1. **Telegram 交付：** 关闭 BotFather 隐私模式，将机器人提升为管理员，或直接提及机器人。如果 Telegram 从未将群组消息交付给机器人，Hermes 无法响应。
2. **更改隐私后重新加入：** 在更改 BotFather 隐私设置后，从群组中移除机器人并重新添加。Telegram 可能会为现有成员保留旧的交付行为。
3. **Hermes 授权：** 确保发送者在 `TELEGRAM_ALLOWED_USERS` 或 `TELEGRAM_GROUP_ALLOWED_USERS` 中列出，或者使用 `TELEGRAM_GROUP_ALLOWED_CHATS` 允许群组聊天。
4. **提及过滤器：** 如果设置了 `telegram.require_mention: true`，除非消息是斜杠命令、回复机器人、`@botusername` 提及或匹配配置的 `mention_patterns`，否则会忽略普通的群组聊天。
5. **多机器人路由：** 如果群组包含多个机器人，请确保每个 Hermes 配置使用唯一的机器人令牌（token），并保持 `exclusive_bot_mentions` 启用，除非你故意想要传统的共享触发行为。

负聊天 ID 对于 Telegram 群组和超级群组是正常的。如果你使用聊天范围授权，将这些 ID 放入 `TELEGRAM_GROUP_ALLOWED_CHATS`，而不是发送者用户允许列表。

### 示例群组触发配置

将此添加到 `~/.hermes/config.yaml`：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

此示例允许所有常见的直接触发，以及以 `chompy` 开头的消息，即使它们不使用 `@mention`。
在提及和自由响应检查运行之前，Telegram 主题 `31` 和 `42` 中的消息始终被忽略。

### 关于 `mention_patterns` 的说明

- 模式使用 Python 正则表达式
- 匹配不区分大小写
- 模式同时针对文本消息和媒体标题进行检查
- 无效的正则表达式模式会被忽略，并在网关（gateway）日志中发出警告，而不是使机器人崩溃
- 如果你希望模式仅在消息开头匹配，请以 `^` 开头

## 私聊主题（Bot API 9.4）

Telegram Bot API 9.4（2026 年 2 月）引入了**私聊主题**——机器人可以直接在 1 对 1 私聊中创建论坛风格的主题线程，无需超级群组。这让你可以在现有的与 Hermes 的私聊中运行多个独立的工作空间。

### 使用场景

如果你在多个长期项目上工作，主题可以保持它们的上下文独立：

- **主题“网站”**——处理你的生产网络服务
- **主题“研究”**——文献综述和论文探索
- **主题“通用”**——杂项任务和快速问题

每个主题都有自己的对话会话、历史和上下文——与其他主题完全隔离。

### 配置

:::caution 前提条件
在向配置添加主题之前，用户必须在与机器人的私聊中**启用主题模式**：

1. 在 Telegram 中打开与 Hermes 机器人的私人聊天
2. 点击顶部的机器人名称以打开聊天信息
3. 启用**主题**（将聊天变为论坛的开关）

如果没有这个，Hermes 会在启动时记录 `The chat is not a forum` 并跳过主题创建。这是 Telegram 客户端设置——机器人无法以编程方式启用它。
:::

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra.dm_topics` 下添加主题：

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # 你的 Telegram 用户 ID
        topics:
        - name: 通用
          icon_color: 7322096
        - name: 网站
          icon_color: 9367192
        - name: 研究
          icon_color: 16766590
          skill: arxiv              # 在此主题中自动加载技能（Skill）
```

**字段：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 主题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 主题图标的自定义表情符号 ID |
| `skill` | 否 | 在此主题的新会话中自动加载的技能（Skill） |
| `thread_id` | 否 | 主题创建后自动填充——不要手动设置 |

### 工作原理

1. 在网关（gateway）启动时，Hermes 为每个没有 `thread_id` 的主题调用 `createForumTopic`
2. `thread_id` 会自动保存回 `config.yaml`——后续重启会跳过 API 调用
3. 每个主题映射到一个独立的会话键：`agent:main:telegram:dm:{chat_id}:{thread_id}`
4. 每个主题中的消息都有自己的对话历史、内存刷新和上下文窗口

### 根私聊处理

默认情况下，发送到根私聊（在任何主题之外）的消息会被正常处理。设置 `ignore_root_dm: true` 将根私聊变为大厅——对于配置了私聊主题的用户，普通消息会被静默忽略，而系统命令（`/start`、`/help`、`/status` 等）仍然有效。

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: 通用
```

检查是**按聊天**进行的：只有在 `dm_topics` 中至少有一条记录的用户才会受到根私聊影响。没有配置主题的用户不受影响。

### 技能（Skill）绑定

带有 `skill` 字段的主题会在新会话在该主题中启动时自动加载该技能（Skill）。这完全类似于在对话开始时输入 `/skill-name`——技能（Skill）内容会被注入到第一条消息中，后续消息会在对话历史中看到它。

例如，一个带有 `skill: arxiv` 的主题，当其会话重置时（由于空闲超时、每日重置或手动 `/reset`），arxiv 技能（Skill）会被预加载。

:::tip
在配置之外创建的主题（例如通过手动调用 Telegram API）会在 `forum_topic_created` 服务消息到达时自动发现。你也可以在网关（gateway）运行时向配置添加主题——它们会在下次缓存未命中时被拾取。
:::

## 多会话私聊模式（`/topic`）

一个类似 ChatGPT 的多会话私聊模式——一个机器人，多个并行对话。与上面由操作员策划的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需配置，无需预先声明的主题名称。最终用户通过 `/topic` 开启它，然后点击 Telegram 的 **+** 按钮创建任意数量的主题，每个主题都是一个完全独立的 Hermes 会话。

### `/topic` 子命令

| 形式 | 上下文 | 效果 |
|------|---------|--------|
| `/topic` | 根私聊，尚未启用 | 检查 BotFather 能力，启用多会话模式，创建置顶的系统主题 |
| `/topic` | 根私聊，已启用 | 显示状态：可用于恢复的未链接会话 |
| `/topic` | 主题内 | 显示当前主题的会话绑定 |
| `/topic help` | 任何位置 | 内联用法 |
| `/topic off` | 根私聊 | 禁用多会话模式并清除此聊天的所有主题绑定 |
| `/topic <session-id>` | 主题内 | 将先前的 Telegram 会话恢复到当前主题中 |

只有授权用户（通过 `TELEGRAM_ALLOWED_USERS` / 平台身份验证配置的允许列表）才能运行 `/topic`。未授权的发送者会收到拒绝而不是激活。

### 私聊主题 vs 多会话私聊模式

| | `extra.dm_topics`（配置驱动） | `/topic`（用户驱动） |
|---|---|---|
| 谁激活 | 操作员，在 `config.yaml` 中 | 最终用户，通过发送 `/topic` |
| 主题列表 | 配置中声明的固定集合 | 用户自由创建/删除主题 |
| 主题名称 | 由操作员选择 | 由用户选择；自动重命名以匹配 Hermes 会话标题 |
| 根私聊行为 | 正常聊天（如果 `ignore_root_dm: true` 则为大厅） | 变为系统大厅（非命令消息被拒绝） |
| 主要用例 | 带有可选技能（Skill）绑定的永久工作空间 | 临时并行会话 |
| 持久化 | `extra.dm_topics` 在配置中 | `telegram_dm_topic_mode` + `telegram_dm_topic_bindings` SQLite 表 |

这两个功能可以在同一个机器人上共存——你会从用户的私聊中运行 `/topic`，而 `extra.dm_topics` 继续管理其他聊天的操作员声明主题。

### 前提条件

在 **@BotFather** 中，打开你的机器人 → **Bot Settings → Threads Settings**：

1. 打开**线程模式**（启用 `has_topics_enabled`）
2. **不要**禁用用户创建主题（保持 `allows_users_to_create_topics` 开启）

当用户第一次运行 `/topic` 时，Hermes 调用 `getMe` 来验证这两个标志。如果任何一个关闭，Hermes 会发送一张 BotFather 线程设置页面的截图并解释要切换什么——在满足前提条件之前不会激活。

### 激活流程

从根私聊发送：

```
/topic
```

Hermes 将：

1. 检查 `getMe().has_topics_enabled` 和 `allows_users_to_create_topics`
2. 如果两者都为真，则为此私聊启用多会话主题模式
3. 创建并置顶一个**系统**主题用于状态/命令（尽力而为）
4. 回复一个列表，列出用户可以恢复的先前未链接的 Telegram 会话

激活后，**根私聊是一个大厅**：普通提示会被拒绝，并附上指向**所有消息**的指导。系统命令（`/status`、`/sessions`、`/usage`、`/help` 等）仍然在根私聊中有效。

### 创建新主题（最终用户流程）

1. 在 Telegram 中打开机器人私聊
2. 点击机器人界面顶部的**所有消息**，然后发送任何消息
3. Telegram 会为该消息创建一个新主题
4. Hermes 在该主题内响应——该主题现在是一个独立的会话

每个主题都有自己的对话历史、模型状态、工具执行和会话 ID。隔离键是 `agent:main:telegram:dm:{chat_id}:{thread_id}`——与配置驱动的私聊主题隔离相同。

### 自动重命名主题

当 Hermes 为主题生成会话标题时（通过自动标题管道，在第一次交互之后），Telegram 主题本身会被重命名以匹配——例如“新主题”变成“数据库迁移计划”。重命名是尽力而为的：失败会被记录但不会破坏会话。

要禁用此功能并保持你手动选择的主题名称不变，请设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志开启时，Hermes 仍然会生成内部会话标题（由 `hermes sessions`、TUI 等使用），但不会编辑 Telegram 主题名称。当你手动在 BotFather 线程模式下组织主题并且不希望每次第一次回复都覆盖标题时，这很有用。

### 主题内的 `/new`

重置当前主题的会话（新的会话 ID，新的历史记录），不影响其他主题。Hermes 会回复提示：对于并行工作，通常创建另一个主题（通过**所有消息**）是你想要的。

### 恢复先前的会话

在主题内发送：

```
/topic <session-id>
```

这将当前主题绑定到现有的 Hermes 会话，而不是从头开始。对于继续在主题模式启用之前开始的对话很有用。限制：

- 目标会话必须属于同一个 Telegram 用户
- 目标会话不得已经绑定到另一个主题

Hermes 会确认会话标题并重放最后一条助手消息作为上下文。

要发现会话 ID，请在根私聊中发送 `/topic`（不带参数）——Hermes 会列出该用户的未链接 Telegram 会话。

### 主题内的 `/topic`（无参数）

显示当前主题的绑定：会话标题、会话 ID，以及关于 `/new` 与创建另一个主题的提示。

### 底层实现

- 激活持久化到 `state.db` 中的 `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)`
- 每个主题绑定持久化到 `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)`，并在 `session_id` 上使用 `ON DELETE CASCADE`——清除会话会自动清除其主题绑定
- 主题模式 SQLite 迁移是**选择加入的**：它在第一次调用 `/topic` 时运行，从不在网关（gateway）启动时运行。直到用户在此配置中运行 `/topic`，`state.db` 保持不变
- 每个入站私聊消息都会查找其 `(chat_id, thread_id)` 绑定。如果存在，查找会通过 `SessionStore.switch_session()` 将消息路由到绑定会话，以便会话键到会话 ID 的映射在磁盘上保持一致
- `/new` 在主题内部会重写绑定行，指向新的会话 ID，以便下一条消息保持在新会话上
- 在 `extra.dm_topics` 中声明的主题**永远不会自动重命名**——即使启用多会话模式，操作员选择的名称也会被保留
- 设置 `extra.disable_topic_auto_rename: true` 以关闭聊天中**所有**主题的自动重命名（包括通过线程模式创建的临时主题）
- 论坛启用的私聊中的 General（置顶顶部）主题被视为根大厅，无论 Telegram 是以 `message_thread_id=1` 还是无 thread_id 交付其消息
- 根大厅提醒消息限制为每聊天 30 秒一条——忘记主题模式已开启并在根中键入十个提示的用户不会收到十个回复
- BotFather 设置截图限制为每聊天 5 分钟发送一次——在线程设置仍禁用时重复尝试 `/topic` 不会重新上传同一张图片
- 在主题内启动的 `/background <prompt>` 会将其结果交付回同一主题；后台会话不会触发所属主题的自动重命名
- `/topic` 本身受到机器人用户授权检查的保护——未授权的私聊会收到拒绝而不是激活

### 禁用多会话模式

在根私聊中发送 `/topic off`。Hermes 会关闭该行，清除聊天的 `(thread_id → session_id)` 绑定，根私聊恢复为正常的 Hermes 聊天。Telegram 中现有的主题不会被删除——它们只是不再作为独立会话被控制。稍后重新运行 `/topic` 可以重新开启。

如果你需要手动清理（例如跨多个聊天的批量重置），直接删除行：

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

### 降级 Hermes

如果你降级到早于 `/topic` 的 Hermes 版本，该功能会停止工作——`telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 表会保留在 `state.db` 中，但会被旧代码忽略。私聊恢复为原生每线程隔离（每个 `message_thread_id` 仍然通过 `build_session_key` 获得自己的会话），因此你现有的 Telegram 主题会继续作为并行会话工作。根私聊不再是大厅——那里的消息会像以前一样进入代理（Agent）。重新升级会再次激活多会话模式，并且状态正好在原来的位置。

## 群组论坛主题技能（Skill）绑定

启用了**主题模式**的超级群组（也称为“论坛主题”）已经实现了每个主题的会话隔离——每个 `thread_id` 映射到自己的对话。但你可能希望在特定群组主题中收到消息时**自动加载一个技能（Skill）**，就像私聊主题技能（Skill）绑定一样。

### 使用场景

一个团队超级群组，拥有不同工作流的论坛主题：

- **工程**主题 → 自动加载 `software-development` 技能（Skill）
- **研究**主题 → 自动加载 `arxiv` 技能（Skill）
- **通用**主题 → 无技能（Skill），通用助手

### 配置

在 `~/.hermes/config.yaml` 中的 `platforms.telegram.extra.group_topics` 下添加主题绑定：

```yaml
platforms:
  telegram:
    extra:
      group_topics:
      - chat_id: -1001234567890       # 超级群组 ID
        topics:
        - name: 工程
          thread_id: 5
          skill: software-development
        - name: 研究
          thread_id: 12
          skill: arxiv
        - name: 通用
          thread_id: 1
          # 无技能（Skill）——通用目的
```

**字段：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群组的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 主题的人类可读标签（仅用于信息） |
| `thread_id` | 是 | Telegram 论坛主题 ID——可在 `t.me/c/<group_id>/<thread_id>` 链接中看到 |
| `skill` | 否 | 在此主题的新会话中自动加载的技能（Skill） |

### 工作原理

1. 当消息到达一个映射的群组主题时，Hermes 在 `group_topics` 配置中查找 `chat_id` 和 `thread_id`
2. 如果匹配的条目有 `skill` 字段，该技能（Skill）会自动加载到会话中——与私聊主题技能（Skill）绑定相同
3. 没有 `skill` 键的主题只会获得会话隔离（现有行为，未更改）
4. 未映射的 `thread_id` 值或 `chat_id` 值会静默通过——没有错误，没有技能（Skill）

### 与私聊主题的区别

| | 私聊主题 | 群组主题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 主题创建 | 如果 `thread_id` 缺失，Hermes 通过 API 创建主题 | 管理员在 Telegram UI 中创建主题 |
| `thread_id` | 创建后自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（管理员控制外观） |
| 技能（Skill）绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛主题已内置） |

:::tip
要找到主题的 `thread_id`，在 Telegram Web 或桌面版中打开该主题，查看 URL：`https://t.me/c/1234567890/5`——最后一个数字（`5`）就是 `thread_id`。对于超级群组，`chat_id` 是群组 ID 加上 `-100` 前缀（例如群组 `1234567890` 变为 `-1001234567890`）。
:::

## 最近的 Bot API 功能

- **Bot API 9.4（2026 年 2 月）：** 私聊主题——机器人可以通过 `createForumTopic` 在 1 对 1 私聊中创建论坛主题。Hermes 将此功能用于两个不同的功能：操作员策划的[私聊主题](#private-chat-topics-bot-api-94)（配置驱动，固定主题列表）和用户驱动的[多会话私聊模式](#multi-session-dm-mode-topic)（通过 `/topic` 激活，无限制用户创建主题）。
- **隐私政策：** Telegram 现在要求机器人拥有隐私政策。通过 BotFather 使用 `/setprivacy_policy` 设置一个，否则 Telegram 可能会自动生成一个占位符。如果你的机器人面向公众，这一点尤其重要。
- **Bot API 9.5（2026 年 3 月）：** 通过 `sendMessageDraft` 实现原生流式传输。Hermes 支持 Telegram 的原生流式草稿 API 作为私人聊天的可选传输方式。默认仍然是传统的 `editMessageText` 路径，因为草稿预览在某些 Telegram 客户端上可能会明显折叠和重新渲染。

### 流式传输（Streaming）传输方式（`gateway.streaming.transport`）

当流式传输（Streaming）启用时（`gateway.streaming.enabled: true`），Hermes 会选择四种传输方式之一：

| 值 | 行为 |
|---|---|
| `auto`（默认） | 在支持的聊天中（当前是 Telegram 私聊）使用原生草稿流式传输；否则使用传统的基于编辑的路径。如果草稿帧失败，会优雅地回退。 |
| `draft` | 强制使用原生草稿。如果聊天不支持草稿（例如群组/主题），会记录降级并回退到编辑。 |
| `edit` | 对所有聊天类型使用传统的渐进式 `editMessageText` 轮询。 |
| `off` | 完全禁用流式传输（仅最终回复，无渐进式更新）。 |

在 `~/.hermes/config.yaml` 中：

```yaml
gateway:
  streaming:
    enabled: true
    transport: auto    # auto | draft | edit | off
```

**使用 `edit`（默认）时在私聊中你会看到什么**——网关（gateway）发送一条普通预览消息，并通过 `editMessageText` 逐步更新它，避免 Telegram 草稿预览折叠/回滚效果。

**使用 `auto` 或 `draft` 时在私聊中你会看到什么**——Telegram 会显示一个动画草稿预览，逐令牌更新。当回复完成时，它会作为常规消息交付，草稿预览在客户端自然清除。草稿没有消息 ID，因此最终答案会保留在你的聊天历史中。

**群组、超级群组、论坛主题呢？** Telegram 将 `sendMessageDraft` 限制为私人聊天（私聊）。网关（gateway）会透明地回退到基于编辑的路径来处理其他所有情况——用户体验与之前相同。

**如果草稿帧失败会怎样？** 任何失败（瞬时网络错误、服务器端拒绝、较旧的 python-telegram-bot 安装）都会将该响应切换回基于编辑的路径，直到流结束。下一个响应会进行新的尝试。

## 渲染：富消息、表格和链接预览

**富消息（Bot API 10.1）。** 包含传统 MarkdownV2 路径会降级的结构（表格、任务列表、可折叠的 `<details>` 和块级数学）的最终回复，会使用代理（Agent）的**原始 markdown** 通过 Telegram 的原生 [`sendRichMessage`](https://core.telegram.org/bots/api#sendrichmessage) 发送，因此它们会原生渲染，无需客户端扁平化。在流式传输（Streaming）期间，最终答案是通过 `editMessageText` 的 `rich_message` 参数**在原地编辑现有预览**来交付的——没有第二条消息，没有删除，因此在回合结束时没有重复交付闪烁。在私聊中，实时流式传输预览也使用 `sendRichMessageDraft`，因此动画草稿与最终富消息匹配。普通回复（纯散文、粗体/斜体、简单列表）保持使用 MarkdownV2 路径，以在不同客户端之间保持一致的字体粗细和间距。

当内容超过 32,768 字符的富文本限制时，富路径会自动跳过，来自 Telegram 的任何拒绝（旧版 `python-telegram-bot` 上不支持的端点、解析器错误、过大的块/列）都会**透明地回退**到 MarkdownV2 路径——你的消息永远不会丢失。瞬时/网络错误不会静默地重新发送（没有重复的最终消息）。

**MarkdownV2 回退。** 当富路径不可用时，Hermes 会将 markdown 转换为 MarkdownV2。由于 MarkdownV2 没有原生表格语法，管道表格会被规范化：

- **小表格**会被扁平化为**行组项目符号**——每一行在列标题下变成一个可读的项目符号列表。适用于 2-4 列和短单元格。
- **较大或较宽的表格**会回退到带有对齐列的**栅栏代码块**，以防止任何东西折叠。

富消息是**选择加入的**。默认保持使用传统的 MarkdownV2 路径，因为当前 Telegram 客户端可能使 Bot API 富消息难以作为纯文本复制，这对于命令片段和移动端交接尤其痛苦。要为表格/任务列表/详情/数学启用原生渲染：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        rich_messages: true
        rich_drafts: false
```

此设置适用于客户端渲染/复制兼容性；Hermes 在 Telegram 拒绝富 API 调用时已经自动回退。`rich_drafts` 控制 Telegram 私聊流式传输期间的实验性富草稿预览路径，默认关闭，因为 Telegram 桌面版/macOS 可能会在聊天重绘之前视觉上覆盖富草稿帧。如果你只想要传统的“始终代码块”表格行为，同时保持富消息启用，可以通过在 `config.yaml` 中设置 `telegram.pretty_tables: false`（默认：`true`）来禁用表格规范化。

**链接预览。** Telegram 会自动为机器人消息中的 URL 生成链接预览。如果你希望抑制这些预览（例如长的 `/tools` 输出、提及十个链接的代理（Agent）回复等）：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用后，Hermes 会将 `LinkPreviewOptions(is_disabled=True)` 附加到每条出站消息，并在旧版 `python-telegram-bot` 上回退到传统的 `disable_web_page_preview` 参数。

## 群组允许列表

Telegram 群组和论坛聊天有两个正交的关卡可以配置：

- **发送者用户 ID** (`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`) —— 仅适用于群组/论坛消息的发送者范围允许列表。当你希望特定用户能够在群组中调用机器人，但又不想将他们添加到 `TELEGRAM_ALLOWED_USERS`（这也会授予他们私聊访问权限）时，使用此选项。
- **聊天 ID** (`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`) —— 聊天范围允许列表。这些群组/论坛的任何成员都可以与机器人交互。对于团队/支持机器人（其中群组成员身份本身就是访问信号）很有用。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 全局访问（私聊 + 群组）。此处的用户始终可以调用机器人。
        allow_from:
          - "123456789"
        # 仅在群组/论坛中允许的发送者 ID。不会授予私聊访问权限。
        group_allow_from:
          - "987654321"
        # 整个群组/论坛——任何成员都被授权。
        group_allowed_chats:
          - "-1001234567890"
```

等效的环境变量：

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

行为：

- `TELEGRAM_ALLOWED_USERS` 涵盖所有聊天类型（私聊、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅授权在群组/论坛中列出的发送者。他们仍然不能私聊机器人，除非也在 `TELEGRAM_ALLOWED_USERS` 中列出。
- `TELEGRAM_GROUP_ALLOWED_CHATS` 中的聊天会授权该聊天的每个成员，无论发送者是谁。
- 在上述任何一项中使用 `*` 可允许任何发送者/聊天。
- 这会叠加在现有的提及/模式触发器以及 `group_topics` + `ignored_threads` 之上。

### 从 PR #17686 之前的版本迁移

在此拆分之前，`TELEGRAM_GROUP_ALLOWED_USERS` 是唯一的旋钮，用户会将**聊天 ID** 放入其中。为了向后兼容，`TELEGRAM_GROUP_ALLOWED_USERS` 中形如聊天 ID 的值（以 `-` 开头）仍会被作为聊天 ID 处理，并且会记录一次弃用警告。迁移：

```bash
# 旧（仍然有效，但已弃用）
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# 新
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

### 访客 @mention 绕过（`guest_mode`）

在典型设置中，`group_allowed_chats` 是一个硬性关卡：来自列表之外的群组的消息会被静默丢弃，即使成员显式 @提及机器人也是如此。这是支持/团队机器人的正确默认设置。

对于更随意的设置——朋友群聊，你希望机器人**大部分时间保持沉默**但**在显式 ping 时偶尔可用**——启用 `guest_mode`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        group_allowed_chats:
          - "-1001234567890"   # 你的主要允许列表群组
        guest_mode: true       # 非允许列表群组：仅在 @mention 时允许
```

环境变量等效：

```bash
TELEGRAM_GUEST_MODE=true
```

默认值：`false`。

使用 `guest_mode: true` 时，来自非允许列表群组的消息**仅当**它显式 @提及机器人时才会被处理。每次互动都需要提及——访客互动没有会话粘性，因此机器人永远不会在没有被 ping 到的朋友群组线程中自动参与。

私聊和允许列表群组的行为与之前完全相同。

## 斜杠命令访问控制

默认情况下，每个允许的用户都可以运行每个斜杠命令。要将你的允许列表拆分为**管理员**（完整斜杠命令访问权限）和**普通用户**（仅显式启用的命令），请在平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands`：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # 现有的允许列表（未更改）
        allow_from:
          - "123456789"     # 管理员
          - "555555555"     # 普通用户
          - "777777777"     # 普通用户

        # 新增——管理员获得所有斜杠命令（内置 + 插件）
        allow_admin_from:
          - "123456789"

        # 新增——非管理员允许用户只能运行这些斜杠命令。
        # /help 和 /whoami 始终允许，以便用户查看其访问权限。
        user_allowed_commands:
          - status
          - model
          - history

        # 可选：群组的管理员/命令列表
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```

**行为：**

- 对于某个范围（私聊或群组），在 `allow_admin_from` 中列出的用户可以运行**每个**已注册的斜杠命令——通过实时注册表的内置命令和插件注册命令。
- 在 `allow_from` 中但**不在** `allow_admin_from` 中的用户只能运行 `user_allowed_commands` 中列出的命令，以及始终允许的基础命令：`/help` 和 `/whoami`。
- 普通聊天（非斜杠消息）不受影响。非管理员用户仍然可以正常与代理（Agent）交谈，只是不能触发任意命令。
- **向后兼容：** 如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令门控被禁用。现有安装无需更改即可继续工作。
- 私聊管理员状态并不意味着群组管理员状态。每个范围都有自己的管理员列表。
- 如果仅设置了 `group_allow_admin_from`，则私聊范围保持不受限制的（向后兼容）模式。

使用 `/whoami` 查看活动范围、你的级别（管理员 / 用户 / 不受限制）以及你可以运行哪些斜杠命令。

## 交互式模型选择器

当你在 Telegram 聊天中发送不带参数的 `/model` 时，Hermes 会显示一个用于切换模型的交互式内联键盘：

1. **提供商选择**——显示每个可用提供商的按钮，并带有模型数量（例如“OpenAI (15)”、“✓ Anthropic (12)”用于当前提供商）。
2. **模型选择**——分页的模型列表，带有**上一个**/**下一个**导航、返回提供商的**返回**按钮以及**取消**。

当前模型和提供商显示在顶部。所有导航都是通过原地编辑同一条消息完成的（没有聊天杂乱）。

:::tip
如果你知道确切的模型名称，直接输入 `/model <name>` 以跳过选择器。你也可以输入 `/model <name> --global` 以使更改在会话之间持久化。
:::

## DNS-over-HTTPS 后备 IP

在某些受限网络中，`api.telegram.org` 可能会解析到一个不可达的 IP。Telegram 适配器包含一个**后备 IP**机制，它会透明地针对替代 IP 重试连接，同时保留正确的 TLS 主机名和 SNI。

### 工作原理

1. 如果设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP。
2. 否则，适配器会自动通过 DNS-over-HTTPS (DoH) 查询 **Google DNS** 和 **Cloudflare DNS**，以发现 `api.telegram.org` 的替代 IP。
3. DoH 返回的与系统 DNS 结果不同的 IP 被用作后备。
4. 如果 DoH 也被屏蔽，则使用硬编码的种子 IP（`149.154.167.220`）作为最后的手段。
5. 一旦后备 IP 成功，它就会变得“粘性”——后续请求直接使用它，而不再首先重试主路径。

### 配置

```bash
# 显式后备 IP（逗号分隔）
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::tip
你通常不需要手动配置此项。通过 DoH 的自动发现处理了大多数受限网络场景。仅当 DoH 在你的网络中也受到屏蔽时，才需要 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持

如果你的网络需要 HTTP 代理才能访问互联网（这在企业环境中很常见），Telegram 适配器会自动读取标准的代理环境变量，并通过代理路由所有连接。

### 支持的变量

适配器按顺序检查这些环境变量，使用第一个被设置的变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写变体）

### 配置

在启动网关（gateway）之前，在你的环境中设置代理：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或将其添加到 `~/.hermes/.env`：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

代理（Proxy）适用于主要传输方式和所有后备 IP 传输方式。不需要额外的 Hermes 配置——如果设置了环境变量，它会自动使用。

:::note
这涵盖了 Hermes 用于 Telegram 连接的自定义后备传输层。其他地方使用的标准 `httpx` 客户端已经原生地遵循代理环境变量。
:::

## 消息反应

机器人可以为消息添加表情符号反应，作为视觉处理反馈：

- 👀 当机器人开始处理你的消息时
- ✅ 当响应成功交付时
- ❌ 如果处理过程中发生错误

反应**默认禁用**。在 `config.yaml` 中启用：

```yaml
telegram:
  reactions: true
```

或通过环境变量：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（反应是累加的）不同，Telegram 的 Bot API 在单次调用中替换所有机器人反应。从 👀 到 ✅/❌ 的转换是原子性的——你不会同时看到两者。
:::

:::tip
如果机器人没有在群组中添加反应的权限，反应调用会静默失败，消息处理会正常继续。
:::

## 每频道提示

为特定的 Telegram 群组或论坛主题分配临时系统提示。提示会在每次回合运行时注入——永远不会持久化到对话记录中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      你是一名研究助手。专注于学术来源、
      引用和简洁的综合。
    "42":  |
      此主题用于创意写作反馈。请保持温暖和建设性。
```

键是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级提示会覆盖群组级提示：

- 群组 `-1001234567890` 中主题 `42` 的消息→使用主题 `42` 的提示
- 主题 `99`（没有显式条目）的消息→回退到群组 `-1001234567890` 的提示
- 没有条目的群组中的消息→不应用频道提示

数字 YAML 键会自动规范化为字符串。

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全不响应 | 验证 `TELEGRAM_BOT_TOKEN` 是否正确。检查 `hermes gateway` 日志中的错误。 |
| 机器人响应“未经授权” | 你的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 中。使用 @userinfobot 仔细检查。 |
| 机器人忽略群组消息 | 很可能隐私模式已开启。禁用它（步骤 3）或将机器人设为群组管理员。**记住在更改隐私后移除并重新添加机器人。** |
| 语音消息未转写 | 验证 STT 是否可用：安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复是文件而不是气泡 | 安装 `ffmpeg`（Edge TTS Opus 转换所需）。 |
| 机器人令牌被撤销/无效 | 在 BotFather 中通过 `/revoke` 然后 `/newbot` 或 `/token` 生成一个新令牌。更新你的 `.env` 文件。 |
| Webhook 未接收更新 | 验证 `TELEGRAM_WEBHOOK_URL` 是否可通过公共网络访问（使用 `curl` 测试）。确保你的平台/反向代理将入站 HTTPS 流量从 URL 的端口路由到 `TELEGRAM_WEBHOOK_PORT` 配置的本地监听端口（它们不必是相同的数字）。确保 SSL/TLS 处于活动状态——Telegram 只发送到 HTTPS URL。检查防火墙规则。 |

## 执行批准

当代理（Agent）尝试运行潜在危险的命令时，它会在聊天中请求你的批准：

> ⚠️ 此命令具有潜在危险（递归删除）。回复“yes”以批准。

回复“yes”/“y”以批准，或“no”/“n”以拒绝。

## 交互式提示（clarify）

当代理（Agent）调用 `clarify` 工具时——例如询问你更喜欢哪种方法、获得任务后反馈，或在非平凡决策前检查——Telegram 会使用**内联键盘按钮**渲染问题：

> ❓ 我应该为仪表板使用哪个框架？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（输入答案）]

点击按钮回答，或点击**其他**输入自由形式的响应（你发送的下一条消息将成为答案）。开放的 `clarify` 调用（没有预设选项）会跳过按钮，仅捕获你的下一条消息。

通过 `~/.hermes/config.yaml` 中的 `agent.clarify_timeout` 配置响应超时（默认 `600` 秒）。如果你在超时内没有响应，代理（Agent）会用哨兵消息解除阻塞并适应，而不是挂起。

## 推送通知音量

Telegram 会在机器人发送的每条消息上触发推送通知。对于发出工具进度气泡、流式更新和状态回调的长代理（Agent）回合，这会很快变得嘈杂。Telegram 适配器有两种通知模式：

| 模式 | 行为 |
|------|----------|
| `important`（默认） | 仅**最终响应**、**批准提示**和**斜杠命令确认**会响铃。工具进度、流式块和状态