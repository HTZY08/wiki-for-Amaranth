---
sidebar_position: 9
title: "Matrix"
description: "将 Hermes Agent 设置为 Matrix 机器人"
---

# Matrix 设置

Hermes Agent 集成了 Matrix——一个开放的、可联邦的消息协议。Matrix 允许你运行自己的 homeserver 或使用公共服务器（如 matrix.org）——无论哪种方式，你都可以控制自己的通信。机器人通过 `mautrix` Python SDK 连接，通过 Hermes Agent 管道处理消息（包括工具使用、记忆和推理），并实时响应。它支持文本、文件附件、图片、音频、视频，以及可选的点对点加密（E2EE）。

Hermes 可与任何 Matrix homeserver 配合使用——Synapse、Conduit、Dendrite 或 matrix.org。

在开始设置之前，这里是大多数人最想了解的部分：Hermes 连接后的行为表现。

## Hermes 的行为表现

| 场景 | 行为 |
|---------|----------|
| **私聊** | Hermes 会回复每条消息。无需 `@提及`。每个私聊都有自己独立的会话。设置 `MATRIX_DM_MENTION_THREADS=true` 可在私聊中收到 `@提及` 时启动一个线程。 |
| **房间** | 默认情况下，Hermes 需要 `@提及` 才会回复。设置 `MATRIX_REQUIRE_MENTION=false` 或将房间 ID 添加到 `MATRIX_FREE_RESPONSE_ROOMS` 可使房间免于提及要求。房间邀请会被自动接受。 |
| **线程** | Hermes 支持 Matrix 线程（MSC3440）。如果你在线程中回复，Hermes 会将线程上下文与主房间时间线隔离。机器人已参与过的线程无需提及。 |
| **自动线程** | 默认情况下，Hermes 会为它在房间中回复的每条消息自动创建一个线程。这有助于隔离对话。设置 `MATRIX_AUTO_THREAD=false` 可禁用。设置 `MATRIX_DM_AUTO_THREAD=true`（默认为 false）可同时为私聊消息自动创建线程——这与 `MATRIX_DM_MENTION_THREADS` 不同，后者仅在私聊中收到 `@提及` 时启动线程。 |
| **命令** | 当你的 Matrix 客户端发送正常 `/commands` 时，Hermes 会接受。如果你的客户端保留 `/` 用于本地命令，请改用 `!commands`；Hermes 会将已知的 `!command` 别名标准化为 `/command`。 |
| **交互式控制** | 危险命令审批和 `/model` 选择可以使用 Matrix 表情反应（reactions）。审批反应可以限制为仅由请求操作的用户使用。 |
| **思考和工具活动** | 当 gateway 进度启用时，Matrix 使用可编辑的线程化思考/工具活动面板，因此更新不会淹没主房间时间线。 |
| **多用户共享房间** | 默认情况下，Hermes 在房间内按用户隔离会话历史。在同一房间内交谈的两个人不会共享同一份对话记录，除非你明确禁用了该功能。 |

:::tip
机器人被邀请时会自动加入房间。只需将机器人的 Matrix 用户邀请到任何房间，它就会加入并开始回复。
:::

## 能力矩阵

下表由 Matrix 适配器能力声明和 Matrix 测试覆盖率支持。E2EE 基于模式，因为部署可选择禁用加密房间、可选加密或强制加密。

| 能力 | Matrix |
|------------|--------|
| 文本 | 是 |
| 线程 | 是 |
| 表情反应 | 是 |
| 审批 | 是 |
| 模型选择器 | 是 |
| 思考面板 | 是 |
| 图片 | 是 |
| 多张图片 | 是 |
| 文件 | 是 |
| 语音/音频 | 是 |
| 视频 | 是 |
| E2EE | 关闭 / 可选 / 强制 |
| 诊断 | 是 |

### Matrix 中的会话模型

默认情况下：

- 每个私聊拥有自己的会话
- 每个线程拥有自己的会话命名空间
- 共享房间中的每个用户在该房间内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个房间共享一个对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作房间可能有用，但也意味着：

- 用户共享上下文增长和 token 成本
- 一个人的长耗时工具密集型任务可能会使其他人的上下文膨胀
- 一个人正在进行的运行可能会中断同房间内另一个人的后续操作

### 提及和线程配置

你可以通过环境变量或 `config.yaml` 配置提及和自动线程行为：

```yaml
matrix:
  require_mention: true           # 在房间中需要 @提及 (默认: true)
  allowed_users:                  # 允许触发代理轮次的 Matrix 用户
    - "@alice:matrix.org"
  allowed_rooms:                  # 允许触发代理轮次的 Matrix 房间
    - "!abc123:matrix.org"
  free_response_rooms:            # 免于提及要求的房间
    - "!abc123:matrix.org"
  ignore_user_patterns:           # 要忽略的桥接/应用服务幽灵用户
    - "^@telegram_"
    - "^@whatsapp_"
  process_notices: false          # 默认忽略 m.notice
  session_scope: room             # auto|room|thread；对于项目房间推荐使用 room
  auto_thread: true               # 自动为回复创建线程 (默认: true)
  dm_mention_threads: false       # 在私聊中被 @提及时创建线程 (默认: false)
```

