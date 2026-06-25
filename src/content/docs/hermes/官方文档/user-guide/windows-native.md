--- 前置信息 ---
---
title: "Windows（原生）指南"
description: "在 Windows 10 / 11 上原生运行 Hermes Agent——安装、功能矩阵、UTF-8 控制台、Git Bash、网关作为计划任务、编辑器处理、PATH、卸载及常见陷阱"
sidebar_label: "Windows（原生）"
sidebar_position: 3
---

--- 正文 ---
# Windows（原生）指南

Hermes 可以在 Windows 10 和 Windows 11 上原生运行——无需 WSL、Cygwin 或 Docker。本章节深入探讨：哪些功能可以原生工作，哪些仅限 WSL，安装程序实际做了什么，以及你可能需要调整的 Windows 特定旋钮。

如果你只想安装，只需要[首页](/)或[安装页面](../getting-started/installation#windows-native-powershell)上的一行命令就够了。当出现异常时再回到这里。

:::tip 想要使用 WSL？
如果你更喜欢真实的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 语义、Linux 风格的文件监视器等），请参阅 **[Windows（WSL2）指南](./windows-wsl-quickstart.md)**。两者可以干净地共存：原生数据位于 `%LOCALAPPDATA%\hermes`，WSL 数据位于 `~/.hermes`。
:::

## 快速安装

打开 **PowerShell**（或 Windows 终端）并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序将进入 `%LOCALAPPDATA%\hermes\` 并将 `hermes` 添加到你的 **用户 PATH**——完成后请打开一个新的终端。

**安装程序选项**（需要使用脚本块形式传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（对于测试 PR 很有用） |
| `-Commit` | 未设置 | 将安装固定到特定的 commit SHA（覆盖 `-Branch`） |
| `-Tag` | 未设置 | 将安装固定到特定的 git tag（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过虚拟环境创建（高级用法——你自行管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码位置 |

安装程序会自动重试不稳定的 git 拉取，并从任何下载的 `install.ps1` 载荷中去除 BOM，因此 HTTP 传输过程中捕获的 UTF-8 BOM 不再破坏 `[scriptblock]::Create((irm ...))` 形式。

### 桌面安装程序（备选）

提供了一个轻量级的 GUI 安装程序——如果你更愿意双击 `.exe` 而不是打开 PowerShell，则很有用。下载 Hermes Desktop，运行安装程序，首次启动时 GUI 会在底层调用 `install.ps1` 来配置 Python（通过 `uv`）、Node、PortableGit 以及下文描述的其他依赖引导过程。首次运行后，桌面应用和通过 PowerShell 安装的 `hermes` CLI 共享同一个 `%LOCALAPPDATA%\hermes\hermes-agent` 安装目录和 `%LOCALAPPDATA%\hermes` 数据目录——你可以自由在 GUI 和 CLI 之间切换。

当你想要熟悉的 Windows 安装体验，或者将 Hermes 交给非开发人员使用时，请使用桌面安装程序；如果你已经身处终端，请使用 PowerShell 单行命令。

### 依赖引导（`dep_ensure`）

在首次启动时（以及检测到缺失工具时按需运行），Hermes 会运行一个小的 Python 引导程序——`hermes_cli/dep_ensure.py`——检查并惰性安装其所需的非 Python 依赖。在 Windows 上，相关的依赖项包括：

| 依赖项 | Hermes 为什么需要它 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，为会话内的克隆提供 `git`。在安装时配置，而不是由 `dep_ensure` 完成。 |
| **Node.js 22** | 浏览器工具（`agent-browser`）、TUI 的 Web 桥接和 WhatsApp 桥接所需。 |
| **ffmpeg** | TTS / 语音消息的音频格式转换。 |
| **ripgrep** | 快速文件搜索——如果不可用则回退到 `grep`。 |
| **npm packages** | `agent-browser`、Playwright Chromium 以及每个工具集的 Node 依赖项在首次使用浏览器工具时一次性安装。 |

每个依赖项都有一个 `shutil.which(...)` 风格的检查；如果二进制文件缺失且运行是交互式的，`dep_ensure` 会提供安装选项（将实际安装逻辑委托给 `scripts\install.ps1 -ensure <dep>`）。非交互式运行（网关、cron、无头桌面启动）会跳过提示，并显示清晰的错误信息：`this feature needs <dep>`。

## 安装程序实际做了什么

从上到下，按顺序：

1. **引导 `uv`**——Astral 的快速 Python 管理器。安装到 `%USERPROFILE%\.local\bin`。
2. **通过 `uv` 安装 Python 3.11**。无需现有 Python。
3. **安装 Node.js 22**（如果可用则使用 winget，否则将可移植的 Node tarball 解压到 `%LOCALAPPDATA%\hermes\node`）。用于浏览器工具和 WhatsApp 桥接。
4. **安装可移植 Git**——如果 `git` 已在 PATH 上，安装程序会使用它；否则，它会下载一个精简的、自包含的 **PortableGit**（约 45 MB，来自官方的 `git-for-windows` 发行版）到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限，无需 Windows 安装程序注册表，不会干扰系统上的其他任何内容。
5. **将代码仓库克隆到** `%LOCALAPPDATA%\hermes\hermes-agent` 并在其中创建虚拟环境。
6. **分层 `uv pip install`**——首先尝试 `.[all]`，如果 `git+https` 依赖在 GitHub 上遇到速率限制而失败，则逐步回退到较小的集合（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。防止“单个依赖失败就将你降到裸安装”的故障模式。
7. **根据 `.env` 自动安装消息相关 SDK**——如果存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED`，则运行 `python -m ensurepip --upgrade` 并针对性地执行 `pip install` 调用，以便每个平台的 SDK 实际上可导入。
8. **设置 `HERMES_GIT_BASH_PATH`** 为解析得到的 `bash.exe`，以便 Hermes 在全新的 shell 中确定性地找到它。
9. **将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到用户 PATH 并设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`**——在你打开新的终端后，`hermes` 命令可用（并指向你的数据目录）。
10. **运行 `hermes setup`**——正常的首次运行向导（模型、提供商、工具集）。可使用 `-SkipSetup` 跳过。

:::tip 在 Windows 上跳过提供商搜索
在 Windows 上，为每个工具设置 API 密钥（Firecrawl、FAL、Browser Use、OpenAI TTS）是让 agent 有用的最高摩擦部分。通过 [Nous Portal](/user-guide/features/tool-gateway) 订阅，可以通过一次 OAuth 登录涵盖模型 **以及** 所有这些工具。安装程序完成后，运行 `hermes setup --portal` 将所有内容关联起来。
:::

## 功能矩阵

除了仪表板的嵌入式终端窗格外，所有功能都在 Windows 上原生运行。

| 功能 | 原生 Windows | WSL2 |
|---|---|---|
| CLI（`hermes chat`、`hermes setup`、`hermes gateway` 等） | ✓ | ✓ |
| 交互式 TUI（`hermes --tui`） | ✓ | ✓ |
| 消息网关（Telegram、Discord、Slack、WhatsApp 以及 15+ 平台） | ✓ | ✓ |
| Cron 调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 的 Chromium） | ✓ | ✓ |
| MCP 服务器（stdio 和 HTTP） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓（通过 WSL 网络） |
| Web 仪表板（会话、作业、指标、配置） | ✓ | ✓ |
| 仪表板 `/chat` 嵌入式终端窗格 | ✗（需要 POSIX PTY） | ✓ |
| 登录时自动启动 | ✓（schtasks） | ✓（systemd） |

仪表板的 `/chat` 标签通过 POSIX PTY（`ptyprocess`）嵌入了一个真实的终端。原生 Windows 没有等效的基元；Python 的 `pywinpty` / Windows ConPTY 可以工作，但需要单独实现——作为未来工作对待。**仪表板的其余部分原生工作**——只有那个标签会显示“请使用 WSL2 获取此功能”的横幅。

## Hermes 如何在 Windows 上运行 shell 命令

Hermes 的终端工具通过 **Git Bash** 运行命令，与 Claude Code 使用的策略相同。这避免了 POSIX 与 Windows 之间的差距，而无需重写每个工具。

`bash.exe` 的解析顺序：

1. 如果设置了 `HERMES_GIT_BASH_PATH` 环境变量，则使用它。
2. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`（安装程序管理的 PortableGit）。
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（较旧的 Git-for-Windows 布局）。
4. 系统安装的 Git-for-Windows（`%ProgramFiles%\Git\bin\bash.exe` 等）。
5. MSYS2、Cygwin 或 PATH 上的任何 `bash.exe` 作为最后手段。

安装程序会显式设置 `HERMES_GIT_BASH_PATH`，因此新的 PowerShell 会话不必重新发现。如果你想让 Hermes 使用特定的 bash（例如系统 Git Bash 或通过符号链接托管的 WSL bash），可以覆盖它。

**陷阱：** MinGit 的布局与完整的 Git-for-Windows 安装程序不同——bash 位于 `usr\bin\bash.exe`，而不是 `bin\bash.exe`。Hermes 会检查两者。如果你手动解压 MinGit zip，请确保选择 **非 busybox** 变体（`MinGit-*-64-bit.zip`，而不是 `MinGit-*-busybox*.zip`）——busybox 构建提供的是 `ash` 而不是 `bash`，并且大多数 coreutils 缺失。

## Windows 上的 UTF-8 控制台

Python 在 Windows 上的默认 stdio 使用控制台的活动代码页（通常是 cp1252 或 cp437）。Hermes 的横幅、斜杠命令列表、工具馈送、Rich 面板和技能描述都包含 Unicode。如果不加干预，任何这些操作都会因 `UnicodeEncodeError: 'charmap' codec can't encode character…` 而崩溃。

修复方法位于 `hermes_cli/stdio.py::configure_windows_stdio()` 中，并在每个入口点（`cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期被调用。它：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 将控制台代码页切换为 CP_UTF8（65001）。
2. 将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8 并设置 `errors='replace'`。
3. 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`（通过 `setdefault`，因此用户显式值优先），以便子 Python 进程继承 UTF-8。
4. 如果既未设置 `EDITOR` 也未设置 `VISUAL`，则设置 `EDITOR=notepad`（请参阅下面的编辑器部分）。

幂等性。在非 Windows 系统上无操作。

**选择退出：** 在环境中设置 `HERMES_DISABLE_WINDOWS_UTF8=1` 将回退到传统的 cp1252 stdio 路径。用于定位编码错误；在正常操作下不太可能是正确的设置。

## 编辑器（`Ctrl-X Ctrl-E`、`/edit`）

在版本 #21561 之前，在 Windows 上按下 `Ctrl-X Ctrl-E` 或输入 `/edit` 会静默无操作。prompt_toolkit 有一个硬编码的 POSIX 绝对路径回退列表（`/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi` 等），这些路径在 Windows 上永远不会解析——即使安装了完整的 Git for Windows。

Hermes 的 Windows stdio 填充现在默认设置 `EDITOR=notepad`。记事本随每个 Windows 安装一起提供，并且可以作为阻塞编辑器工作——`subprocess.call(["notepad", file])` 会阻塞直到窗口关闭。

**用户覆盖仍然优先**（它们在 setdefault 之前被检查）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 上的 `--wait` 标志至关重要——没有它，编辑器会立即返回，Hermes 得到的是一个空白缓冲区。

在 PowerShell 配置文件中永久设置它：

```powershell
# In $PROFILE
$env:EDITOR = "code --wait"
```

或者在系统设置中作为用户环境变量设置，以便每个新的 shell 都能获取到。

## CLI 中用于换行的 `Ctrl+Enter`

Windows 终端将 `Ctrl+Enter` 作为专用键序列传递。Hermes 将其绑定到“插入换行符”，因此你可以在 CLI 中编写多行提示，而无需回退到 `Esc` 然后 `Enter`。在 Windows 终端、VS Code 集成终端以及任何支持 VT 转义序列的现代 Windows 控制台主机中均可工作。

在传统的 `cmd.exe` 控制台中，`Ctrl+Enter` 会退化为普通 `Enter`——请改用 `Esc Enter`，或者升级到 Windows 终端（它是免费的，并且在 Windows 11 上默认安装）。

## 在 Windows 登录时运行网关

`hermes gateway install` 在 Windows 上使用 **计划任务**，并带有启动文件夹回退——无需管理员权限。

### 安装

```powershell
hermes gateway install
```

底层发生的事情：

1. `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway`——注册一个任务，该任务在你登录时以标准（非提升）权限运行。没有 UAC 提示。
2. 如果 schtasks 被组策略阻止，则回退到将 `start /min cmd.exe /d /c <wrapper>` 快捷方式写入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`。效果相同，但稍微粗糙一些。
3. 通过 `pythonw.exe` **分离地** 启动网关——而不是 `python.exe`。`pythonw.exe` 没有附加控制台，这使其免受来自同组进程的 `CTRL_C_EVENT` 广播（这是一个真实的问题，以前当你 Ctrl+C 同一进程组中的任何内容时，网关会被杀死）。

启动时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # 合并视图：schtasks + 启动文件夹 + 运行中的 PID
hermes gateway start       # 立即启动计划任务
hermes gateway stop        # 优雅的 SIGTERM 等效（通过 psutil 的 TerminateProcess）
hermes gateway restart
hermes gateway uninstall   # 移除 schtasks 条目、启动快捷方式、pid 文件
```

`hermes gateway status` 是幂等的——连续调用一千次也不会意外杀死网关。（在 PR #21561 之前，它会通过 `os.kill(pid, 0)` 在 C 级别与 `CTRL_C_EVENT` 冲突而静默杀死目标——如果你关心这个故事，请参阅下面的“进程管理内部”部分。）

### 为什么不是 Windows 服务？

服务需要管理员权限才能安装，并将网关的生命周期绑定到机器启动，而不是用户登录。典型的 Hermes 用户希望：登录 → 网关可用，注销 → 网关关闭。计划任务完全做到这一点，无需提权。如果你确实需要服务，请手动使用 `nssm` 或 `sc create`——但你可能不需要。

## 数据布局

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出 + 虚拟环境。`venv\Scripts\hermes.exe` 是添加到用户 PATH 的命令。可以安全地 `Remove-Item -Recurse` 并重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit（仅当安装程序配置了它时才存在）。 |
| `%LOCALAPPDATA%\hermes\node\` | 可移植 Node.js（仅当安装程序配置了它时才存在）。 |
| `%LOCALAPPDATA%\hermes\bin\` | Hermes 管理的 `uv.exe`（用于更新的 Python 管理器）。 |
| `%LOCALAPPDATA%\hermes\`（根目录） | 你的配置、认证、技能、会话、日志（`config.yaml`、`.env`、`skills\`、`sessions\`、`logs\` 等）。**在重新安装时保留。** |

在原生 Windows 上，安装程序设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`，因此你的数据和可丢弃的安装位于同一个 `%LOCALAPPDATA%\hermes` 根目录下：安装/运行时是 `hermes-agent\`、`git\`、`node\` 和 `bin\` 子目录，而你的数据文件直接位于 `%LOCALAPPDATA%\hermes` 中。重新安装仅替换 `hermes-agent\` 检出，因此你的数据会保留——但由于两者共享一个根目录，**不要** 如果你想保留数据，则不要 `Remove-Item -Recurse %LOCALAPPDATA%\hermes`；而是删除 `hermes-agent\` 子目录。你的数据目录在结构上与 Linux 的 `~/.hermes` 相同，因此你可以在机器之间镜像。

**覆盖 `HERMES_HOME`：** 设置环境变量指向不同的数据目录（例如 `%USERPROFILE%\.hermes` 以匹配 Linux/WSL 布局）。与 Linux 上工作方式相同。

## 浏览器工具

浏览器工具使用 `agent-browser`（一个 Node 辅助程序）来驱动 Chromium。在 Windows 上：

- 安装程序通过 npm 将 `agent-browser` 放在 PATH 上。
- `shutil.which("agent-browser", path=...)` 会自动拾取 `.cmd` 填充——`CreateProcessW` 无法执行没有扩展名的 shebang，因此 Hermes 总是解析到 `.CMD` 包装器。不要手动调用 shebang 脚本；始终通过 `.cmd`。
- Playwright Chromium 在首次运行时自动安装（`npx playwright install chromium`）。如果安装失败，`hermes doctor` 会显示它并附带修复提示。

## 在 Windows 上运行 Hermes——实用说明

### 安装后的 PATH

安装程序通过 `[Environment]::SetEnvironmentVariable` 将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到你的 **用户 PATH**。现有终端不会获取此更改——请在安装后打开一个新的 PowerShell 窗口（或 Windows 终端标签页）。关闭并重新打开，不要手动执行 `$env:PATH += …`，除非你知道自己在做什么。

验证：

```powershell
Get-Command hermes        # 应打印 C:\Users\<你>\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe
hermes --version
```

### 环境变量

Hermes 同时识别 `$env:X`（进程范围）和用户环境变量（永久，在系统属性 → 环境变量中设置）。在 `%LOCALAPPDATA%\hermes\.env`（你的 `HERMES_HOME`）中设置 API 密钥是正常路径——与 Linux 相同：

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

除非你特别希望每个 Windows 进程都能看到它们，否则不要将密钥放在用户环境变量中（这并不是你想要的）。

### Windows 特定的环境变量

这些仅影响原生 Windows 安装：

| 变量 | 效果 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 发现。指向任何 bash——完整的 Git-for-Windows、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序会自动设置此变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设置为 `1` 以禁用 UTF-8 stdio 填充并回退到区域设置代码页。用于定位编码错误。 |
| `EDITOR` / `VISUAL` | 用于 `/edit` 和 `Ctrl-X Ctrl-E` 的编辑器。如果两者都未设置，Hermes 默认为 `notepad`。 |

## 卸载

从 PowerShell 执行：

```powershell
hermes uninstall
```

这是干净路径——移除 schtasks 条目、启动文件夹快捷方式、`hermes.cmd` 填充、删除 `%LOCALAPPDATA%\hermes\hermes-agent\`，并修剪用户 PATH。它保留 `%LOCALAPPDATA%\hermes\` 的其余部分（你的配置、认证、技能、会话、日志）不变，以防你重新安装。

要彻底清除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
# 如果你曾经使用过，还要移除旧的 CLI/WSL 数据目录：
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
```

`hermes uninstall` CLI 子命令也处理 schtasks 条目以不同任务名称注册的情况（较旧的安装）——它通过安装路径而不是硬编码的任务名称进行搜索。

## 进程管理内部

这是背景材料——除非你正在调试“它杀死了自己”的奇怪现象，否则跳过。

在 Linux 和 macOS 上，POSIX 习惯 `os.kill(pid, 0)` 是一个无操作权限检查：“这个 PID 还活着吗？我能信号它吗？”在 Windows 上，Python 的 `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`——它们在整数值 0 处冲突——并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由它，该函数将 Ctrl+C 广播到包含目标 PID 的 **整个控制台进程组**。这是 [bpo-14484](https://bugs.python.org/issue14484)，自 2012 年以来一直开放。它不会被修复，因为更改它会破坏依赖于当前行为的脚本。

后果：任何在 Windows 上通过 `os.kill(pid, 0)` 来“检查此 PID 是否存活”的代码路径都会静默地杀死目标。Hermes 已将每个这样的位置（跨 11 个文件的 14 处）迁移到 `gateway.status._pid_exists()`，后者使用 `psutil.pid_exists()`（在 Windows 上，后者使用 `OpenProcess + GetExitCodeProcess`——无信号）。如果你正在编写插件或补丁，请直接使用 `psutil.pid_exists()` 或 `gateway.status._pid_exists()`——永远不要使用 `os.kill(pid, 0)`。

`scripts/check-windows-footguns.py` 在 CI 中强制执行此操作：任何新的 `os.kill(pid, 0)` 调用都会导致 `Windows footguns (blocking)` 检查失败，除非该行带有 `# windows-footgun: ok — <reason>` 标记。

## 常见陷阱

**安装后立即出现 `hermes: command not found`。**
打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH，但现有 shell 需要重新启动才能获取。在此期间，你可以运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`。

**运行工具时出现 `WinError 193: %1 is not a valid Win32 application`。**
你遇到了绕过 `.cmd` 填充的 shebang 脚本调用。Hermes 通过 `shutil.which(cmd, path=local_bin)` 解析命令，以便 PATHEXT 拾取 `.CMD`——如果你通过硬编码路径调用工具，请切换到 `.cmd` 变体（例如，`npx.cmd` 而非 `npx`）。

**`[scriptblock]::Create(...)` 失败，错误为 `The assignment expression is not valid`。**
你的 `install.ps1` 下载拾取了一个 UTF-8 BOM。`irm | iex` 形式会自动去除 BOM；`[scriptblock]::Create((irm ...))` 不会。请使用简单的 `irm | iex` 形式重新运行，或者手动下载脚本并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 不包含 BOM 地保存它。

**网关在重启后无法保持运行。**
检查 `hermes gateway status`——它合并了 schtasks 条目、启动文件夹快捷方式（如果使用）和实时 PID。如果 schtasks 已注册但未运行，组策略可能正在阻止 `ONLOGON` 触发器。运行 `schtasks /Query /TN HermesGateway /V /FO LIST` 查看任务的失败原因，或者通过卸载并重新安装（设置 `HERMES_GATEWAY_FORCE_STARTUP=1`）回退到启动文件夹路径。

**设置 `$env:EDITOR` 后 `/edit` 仍然无效。**
你仅在当前进程中设置了它；请关闭并重新打开 shell，或者在系统属性 → 环境变量中设置为用户范围。在新的 PowerShell 窗口中用 `echo $env:EDITOR` 验证。

**浏览器工具启动但工具超时。**
Chromium 在首次运行时自动安装。如果安装失败（GitHub 速率限制、Playwright CDN 故障），请运行 `hermes doctor`——它会显示缺失的 Chromium 并打印用于修复的确切 `npx playwright install chromium` 命令。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**
安装程序在 `%LOCALAPPDATA%\hermes\node` 处配置了 Node 22，但你的 PATH 可能首先指向一个较旧的系统 Node 18。要么将 Hermes 的 node 目录在 PATH 中提前，要么如果你不在其他地方使用 Node，则删除系统安装。

**中文 / 日文 / 阿拉伯文字符在 CLI 中显示为 `?`。**
UTF-8 stdio 填充未激活。检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否**未**设置（`Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8`）。如果它为空，并且你仍然看到 `?`，则控制台主机（非常旧的 `cmd.exe`）可能根本不支持 UTF-8——请切换到 Windows 终端。

**网关无法发送 Telegram 照片——“`BadRequest: payload contains invalid characters`”。**
这与 Windows 无关，但有时首先会在这里出现。通常意味着你的文件路径在 JSON 正文中包含未转义的反斜杠。Telegram 应该接收 Hermes 规范化的路径，而不是原始的 Windows 路径——如果你在自定义插件中看到此问题，请确保你传递的是 Hermes 提供的路径，而不是来自用户输入的 `str(Path(...))`。

**`git pull` 后出现“在其他机器上有效”的编码奇怪现象。**
如果你在 Windows 上使用非 UTF-8 编辑器（旧版 Windows 上的记事本、某些中文输入法）编辑了 Hermes 配置或技能，文件可能已保存为带 BOM 的格式。Hermes 在大多数配置读取中容忍 `utf-8-sig`，但折叠的 YAML 标量（`description: >`）内部的 BOM 会静默破坏 YAML 解析。请将文件重新保存为不带 BOM 的纯 UTF-8。

## 下一步

- **[安装](../getting-started/installation.md)**——完整的安装页面，包括 Linux/macOS/WSL2/Termux。
- **[Windows（WSL2）指南](./windows-wsl-quickstart.md)**——如果你想要 POSIX 语义或仪表板终端窗格。
- **[CLI 参考](../reference/cli-commands.md)**——每个 `hermes` 子命令。
- **[FAQ](../reference/faq.md)**——常见的非 Windows 特定问题。
- **[消息网关](./messaging/index.md)**——在 Windows 上运行 Telegram/Discord/Slack。