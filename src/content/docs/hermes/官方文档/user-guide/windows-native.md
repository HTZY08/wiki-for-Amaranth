--- frontmatter ---
---
title: "Windows (原生) 指南"
description: "在 Windows 10 / 11 上原生运行 Hermes Agent — 安装、特性矩阵、UTF-8 控制台、Git Bash、作为计划任务的网关、编辑器处理、PATH、卸载及常见问题"
sidebar_label: "Windows (原生)"
sidebar_position: 3
---

--- body ---
# Windows (原生) 指南

Hermes 可直接在 Windows 10 和 Windows 11 上原生运行——无需 WSL、Cygwin 或 Docker。本页是深度指南：哪些功能原生可用，哪些功能仅限 WSL，安装程序实际做了什么，以及你可能需要调整的 Windows 特定参数。

如果你只是想安装，只需使用[首页](/)或[安装页面](../getting-started/installation#windows-native-powershell)上的单行命令即可。当遇到意外情况时，请回到这里查阅。

:::tip 想要使用 WSL 吗？
如果你更喜欢真正的 POSIX 环境（用于仪表盘的内嵌终端、`fork` 语义、Linux 风格的文件监视器等），请参阅 **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)**。两者可以干净地共存：原生数据位于 `%LOCALAPPDATA%\hermes`，WSL 数据位于 `~/.hermes`。
:::

## 快速安装

