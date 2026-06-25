--- frontmatter ---
---
title: "Imessage — 通过 macOS 上的 imsg CLI 发送和接收 iMessages/SMS"
sidebar_label: "Imessage"
description: "通过 macOS 上的 imsg CLI 发送和接收 iMessages/SMS"
---

--- body ---
{/* 此页面由 skill 的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Imessage

通过 macOS 上的 imsg CLI 发送和接收 iMessages/SMS。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/apple/imessage` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | macos |
| 标签 | `iMessage`, `SMS`, `messaging`, `macOS`, `Apple` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）将看到此指令。
:::

# iMessage

使用 `imsg` 通过 macOS Messages.app 读取和发送 iMessage/SMS。

## 前提条件

- **macOS** 且已登录 Messages.app
- 安装：`brew install steipete/tap/imsg`
- 为终端授予完全磁盘访问权限（系统设置 → 隐私 → 完全磁盘访问权限）
- 在提示时为 Messages.app 授予自动化权限

## 何时使用

- 用户要求发送 iMessage 或短信
- 读取 iMessage 对话历史
- 查看最近的 Messages.app 聊天记录
- 向电话号码或 Apple ID 发送消息

## 何时不使用

- Telegram/Discord/Slack/WhatsApp 消息 → 使用相应的网关通道
- 群聊管理（添加/删除成员）→ 不支持
- 批量/群发消息 → 务必先向用户确认

## 快速参考

### 列出聊天

```bash
imsg chats --limit 10 --json
```

### 查看历史

```bash
# 按聊天 ID
imsg history --chat-id 1 --limit 20 --json

# 包含附件信息
imsg history --chat-id 1 --limit 20 --attachments --json
```

### 发送消息

```bash
# 仅文本
imsg send --to "+14155551212" --text "Hello!"

# 带附件
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# 强制使用 iMessage 或 SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### 监听新消息

```bash
imsg watch --chat-id 1 --attachments
```

## 服务选项

- `--service imessage` — 强制使用 iMessage（要求收件人已启用 iMessage）
- `--service sms` — 强制使用 SMS（绿色气泡）
- `--service auto` — 让 Messages.app 自行决定（默认）

## 规则

1. **发送前务必确认收件人和消息内容**
2. **未经用户明确批准，切勿向未知号码发送**
3. **附加文件前验证文件路径是否存在**
4. **不要滥用** — 限制自身频率

## 示例工作流

用户："发消息给妈妈说我会晚到"

```bash
# 1. 查找妈妈的聊天
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. 向用户确认："找到 Mom (+1555123456)。通过 iMessage 发送 'I'll be late' 吗？"

# 3. 确认后发送
imsg send --to "+1555123456" --text "I'll be late"
```