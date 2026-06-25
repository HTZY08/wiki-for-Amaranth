# Spotify

Hermes 可以直接控制 Spotify —— 播放、队列、搜索、播放列表、已保存的曲目/专辑以及收听历史 —— 使用 Spotify 的官方 Web API 和 PKCE OAuth。令牌存储在 `~/.hermes/auth.json` 中，并在遇到 401 时自动刷新；每台机器只需登录一次（刷新令牌约 6 个月后过期；过期后重新运行 `hermes auth spotify`）。

与 Hermes 内置的 OAuth 集成（Google、GitHub Copilot、Codex）不同，Spotify 要求每个用户注册自己的轻量级开发者应用。Spotify 不允许第三方发布任何人都可以使用的公共 OAuth 应用。这个过程大约需要两分钟，`hermes auth spotify` 会引导你完成。

## 先决条件

- 一个 Spotify 账户。**免费版（Free）** 可用于搜索、播放列表、资料库和活动工具。**高级版（Premium）** 是播放控制（播放、暂停、跳过、跳转、音量、队列添加、转移）所需的。
- Hermes Agent 已安装并运行。
- 对于播放工具：需要一个**活跃的 Spotify Connect 设备** —— Spotify 应用必须在至少一台设备（手机、桌面、网页播放器、音箱）上打开，这样 Web API 才能控制。如果没有活跃设备，你会收到 `403 Forbidden` 并显示"no active device"消息；在任何设备上打开 Spotify 然后重试。

## 设置

### 一次性设置：`hermes tools` 或首次运行设置

最快的方式。运行：

```bash
hermes tools
```

滚动到 `🎵 Spotify`，按空格键启用，然后按 `s` 保存。在首次运行的 `hermes setup` / `hermes setup tools` 流程中也有相同的开关。Spotify 保持可选加入（opt-in），因此在此处启用它会像 `hermes tools` 一样运行提供商感知的配置。

Hermes 会直接将你带入 OAuth 流程 —— 如果你还没有 Spotify 应用，它会引导你内联创建一个。完成后，工具集在一次操作中同时启用并完成身份验证。

如果你更喜欢分别执行这些步骤（或者稍后重新身份验证），请使用下面的两步流程。

### 两步流程

#### 1. 启用工具集

```bash
hermes tools
```

打开 `🎵 Spotify` 开关，保存，当内联向导打开时，按 Ctrl+C 关闭。工具集保持启用；只有身份验证步骤被推迟。

#### 2. 运行登录向导

```bash
hermes auth spotify
```

7 个 Spotify 工具仅在步骤 1 之后才会出现在代理（Agent）的工具集中 —— 它们默认关闭，这样不需要这些工具的用户就不会在每次 API 调用中发送额外的工具模式（tool schemas）。

如果没有设置 `HERMES_SPOTIFY_CLIENT_ID`，Hermes 会内联引导你完成应用注册：

1. 在浏览器中打开 `https://developer.spotify.com/dashboard`
2. 打印出需要粘贴到 Spotify"创建应用"表单中的精确值
3. 提示你输入获得的 Client ID
4. 将其保存到 `~/.hermes/.env`，以便后续运行跳过此步骤
5. 直接进入 OAuth 同意流程

批准后，令牌写入 `~/.hermes/auth.json` 的 `providers.spotify` 下。活动的推理提供商（inference provider）不会被更改 —— Spotify 身份验证独立于你的 LLM 提供商。

### 创建 Spotify 应用（向导要求的内容）

当仪表板打开时，点击**创建应用（Create app）**并填写：

| 字段 | 值 |
|-------|-------|
| 应用名称（App name） | 任意（例如 `hermes-agent`） |
| 应用描述（App description） | 任意（例如 `personal Hermes integration`） |
| 网站（Website） | 留空 |
| 重定向 URI（Redirect URI） | `http://127.0.0.1:43827/spotify/callback` |
| 哪些 API/SDK？ | 勾选 **Web API** |

同意条款并点击**保存（Save）**。在下一页点击**设置（Settings）** → 复制**客户端 ID（Client ID）**并粘贴到 Hermes 提示中。这是 Hermes 需要的唯一值 —— PKCE 不使用客户端密钥。