或通过环境变量：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_ALLOWED_USERS=@alice:matrix.org
MATRIX_ALLOWED_ROOMS=!abc123:matrix.org
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_IGNORE_USER_PATTERNS='^@telegram_,^@whatsapp_'
MATRIX_PROCESS_NOTICES=false
MATRIX_SESSION_SCOPE=room       # 推荐用于稳定的项目房间上下文
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
MATRIX_REACTIONS=true          # 默认: true — 处理过程中的表情反应
MATRIX_ALLOW_ROOM_MENTIONS=false
```

:::tip 禁用表情反应
`MATRIX_REACTIONS=false` 会关闭机器人在入站消息上发布的处理生命周期表情反应（👀/✅/❌）。适用于反应事件过多或某些参与客户端不支持反应的房间。
:::

:::tip 全房间提及
Hermes 会为明确的 Matrix ID（如 `@alice:example.org`）发送结构化的 Matrix 用户提及。默认禁用全房间 `@room` 通知；仅当允许机器人通知整个房间时，才设置 `MATRIX_ALLOW_ROOM_MENTIONS=true`。
:::

:::note
如果你是从没有 `MATRIX_REQUIRE_MENTION` 的版本升级，之前机器人会回复房间中的所有消息。要保留该行为，请设置 `MATRIX_REQUIRE_MENTION=false`。
:::

### 项目房间隔离

如果你在多个项目房间中使用同一个 Matrix 机器人，请配置稳定的房间级会话：

```bash
MATRIX_SESSION_SCOPE=room
MATRIX_AUTO_THREAD=false
```

`MATRIX_SESSION_SCOPE` 接受：

| 范围 | 行为 |
|-------|----------|
| `auto` | 向后兼容的默认值。现有的 `MATRIX_AUTO_THREAD` 行为控制合成线程。 |
| `room` | 非线程房间消息保留在一个稳定的房间会话中。真实的 Matrix 线程仍使用其线程根。 |
| `thread` | 非线程房间消息根据触发事件 ID 合成一个线程/会话。 |

Hermes 现在在代理（Agent）提示中包含当前的 Matrix 房间名称、房间 ID、主题、消息 ID 以及 Matrix 房间边界说明。`/status` 也会显示当前的 Matrix 房间/会话范围，而 `/resume` 不会静默地从另一个 Matrix 房间恢复一个命名会话，除非你明确使用 `/resume --cross-room <session name>`。

`MATRIX_SESSION_SCOPE=room` 控制房间/线程通道。现有的 `group_sessions_per_user` 设置仍然控制该房间内的用户是否共享该通道。如果 `group_sessions_per_user: true`（默认），Alice 和 Bob 会获得各自独立的项目 B 会话。如果 `group_sessions_per_user: false`，房间内只有一个共享的项目 B 对话记录。

本指南将引导你完成完整的设置过程——从创建机器人账户到发送第一条消息。

## 步骤 1：创建机器人账户

你需要为机器人创建一个 Matrix 用户账户。有几种方法：

### 选项 A：在你的 Homeserver 上注册（推荐）

如果你运行自己的 homeserver（Synapse、Conduit、Dendrite）：

1. 使用管理 API 或注册工具创建一个新用户：

```bash
# Synapse 示例
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择用户名，例如 `hermes`——完整的用户 ID 将是 `@hermes:your-server.org`。

### 选项 B：使用 matrix.org 或其他公共 Homeserver

1. 前往 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为你的机器人选择一个用户名（例如 `hermes-bot`）。

### 选项 C：使用你自己的账户

你也可以以你自己的用户身份运行 Hermes。这意味着机器人将以你的身份发布消息——适用于个人助手。

## 步骤 2：获取访问令牌

Hermes 需要一个访问令牌来与 homeserver 进行身份验证。你有两个选择：

### 选项 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 进入 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级**——访问令牌会显示在那里。
4. **立即复制它。**

**通过 API：**

```bash
curl -X POST https://your-server/_matrix/client/v3/login \
  -H "Content-Type: application/json" \
  -d '{
    "type": "m.login.password",
    "user": "@hermes:your-server.org",
    "password": "your-password"
  }'
```

响应中包含一个 `access_token` 字段——复制它。

:::warning[保护好你的访问令牌]
访问令牌可以完全访问机器人的 Matrix 账户。切勿公开分享或将其提交到 Git。如果泄露，请通过注销该用户的所有会话来撤销它。
:::

### 选项 B：密码登录