打开 **PowerShell**（或 Windows Terminal）并运行：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序会安装到 `%LOCALAPPDATA%\hermes\` 并将 `hermes` 添加到你的**用户 PATH**——完成后请打开一个新的终端窗口。

**安装程序选项**（需要使用脚本块形式传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（用于测试 PR） |
| `-Commit` | 未设置 | 将安装固定到特定提交 SHA（覆盖 `-Branch`） |
| `-Tag` | 未设置 | 将安装固定到特定 git 标签（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过创建虚拟环境（高级用法——你自己管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码位置 |

安装程序会自动重试不稳定的 git 拉取操作，并剥离从任何下载的 `install.ps1` 有效负载中的 BOM，因此，在 HTTP 传输过程中拾取的 UTF-8 BOM 不会再破坏 `[scriptblock]::Create((irm ...))` 形式。

### 桌面安装程序（替代方案）

也提供了一个轻量级 GUI 安装程序——如果你更愿意双击一个 `.exe` 而不打开 PowerShell。下载 Hermes Desktop，运行安装程序，首次启动时 GUI 会在后台调用 `install.ps1` 来提供 Python（通过 `uv`）、Node、PortableGit 以及下面描述的其他依赖项。首次运行后，桌面应用程序和通过 PowerShell 安装的 `hermes` CLI 共享相同的 `%LOCALAPPDATA%\hermes\hermes-agent` 安装和 `%LOCALAPPDATA%\hermes` 数据目录——可以在 GUI 和 CLI 之间自由切换。

当你希望获得熟悉的 Windows 安装体验，或者将 Hermes 交给非开发者使用时，请使用桌面安装程序；当你已经处于终端中时，请使用 PowerShell 单行命令。

### 依赖引导（`dep_ensure`）

首次启动时（以及在检测到缺失工具时按需），Hermes 会运行一个小的 Python 引导程序——`hermes_cli/dep_ensure.py`——它检查并惰性安装所需的非 Python 依赖项。在 Windows 上，相关的依赖项如下：

| 依赖项 | Hermes 为何需要它 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，以及为会话内克隆提供 `git`。在安装时预置，而非由 `dep_ensure` 提供。 |
| **Node.js 22** | 需要用于浏览器工具（`agent-browser`）、TUI 的 Web 桥接和 WhatsApp 桥接。 |
| **ffmpeg** | 用于 TTS / 语音消息的音频格式转换。 |
| **ripgrep** | 快速文件搜索——如果不可用则回退到 `grep`。 |
| **npm packages** | `agent-browser`、Playwright Chromium 以及每个工具集的 Node 依赖项在首次使用浏览器工具时安装一次。 |

每个依赖项都有一个 `shutil.which(...)` 风格的检查；如果二进制文件缺失且运行是交互式的，`dep_ensure` 会提供安装选项（将实际安装逻辑委派给 `scripts\install.ps1 -ensure <dep>`）。非交互式运行（网关、cron、无头桌面启动）会跳过提示，而是明确显示 `此功能需要 <dep>` 错误。

## 安装程序实际做了什么

按顺序从头到尾：

1. **引导 `uv`** — Astral 的快速 Python 管理器。安装到 `%USERPROFILE%\.local\bin`。
2. **通过 `uv` 安装 Python 3.11**。无需现有 Python。
3. **安装 Node.js 22**（如果可用则使用 winget，否则将便携式 Node tarball 解压到 `%LOCALAPPDATA%\hermes\node`）。用于浏览器工具和 WhatsApp 桥接。
4. **安装便携式 Git** — 如果 `git` 已在 PATH 上，安装程序将使用它；否则，它会将精简且自包含的 **PortableGit**（约 45 MB，来自官方的 `git-for-windows` 发行版）下载到 `%LOCALAPPDATA%\hermes\git`。无需管理员权限，无需 Windows 安装程序注册表，不会干扰系统上的其他任何内容。
5. **将仓库克隆**到 `%LOCALAPPDATA%\hermes\hermes-agent` 并在其中创建一个虚拟环境。
6. **分层的 `uv pip install`** — 首先尝试 `.[all]`，如果某个 `git+https` 依赖因 GitHub 速率限制而失败，则逐步回退到较小的集合（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。防止“单个依赖失败就导致裸安装”的故障模式。
7. **自动安装消息传递 SDK**，依据 `.env` 中的键——如果存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED`，则运行 `python -m ensurepip --upgrade` 和针对性的 `pip install` 调用，以便每个平台的 SDK 实际上可以被导入。
8. **设置 `HERMES_GIT_BASH_PATH`** 为解析出的 `bash.exe`，以便 Hermes 在新的 shell 中确定性地找到它。
9. **将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到用户 PATH 并设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`** — 在打开新的终端后，`hermes` 命令变得可用（并指向你的数据目录）。
10. **运行 `hermes setup`** — 正常的首次运行向导（模型、提供商、工具集）。使用 `-SkipSetup` 跳过。

:::tip 在 Windows 上跳过提供商搜索
在 Windows 上，每个工具（Firecrawl、FAL、Browser Use、OpenAI TTS）的 API 密钥设置是获得有用代理（Agent）过程中摩擦最大的部分。一个 [Nous Portal](/user-guide/features/tool-gateway) 订阅通过一次 OAuth 登录涵盖了模型**和**所有这些工具。安装程序完成后，运行 `hermes setup --portal` 来配置一切。
:::

## 特性矩阵

除了仪表盘的嵌入式终端窗格外，其余所有功能都能在 Windows 上原生运行。

| 特性 | 原生 Windows | WSL2 |
|---|---|---|
| CLI（`hermes chat`、`hermes setup`、`hermes gateway`……） | ✓ | ✓ |
| 交互式 TUI（`hermes --tui`） | ✓ | ✓ |
| 消息网关（Telegram、Discord、Slack、WhatsApp，15+ 平台） | ✓ | ✓ |
| Cron 调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 使用 Chromium） | ✓ | ✓ |
| MCP 服务器（stdio 和 HTTP） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓（通过 WSL 网络） |
| Web 仪表盘（会话、作业、指标、配置） | ✓ | ✓ |
| 仪表盘 `/chat` 嵌入式终端窗格 | ✗（需要 POSIX PTY） | ✓ |
| 登录时自动启动 | ✓（schtasks） | ✓（systemd） |

仪表盘的 `/chat` 标签页通过 POSIX PTY（`ptyprocess`）嵌入了一个真正的终端。原生 Windows 没有等效的原语；Python 的 `pywinpty` / Windows ConPTY 可以工作，但属于单独的实现——视为未来工作。**仪表盘的其余部分原生工作**——只有那个标签页会显示“请使用 WSL2 实现此功能”的横幅。

## Hermes 如何在 Windows 上运行 shell 命令

Hermes 的终端工具通过 **Git Bash** 运行命令，这与 Claude Code 使用的策略相同。这绕过了 POSIX 与 Windows 之间的差距，而无需重写每个工具。

`bash.exe` 的解析顺序：

1. 如果设置了环境变量 `HERMES_GIT_BASH_PATH`，则使用该值。
2. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`（安装程序管理的便携 Git）。
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（较旧的 Git-for-Windows 布局）。
4. 系统 Git-for-Windows 安装（`%ProgramFiles%\Git\bin\bash.exe` 等）。
5. 最后，MSYS2、Cygwin 或 PATH 上的任何 `bash.exe` 作为后备。