### 通过 SSH / 在无头环境中运行

如果设置了 `SSH_CLIENT` 或 `SSH_TTY`，Hermes 会在向导和 OAuth 步骤中跳过自动打开浏览器的操作。复制 Hermes 打印出的仪表板 URL 和授权 URL，在本地机器的浏览器中打开它们，然后正常进行 —— 本地 HTTP 监听器仍然在远程主机的 `43827` 端口上运行。你的笔记本电脑的浏览器无法在没有 SSH 本地转发的情况下访问远程回环地址：

```bash
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

对于跳板机/堡垒机设置和其他问题（mosh、tmux、端口冲突），请参阅 [通过 SSH / 远程主机进行 OAuth](../../guides/oauth-over-ssh.md)。

## 验证

```bash
hermes auth status spotify
```

显示令牌是否存在以及访问令牌何时过期。刷新是自动的：当任何 Spotify API 调用返回 401 时，客户端会交换刷新令牌并重试一次。刷新令牌在 Hermes 重启后依然存在，因此只有在 Spotify 账户设置中撤销应用或运行 `hermes auth logout spotify` 时才需要重新身份验证。

## 使用

一旦登录，代理（Agent）就可以使用 7 个 Spotify 工具。你可以自然地与代理对话 —— 它会选择正确的工具和操作。为了获得最佳行为，代理（Agent）会加载一个配套的技能（Skill），该技能教授规范的用法模式（单次搜索然后播放、何时不预检 `get_state` 等）。

```
> 播放一些迈尔斯·戴维斯（Miles Davis）
> 我现在在听什么
> 将这首曲目添加到我的深夜爵士乐（Late Night Jazz）播放列表
> 跳到下一首歌
> 创建一个名为“Focus 2026”的新播放列表，并添加我最后播放的三首歌
> 我保存的专辑中哪些是 Radiohead 的
> 搜索 Blackbird 的原声翻唱
> 将播放转移到我的厨房音箱
```

### 工具参考

所有改变播放的操作都接受一个可选的 `device_id` 来指定目标设备。如果省略，Spotify 将使用当前活跃的设备。

#### `spotify_playback`
控制并检查播放，以及获取最近播放的历史。

| 操作 | 用途 | 需要高级版（Premium）？ |
|--------|---------|----------|
| `get_state` | 完整播放状态（曲目、设备、进度、随机播放/重复） | 否 |
| `get_currently_playing` | 仅当前曲目（返回 204 时为空 —— 见下文） | 否 |
| `play` | 开始/恢复播放。可选：`context_uri`、`uris`、`offset`、`position_ms` | 是 |
| `pause` | 暂停播放 | 是 |
| `next` / `previous` | 跳过曲目 | 是 |
| `seek` | 跳转到 `position_ms` | 是 |
| `set_repeat` | `state` = `track` / `context` / `off` | 是 |
| `set_shuffle` | `state` = `true` / `false` | 是 |
| `set_volume` | `volume_percent` = 0-100 | 是 |
| `recently_played` | 最近播放的曲目。可选 `limit`、`before`、`after`（Unix 毫秒） | 否 |

#### `spotify_devices`
| 操作 | 用途 |
|--------|---------|
| `list` | 你的账户可见的每个 Spotify Connect 设备 |
| `transfer` | 将播放转移到 `device_id`。可选 `play: true` 在转移时开始播放 |

### Home Assistant 管理的音箱

如果 Home Assistant 管理已经支持 Spotify Connect 的音箱（例如 Sonos、Echo、Nest 或其他支持 Connect 的音箱），只要 Spotify 能看见它们，它们就会自动出现在 `spotify_devices list` 中。对于此路径，Hermes 不需要 Home Assistant ↔ Spotify 桥接器 —— Spotify 本身负责设备路由。

请 Hermes 通过音箱的显示名称转移播放（例如“将 Spotify 转移到厨房音箱”），或者在编写脚本时调用 `spotify_devices list` 并将确切的 `device_id` 传递给 `spotify_devices transfer`。如果音箱缺失，请打开 Spotify 应用或音箱的 Spotify 集成一次，以便 Spotify 将其注册为活跃的 Connect 目标。

#### `spotify_queue`
| 操作 | 用途 | 需要高级版（Premium）？ |
|--------|---------|----------|
| `get` | 当前队列中的曲目 | 否 |
| `add` | 将 `uri` 附加到队列 | 是 |

#### `spotify_search`
搜索目录。`query` 是必需的。可选：`types`（`track` / `album` / `artist` / `playlist` / `show` / `episode` 数组）、`limit`、`offset`、`market`。

#### `spotify_playlists`
| 操作 | 用途 | 必需参数 |
|--------|---------|---------------|
| `list` | 用户的播放列表 | — |
| `get` | 一个播放列表 + 曲目 | `playlist_id` |
| `create` | 新播放列表 | `name`（+ 可选 `description`、`public`、`collaborative`） |
| `add_items` | 添加曲目 | `playlist_id`、`uris`（可选 `position`） |
| `remove_items` | 移除曲目 | `playlist_id`、`uris`（+ 可选 `snapshot_id`） |
| `update_details` | 重命名/编辑 | `playlist_id` + `name`、`description`、`public`、`collaborative` 中的任意 |

#### `spotify_albums`
| 操作 | 用途 | 必需参数 |
|--------|---------|---------------|
| `get` | 专辑元数据 | `album_id` |
| `tracks` | 专辑曲目列表 | `album_id` |

#### `spotify_library`
统一访问已保存的曲目和已保存的专辑。使用 `kind` 参数选择集合。

| 操作 | 用途 |
|--------|---------|
| `list` | 分页的库列表 |
| `save` | 将 `ids` / `uris` 添加到库 |
| `remove` | 从库中移除 `ids` / `uris` |

必需：`kind` = `tracks` 或 `albums`，加上 `action`。

### 功能矩阵：免费版（Free） vs 高级版（Premium）

只读工具在免费版账户上可用。任何改变播放或队列的操作都需要高级版。

| 免费版可用 | 需要高级版 |
|---------------|------------------|
| `spotify_search`（全部） | `spotify_playback` — play、pause、next、previous、seek、set_repeat、set_shuffle、set_volume |
| `spotify_playback` — get_state、get_currently_playing、recently_played | `spotify_queue` — add |
| `spotify_devices` — list | `spotify_devices` — transfer |
| `spotify_queue` — get | |
| `spotify_playlists`（全部） | |
| `spotify_albums`（全部） | |
| `spotify_library`（全部） | |

## 调度：Spotify + cron

由于 Spotify 工具是常规的 Hermes 工具，在 Hermes 会话中运行的 cron 作业可以按任何计划触发播放。无需新代码。

### 早晨唤醒播放列表

```bash
hermes cron add \
  --name "morning-commute" \
  "0 7 * * 1-5" \
  "将播放转移到我的厨房音箱，并开始我的'Morning Commute'播放列表。音量设为40。打开随机播放。"
