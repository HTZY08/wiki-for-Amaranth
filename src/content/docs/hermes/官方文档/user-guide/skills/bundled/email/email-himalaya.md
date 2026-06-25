--- frontmatter ---
---
title: "Himalaya — Himalaya CLI：通过终端管理IMAP/SMTP电子邮件"
sidebar_label: "Himalaya"
description: "Himalaya CLI：通过终端管理IMAP/SMTP电子邮件的命令行工具"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是此页面。 */}

# Himalaya

Himalaya CLI：通过终端管理IMAP/SMTP电子邮件。

## 技能元数据（Skill Metadata）

|                          |                                                              |
|--------------------------|--------------------------------------------------------------|
| 来源（Source）           | 内置（默认安装）                                             |
| 路径（Path）             | `skills/email/himalaya`                                      |
| 版本（Version）          | `1.1.0`                                                      |
| 作者（Author）           | 社区（community）                                            |
| 许可证（License）        | MIT                                                          |
| 平台（Platforms）        | linux, macos, windows                                        |
| 标签（Tags）             | `电子邮件`, `IMAP`, `SMTP`, `CLI`, `通信`                    |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，这是代理（Agent）看到的指令。
:::

# Himalaya 电子邮件 CLI

Himalaya 是一个 CLI 电子邮件客户端，允许您通过终端使用 IMAP、SMTP、Notmuch 或 Sendmail 后端管理电子邮件。

此技能与 Hermes 电子邮件网关适配器（Email gateway adapter）不同。网关适配器允许人们向代理发送电子邮件，并使用 Hermes 内置的 IMAP/SMTP 适配器；而此技能允许代理通过终端工具操作邮箱，并且需要外部安装 `himalaya` CLI。

## 参考（References）

- `references/configuration.md`（配置文件设置 + IMAP/SMTP 认证）
- `references/message-composition.md`（用于撰写电子邮件的 MML 语法）

## 先决条件（Prerequisites）

1. 已安装 Himalaya CLI（通过 `himalaya --version` 验证）
2. 配置文件位于 `~/.config/himalaya/config.toml`
3. 已配置 IMAP/SMTP 凭据（密码安全存储）

### 安装（Installation）

```bash
# 预编译二进制文件（Linux/macOS — 推荐）
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh

# 通过 Homebrew 在 macOS 上安装
brew install himalaya

# 或通过 cargo 安装（任何安装有 Rust 的平台）
cargo install himalaya --locked
```

## 配置设置（Configuration Setup）

运行交互式向导设置账户：

```bash
himalaya account configure
```

或手动创建 `~/.config/himalaya/config.toml`：