安装程序明确设置了 `HERMES_GIT_BASH_PATH`，以便新的 PowerShell 会话无需重新发现。如果你希望 Hermes 使用特定的 bash（例如系统 Git Bash 或通过符号链接的 WSL 托管的 bash），可以覆盖该变量。

**陷阱：** MinGit 的布局与完整的 Git-for-Windows 安装程序不同——bash 位于 `usr\bin\bash.exe`，而不是 `bin\bash.exe`。Hermes 会检查两者。如果你手动解压 MinGit zip 文件，请确保选择**非 busybox** 变体（`MinGit-*-64-bit.zip`，而不是 `MinGit-*-busybox*.zip`）——busybox 构建版提供 `ash` 而不是 `bash`，并且大多数 coreutils 缺失。

## Windows 上的 UTF-8 控制台

Python 在 Windows 上的默认 stdio 使用控制台的活动代码页（通常是 cp1252 或 cp437）。Hermes 的横幅、斜杠命令列表、工具馈送、Rich 面板和技能描述都包含 Unicode。如果不加干预，其中任何一个都会崩溃并显示 `UnicodeEncodeError: 'charmap' codec can't encode character…`。

修复方法在 `hermes_cli/stdio.py::configure_windows_stdio()` 中，该函数在每个入口点（`cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期被调用。它：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 将控制台代码页切换为 CP_UTF8（65001）。
2. 将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8，并使用 `errors='replace'`。
3. 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`（通过 `setdefault`，因此显式的用户值优先），以便子 Python 进程继承 UTF-8。
4. 如果 `EDITOR` 和 `VISUAL` 都未设置，则设置 `EDITOR=notepad`（参见下面的编辑器部分）。

幂等。在非 Windows 系统上无操作。

**退出：** 在环境中设置 `HERMES_DISABLE_WINDOWS_UTF8=1` 将回退到传统的 cp1252 stdio 路径。用于定位编码错误；在正常操作中不太可能需要。

## 编辑器（`Ctrl-X Ctrl-E`、`/edit`）

在 #21561 之前，在 Windows 上按下 `Ctrl-X Ctrl-E` 或输入 `/edit` 会静默地不执行任何操作。prompt_toolkit 有一个硬编码的 POSIX 绝对路径后备列表（`/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi`……），在 Windows 上永远无法解析——即使安装了完整的 Git for Windows。

Hermes 的 Windows stdio 填充现在默认设置 `EDITOR=notepad`。记事本随每个 Windows 安装一起提供，并且可以作为阻塞编辑器使用——`subprocess.call(["notepad", file])` 会阻塞直到窗口关闭。

**用户覆盖仍然优先**（它们在使用 setdefault 之前被检查）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 上的 `--wait` 标志至关重要——如果没有它，编辑器会立即返回，Hermes 将收到一个空缓冲区。

永久设置到你的 PowerShell 配置文件中：

```powershell
# 在 $PROFILE 中
$env:EDITOR = "code --wait"
```

或者在系统设置中作为用户环境变量设置，这样每个新的 shell 都会自动拾取。

## CLI 中使用 `Ctrl+Enter` 换行

Windows Terminal 将 `Ctrl+Enter` 作为专用按键序列传递。Hermes 将其绑定为“插入换行”，以便你可以在 CLI 中编写多行提示，而无需回退到 `Esc` 然后 `Enter`。在 Windows Terminal、VS Code 集成终端以及任何遵循 VT 转义序列的现代 Windows 控制台宿主中均可工作。

在旧版 `cmd.exe` 控制台中，`Ctrl+Enter` 会退化为普通 `Enter`——请改用 `Esc Enter`，或者升级到 Windows Terminal（免费，Windows 11 默认安装）。