```

工作日上午7点会发生什么：
1. Cron 启动一个无头的 Hermes 会话。
2. 代理（Agent）读取提示，调用 `spotify_devices list` 按名称找到"厨房音箱"，然后 `spotify_devices transfer` → `spotify_playback set_volume` → `spotify_playback set_shuffle` → `spotify_search` + `spotify_playback play`。
3. 音乐在目标音箱上开始播放。总成本：一个会话，几次工具调用，无需人工输入。

### 晚上放松

```bash
hermes cron add \
  --name "wind-down" \
  "30 22 * * *" \
  "暂停 Spotify。然后将音量设为20，这样明天再启动时就不会太吵。"
```

### 注意事项

- **cron 触发时必须存在一个活跃设备。** 如果没有 Spotify 客户端在运行（手机/桌面/Connect 音箱），播放操作会返回 `403 no active device`。对于早晨播放列表，技巧是瞄准一个始终在线的设备（Sonos、Echo、智能音箱）而不是你的手机。
- **任何改变播放的操作都需要高级版（Premium）** —— 播放、暂停、跳过、音量、转移。只读的 cron 作业（例如定时“邮件发送我最近播放的曲目”）在免费版上可以正常使用。
- **cron 代理（Agent）继承你的活跃工具集。** 必须在 `hermes tools` 中启用 Spotify，cron 会话才能看到 Spotify 工具。
- **Cron 作业以 `skip_memory=True` 运行**，因此它们不会写入你的记忆存储。

完整的 cron 参考：[Cron 作业](./cron)。

## 退出登录

```bash
hermes auth logout spotify
```

从 `~/.hermes/auth.json` 中移除令牌。要同时清除应用配置，从 `~/.hermes/.env` 中删除 `HERMES_SPOTIFY_CLIENT_ID`（以及你设置过的 `HERMES_SPOTIFY_REDIRECT_URI`），或者再次运行向导。

要在 Spotify 端撤销应用，请访问[连接到你账户的应用](https://www.spotify.com/account/apps/)并点击**移除访问权限（REMOVE ACCESS）**。

## 故障排除

**`403 Forbidden — Player command failed: No active device found`** —— 你需要在至少一台设备上运行 Spotify。在手机、桌面或网页播放器上打开 Spotify 应用，启动任意曲目一秒钟以注册设备，然后重试。`spotify_devices list` 显示当前可见的设备。

**`403 Forbidden — Premium required`** —— 你使用的是免费版账户，试图使用改变播放的操作。请参阅上面的功能矩阵。

**`get_currently_playing` 返回 `204 No Content`** —— 目前没有任何设备在播放内容。这是 Spotify 的正常响应，不是错误；Hermes 将其显示为解释性的空结果（`is_playing: false`）。

**`INVALID_CLIENT: Invalid redirect URI`** —— 你的 Spotify 应用设置中的重定向 URI 与 Hermes 使用的 URI 不匹配。默认是 `http://127.0.0.1:43827/spotify/callback`。要么将其添加到应用允许的重定向 URI 列表中，要么在 `~/.hermes/.env` 中设置 `HERMES_SPOTIFY_REDIRECT_URI` 为你注册的值。

