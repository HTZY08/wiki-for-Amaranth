---
title: Photon
---

sidebar_position: 18
---

--- body ---
# Photon iMessage

通过 [Photon][photon]（一项托管服务，负责处理 Apple 线路分配和滥用防护层，因此您无需自行运行 Mac 中继）将 Hermes 连接到 **iMessage**。

免费层级使用 Photon 的共享 iMessage 线路池——不同的收件人可能会看到不同的发送号码，但每个对话保持稳定。付费的企业层级为每位用户提供相同的专属号码；该插件同时支持这两种模式，免费层级是推荐的起点。

:::info 免费开始
Photon 的共享线路池是免费的。无需订阅即可从 Hermes 发送您的第一条 iMessage——只需一个我们可以绑定到您账户的手机号码。
:::

## 架构

Photon 是一个**持久连接**通道，类似 Discord 或 Slack——**无需 Webhook、无需公网 URL、无需管理签名密钥。**

`spectrum-ts` SDK 维护着一个与 Photon 之间的长期 **gRPC 流**，用于双向通信。由于该 SDK 仅支持 TypeScript，Hermes 在一个小型受监督的 **Node 边车（Sidecar）** 中运行它，并通过回环（Loopback）与之通信：

- **入站（Inbound）**——边车消费 SDK 的 `app.messages` gRPC 流，并通过回环 `GET /inbound`（NDJSON）将每条消息转发给 Python 适配器。适配器对消息进行去重并分发给代理（Agent），如果流断开则自动重连。
- **出站（Outbound）**——回复以回环 POST 方式发送到边车，边车调用 SDK 的 `space.send(...)`。

Python 插件会自动启动、监督并关闭边车。

## 前提条件

- 一个 Photon 账户——在 [app.photon.codes][app] 注册
- PATH 中包含 **Node.js 18.17 或更新版本**（`node --version`）
- 一个可以接收 iMessage 的手机号码（用于绑定您的账户）

仅此而已——无需设置公网 URL 或隧道。

## 首次设置

运行统一网关向导并选择 **Photon iMessage**：

```bash
hermes gateway setup
```

……或者直接运行 Photon 设置（向导调用的也是同一流程）：

```bash
# 设备码登录 + 项目 + 用户 + 边车依赖，一步完成
hermes photon setup --phone +15551234567
```

设置顺序如下：

1. **设备登录**（`client_id=photon-cli`）——打开 `https://app.photon.codes/` 进行授权，并存储 bearer token。
2. **查找或创建**您账户上的 `Hermes Agent` 项目。
3. **启用 Spectrum**，读取项目的 Spectrum ID，并轮换项目密钥。
4. **将您的手机号码注册为 Spectrum 用户**——如果该号码的用户已存在则跳过，因此重复运行是安全的。
5. **打印分配的 iMessage 线路**——用于向您的代理发送消息的号码。
6. **在插件的边车目录内运行 `npm install`**。

运行时凭据写入 `~/.hermes/.env`（`PHOTON_PROJECT_ID` = Spectrum 项目 ID，`PHOTON_PROJECT_SECRET`），与其他通道存储其 token 的位置相同。管理元数据（设备 token、仪表板项目 ID）存放在 `~/.hermes/auth.json` 的 `credential_pool.photon` / `credential_pool.photon_project` 下。

## 授权用户

Photon 使用与其他 Hermes 通道相同的授权模型。选择一种方式：

**DM 配对（默认）。** 当未知号码向您的 Photon 线路发送消息时，Hermes 会回复一个配对码。使用以下命令批准：

```bash
hermes pairing approve photon <CODE>
```

使用 `hermes pairing list` 查看待处理的配对码和已批准的用户。

**预授权特定号码**（在 `~/.hermes/.env` 中）：

```bash
PHOTON_ALLOWED_USERS=+15551234567,+15559876543
```

**开放访问**（仅开发环境，在 `~/.hermes/.env` 中）：

```bash
PHOTON_ALLOW_ALL_USERS=true
```

当设置了 `PHOTON_ALLOWED_USERS` 时，未知发送者会被静默忽略，而不是提供配对码（白名单表明您有意限制了访问权限）。

### 在群聊中要求提及（Mention）

默认情况下，Hermes 会回复所有授权的私聊和群消息。要使群聊成为可选加入，请启用提及限制（私聊始终有效）：

```yaml
gateway:
  platforms:
    photon:
      enabled: true
      require_mention: true
```

