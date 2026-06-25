---
title: Mattermost
---

sidebar_position: 8
title: "Mattermost"
description: "将 Hermes Agent 设置为 Mattermost 机器人"
---

--- body ---
# Mattermost 设置

Hermes Agent 以机器人（bot）的形式与 Mattermost 集成，让你可以通过直接消息或团队频道与 AI 助手聊天。Mattermost 是一个自托管、开源的 Slack 替代品——你可以将其部署在自己的基础设施上，完全掌控数据。该机器人通过 Mattermost 的 REST API（v4）和 WebSocket 连接以获取实时事件，通过 Hermes Agent 管道（包括工具使用、记忆和推理）处理消息，并实时响应。它支持文本、文件附件、图片和斜杠命令。

无需外部 Mattermost 库——适配器使用了 `aiohttp`，这已经是 Hermes 的依赖项。

在设置之前，这是大多数人最想了解的部分：Hermes 在你的 Mattermost 实例中如何运行。

## Hermes 的运行方式

| 上下文 | 行为 |
|---------|----------|
| **私信（DM）** | Hermes 会回复每一条消息。无需 `@提及`。每条私信有独立的会话（session）。 |
| **公共/私有频道** | 当你 `@提及` Hermes 时，它会回复。没有提及则忽略消息。 |
| **线程（Thread）** | 如果 `MATTERMOST_REPLY_MODE=thread`，Hermes 会在你的消息下方的线程中回复。线程上下文与父频道隔离。 |
| **有多用户的共享频道** | 默认情况下，Hermes 会为频道内的每个用户隔离会话历史。两个人在同一频道发言不会共享一个对话记录，除非你明确禁用此功能。 |

:::tip
如果你希望 Hermes 以线程方式回复（嵌套在原消息下方），请设置 `MATTERMOST_REPLY_MODE=thread`。默认值为 `off`，会在频道中发送扁平消息。
:::

### Mattermost 中的会话模型

默认情况下：

- 每条私信（DM）拥有自己的会话
- 每个线程拥有自己的会话命名空间
- 共享频道中的每个用户在该频道内拥有自己的会话

这由 `config.yaml` 控制：

```yaml
group_sessions_per_user: true
```

仅当你明确希望整个频道使用一个共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作频道可能很有用，但也意味着：

- 用户共享上下文增长和 token 成本
- 某人的冗长工具依赖任务可能会膨胀其他人的上下文
- 某人的进行中运行可能会中断同频道内另一个人的后续操作

本指南将带你完成完整的设置流程——从在 Mattermost 上创建机器人到发送第一条消息。

## 第 1 步：启用机器人账户

在创建机器人账户之前，必须先在 Mattermost 服务器上启用机器人账户。

1. 以**系统管理员**身份登录 Mattermost。
2. 进入**系统控制台** → **集成** → **机器人账户**。
3. 将**启用机器人账户创建**设置为 **true**。
4. 点击**保存**。

:::info
如果你没有系统管理员访问权限，请让你的 Mattermost 管理员启用机器人账户并为你创建一个。
:::

## 第 2 步：创建一个机器人账户

1. 在 Mattermost 中，点击 **☰** 菜单（左上角）→ **集成** → **机器人账户**。
2. 点击**添加机器人账户**。
3. 填写详细信息：
   - **用户名**：例如 `hermes`
   - **显示名称**：例如 `Hermes Agent`
   - **描述**：可选
   - **角色**：`成员` 即可
4. 点击**创建机器人账户**。
5. Mattermost 会显示**机器人令牌（token）**。**请立即复制它。**

:::warning[令牌仅显示一次]
机器人令牌在创建机器人账户时只显示一次。如果丢失，你需要从机器人账户设置中重新生成。切勿公开分享你的令牌或将其提交到 Git——拥有此令牌的任何人都能完全控制该机器人。
:::

将令牌安全地存储起来（例如密码管理器）。你将在第 5 步中用到它。

:::tip
你也可以使用**个人访问令牌**代替机器人账户。进入**个人资料** → **安全** → **个人访问令牌** → **创建令牌**。如果你希望 Hermes 以你自己的用户身份发帖（而不是单独的机器人用户），这将很有用。
:::

## 第 3 步：将机器人添加到频道

机器人必须是它要回复的任何频道的成员：

1. 打开你想添加机器人的频道。
2. 点击频道名称 → **添加成员**。
3. 搜索你的机器人用户名（例如 `hermes`）并将其添加。