```toml
[accounts.personal]
email = "you@example.com"
display-name = "您的姓名"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"  # 或使用 keyring

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"

# 文件夹别名（folder aliases）（himalaya v1.2.0+ 语法）。当服务器的文件夹名称与 himalaya 的规范名称（inbox/sent/drafts/trash）不一致时必需。Gmail 是常见情况——请参阅 `references/configuration.md` 了解 `[Gmail]/Sent Mail` 映射。
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

> **关于别名语法的注意事项。** v1.2.0 之前的文档使用 `[accounts.NAME.folder.alias]` 子段（单数 `alias`）。v1.2.0 会静默忽略该形式——TOML 解析正常，但别名解析器不会读取它，因此所有查找都会回退到规范名称。在 Gmail 上这意味着 SMTP 投递成功后保存到“已发送”会失败，并且 `himalaya message send` 会以非零状态退出。任何根据此退出码重试的调用者（代理、脚本、用户）都会重新执行整个发送过程——包括 SMTP——从而向收件人产生重复邮件。请始终使用 `folder.aliases.X`（复数形式，点号分隔的键，直接位于 `[accounts.NAME]` 下）。

## Hermes 集成注意事项（Hermes Integration Notes）

- **阅读、列出、搜索、移动、删除** 均直接通过终端工具完成
- **撰写/回复/转发**——建议使用管道输入（`cat << EOF | himalaya template send`）以确保可靠性。交互式 `$EDITOR` 模式可以与 `pty=true` + 后台 + 进程工具配合使用，但需要了解编辑器及其命令
- 使用 `--output json` 获取结构化输出，便于程序化解析
- `himalaya account configure` 向导需要交互式输入——请使用 PTY 模式：`terminal(command="himalaya account configure", pty=true)`

## 常见操作（Common Operations）

### 列出文件夹（List Folders）

```bash
himalaya folder list
```

### 列出电子邮件（List Emails）

列出收件箱（INBOX）中的邮件（默认）：

```bash
himalaya envelope list
```

列出特定文件夹中的邮件：

```bash
himalaya envelope list --folder "Sent"
```

分页列出：

```bash
himalaya envelope list --page 1 --page-size 20
```

### 搜索电子邮件（Search Emails）

```bash
himalaya envelope list from john@example.com subject meeting
```

### 阅读电子邮件（Read an Email）

按 ID 阅读邮件（显示纯文本）：

```bash
himalaya message read 42
```

导出原始 MIME：

```bash
himalaya message export 42 --full
```

### 回复一封邮件（Reply to an Email）

要从 Hermes 非交互地回复，请先阅读原始邮件，撰写回复，然后通过管道发送：

```bash
# 获取回复模板，编辑后发送
himalaya template reply 42 | sed 's/^$/\n您的回复内容在此\n/' | himalaya template send
```

或手动构建回复：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: sender@example.com
Subject: Re: 原始主题
In-Reply-To: <original-message-id>

您的回复在此。
EOF
```

回复所有人（reply-all）（交互式——需要 $EDITOR，请改用上述模板方法）：

```bash
himalaya message reply 42 --all
```

### 转发一封邮件（Forward an Email）

```bash
# 获取转发模板并通过管道修改
himalaya template forward 42 | sed 's/^To:.*/To: newrecipient@example.com/' | himalaya template send
```

### 撰写一封新邮件（Write a New Email）

**非交互式（在 Hermes 中使用此方法）**——通过标准输入传递邮件内容：

```bash
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: 测试邮件

来自 Himalaya 的问候！
EOF
```

或使用 headers 标志：

```bash
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "邮件正文在此"
```

注意：如果没有通过管道输入，`himalaya message write` 会打开 `$EDITOR`。这可以通过 `pty=true` + 后台模式工作，但使用管道更简单可靠。

### 移动/复制邮件（Move/Copy Emails）

移动到文件夹：

```bash
himalaya message move "Archive" 42
```

复制到文件夹：

```bash
himalaya message copy "Important" 42
```

### 删除邮件（Delete an Email）

```bash
himalaya message delete 42
```

### 管理标志（Manage Flags）

添加标志：

```bash
himalaya flag add 42 --flag seen
```

移除标志：

```bash
himalaya flag remove 42 --flag seen
```

## 多账户（Multiple Accounts）

列出账户：

```bash
himalaya account list
```

使用特定账户：

```bash
himalaya --account work envelope list
```

## 附件（Attachments）

从邮件中保存附件：

```bash
himalaya attachment download 42
```

保存到特定目录：

```bash
himalaya attachment download 42 --downloads-dir ~/Downloads
```

## 输出格式（Output Formats）

大多数命令支持 `--output` 选项以获取结构化输出：

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

## 调试（Debugging）

启用调试日志：

```bash
RUST_LOG=debug himalaya envelope list
```

带回溯的完整跟踪：

```bash
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## 提示（Tips）

- 使用 `himalaya --help` 或 `himalaya <command> --help` 查看详细用法。
- 消息 ID 相对于当前文件夹；切换文件夹后需要重新列出。
- 要撰写带附件的富文本邮件，请使用 MML 语法（参见 `references/message-composition.md`）。
- 使用 `pass`、系统钥匙串或输出密码的命令安全存储密码。