## 在 Windows 登录时运行网关

`hermes gateway install` 在 Windows 上使用**计划任务**，并附带启动文件夹回退方案——无需管理员权限。

### 安装

```powershell
hermes gateway install
```

底层发生的过程：

1. `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway` — 注册一个在登录时以标准（非提升）权限运行的任务。不会出现 UAC 提示。
2. 如果 schtasks 被组策略阻止，则回退到在 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` 中创建一个 `start /min cmd.exe /d /c <wrapper>` 快捷方式。效果相同，但稍显粗糙。
3. 通过 `pythonw.exe` **分离式**地启动网关——而不是 `python.exe`。`pythonw.exe` 没有附加控制台，这使其免受来自同级进程的 `CTRL_C_EVENT` 广播的影响（这是一个真实问题，曾经在你 Ctrl+C 同一进程组中的任何内容时杀死网关）。

启动时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # 合并视图：schtasks + Startup 文件夹 + 运行中的 PID
hermes gateway start       # 立即启动计划任务
hermes gateway stop        # 优雅的 SIGTERM 等效（通过 psutil 的 TerminateProcess）
hermes gateway restart
hermes gateway uninstall   # 移除 schtasks 条目、Startup 快捷方式、pid 文件
```

`hermes gateway status` 是幂等的——连续调用一千次也绝不会意外杀死网关。（在 PR #21561 之前，它通过 `os.kill(pid, 0)` 在 C 级别与 `CTRL_C_EVENT` 冲突而静默执行杀死操作——如果你关心这个故事，请参阅下面的“进程管理内部”部分。）

### 为什么不使用 Windows 服务？

服务需要管理员权限才能安装，并将网关的生命周期绑定到机器启动，而不是用户登录。典型的 Hermes 用户希望：登录 → 网关可用，注销 → 网关停止。计划任务正好做到这一点，无需提升权限。如果你真的想要一个服务，请手动使用 `nssm` 或 `sc create`——但你可能不需要。

