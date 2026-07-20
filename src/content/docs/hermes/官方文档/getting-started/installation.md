---
title: 安装
---

# 安装

在两分钟之内让 Hermes Agent 运行起来！

## 平台支持

完整的平台支持矩阵，请参见[平台支持](../reference/platform-support.md)。

## 快速安装

### 使用 Hermes Desktop 安装器（macOS 或 Windows，推荐）

要轻松安装命令行和桌面应用程序，请从我们的网站下载 Hermes Desktop 安装器并运行。

### 不使用 Hermes Desktop：

如需仅安装命令行版本（无需 Hermes Desktop），请运行：

#### Linux / macOS / WSL2 / Android (Termux)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生）

在 Powershell 中运行：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

如果先安装了纯命令行版本，之后想安装并运行 Hermes Desktop，只需执行 `hermes desktop`。

### 安装器的功能

安装器会自动处理所有事项——所有依赖（Python、Node.js、ripgrep、ffmpeg）、仓库克隆、虚拟环境、全局 `hermes` 命令设置以及 LLM 提供商配置。

#### 安装布局

| 安装器类型 | 代码存放位置 | `hermes` 可执行文件 | 数据目录 |
|-----------|-------------|-------------------|---------|
| 单用户（git 安装器） | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes`（符号链接） | `~/.hermes/` |
| 全局模式（`sudo curl ...`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/`（或 `$HERMES_HOME`） |

### 安装完成后

重新加载 shell 并开始聊天：

```bash
source ~/.bashrc
hermes
```

之后如需重新配置单项设置：

```bash
hermes model
hermes tools
hermes gateway setup
hermes config set
hermes config get
hermes setup
```

最快捷的方式：Nous Portal

```bash
hermes setup --portal
```

## 前置条件

安装器：在非 Windows 平台上，唯一的前置条件是 Git。在 Linux 上，还需确保 `curl` 和 `xz-utils` 可用。桌面应用程序额外需要 `g++`（或 `build-essential`）。

Nix 用户：Nix 不再是明确支持的安装方式（仅限尽力而为）。

## 手动/开发者安装

请参阅贡献指南中的[开发环境搭建](../contributing/development-setup.md)部分。

## 非 Root / 系统服务用户安装

支持以专用的非特权用户身份运行 Hermes。安装过程中真正需要 root 权限的唯一步骤是 Playwright 的 `--with-deps`。

## 故障排除

| 问题 | 解决方法 |
|------|---------|
| `hermes: command not found` | 重新加载 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置您的提供商 |
| 更新后配置缺失 | 先运行 `hermes config check`，然后运行 `hermes config migrate` |

## 安装方法自动检测

Hermes 会自动检测是通过 `pip`、git 安装器、Homebrew 还是 NixOS 安装的，并且 `hermes update` 会打印出对应路径的更新命令。