对于私信（DM），只需打开与机器人的直接消息——它即可立即回复。

## 第 4 步：找到你的 Mattermost 用户 ID

Hermes Agent 使用你的 Mattermost 用户 ID 来控制谁可以与机器人交互。要查找它：

1. 点击你的**头像**（左上角）→ **个人资料**。
2. 你的用户 ID 会显示在个人资料对话框中——点击即可复制。

你的用户 ID 是一个 26 字符的字母数字字符串，例如 `3uo8dkh1p7g1mfk49ear5fzs5c`。

:::warning
你的用户 ID **不是**你的用户名。用户名是 `@` 后面的内容（例如 `@alice`）。用户 ID 是 Mattermost 内部使用的长字母数字标识符。
:::

**替代方法**：你也可以通过 API 获取你的用户 ID：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-mattermost-server/api/v4/users/me | jq .id
```

:::tip
要获取**频道 ID**：点击频道名称 → **查看信息**。频道 ID 会显示在信息面板中。如果你希望手动设置主频道（home channel），则需要此 ID。
:::

## 第 5 步：配置 Hermes Agent

### 选项 A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择 **Mattermost**，然后按要求粘贴服务器 URL、机器人令牌和用户 ID。

### 选项 B：手动配置

将以下内容添加到你的 `~/.hermes/.env` 文件中：

```bash
# 必需
MATTERMOST_URL=https://mm.example.com
MATTERMOST_TOKEN=***
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c

# 多个允许的用户（逗号分隔）
# MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c,8fk2jd9s0a7bncm1xqw4tp6r3e

# 可选：回复模式（thread 或 off，默认：off）
# MATTERMOST_REPLY_MODE=thread

# 可选：无需 @提及 即可回复（默认：true = 需要提及）
# MATTERMOST_REQUIRE_MENTION=false

# 可选：机器人无需 @提及 即可回复的频道（逗号分隔的频道 ID）
# MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 保持共享频道和线程中每个参与者的上下文隔离

### 启动网关

配置完成后，启动 Mattermost 网关：

```bash
hermes gateway
```

机器人应在几秒内连接到你的 Mattermost 服务器。发送一条消息——无论是私信还是已添加的频道——以测试。

:::tip
你可以将 `hermes gateway` 在后台运行或设为 systemd 服务以实现持久运行。详情请参阅部署文档。
:::

## 主频道（Home Channel）

你可以指定一个“主频道”，机器人会在此频道发送主动消息（例如定时任务输出、提醒和通知）。有两种设置方式：

### 使用斜杠命令

在包含机器人的任何 Mattermost 频道中键入 `/sethome`。该频道即成为主频道。

### 手动配置

将以下内容添加到你的 `~/.hermes/.env`：

```bash
MATTERMOST_HOME_CHANNEL=abc123def456ghi789jkl012mn
```

将 ID 替换为实际的频道 ID（点击频道名称 → 查看信息 → 复制 ID）。

## 回复模式

`MATTERMOST_REPLY_MODE` 设置控制 Hermes 如何发布回复：

| 模式 | 行为 |
|------|----------|
| `off`（默认） | Hermes 在频道中发布扁平消息，如同普通用户。 |
| `thread` | Hermes 在你的原始消息下方的线程中回复。在双方频繁交流时保持频道整洁。 |

在 `~/.hermes/.env` 中设置：

```bash
MATTERMOST_REPLY_MODE=thread
```

## 提及行为

默认情况下，机器人仅在频道中被 `@提及` 时回复。你可以更改此设置：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | 设置为 `false` 以回复频道中的所有消息（私信始终有效）。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | （无） | 逗号分隔的频道 ID，在这些频道中机器人无需 `@提及` 即可回复，即使 require_mention 为 true 时也有效。 |

在 Mattermost 中查找频道 ID：打开频道，点击频道名称标题，在 URL 或频道详情中查找 ID。

当机器人被 `@提及` 时，提及内容会在处理前自动从消息中移除。

## 频道白名单（`allowed_channels`）

将机器人限制在一组固定的 Mattermost 频道中。设置后，机器人**仅**在 ID 出现在列表中的频道内回复——来自其他频道的消息会被静默忽略，即使机器人被 `@提及` 也是如此。

**私信（DM）不受此过滤器限制**，因此授权用户始终可以通过直接消息联系到机器人。

```yaml
mattermost:
  allowed_channels:
    - "abc123def456ghi789jkl012mno"   # #ops
    - "xyz987uvw654rst321opq098nml"   # #incident-response
```