你无需提供访问令牌，可以直接给 Hermes 提供机器人的用户 ID 和密码。Hermes 会在启动时自动登录。这更简单，但意味着密码会存储在 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 步骤 3：查找你的 Matrix 用户 ID

Hermes Agent 使用你的 Matrix 用户 ID 来控制谁可以与机器人交互。Matrix 用户 ID 的格式为 `@username:server`。

要查找你的用户 ID：

1. 打开 [Element](https://app.element.io)（或你喜欢的 Matrix 客户端）。
2. 点击你的头像 → **设置**。
3. 你的用户 ID 会显示在个人资料顶部（例如 `@alice:matrix.org`）。

:::tip
Matrix 用户 ID 始终以 `@` 开头，并包含一个 `:` 后跟服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 步骤 4：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Matrix**，然后提供你的 homeserver URL、访问令牌（或用户 ID + 密码）以及允许的用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

**使用访问令牌：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# 可选：用户 ID（如果省略，会从令牌自动检测）
# MATRIX_USER_ID=@hermes:matrix.example.org

# 安全：限制谁可以与机器人交互
MATRIX_ALLOWED_USERS=@alice:matrix.example.org

# 可选：限制哪些房间可以触发机器人
MATRIX_ALLOWED_ROOMS=!abc123:matrix.example.org

# 多个允许的用户（逗号分隔）
# MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
```

**使用密码登录：**

```bash
# 必需
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_USER_ID=@hermes:matrix.example.org
MATRIX_PASSWORD=***

# 安全
MATRIX_ALLOWED_USERS=@alice:matrix.example.org
```

## 私有部署强化

对于私有 Matrix 部署，建议同时设置用户和房间白名单。如果 `MATRIX_ALLOWED_USERS` 未设置，任何能通过已加入房间联系到机器人的发送者都可以触发代理轮次。如果 `MATRIX_ALLOWED_ROOMS` 未设置，机器人加入的任何房间都可以触发代理轮次。一个锁定式的部署应同时设置两者：

```bash
MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
MATRIX_ALLOWED_ROOMS=!ops:matrix.example.org,!dmroom:matrix.example.org
```

桥接和应用服务部署需要额外的循环保护。Hermes 默认会忽略自身的事件、本地部分以 `_` 开头的 Matrix 应用服务类型用户、重复的事件 ID、旧的启动事件、编辑替换事件以及 `m.notice` 事件。当你的桥接使用不同的命名约定时，添加特定于部署的桥接幽灵模式：

```bash
MATRIX_IGNORE_USER_PATTERNS='^@telegram_,^@slack_,^@whatsapp_'
```

仅在受信任的人工工作流确实发送 `m.notice` 时，才启用通知：

```bash
MATRIX_PROCESS_NOTICES=true
```

默认禁用出站的全房间通知。除非明确允许机器人使用 `@room` 唤醒整个房间，否则请保持 `MATRIX_ALLOW_ROOM_MENTIONS=false`。

诊断和调试负载会编辑掉 Matrix 访问令牌、恢复密钥、设备标识符和消息正文。媒体下载仅限于 Matrix `mxc://` 内容 URI，并在超过 `MATRIX_MAX_MEDIA_BYTES` 时被拒绝。将联邦房间和不可信的 homeserver 视为不可信输入：收紧房间白名单，对于工具密集型工作优先使用私聊或私有房间，并避免将桥接幽灵或应用服务傀儡授权为允许用户。

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 保持每个参与者的上下文在共享房间内隔离

### 启动 Gateway

配置完成后，启动 Matrix gateway：

```bash
hermes gateway
```

机器人应在几秒钟内连接到你的 homeserver 并开始同步。向其发送一条消息——可以是私聊，也可以是它已加入的房间——以进行测试。

:::tip
你可以将 `hermes gateway` 作为后台进程或 systemd 服务运行，以实现持久化操作。详情请参阅部署文档。
:::

## 点对点加密（E2EE）

Hermes 支持 Matrix 的点对点加密，因此你可以在加密房间中与机器人聊天。

### 要求

E2EE 需要带有加密扩展的 `mautrix` 库和 `libolm` C 库：

```bash
# 安装支持 E2EE 的 mautrix
pip install 'mautrix[encryption]'

# 或者使用 hermes 额外选项安装
cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"
```

你还需要在系统上安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用 E2EE

添加到你的 `~/.hermes/.env`：

```bash
MATRIX_E2EE_MODE=required
```

`MATRIX_E2EE_MODE` 接受：

| 模式 | 行为 |
|------|----------|
| `off` | 不初始化 Matrix E2EE。 |
| `optional` | 当依赖可用时尝试 E2EE，但如果加密无法初始化，则保持未加密房间正常工作。 |
| `required` | 如果 E2EE 依赖或加密设置不可用，则关闭失败。 |

可选模式可能在加密设置不可用时回退到非 E2EE 操作。强制模式会关闭失败，而不是静默降级。

为了向后兼容，`MATRIX_ENCRYPTION=true` 仍然启用强制的 E2EE 行为。

当 E2EE 启用时，Hermes：

- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/`（旧版安装：`~/.hermes/matrix/store/`）
- 首次连接时上传设备密钥
- 自动解密入站消息并加密出站消息
- 被邀请时自动加入加密房间

### Matrix 工具和控制

在 Matrix 对话中，Hermes 向代理（Agent）公开 Matrix 特定的工具：

- `matrix_send_reaction`
- `matrix_redact_message`
- `matrix_create_room`
- `matrix_invite_user`
- `matrix_fetch_history`
- `matrix_set_presence`

这些工具限定在 Matrix 上下文中，不能在非 Matrix 工具集中使用。管理风格的工具默认禁用：编辑需要 `MATRIX_TOOLS_ALLOW_REDACTION=true`，邀请需要 `MATRIX_TOOLS_ALLOW_INVITES=true`，创建房间需要 `MATRIX_TOOLS_ALLOW_ROOM_CREATE=true`。创建公共房间还需要 `MATRIX_ALLOW_PUBLIC_ROOMS=true`。
Matrix 工具默认限制在当前 Matrix 房间。显式的跨房间目标需要 `MATRIX_TOOLS_ALLOW_CROSS_ROOM=true`；编辑和邀请类的跨房间操作额外需要 `MATRIX_TOOLS_ALLOW_CROSS_ROOM_DESTRUCTIVE=true`。如果设置了 `MATRIX_ALLOWED_ROOMS`，则 Matrix 工具只能针对这些房间。

表情反应控制使用：

- ✅ 批准一次
- ♾️ 始终批准
- ❌ 拒绝
- 用于 `/model` 选择的数字反应

如果你有意允许房间中任何授权的 Matrix 用户操作审批/模型选择器提示，请设置 `MATRIX_APPROVAL_REQUIRE_SENDER=false`。当 Hermes 知道谁请求了操作时，默认为请求者绑定。

### 媒体限制

Hermes 通过 Matrix 媒体 API 上传和下载 Matrix 图片、文件、音频和视频。多张生成的图像作为有序逻辑批次发送，跨批次保留标题和线程上下文。

默认情况下，超过 100 MB 的 Matrix 媒体在上传/下载前被拒绝。通过以下方式覆盖：

```bash
MATRIX_MAX_MEDIA_BYTES=104857600
```

入站媒体必须使用 Matrix `mxc://` 内容 URI。Hermes 拒绝 Matrix 事件中的任意 HTTP(S) 媒体 URL，以避免将联邦房间变成无限制的下载器。

## Synapse 集成测试

Hermes 包含一个可选的 Synapse 测试工具，用于本地验证：

```bash
docker compose -f tests/e2e/matrix_synapse_gateway/docker-compose.yml up -d
HERMES_MATRIX_SYNAPSE_INTEGRATION=1 \
  scripts/run_tests.sh -m "integration and matrix_synapse" \
  tests/e2e/matrix_synapse_gateway/test_gateway.py
docker compose -f tests/e2e/matrix_synapse_gateway/docker-compose.yml down -v
```

该工具通过 Synapse 共享密钥注册创建临时用户，并涵盖私密房间的发送/接收、命名房间的邀请/加入、媒体上传/下载、机器人响应传递以及启动旧事件过滤。E2EE 烟雾测试单独标记为 `matrix_e2ee`，以便在开发机器上保持可选。

### 交叉签名验证（推荐）

如果你的 Matrix 账户启用了交叉签名（Element 中的默认设置），请设置恢复密钥，以便机器人在启动时自行签署其设备。否则，在设备密钥轮换后，其他 Matrix 客户端可能拒绝与机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥在此
```

**在哪里找到：** 在 Element 中，前往 **设置** → **安全与隐私** → **加密** → 你的恢复密钥（也称为“安全密钥”）。这是你首次设置交叉签名时要求保存的密钥。

每次启动时，如果设置了 `MATRIX_RECOVERY_KEY`，Hermes 会从 homeserver 的安全密钥存储中导入交叉签名密钥并签署当前设备。这是幂等的，可以安全地永久保持启用状态。

如果 Hermes 引导了一个新的 Matrix 恢复密钥，它不会记录原始密钥。在启动前设置 `MATRIX_RECOVERY_KEY_OUTPUT_FILE=/secure/path/matrix-recovery-key.txt`，以一次性写入生成的密钥，文件模式为 `0600`；如果文件已存在，则不会被覆盖。

:::warning[删除加密存储]
如果你删除了 `~/.hermes/platforms/matrix/store/crypto.db`，机器人将失去其加密身份。简单地使用相同的设备 ID 重新启动 **无法** 完全恢复——homeserver 仍然持有用旧身份密钥签名的单次密钥，对等方无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况，并拒绝启用 E2EE，记录日志：`device XXXX has stale one-time keys on the server signed with a previous identity key`。

**最简单的恢复方法：生成一个新的访问令牌**（这样会获得一个全新的设备 ID，没有旧的密钥历史记录）。请参阅下面的“从含有 E2EE 的先前版本升级”部分。这是最可靠的路径，避免接触 homeserver 数据库。

**手动恢复**（高级——保持相同的设备 ID）：

1. 停止 Synapse 并从其数据库中删除旧设备：
   ```bash
   sudo systemctl stop matrix-synapse
   sudo sqlite3 /var/lib/matrix-synapse/homeserver.db "
     DELETE FROM e2e_device_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_one_time_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_fallback_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM devices WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
   "
   sudo systemctl start matrix-synapse
   ```
   或者通过 Synapse 管理 API（注意 URL 编码的用户 ID）：
   ```bash
   curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
     'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
   ```
   注意：通过管理 API 删除设备也可能使关联的访问令牌失效。你可能需要之后生成一个新令牌。

2. 删除本地加密存储并重新启动 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # 重新启动 hermes
   ```

其他 Matrix 客户端（Element、matrix-commander）可能会缓存旧设备密钥。恢复后，在 Element 中输入 `/discardsession` 以强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人将自动回退到普通（未加密）客户端。你会在日志中看到一条警告。
:::

## 主房间（Home Room）

你可以指定一个“主房间”，机器人会在其中发送主动消息（例如 cron 任务输出、提醒和通知）。有两种设置方法：

### 使用斜杠命令

在机器人所在的任何 Matrix 房间中输入 `/sethome`。该房间就成为主房间。
如果你的 Matrix 客户端拦截了斜杠命令，请改用 `!sethome`。

### 手动配置

将其添加到你的 `~/.hermes/.env`：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

## 房间白名单（allowed_rooms）

将机器人限制在固定的 Matrix 房间集合内。设置后，机器人**只**回复列表中存在的房间 ID 中的消息——来自任何其他房间的消息都会被静默忽略，即使提到了机器人。

**私聊（直接聊天房间）不受此过滤器的限制**，因此授权用户始终可以一对一地与机器人联系。

```yaml
matrix:
  allowed_rooms:
    - "!abc123def456:matrix.example.org"
    - "!opsroom789:matrix.example.org"
```

或通过环境变量（逗号分隔）：

```bash
MATRIX_ALLOWED_ROOMS="!abc123def456:matrix.example.org,!opsroom789:matrix.example.org"
```

行为：

- 空/未设置 → 无限制（默认）。
- 非空 → 房间 ID 必须在列表中。该检查在任何其他门控**之前**运行（提及要求、发送者白名单等）。
- 请使用房间的**内部 ID**（`!abc...:server`），而不是其别名（`#room:server`）。你可以在 Element 中通过 房间 → 设置 → 高级 找到房间的内部 ID。

另请参阅：[管理员/用户斜杠命令拆分](../../reference/slash-commands.md#permissions-and-adminuser-split)。

:::tip
要查找房间 ID：在 Element 中，进入房间 → **设置** → **高级** → **内部房间 ID** 会显示在那里（以 `!` 开头）。
:::

## Matrix 中的命令

Hermes 在 Matrix 中支持与其他消息平台相同的 gateway 命令，包括 `/commands`、`/model`、`/stop`、`/queue`、`/steer`、`/goal`、`/subgoal`、`/background`、`/bg`、`/btw`、`/tasks` 和 `/yolo`。

某些 Matrix 客户端将前导 `/` 保留给本地客户端命令，并且可能不会将未知的斜杠命令发送到房间。在这种情况下，请使用 `!` 作为 Matrix 安全的别名：

```text
!commands
!model
!model gpt-5.5 --provider openrouter
!queue continue with the next task
!stop
```

Hermes 仅在命令是 gateway 已知的、已注册的插件命令或已安装的技能（Skill）命令时，才会标准化 `!command`。普通感叹句如 `!important` 仍然是正常的聊天消息。

## 故障排除

### 机器人不回复消息

**原因**：机器人未加入房间，`MATRIX_ALLOWED_USERS` 不包含你的用户 ID，`MATRIX_ALLOWED_ROOMS` 不包含该房间，或者房间消息未提及机器人。

**修复**：邀请机器人加入房间——它会在被邀请时自动加入。验证你的用户 ID 在 `MATRIX_ALLOWED_USERS` 中（使用完整的 `@user:server` 格式），并且如果配置了房间白名单，房间 ID 在 `MATRIX_ALLOWED_ROOMS` 中。在房间中提及机器人，或将房间添加到 `MATRIX_FREE_RESPONSE_ROOMS`。重新启动 gateway。

### 机器人加入房间但静默丢弃每条消息（时钟偏差）

**原因**：主机的系统时钟设置为快于实际时间。Matrix 适配器应用 5 秒的启动过滤（`event_ts < startup_ts - 5`）以忽略从初始同步重播的事件。当墙上时钟超前时，每个传入事件看起来都“早于启动”，并被丢弃，永远不会到达消息处理器——机器人看起来已连接但从不回复。参见 [#12614](https://github.com/NousResearch/hermes-agent/issues/12614)。

**症状**：Gateway 日志显示 `Matrix: dropped N live events as 'too old' more than 30s after startup`。

**修复**：使用 NTP 同步主机时钟并重新启动机器人：

```bash
# Debian/Ubuntu
sudo timedatectl set-ntp true
timedatectl status   # 确认 "System clock synchronized: yes"

# macOS
sudo sntp -sS time.apple.com
```

### 启动时出现“Failed to authenticate”/“whoami failed”

**原因**：访问令牌或 homeserver URL 不正确。

**修复**：验证 `MATRIX_HOMESERVER` 指向你的 homeserver（包含 `https://`，没有尾部斜杠）。检查 `MATRIX_ACCESS_TOKEN` 是否有效——使用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回你的用户信息，说明令牌有效。如果返回错误，请生成一个新令牌。

### “mautrix not installed” 错误

**原因**：未安装 `mautrix` Python 包。

**修复**：安装它：

```bash
pip install 'mautrix[encryption]'
```

或者使用 Hermes 额外选项：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"
```

### 加密错误 / “could not decrypt event”

**原因**：缺少加密密钥，未安装 `libolm`，或机器人的设备不受信任。

**修复**：
1. 验证系统上安装了 `libolm`（请参见上面的 E2EE 部分）。
2. 确保在 `.env` 中设置了 `MATRIX_ENCRYPTION=true`。
3. 在你的 Matrix 客户端（Element）中，转到机器人的个人资料 -> 会话 -> 验证/信任机器人的设备。
4. 如果机器人刚刚加入加密房间，它只能解密 *加入后* 发送的消息。旧消息不可访问。

### 从含有 E2EE 的先前版本升级

:::tip
如果你还手动删除了 `crypto.db`，请参见上面 E2EE 部分的“删除加密存储”警告——还有额外的步骤需要清除 homeserver 上的陈旧单次密钥。
:::

如果你以前使用 `MATRIX_ENCRYPTION=true` 运行 Hermes，现在正在升级到使用新的基于 SQLite 的加密存储的版本，机器人的加密身份已经改变。你的 Matrix 客户端（Element）可能会缓存旧的设备密钥，并拒绝与机器人共享加密会话。

**症状**：机器人连接并在日志中显示“E2EE enabled”，但所有消息都显示“could not decrypt event”，并且机器人从不回复。

**发生了什么**：旧的加密状态（来自先前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。机器人创建了一个全新的加密身份，但你的 Matrix 客户端仍然缓存了旧密钥，并且不会与密钥已更改的设备共享房间的加密会话。这是 Matrix 的安全特性——客户端会将同一设备的身份密钥更改视为可疑。

**修复**（一次性迁移）：

1. **生成一个新的访问令牌** 以获得全新的设备 ID。最简单的方法：

   ```bash
   curl -X POST https://your-server/_matrix/client/v3/login \
     -H "Content-Type: application/json" \
     -d '{
       "type": "m.login.password",
       "identifier": {"type": "m.id.user", "user": "@hermes:your-server.org"},
       "password": "***",
       "initial_device_display_name": "Hermes Agent"
     }'
   ```

   复制新的 `access_token` 并更新 `~/.hermes/.env` 中的 `MATRIX_ACCESS_TOKEN`。

2. **删除旧的加密状态**：

   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db
   rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
   ```

3. **设置你的恢复密钥**（如果你使用交叉签名——大多数 Element 用户都使用）。添加到 `~/.hermes/.env`：

   ```bash
   MATRIX_RECOVERY_KEY=EsT... 你的恢复密钥在此
   ```

   这允许机器人在启动时使用交叉签名密钥自行签署，因此 Element 立即信任新设备。如果没有这个，Element 可能会将新设备视为未验证并拒绝共享加密会话。在 Element 的 **设置** → **安全与隐私** → **加密** 中找到你的恢复密钥。

4. **强制你的 Matrix 客户端轮换加密会话**。在 Element 中，打开与机器人的私聊房间并输入 `/discardsession`。这会强制 Element 创建一个新的加密会话并与机器人的新设备共享。

5. **重新启动 gateway**：

   ```bash
   hermes gateway run
   ```

   如果设置了 `MATRIX_RECOVERY_KEY`，你应该会在日志中看到 `Matrix: cross-signing verified via recovery key`。

6. **发送一条新消息**。机器人应该能够正常解密并回复。

:::note
迁移后，*升级前* 发送的消息无法解密——旧的加密密钥已消失。这只影响过渡期；新消息正常工作。
:::

:::tip
**新安装不受影响。** 只有在你之前使用旧版 Hermes 并拥有正常工作的 E2EE 设置，并且正在升级时，才需要进行此迁移。

**为什么要用新的访问令牌？** 每个 Matrix 访问令牌都绑定到一个特定的设备 ID。使用相同的设备 ID 但新的加密密钥会导致其他 Matrix 客户端不信任该设备（它们将身份密钥更改视为潜在的安全漏洞）。新的访问令牌会获得一个没有陈旧密钥历史记录的新设备 ID，因此其他客户端会立即信任它。
:::

## 代理模式（macOS 上的 E2EE）

Matrix E2EE 需要 `libolm`，但它在 macOS ARM64（Apple Silicon）上无法编译。`hermes-agent[matrix]` 额外选项仅限于 Linux。如果你使用的是 macOS，代理模式允许你在 Linux VM 上的 Docker 容器中运行 E2EE，而实际的代理（Agent）则在 macOS 本地运行，完全访问本地文件、内存和技能。

### 工作原理

```
macOS (主机):
  └─ hermes gateway
       ├─ api_server 适配器 ← 监听 0.0.0.0:8642
       ├─ AIAgent ← 单一事实来源
       ├─ 会话、记忆、技能
       └─ 本地文件访问 (Obsidian、项目等)

Linux VM (Docker):
  └─ hermes gateway (代理模式)
       ├─ Matrix 适配器 ← E2EE 解密/加密
       └─ HTTP 转发 → macOS:8642/v1/chat/completions
           (无 LLM API 密钥、无代理、无推理)
```

Docker 容器仅处理 Matrix 协议 + E2EE。当消息到达时，它解密该消息并将文本通过标准 HTTP 请求转发到主机。主机运行代理（Agent）、调用工具、生成响应并将其流式返回。容器加密并将响应发送到 Matrix。所有会话都是统一的——CLI、Matrix、Telegram 和任何其他平台共享相同的记忆和对话历史。

### 步骤 1：配置主机（macOS）

启用 API 服务器，以便主机接受来自 Docker 容器的传入请求。

添加到 `~/.hermes/.env`：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```

- `API_SERVER_HOST=0.0.0.0` 绑定到所有接口，以便 Docker 容器可以访问。
- `API_SERVER_KEY` 对于非环回绑定是必需的。选择一个强随机字符串。
- API 服务器默认运行在端口 8642（如果需要，可以使用 `API_SERVER_PORT` 更改）。

启动 gateway：

```bash
hermes gateway
```

你应该会看到 API 服务器与已配置的任何其他平台一起启动。从 VM 验证是否可以访问：

```bash
# 从 Linux VM
curl http://<mac-ip>:8642/health
```

### 步骤 2：配置 Docker 容器（Linux VM）

容器需要 Matrix 凭据和代理 URL。它**不需要** LLM API 密钥。

**`docker-compose.yml`：**

```yaml
services:
  hermes-matrix:
    build: .
    environment:
      # Matrix 凭据
      MATRIX_HOMESERVER: "https://matrix.example.org"
      MATRIX_ACCESS_TOKEN: "syt_..."
      MATRIX_ALLOWED_USERS: "@you:matrix.example.org"
      MATRIX_ENCRYPTION: "true"
      MATRIX_DEVICE_ID: "HERMES_BOT"

      # 代理模式 — 转发到主机代理
      GATEWAY_PROXY_URL: "http://192.168.1.100:8642"
      GATEWAY_PROXY_KEY: "your-secret-key-here"
    volumes:
      - ./matrix-store:/root/.hermes/platforms/matrix/store
```

**`Dockerfile`：**

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libolm-dev && rm -rf /var/lib/apt/lists/*
RUN cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"

CMD ["hermes", "gateway"]
```

这就是整个容器。没有 OpenRouter、Anthropic 或任何推理提供商的 API 密钥。

### 步骤 3：启动两者

1. 首先启动主机 gateway：
   ```bash
   hermes gateway
   ```

2. 启动 Docker 容器：
   ```bash
   docker compose up -d
   ```

3. 在加密的 Matrix 房间中发送一条消息。容器解密它，转发到主机，并流式返回响应。

### 配置参考

代理模式在**容器端**（瘦 gateway）配置：

| 设置 | 描述 |
|---------|-------------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如 `http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于身份验证的 Bearer 令牌（必须与主机上的 `API_SERVER_KEY` 匹配） |
| `gateway.proxy_url` | 与 `GATEWAY_PROXY_URL` 相同，但在 `config.yaml` 中 |

主机端需要：

| 设置 | 描述 |
|---------|-------------|
| `API_SERVER_ENABLED` | 设置为 `true` |
| `API_SERVER_KEY` | Bearer 令牌（与容器共享） |
| `API_SERVER_HOST` | 设置为 `0.0.0.0` 以允许网络访问 |
| `API_SERVER_PORT` | 端口号（默认：`8642`） |

### 适用于任何平台

代理模式不仅限于 Matrix。任何平台适配器都可以使用——在任何 gateway 实例上设置 `GATEWAY_PROXY_URL`，它就会将请求转发到远程代理（Agent），而不是在本地运行一个。这对于平台适配器需要在与代理不同的环境中运行（网络隔离、E2EE 要求、资源限制）的任何部署都很有用。

:::tip
会话连续性通过 `X-Hermes-Session-Id` 头部维护。主机的 API 服务器通过此 ID 跟踪会话，因此对话会像使用本地代理一样跨消息持久存在。
:::

:::note
**限制（v1）：** 来自远程代理的工具进度消息不会回传给用户——用户只会看到流式传输的最终响应，而不会看到单个工具调用。危险命令审批提示在主机端处理，不会中继给 Matrix 用户。这些问题可以在未来的更新中解决。
:::

### 机器人已连接并能发送消息，但忽略了入站消息

**原因**：只有当同步负载通过 mautrix 的 `handle_sync()` 机制分发时，Matrix 事件处理器才会触发。如果使用原始的 `client.sync()` 轮询而不调用 `handle_sync()`，适配器可以保持连接（发送正常），但入站消息永远不会到达 `_on_room_message`。

**修复**：Hermes 使用一个显式的同步循环，在初始同步和每次增量同步响应中调用 `client.handle_sync()`。这与上游 issue #7914 和关闭的 PR #37807 的诊断一致，但 Hermes 保留了自身的后台维护任务（已加入房间跟踪、邀请处理、E2EE 密钥共享），而不是将整个生命周期委托给 `client.start()`。如果 gateway 重启后入站消息仍然失败，请验证处理器是否在第一次同步之前注册，并检查日志中是否有 `sync event dispatch error`。

### 同步问题 / 机器人落后

**原因**：长时间运行的工具执行可能会延迟同步循环，或者 homeserver 速度慢。

**修复**：同步循环在出错时每 5 秒自动重试。检查 Hermes 日志中与同步相关的警告。如果机器人持续落后，请确保你的 homeserver 有足够的资源。

### 机器人离线

**原因**：Hermes gateway 未运行，或者连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出中的错误消息。常见问题：错误的 homeserver URL、过期的访问令牌、homeserver 不可达。

### “User not allowed” / 机器人忽略你

**原因**：你的用户 ID 不在 `MATRIX_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 中的 `MATRIX_ALLOWED_USERS`，然后重新启动 gateway。使用完整的 `@user:server` 格式。

### 机器人忽略整个房间

**原因**：设置了 `MATRIX_ALLOWED_ROOMS`，但当前房间 ID 不在列表中，或者房间需要提及，而消息未提及机器人。

**修复**：将房间 ID 添加到 `MATRIX_ALLOWED_ROOMS`，或者如果这是一个个人部署，则移除房间白名单。要查找 Element 中的房间 ID，请打开房间设置并检查 **高级**。

### 桥接消息循环或回显

**原因**：桥接/应用服务傀儡正在将机器人输出作为新用户消息重播，或者桥接使用了非标准的幽灵用户 ID。

**修复**：将桥接幽灵排除在 `MATRIX_ALLOWED_USERS` 之外，添加匹配的 `MATRIX_IGNORE_USER_PATTERNS` 条目，并保持 `MATRIX_PROCESS_NOTICES=false`，除非通知是受信任的工作流的一部分。

## 安全性

:::warning
始终设置 `MATRIX_ALLOWED_USERS`，对于共享/私有部署，还要设置 `MATRIX_ALLOWED_ROOMS`。否则，任何能在已加入房间中向机器人发送消息的人都可能触发代理（Agent）。仅授权你信任的人员和房间——授权用户拥有对代理能力的完全访问权限，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 说明

- **任意 Homeserver**：可与 Synapse、Conduit、Dendrite、matrix.org 或任何符合规范的 Matrix homeserver 配合使用。无需特定的 homeserver 软件。
- **联邦**：如果你在联邦 homeserver 上，机器人可以与来自其他服务器的用户通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS`。
- **自动加入**：机器人自动接受房间邀请并加入。加入后立即开始响应。
- **媒体支持**：Hermes 可以发送和接收图片、音频、视频和文件附件。媒体使用 Matrix 内容存储库 API 上传到你的 homeserver。
- **原生语音消息（MSC3245）**：Matrix 适配器会自动为出站语音消息标记 `org.matrix.msc3245.voice` 标志。这意味着 TTS 响应和语音音频在 Element 和支持 MSC3245 的其他客户端中会渲染为**原生语音气泡**，而不是通用的音频文件附件。带有 MSC3245 标志的入站语音消息也会被正确识别并路由到语音转文字转录。无需配置——这会自动工作。