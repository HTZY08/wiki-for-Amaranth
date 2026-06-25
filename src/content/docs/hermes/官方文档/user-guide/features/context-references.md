---
sidebar_position: 9
sidebar_label: "上下文引用（Context References）"
title: "上下文引用（Context References）"
description: "内联 @ 语法，用于将文件、文件夹、Git 差异和 URL 直接附加到消息中"
---

# 上下文引用（Context References）

输入 `@` 后跟引用内容，即可将内容直接注入到消息中。Hermes 会将引用展开内联，并在 `--- Attached Context ---` 部分下附加内容。

## 支持的引用

| 语法 | 描述 |
|--------|-------------|
| `@file:path/to/file.py` | 注入文件内容 |
| `@file:path/to/file.py:10-25` | 注入指定行范围（从1开始计数，包含两端） |
| `@folder:path/to/dir` | 注入目录树列表及文件元数据 |
| `@diff` | 注入 `git diff`（未暂存的工作树更改） |
| `@staged` | 注入 `git diff --staged`（已暂存的更改） |
| `@git:5` | 注入最近 N 次提交及其补丁（最多10次） |
| `@url:https://example.com` | 获取并注入网页内容 |

## 使用示例

```text
Review @file:src/main.py and suggest improvements

What changed? @diff

Compare @file:old_config.yaml and @file:new_config.yaml

What's in @folder:src/components?

Summarize this article @url:https://arxiv.org/abs/2301.00001
```

一条消息中可以包含多个引用：

```text
Check @file:main.py, and also @file:test.py.
```

引用值后面的尾部标点（`,`、`.`、`;`、`!`、`?`）会被自动去除。

## CLI Tab 补全

在交互式 CLI 中，输入 `@` 会触发自动补全：

- `@` 显示所有引用类型（`@diff`, `@staged`, `@file:`, `@folder:`, `@git:`, `@url:`）
- `@file:` 和 `@folder:` 触发文件系统路径补全，并显示文件大小元数据
- 单独的 `@` 后跟部分文本会显示当前目录下匹配的文件和文件夹

## 行范围

`@file:` 引用支持行范围，用于精确注入内容：

```text
@file:src/main.py:42        # 第 42 行
@file:src/main.py:10-25     # 第 10 到 25 行（包含两端）
```

行号从 1 开始计数。无效范围会被静默忽略（返回完整文件）。

## 大小限制

上下文引用受限于防止模型上下文窗口过载：

| 阈值 | 值 | 行为 |
|-----------|-------|----------|
| 软限制 | 上下文长度的 25% | 追加警告，继续展开 |
| 硬限制 | 上下文长度的 50% | 拒绝展开，返回原始消息不变 |
| 文件夹条目 | 最多 200 个文件 | 超出条目替换为 `- ...` |
| Git 提交 | 最多 10 个 | `@git:N` 被限制在 1 到 10 之间 |

## 安全性

### 敏感路径拦截

以下路径始终被 `@file:` 引用拦截，以防止凭据泄露：

- SSH 密钥和配置：`~/.ssh/id_rsa`, `~/.ssh/id_ed25519`, `~/.ssh/authorized_keys`, `~/.ssh/config`
- Shell 配置文件：`~/.bashrc`, `~/.zshrc`, `~/.profile`, `~/.bash_profile`, `~/.zprofile`
- 凭据文件：`~/.netrc`, `~/.pgpass`, `~/.npmrc`, `~/.pypirc`
- Hermes 环境文件：`$HERMES_HOME/.env`

以下目录被完全拦截（其内部任何文件均被拦截）：
- `~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `~/.kube/`, `$HERMES_HOME/skills/.hub/`

### 路径遍历保护

所有路径都相对于工作目录进行解析。如果引用解析后超出允许的工作空间根目录，则会被拒绝。

### 二进制文件检测

二进制文件通过 MIME 类型和空字节扫描进行检测。已知的文本扩展名（`.py`, `.md`, `.json`, `.yaml`, `.toml`, `.js`, `.ts` 等）会绕过基于 MIME 的检测。二进制文件会被拒绝并显示警告。

## 平台可用性

上下文引用主要是一个 **CLI 特性**。它们在交互式 CLI 中工作，其中 `@` 会触发 Tab 补全，并且引用会在消息发送给代理（Agent）之前展开。

在**消息平台**（Telegram、Discord 等）中，`@` 语法不会被网关展开——消息按原样传递。代理本身仍然可以通过 `read_file`、`search_files` 和 `web_extract` 工具引用文件。

## 与上下文压缩的交互

当对话上下文被压缩时，展开的引用内容会包含在压缩摘要中。这意味着：

- 通过 `@file:` 注入的大文件内容会占用上下文空间
- 如果后续对话被压缩，文件内容会被总结（不会逐字保留）
- 对于非常大的文件，建议使用行范围（`@file:main.py:100-200`）只注入相关部分

## 常见模式

```text
# 代码审查工作流
Review @diff and check for security issues

# 基于上下文的调试
This test is failing. Here's the test @file:tests/test_auth.py
and the implementation @file:src/auth.py:50-80

# 项目探索
What does this project do? @folder:src @file:README.md

# 研究
Compare the approaches in @url:https://arxiv.org/abs/2301.00001
and @url:https://arxiv.org/abs/2301.00002
```

## 错误处理

无效的引用会产生内联警告，而不是导致失败：

| 条件 | 行为 |
|-----------|----------|
| 文件未找到 | 警告：“file not found” |
| 二进制文件 | 警告：“binary files are not supported” |
| 文件夹未找到 | 警告：“folder not found” |
| Git 命令失败 | 警告，附带 git 错误输出 |
| URL 返回空内容 | 警告：“no content extracted” |
| 敏感路径 | 警告：“path is a sensitive credential file” |
| 路径超出工作空间 | 警告：“path is outside the allowed workspace” |