## 数据布局

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出 + 虚拟环境。`venv\Scripts\hermes.exe` 是添加到用户 PATH 的命令。可以安全地 `Remove-Item -Recurse` 并重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit（仅当安装程序提供了它时）。 |
| `%LOCALAPPDATA%\hermes\node\` | 便携式 Node.js（仅当安装程序提供了它时）。 |
| `%LOCALAPPDATA%\hermes\bin\` | Hermes 管理的 `uv.exe`（它用于更新的 Python 管理器）。 |
| `%LOCALAPPDATA%\hermes\`（根目录） | 你的配置、认证、技能、会话、日志（`config.yaml`、`.env`、`skills\`、`sessions\`、`logs\`……）。**在重新安装后保持不变。** |

在原生 Windows 上，安装程序设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`，因此你的数据和可丢弃的安装位于**同一** `%LOCALAPPDATA%\hermes` 根目录下：安装/运行时是 `hermes-agent\`、`git\`、`node\` 和 `bin\` 子目录，而你的数据文件直接位于 `%LOCALAPPDATA%\hermes` 中。重新安装仅替换 `hermes-agent\` 检出，因此你的数据得以保留——但由于两者共享一个根目录，如果你希望保留数据，请**不要** `Remove-Item -Recurse %LOCALAPPDATA%\hermes`；而是删除 `hermes-agent\` 子目录。你的数据目录在结构上与 Linux 的 `~/.hermes` 完全相同，因此你可以在机器之间镜像它。

**覆盖 `HERMES_HOME`：** 设置环境变量指向不同的数据目录（例如 `%USERPROFILE%\.hermes` 以匹配 Linux/WSL 布局）。工作方式与 Linux 上相同。

## 浏览器工具

浏览器工具使用 `agent-browser`（一个 Node 辅助工具）来驱动 Chromium。在 Windows 上：

- 安装程序通过 npm 将 `agent-browser` 放到 PATH 上。
- `shutil.which("agent-browser", path=...)` 会自动拾取 `.cmd` 填充程序——`CreateProcessW` 无法执行没有扩展名的 shebang，因此 Hermes 总是解析到 `.CMD` 包装器。不要手动调用 shebang 脚本；始终使用 `.cmd`。
- Playwright Chromium 在首次运行时自动安装（`npx playwright install chromium`）。如果安装失败，`hermes doctor` 会显示它并附带修复提示。

## 在 Windows 上运行 Hermes — 实用说明

### 安装后的 PATH

安装程序通过 `[Environment]::SetEnvironmentVariable` 将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到你的**用户 PATH**。现有终端不会拾取此更改——安装后请打开一个新的 PowerShell 窗口（或 Windows Terminal 选项卡）。关闭并重新打开，不要手动使用 `$env:PATH += …`，除非你清楚自己在做什么。

验证：

```powershell
Get-Command hermes        # 应打印 C:\Users\<你>\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe
hermes --version
```

### 环境变量

Hermes 同时遵循 `$env:X`（进程作用域）和用户环境变量（永久，在系统属性 → 环境变量中设置）。在 `%LOCALAPPDATA%\hermes\.env`（你的 `HERMES_HOME`）中设置 API 密钥是正常方式——与 Linux 相同：

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

不要将秘密放在用户环境变量中，除非你特别希望每个 Windows 进程都能看到它们（这通常不是你想要的）。

### Windows 特定的环境变量

这些仅影响原生 Windows 安装：

| 变量 | 效果 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 发现。指向任何 bash——完整的 Git-for-Windows、通过符号链接的 WSL bash、MSYS2、Cygwin。安装程序会自动设置此变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设置为 `1` 以禁用 UTF-8 stdio 填充并回退到区域设置代码页。用于定位编码错误。 |
| `EDITOR` / `VISUAL` | 用于 `/edit` 和 `Ctrl-X Ctrl-E` 的编辑器。如果两者都未设置，Hermes 默认使用 `notepad`。 |

## 卸载

从 PowerShell 中：

```powershell
hermes uninstall
```

这是干净的做法——移除 schtasks 条目、Startup 文件夹快捷方式、`hermes.cmd` 填充程序，删除 `%LOCALAPPDATA%\hermes\hermes-agent\`，并修剪用户 PATH。它会保留 `%LOCALAPPDATA%\hermes\` 的其余部分（你的配置、认证、技能、会话、日志），以防你会重新安装。

要彻底删除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
# 如果你曾经使用过旧的 CLI/WSL 数据目录，也将其删除：
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
```

`hermes uninstall` CLI 子命令也处理 schtasks 条目以不同任务名称注册的情况（旧安装）——它按安装路径搜索，而不是按硬编码的任务名称。

## 进程管理内部

这是背景资料——除非你在调试“自己杀死自己”的奇怪现象，否则可以跳过。