当 `require_mention: true` 时，除非消息匹配唤醒词模式，否则群聊消息会被忽略。默认匹配 `Hermes` 和 `@Hermes agent` 的变体。如需自定义代理名称，请设置正则表达式模式：

```yaml
gateway:
  platforms:
    photon:
      require_mention: true
      mention_patterns:
        - '(?<![\w@])@?amos\b[,:\-]?'
```

这两个键也接受环境变量（`PHOTON_REQUIRE_MENTION`、`PHOTON_MENTION_PATTERNS`）。这与 BlueBubbles iMessage 通道使用的提及限制模型相同。

## 启动网关

```bash
hermes gateway start
```

您会看到类似以下内容：

```
[photon] connected — sidecar on 127.0.0.1:8789, streaming inbound over gRPC
```

向您的分配号码发送一条 iMessage，Hermes 将会回复。

## 状态与故障排除

```bash
hermes photon status
```

显示已保存的凭据、边车健康状态、您的注册号码以及 Hermes 使用的分配 iMessage 线路。当 Photon token 和仪表板项目可用时，`status` 会从仪表板刷新缺失的号码行，而无需预配新线路。

```
Photon iMessage status
──────────────────────
  device token        : ✓ stored
  dashboard project   : 3c90c3cc-0d44-4b50-...
  spectrum project id : sp-...
  project secret      : ✓ stored
  my number           : +15551234567
  assigned number     : +16282679185
  node binary         : /usr/bin/node
  sidecar deps        : ✓ installed
```

常见问题：

- **`sidecar deps : ✗ run hermes photon install-sidecar`** —— Node 已安装，但 `spectrum-ts` 未安装。请运行建议的命令。
- **`device token : ✗ missing`** —— 运行 `hermes photon setup` 进行登录。
- **`No iMessage line assigned yet`** —— Spectrum 已启用，但尚未预配线路；请重新运行 `hermes photon setup` 或检查 [仪表板][app]。
- **边车无法启动** —— 确认 `node --version` 为 18.17 或更高，并且 `hermes photon install-sidecar` 已成功完成。

## 当前限制

- **入站附件仅包含元数据。** 入站事件携带文件名 + MIME 类型；代理会看到一个标记，但尚不能读取字节。SDK 通过 `content.read()` 暴露附件字节，因此这是边车的后续工作。
- **支持出站附件。** Hermes 通过 spectrum-ts 的 `attachment()` / `voice()` 内容构建器，经由边车的 `/send-attachment` 端点发送图片、语音消息、视频和文档。媒体后，说明文字作为单独的 iMessage 气泡到达。
- **Photon 免费配额：** 每台服务器每天 5000 条消息，每个共享线路每天 50 次新对话发起。可增加配额——发送邮件至 `help@photon.codes`。

## 环境变量

| 变量                      | 默认值                 | 说明                                      |
|---------------------------|------------------------|-------------------------------------------|
| `PHOTON_PROJECT_ID`       | 来自 `.env`           | Spectrum 项目 ID（SDK 的 `projectId`）；由设置命令设定 |
| `PHOTON_PROJECT_SECRET`   | 来自 `.env`           | 项目密钥；由设置命令设定                   |
| `PHOTON_SIDECAR_PORT`     | `8789`                 | 边车控制及入站通道的回环端口              |
| `PHOTON_SIDECAR_AUTOSTART`| `true`                 | 适配器是否自动生成边车进程                |
| `PHOTON_NODE_BIN`         | `which node`           | 覆盖 Node 二进制路径                      |
| `PHOTON_HOME_CHANNEL`     | （未设置）             | 用于 cron / 通知的默认空间 ID             |
| `PHOTON_HOME_CHANNEL_NAME`| （未设置）             | 主频道的人类可读标签                       |
| `PHOTON_ALLOWED_USERS`    | （未设置）             | 以逗号分隔的 E.164 白名单                 |
| `PHOTON_ALLOW_ALL_USERS`  | `false`                | 仅开发环境——接受任何发送者                |
| `PHOTON_REQUIRE_MENTION`  | `false`                | 在群聊中要求回复前有唤醒词                |
| `PHOTON_MENTION_PATTERNS` | Hermes 唤醒词          | 用于群提及的 JSON 列表 / 逗号 / 换行正则模式 |
| `PHOTON_DASHBOARD_HOST`   | `app.photon.codes`     | 覆盖仪表板 / 设备登录主机                 |
| `PHOTON_SPECTRUM_HOST`    | `spectrum.photon.codes`| 覆盖 Spectrum API 主机                    |

[photon]: https://photon.codes/
[app]: https://app.photon.codes/