或通过环境变量（逗号分隔）：

```bash
MATTERMOST_ALLOWED_CHANNELS="abc123def456ghi789jkl012mno,xyz987uvw654rst321opq098nml"
```

行为：

- 空/未设置 → 无限制（完全向后兼容）。
- 非空 → 频道 ID 必须在列表中，否则消息在任何其他门控（提及要求、`MATTERMOST_FREE_RESPONSE_CHANNELS` 等）运行之前被丢弃。
- 通过 Mattermost UI → 频道标题 → “查看信息”查找频道 ID，或从频道 URL 中读取。

另请参阅：[管理员/用户斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。

## 故障排除

### 机器人不响应消息

**原因**：机器人不是频道的成员，或者 `MATTERMOST_ALLOWED_USERS` 不包含你的用户 ID。

**修复**：将机器人添加到频道（频道名称 → 添加成员 → 搜索机器人）。确认你的用户 ID 在 `MATTERMOST_ALLOWED_USERS` 中。重启网关。

### 403 禁止错误

**原因**：机器人令牌无效，或机器人没有在频道中发帖的权限。

**修复**：检查 `.env` 文件中的 `MATTERMOST_TOKEN` 是否正确。确保机器人账户未被停用。确认机器人已被添加到频道。如果使用个人访问令牌，请确保你的账户具有所需权限。

### WebSocket 断开/重连循环

**原因**：网络不稳定、Mattermost 服务器重启，或 WebSocket 连接的防火墙/代理问题。

**修复**：适配器会自动重连并采用指数退避（2秒 → 60秒）。检查服务器的 WebSocket 配置——反向代理（nginx、Apache）需要配置 WebSocket 升级头。确认没有防火墙阻止 Mattermost 服务器上的 WebSocket 连接。

对于 nginx，确保配置包含：

```nginx
location /api/v4/websocket {
    proxy_pass http://mattermost-backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

### 启动时“身份验证失败”

**原因**：令牌或服务器 URL 不正确。

**修复**：确认 `MATTERMOST_URL` 指向你的 Mattermost 服务器（包括 `https://`，无尾部斜杠）。检查 `MATTERMOST_TOKEN` 是否有效——用 curl 测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/api/v4/users/me
```

如果返回你的机器人用户信息，则令牌有效。如果返回错误，请重新生成令牌。

### 机器人离线

**原因**：Hermes 网关未运行，或连接失败。

**修复**：检查 `hermes gateway` 是否正在运行。查看终端输出的错误信息。常见问题：错误 URL、令牌过期、Mattermost 服务器不可达。

### “用户不被允许”/机器人忽略你

**原因**：你的用户 ID 未包含在 `MATTERMOST_ALLOWED_USERS` 中。

**修复**：将你的用户 ID 添加到 `~/.hermes/.env` 的 `MATTERMOST_ALLOWED_USERS` 中，并重启网关。请记住：用户 ID 是 26 字符的字母数字字符串，而不是你的 `@用户名`。

## 每个频道的提示词（Per-Channel Prompts）

为特定的 Mattermost 频道分配临时系统提示词。该提示词在每次对话时运行时注入，从不持久化到对话历史中，因此更改会立即生效。

```yaml
mattermost:
  channel_prompts:
    "channel_id_abc123": |
      你是一名研究助理。专注于学术来源、
      引用和简洁的总结。
    "channel_id_def456": |
      代码审查模式。请精确关注边界情况和
      性能影响。
```

键是 Mattermost 频道 ID（在频道 URL 中或通过 API 获取）。匹配频道中的所有消息都会注入该提示词作为临时系统指令。

## 安全

:::warning
始终设置 `MATTERMOST_ALLOWED_USERS` 以限制谁可以与机器人交互。如果没有此设置，网关默认会拒绝所有用户，以确保安全。仅添加你信任的用户的 ID——授权用户拥有完全的代理能力，包括工具使用和系统访问。
:::

有关保护 Hermes Agent 部署的更多信息，请参阅[安全指南](../security.md)。

## 注意事项

- **对自托管友好**：适用于任何自托管的 Mattermost 实例。无需 Mattermost Cloud 账户或订阅。
- **无额外依赖**：适配器使用 `aiohttp` 进行 HTTP 和 WebSocket 通信，该库已包含在 Hermes Agent 中。
- **与团队版兼容**：同时适用于 Mattermost 团队版（免费）和企业版。