**`429 Too Many Requests`** —— Spotify 的速率限制。Hermes 会返回友好的错误信息；等待一分钟然后重试。如果持续发生，你可能在脚本中运行了紧密的循环 —— 大致每 30 秒重置一次配额。

**`401 Unauthorized` 反复出现** —— 你的刷新令牌已被撤销（通常是因为你从账户中移除了应用，或者应用被删除）。再次运行 `hermes auth spotify`。

**向导没有打开浏览器** —— 如果你通过 SSH 或在没有显示器的容器中操作，Hermes 会检测到并跳过自动打开。复制它打印出的仪表板 URL 并手动打开。

## 高级：自定义作用域（scopes）

默认情况下，Hermes 会请求每个已提供工具所需的全部作用域。如果你想限制访问，可以覆盖：

```bash
hermes auth spotify --scope "user-read-playback-state user-modify-playback-state playlist-read-private"
```

作用域参考：[Spotify Web API 作用域](https://developer.spotify.com/documentation/web-api/concepts/scopes)。如果你请求的作用域少于工具所需的，该工具的调用将返回 403 失败。

## 高级：自定义客户端 ID / 重定向 URI

```bash
hermes auth spotify --client-id <id> --redirect-uri http://localhost:3000/callback
```

或者永久设置它们到 `~/.hermes/.env`：

```
HERMES_SPOTIFY_CLIENT_ID=<your_id>
HERMES_SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

重定向 URI 必须在你的 Spotify 应用设置中被允许列表覆盖。默认值适用于大多数人 —— 仅在端口 43827 被占用时才更改它。

## 文件位置

| 文件 | 内容 |
|------|----------|
| `~/.hermes/auth.json` → `providers.spotify` | 访问令牌、刷新令牌、过期时间、作用域、重定向 URI |
| `~/.hermes/.env` | `HERMES_SPOTIFY_CLIENT_ID`、可选的 `HERMES_SPOTIFY_REDIRECT_URI` |
| Spotify 应用 | 由你拥有，位于 [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)；包含客户端 ID 和重定向 URI 允许列表 |