在 Linux 和 macOS 上，POSIX 惯用法 `os.kill(pid, 0)` 是一种无操作权限检查：“这个 PID 是否存活，我能向它发送信号吗？”在 Windows 上，Python 的 `os.kill` 将 `sig=0` 映射到 `CTRL_C_EVENT`——它们在整数值 0 上冲突——并通过 `GenerateConsoleCtrlEvent(0, pid)` 路由它，该函数向包含目标 PID 的**整个控制台进程组**广播 Ctrl+C。这是 [bpo-14484](https://bugs.python.org/issue14484)，自 2012 年以来一直开放。它不会被修复，因为更改它会破坏依赖当前行为的脚本。

后果：任何在 Windows 上通过 `os.kill(pid, 0)` 执行“检查此 PID 是否存活”的代码路径都会静默杀死目标。Hermes 将所有此类位置（跨越 11 个文件共 14 处）迁移到 `gateway.status._pid_exists()`，后者使用 `psutil.pid_exists()`（在 Windows 上依次使用 `OpenProcess + GetExitCodeProcess`——不发送信号）。如果你在编写插件或补丁，请直接使用 `psutil.pid_exists()` 或 `gateway.status._pid_exists()`——永远不要使用 `os.kill(pid, 0)`。

`scripts/check-windows-footguns.py` 在 CI 中强制执行此规定：任何新的 `os.kill(pid, 0)` 调用都会导致 `Windows footguns (blocking)` 检查失败，除非该行带有 `# windows-footgun: ok — <reason>` 标记。

## 常见问题

**安装后立即出现 `hermes: command not found`。**
打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH，但现有 shell 需要重新启动才能拾取。在此期间，你可以运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`。

**运行工具时出现 `WinError 193: %1 is not a valid Win32 application`。**
你遇到了绕过 `.cmd` 填充程序的 shebang 脚本调用。Hermes 通过 `shutil.which(cmd, path=local_bin)` 解析命令，以便 PATHEXT 拾取 `.CMD`——如果你通过硬编码路径调用工具，请改用 `.cmd` 变体（例如 `npx.cmd`，而不是 `npx`）。

**`[scriptblock]::Create(...)` 失败并显示 `The assignment expression is not valid`。**
你的 `install.ps1` 下载可能拾取了 UTF-8 BOM。`irm | iex` 形式会自动剥离 BOM；`[scriptblock]::Create((irm ...))` 不会。使用简单的 `irm | iex` 形式重新运行，或手动下载脚本并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 保存为不带 BOM 的文件。

**网关在重启后无法保持运行。**
检查 `hermes gateway status`——它合并了 schtasks 条目、Startup 文件夹快捷方式（如果使用）和活动 PID。如果 schtasks 已注册但未运行，组策略可能阻止了 `ONLOGON` 触发器。运行 `schtasks /Query /TN HermesGateway /V /FO LIST` 查看任务的失败原因，或者通过设置 `HERMES_GATEWAY_FORCE_STARTUP=1` 并卸载重装来使用 Startup 文件夹路径。

**设置 `$env:EDITOR` 后 `/edit` 仍然不起作用。**
你只在当前进程中设置了它；关闭并重新打开 shell，或者在系统属性 → 环境变量中将其设置为用户作用域。在新的 PowerShell 窗口中用 `echo $env:EDITOR` 验证。

**浏览器工具启动但工具超时。**
Chromium 在首次运行时自动安装。如果安装失败（GitHub 速率限制、Playwright CDN 问题），运行 `hermes doctor`——它会显示缺失的 Chromium 并打印用于修复的确切 `npx playwright install chromium` 命令。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**
安装程序在 `%LOCALAPPDATA%\hermes\node` 处提供 Node 22，但你的 PATH 可能首先有一个较老的系统 Node 18。要么将 Hermes 的 node 目录移到 PATH 的更前面，要么删除系统安装（如果你不在其他地方使用 Node）。

**中文 / 日文 / 阿拉伯文字符在 CLI 中显示为 `?`。**
UTF-8 stdio 填充未激活。检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否**未**设置（`Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8`）。如果它是空的而你仍然看到 `?`，则控制台宿主（非常旧的 `cmd.exe`）可能根本不支持 UTF-8——请切换到 Windows Terminal。

**网关无法发送 Telegram 照片——“`BadRequest: payload contains invalid characters`”。**
这与 Windows 无关，但有时首先在那里出现。通常意味着你的文件路径在 JSON 正文中包含未转义的反斜杠。Telegram 应该接收 Hermes 规范化的路径，而不是原始的 Windows 路径——如果你在自定义插件中看到此问题，请确保你传递的是 Hermes 提供的路径，而不是来自用户输入的 `str(Path(...))`。

**`git pull` 后出现“在我的其他机器上能工作”的编码怪异现象。**
如果你在 Windows 上使用非 UTF-8 编辑器（旧版 Windows 上的记事本、某些中文输入法）编辑了 Hermes 配置或技能，文件可能已使用 BOM 保存。Hermes 在大多数配置读取时容忍 `utf-8-sig`，但折叠的 YAML 标量（`description: >`）中的 BOM 会静默破坏 YAML 解析。将文件重新保存为纯 UTF-8（无 BOM）。

## 下一步去哪里

- **[安装](../getting-started/installation.md)** — 完整的安装页面，包括 Linux/macOS/WSL2/Termux。
- **[Windows (WSL2) 指南](./windows-wsl-quickstart.md)** — 如果你想要 POSIX 语义或仪表盘终端窗格。
- **[CLI 参考](../reference/cli-commands.md)** — 每个 `hermes` 子命令。
- **[常见问题](../reference/faq.md)** — 非 Windows 特定的常见问题。
- **[消息网关](./messaging/index.md)** — 在 Windows 上运行 Telegram/Discord/Slack。