--- frontmatter ---
---
title: ntfy
description: Hermes Agent 官方文档汉化版
---

--- body ---

# ntfy

[ntfy](https://ntfy.sh/) 是一个基于 HTTP 的简单发布-订阅通知服务。它可以使用 `ntfy.sh` 的免费公共服务器，也可以自行托管实例，并支持任何能够发起 HTTP 请求的客户端——手机、浏览器、脚本、手表等。

ntfy 是 Hermes 的一个极佳轻量推送通道：在 [ntfy 手机应用](https://ntfy.sh/docs/subscribe/phone/) 中订阅一个主题（topic），向该主题发送消息即可与代理（Agent）对话，回复则会直接推送到手机。

> 运行 `hermes gateway setup` 并选择 **ntfy**，即可获得引导式设置体验。

## 前置条件

- 一个主题名称（任意唯一字符串——`hermes-myname-2026` 即可）
- 已安装 [ntfy 手机应用](https://ntfy.sh/docs/subscribe/phone/) 并订阅了该主题
- 可选：自托管的 ntfy 服务器，或者用于私有/保留主题的 `ntfy.sh` 账户令牌（token）

仅此而已。不需要 SDK、守护进程或 Node.js。该适配器（adapter）使用 `httpx`，它已经是 Hermes 的依赖项。

## 配置 Hermes

### 通过设置向导

```bash
hermes gateway setup
```

选择 **ntfy** 并按照提示操作。

### 通过环境变量

将以下内容添加到 `~/.hermes/.env`：

```
NTFY_TOPIC=hermes-myname-2026
NTFY_ALLOWED_USERS=hermes-myname-2026
NTFY_HOME_CHANNEL=hermes-myname-2026
```

| 变量 | 必需 | 描述 |
|---|---|---|
| `NTFY_TOPIC` | 是 | 要订阅的主题（接收消息） |
| `NTFY_SERVER_URL` | 可选 | 服务器地址（默认：`https://ntfy.sh`）—— 可指向自托管 ntfy 以保护隐私 |
| `NTFY_TOKEN` | 可选 | Bearer 令牌（例如 `tk_xyz`）或用于基本认证的 `user:pass` |
| `NTFY_PUBLISH_TOPIC` | 可选 | 用于发送回复的另一个主题（默认为 `NTFY_TOPIC`） |
| `NTFY_MARKDOWN` | 可选 | 设置为 `true` 以发送带有 `X-Markdown: true` 头的回复 |
| `NTFY_ALLOWED_USERS` | 推荐 | 允许的主题名称列表（以逗号分隔），会被视为用户 ID（详见下文） |
| `NTFY_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 以允许所有发布者——仅适用于使用读取令牌保护的私有主题 |
| `NTFY_HOME_CHANNEL` | 可选 | 用于定时任务（cron）/ 通知投递的默认主题 |
| `NTFY_HOME_CHANNEL_NAME` | 可选 | 主频道（home channel）的人类可读标签 |

## 身份模型——部署前请阅读

ntfy 没有原生的认证用户身份。已发布消息上的 `title` 字段是**由发布者控制的**，发送者可以随意设置。Hermes 适配器 **不会** 使用 `title` 进行授权——否则任何知道该主题的发布者都可以冒充允许的用户。

相反，**主题名称本身即为身份**。发布到该主题的每条消息都被视为来自同一个逻辑用户（即主题）。因此，`NTFY_ALLOWED_USERS` 通常只需要设置为该主题名称本身——一个单一入口的允许列表，用于控制整个频道。

这意味着**任何知道该主题的人都可以与代理对话**。要建立真正的信任边界：

- **自托管 ntfy**，并通过[访问控制](https://docs.ntfy.sh/config/#access-control)锁定主题。只有持有读写令牌的授权客户端才能发布消息。
- 或者**在 ntfy.sh 上使用私有主题**（[保留主题](https://docs.ntfy.sh/publish/#reserved-topics)需要账户），并用 `NTFY_TOKEN` 保护。
- 或者**选择一个长且难以猜测的主题名称**（如 `hermes-7d4f9c8b-2026`），并将其视为共享密钥。这是最轻量的设置，但主题名称可能通过日志或截图泄露。

无论哪种情况，除非底层主题受访问控制保护，否则不要通过 ntfy 传输敏感数据。

## 快速开始——从手机与代理对话

1. 选择一个主题名称：`hermes-myname-2026`
2. 在手机上：安装 [ntfy 应用](https://ntfy.sh/docs/subscribe/phone/)，点击 **+**，输入 `hermes-myname-2026`
3. 在主机上：
   ```bash
   echo 'NTFY_TOPIC=hermes-myname-2026' >> ~/.hermes/.env
   echo 'NTFY_ALLOWED_USERS=hermes-myname-2026' >> ~/.hermes/.env
   hermes gateway restart
   ```
4. 在 ntfy 应用中，向该主题发送一条消息。代理的回复将以推送通知的形式送达。

## 将 ntfy 用于定时任务（cron jobs）

一旦设置了 `NTFY_HOME_CHANNEL`，定时任务即可投递到 ntfy：

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="ntfy",          # 使用 NTFY_HOME_CHANNEL
    prompt="检查警报并总结。"
)
```

或者显式指定目标主题：

```python
send_message(target="ntfy:alerts-channel", message="完成！")
```

即使定时任务在网关（gateway）进程外运行，这种用法仍然有效——该插件注册了一个 `standalone_sender_fn`，它会打开自己的 HTTP 连接。

## 自托管 ntfy

如果你想要完全控制：

```bash
# Docker
docker run -p 80:80 -it binwiederhier/ntfy serve

# 原生安装
go install heckel.io/ntfy/v2@latest
ntfy serve
```

然后将 Hermes 指向它：

```
NTFY_SERVER_URL=https://ntfy.mydomain.com
NTFY_TOPIC=hermes
NTFY_TOKEN=tk_abc123  # 如果你已设置访问控制
```

自托管可以让你拥有主题访问控制、消息持久化策略、附件和表情符号标签等功能。详情请参阅 [ntfy 服务器文档](https://docs.ntfy.sh/install/)。

## Markdown 格式化

ntfy 客户端在发布者设置 `X-Markdown: true` 头时会渲染 Markdown。要为 Hermes 的回复启用此功能：

```
NTFY_MARKDOWN=true
```

或者在 `config.yaml` 中：

```yaml
platforms:
  ntfy:
    extra:
      markdown: true
```

手机应用支持 CommonMark 的子集——粗体、斜体、列表、链接、围栏代码块。具体支持范围请参见 [ntfy 的 Markdown 文档](https://docs.ntfy.sh/publish/#markdown-formatting)。

## 仅发送设置（仅通知，不接受输入）

如果你只希望 Hermes *推送* 通知到 ntfy（例如定时任务摘要、警报），而不接受任何回复消息，可以将 `NTFY_TOPIC` 和 `NTFY_PUBLISH_TOPIC` 设置为相同值，并完全跳过 `NTFY_ALLOWED_USERS`。没有允许列表，代理就不会响应任何输入消息——你的手机会收到推送，但对话是单向的。

## 限制

- **消息大小**：ntfy 将消息正文限制在 4096 字符。Hermes 会在超出时截断并发出警告。
- **无输入状态指示**：协议未提供此类支持；`send_typing` 为空操作（no-op）。
- **无线程或附件**：ntfy 仅提供纯推送通知。长回复保留在消息正文中，不支持线程分支。
- **无原生用户身份**：请参阅上文身份模型部分。

## 故障排查

**认证失败 / 401** —— `NTFY_TOKEN` 错误，或该令牌对此主题没有发布/订阅权限。适配器会在遇到 401 时停止重连循环，网关运行状态将显示 `fatal: ntfy_unauthorized`。修正令牌后重启网关。

**主题未找到 / 404** —— 配置的服务器上不存在 `NTFY_TOPIC`。对于 ntfy.sh，主题在首次发布时会自动创建，因此 404 意味着你指向了一个自托管服务器，且该服务器上未预置该主题。适配器会停止重连循环并显示 `fatal: ntfy_topic_not_found`。

**已连接但收不到消息** —— 检查 `NTFY_ALLOWED_USERS` 是否包含主题名称本身。在 ntfy 的身份模型下，主题即用户；允许列表为空会拒绝所有消息。

**每 60 秒重连** —— 流 keepalive 默认间隔为 55 秒；ntfy 可能存在间歇性网络问题。适配器会采用指数退避策略（2 → 5 → 10 → 30 → 60 秒），并在流稳定存活超过 60 秒后重置退避值。