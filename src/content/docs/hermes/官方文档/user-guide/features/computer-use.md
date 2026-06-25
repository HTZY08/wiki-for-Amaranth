---
title: Computer Use
---

title: 计算机使用（Computer Use）
sidebar_position: 16
---

--- body ---
# 计算机使用（Computer Use）

Hermes Agent 可以驱动你的桌面——在 **macOS、Windows 和 Linux** 的 **后台** 进行点击、输入、滚动和拖拽。你的光标不会移动，键盘焦点不会改变，虚拟桌面 / 空间不会切换。你和代理（Agent）在同一台机器上协同工作。

与大多数计算机使用集成不同，此功能适用于 **任何支持工具（Tool）的模型**——Claude、GPT、Gemini，或本地兼容 OpenAI 的端点上的开放模型。无需担心 Anthropic 原生模式。

## 工作原理

`computer_use` 工具集通过 stdio 上的 MCP 与 [`cua-driver`](https://github.com/trycua/cua) 通信，这是一个开源的背景计算机使用驱动程序。每个平台在底层使用适当的无障碍 + 输入堆栈：

| 平台 | 无障碍树（Accessibility tree） | 输入分发（Input dispatch） |
|---|---|---|
| macOS | AX（私有 SkyLight SPI） | `SLPSPostEventRecordTo` — 按 pid 限定，无光标跳动 |
| Windows | UIAutomation | `SendInput` + `PostMessage` — 不抢夺焦点 |
| Linux | AT-SPI（X11 + Wayland） | XTest（X11）/ 虚拟键盘（Wayland） |

所有平台的结果相同：代理可以读取任何可见窗口的无障碍树，并发布合成事件，而无需将窗口移到前台、切换虚拟桌面或移动真实的操作系统光标。

关于底层约定——*为什么* 后台模式很重要、无前台不变量、点击分发内部机制——请参见 **[cua.ai/docs/explanation/the-no-foreground-contract](https://cua.ai/docs/explanation/the-no-foreground-contract)**。

## 启用方式

选择最方便的方式——两者都运行相同的上游安装程序：

**选项 1：专用 CLI 命令（最直接）。**

```
hermes computer-use install
```

这将获取并运行上游的 cua-driver 安装程序——macOS/Linux 上为 `install.sh`，Windows 上为 `install.ps1`。使用 `hermes computer-use status` 验证安装。

**选项 2：交互式启用工具集。**

1. 运行 `hermes tools`，选择 `🖱️  Computer Use (macOS/Windows/Linux)`。
2. 设置会运行上游安装程序（与选项 1 相同）。

安装后，无论采取哪种方式，都需要授予平台相应的先决条件：

| 平台 | 先决条件 |
|---|---|
| **macOS** | 系统设置 → 隐私与安全性 → **辅助功能** + **屏幕录制** → 允许你的终端（或 Hermes 应用）。`hermes computer-use doctor` 会告诉你缺少哪个权限。 |
| **Windows** | 安装时无需任何操作。如果你通过 SSH（而非 RDP / 控制台）进行驱动，则需要自动启动模式——参见 [cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh) 了解 Session 0 ↔ Session 1+ 代理。 |
| **Linux** | 一个可访问的显示服务器：X11 需要设置 `DISPLAY`，或设置 `XDG_SESSION_TYPE=wayland`。Wayland 会话需要 XWayland 桥接进行捕获。AT-SPI 必须运行（GNOME/KDE/Xfce 上默认开启）。 |

然后，使用启用了工具集的会话启动：

```
hermes -t computer_use chat
```

或者将 `computer_use` 添加到 `~/.hermes/config.yaml` 中已启用的工具集列表中。

## `hermes computer-use doctor` —— 你的首要排查工具

`hermes computer-use doctor` 运行 cua-driver 的结构化 `health_report` MCP 工具，并打印每个检查项的矩阵。这是找出 *为什么* 某个操作不起作用的最快方法。

```
$ hermes computer-use doctor
⚠️  cua-driver 0.5.8 on darwin — degraded
  ✅ binary_version: cua-driver 0.5.8
  ✅ platform_supported: macOS 26.4.1 (arm64)
  ✅ session_active: MCP session is active.
  ❌ bundle_identity: Process has no CFBundleIdentifier.
      → Run the binary inside CuaDriver.app so TCC grants attribute correctly.
  ✅ tcc_accessibility: Accessibility is granted.
  ✅ tcc_screen_recording: Screen Recording is granted.
  ✅ ax_capability: AX is trusted and reachable.
  ✅ screen_capture_capability: ScreenCaptureKit reachable; 1 display(s) shareable.
```

- **退出码 0** 当整体状态为 `ok` 时——一切已就绪。
- **退出码 1** 当状态为 `degraded` 或 `failed` 时——至少一项检查失败；每个失败项旁边的提示告诉你需要修复什么。
- **退出码 2** 当 cua-driver 二进制文件本身不可达时。

有用的选项：

- `--include CHECK` —— 仅运行列出的检查项（可重复以指定多个）
- `--skip CHECK` —— 跳过某个检查项（优先级高于 `--include`）
- `--json` —— 输出原始的载荷结构，与 `tools/call health_report` MCP 响应格式相同

检查矩阵是平台感知的：`bundle_identity` / `tcc_*` 在 Windows + Linux 上会被 `skip`，因为这些概念不适用。`ax_capability` 在 macOS 上检查 AX，在 Windows 上检查 UIA，在 Linux 上检查 AT-SPI——当无法访问时，每个检查项都会给出正确的诊断提示。

## 代理光标与会话

当代理执行操作时，你会看到一个 **带色调的叠加光标** 在屏幕上移动到每个点击/输入/滚动的位置。真实的操作系统光标永远不会移动——这个叠加光标是一个视觉提示，表明“代理正在此处操作”。每个 Hermes 运行都会声明自己的 cua-driver **会话 ID**（类似于 `hermes-3a7b9c14d2e8`）；光标的身份与该会话绑定，因此并发运行 / 子代理各自拥有自己的光标，不会相互干扰。

使用 `cua-driver` 的 CLI 选项或运行时 `set_agent_cursor_style` MCP 工具来调整光标——参见 [cua.ai/docs/how-to-guides/driver/personalize-cursor](https://cua.ai/docs/how-to-guides/driver/personalize-cursor) 了解完整菜单（内置的 `arrow` 与 `teardrop` 轮廓、通过 `--cursor-icon` 自定义 SVG / PNG / ICO、运行时渐变颜色、发光光晕）。

## 深入探索——cua-driver 技能包

Hermes 有意将其技能（`skills/computer-use/SKILL.md`）专注于 Hermes 端的 `computer_use` 动作词汇表——这是代理加载的唯一真实来源。对于更深入的内容——平台特定深度剖析、录制语义、浏览器页面交互——将你的代理工具指向 cua-driver 团队直接发布和维护的技能包：

```
cua-driver skills install
```

这将把技能包符号链接到你的代理工具的技能目录中。运行后，代理可以访问以下内容：

| 文件 | 主题 |
|---|---|
| `SKILL.md` | 跨平台核心（快照不变量、无前台约定、点击分发、AX 树机制） |
| `MACOS.md` | macOS 特定内容：无前台约定、AXMenuBar 导航、SkyLight 点击分发、Apple Events JS 桥接 |
| `WINDOWS.md` | Windows 特定内容：UIA 树、UWP / `ApplicationFrameHost` 托管、Session 0 隔离、自动启动模式 |
| `LINUX.md` | Linux 特定内容：AT-SPI 树、X11 / Wayland、终端仿真器检测 |
| `RECORDING.md` | 轨迹 + 视频录制语义 |
| `WEB_APPS.md` | 浏览器页面交互技巧 |
| `TESTS.md` | 按轨迹回放工作流 |

这些是 **平台深度剖析，而非 Hermes 技能的重复**——当代理报告“在 Windows 上，我的点击落在了错误元素上”时，它会读取 `WINDOWS.md` 以获取 UIA / UWP 上下文，从而解释原因以及应该如何调整。

`cua-driver skills status` 显示已安装的内容以及它链接到了哪些代理工具中。目前，自动检测列表涵盖 Claude Code、Codex、OpenCode、OpenClaw 和 Antigravity；**Hermes 的自动检测计划作为 `trycua/cua` 的后续跟进**——在此之前，运行一次 `cua-driver skills install` 并将你的代理工具指向生成的 `~/.cua-driver/skills/cua-driver` 目录（或将其符号链接到你常用的技能空间）。

## 快速示例

用户提示：*“找到我最新来自 Stripe 的邮件，并总结他们希望我做什么。”*

代理的计划（在 macOS / Windows / Linux 上格式相同——模型会替换平台惯用的快捷键和应用程序名称）：

1. `computer_use(action="capture", mode="som", app="Mail")` —— 获取邮件应用的截图，每个侧边栏项、工具栏按钮和消息行都带有编号。
2. `computer_use(action="click", element=14)` —— 点击搜索字段。
3. `computer_use(action="type", text="from:stripe")`
4. `computer_use(action="key", keys="return", capture_after=True)` —— 提交并获取新截图。
5. 点击顶部结果，阅读正文，总结。

在此期间，你的光标会停留在你离开的位置，邮件应用永远不会进入前台。

## 提供商兼容性

| 提供商 | 视觉能力？ | 有效？ | 备注 |
|---|---|---|---|
| Anthropic (Claude Sonnet/Opus 3+) | ✅ | ✅ | 整体最佳；支持 SOM + 原始坐标。 |
| OpenRouter (任意视觉模型) | ✅ | ✅ | 支持多部分工具消息。 |
| OpenAI (GPT-4+, GPT-5) | ✅ | ✅ | 同上。 |
| Google (Gemini 2+) | ✅ | ✅ | 同时支持工具调用和视觉能力。 |
| 本地 vLLM / LM Studio / Ollama (视觉模型) | ✅ | ✅ | 如果模型支持多部分工具内容。 |
| 纯文本模型 | ❌ | ✅ (降级) | 使用 `mode="ax"` 仅通过无障碍树运行。 |

截图作为 OpenAI 风格的 `image_url` 部分随工具结果内联发送。对于 Anthropic，适配器将其转换为原生的 `tool_result` 图像块。图像 MIME 类型来自 cua-driver 的显式 `mimeType` 字段（`image/png` 或 `image/jpeg`）——无需客户端魔术字节嗅探。

## 安全性

Hermes 应用多层护栏：

- 破坏性操作（click, type, drag, scroll, key, focus_app）需要批准——要么通过 CLI 对话框交互式批准，要么通过消息平台的批准按钮。
- 工具级别硬阻止的按键组合：清空废纸篓、强制删除、锁定屏幕、注销、强制注销。
- 硬阻止的输入模式：`curl | bash`，`sudo rm -rf /`，fork 炸弹等。
- 代理的系统提示明确告知：不得点击权限对话框、不得输入密码、不得遵循嵌入在截图中的指令。

如果你希望每个操作都经过确认，可以在 `~/.hermes/config.yaml` 中设置 `approvals.mode: manual`。

## Token 效率

截图的成本很高。Hermes 应用了四层优化：

- **截图淘汰策略**——Anthropic 适配器在上下文中仅保留最近的 3 张截图；较旧的截图会变成 `[screenshot removed to save context]` 占位符。
- **客户端压缩裁剪**——上下文压缩器检测多模态工具结果，并从旧结果中移除图像部分。
- **图像感知的 Token 估算**——每张图像计为约 1500 个 token（Anthropic 的固定费率），而不是基于 base64 字符长度。
- **服务器端上下文编辑（仅限 Anthropic）**——激活时，适配器通过 `context_management` 启用 `clear_tool_uses_20250919`，使 Anthropic 的 API 在服务器端清除旧的工具结果。

在 1568×900 显示屏上执行 20 次操作的会话通常消耗约 30K 个令牌的截图上下文，而不是约 600K 个。

## 限制

- **性能。** 后台模式比前台慢——无障碍路由的事件在 macOS 上需要约 5-20 毫秒，Windows UIA 上约 3-10 毫秒，Linux AT-SPI 上约 5-15 毫秒，而直接 HID 投递则更慢。对于代理速度的点击来说不明显；但如果你尝试录制速度跑，会明显感觉到。
- **无键盘密码输入。** `type` 对命令 shell 载荷有硬阻止模式；对于密码，请使用系统的自动填充功能（macOS 钥匙串 / Windows 凭据管理器 / GNOME 钥匙环 / KWallet）。
- **某些应用不暴露无障碍树。** Windows 上的现代 UWP 应用、Linux 上 Electron < 28 的应用，以及一些具有自定义绘图的 macOS 应用（Logic、Final Cut、某些游戏）拥有稀疏或空的无障碍树。如果树为空，则回退到像素坐标——或者完全跳过该任务。
- **Windows：无法从普通代理驱动提升的（管理员）窗口。** Windows UIPI（用户界面特权隔离）强制完整性级别边界：中等完整性进程（默认的 Hermes 代理）无法枚举高完整性（管理员）进程拥有的 UIA 树，也无法向其中注入鼠标输入。症状：`capture(mode='som')` 返回 0 个元素，`click(...)` 报告成功但实际上无任何操作，尽管截图正常渲染（GDI 捕获位于完整性检查之下）。键盘事件部分绕过 UIPI，因此 Tab / Enter 仍可导航提升的对话框。这是一个操作系统约束，而非 cua-driver 的错误——它影响所有 Windows 自动化栈。要驱动提升的窗口，请以高完整性运行 Hermes 代理本身（从提升的终端启动）；否则，目标为非提升的窗口。
- **平台特定的部署陷阱：**
  - **macOS** 使用私有的 SkyLight SPI。苹果可以在任何操作系统更新中更改它们。当安装的 cua-driver 版本早于经过测试的版本时，Hermes 会发出警告。
  - **Windows** SSH 会话在 **Session 0** 中运行，该会话没有交互式桌面。请在 RDP / 控制台会话内驱动 Hermes，或设置 cua-driver 的自动启动计划任务——[windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh) 提供了方法。
  - **Linux** 需要一个可访问的显示服务器。无头服务器需要 Xvfb（`Xvfb :99 -screen 0 1920x1080x24`）才能让 `computer_use` 捕获或注入事件。纯 Wayland 会话需要一个 XWayland 桥接用于屏幕捕获（cua-driver 的 Wayland 注入路径独立处理输入）。

对于不需要桌面开销（以及无需 TCC / Session 0 / X11 设置）的跨平台 GUI 自动化，`browser` 工具集使用真正的无头 Chromium，并且是仅需要 Web 任务时的正确答案。

## 配置

覆盖驱动程序二进制路径（测试 / CI / 本地构建）：

```
HERMES_CUA_DRIVER_CMD=/path/to/your/cua-driver
```

完全切换后端（用于测试）：

```
HERMES_COMPUTER_USE_BACKEND=noop   # 记录调用，无副作用
```

### 遥测

cua-driver 默认在上游启用了匿名使用遥测（PostHog）。**Hermes 为你禁用了它**——在每次 cua-driver 调用（MCP 后端、`status`、`doctor` 和安装）中，Hermes 会在驱动程序的环境中设置 `CUA_DRIVER_RS_TELEMETRY_ENABLED=0`。

要重新选择加入（让 cua-driver 使用其自己的默认设置并发送遥测数据），请在 `config.yaml` 中设置：

```yaml
computer_use:
  cua_telemetry: true   # 默认: false（遥测关闭）
```

当启用时，`hermes computer-use doctor` 报告 `telemetry: enabled`；当关闭时（默认），报告 `telemetry: disabled via CUA_DRIVER_RS_TELEMETRY_ENABLED`。

## 针对本地 cua-driver 构建进行测试

当你正在开发 cua-driver 本身——或者想测试一个未发布的修复时——将 Hermes 指向你从源代码构建的二进制文件，而不是已发布的版本。Hermes 使用 `shutil.which("cua-driver")` 解析驱动程序，并且 **不强制要求 `HERMES_CUA_DRIVER_VERSION`**，因此本地构建（报告为 `0.0.0-local-*`）会被原样接受。两种方法：

### 选项 A — `install-local`（构建并放入 PATH）

从你的 `trycua/cua` 检出目录中，运行上游本地安装程序。它将以 release 模式构建 Rust 后端，并将 `cua-driver` 放入生产安装程序使用的相同安装布局中，将其 bin 目录添加到你的 PATH：

```powershell
# Windows (PowerShell)，从 cua 仓库根目录运行
./libs/cua-driver/scripts/install-local.ps1 -NoAutoStart
```

```bash
# macOS / Linux，从 cua 仓库根目录运行（默认使用 debug 构建，不带 --release）
./libs/cua-driver/scripts/install-local.sh --release
```

- Windows 将构建结果放到 `%USERPROFILE%\.cua-driver\packages\…` 下，并将 `%LOCALAPPDATA%\Programs\Cua\cua-driver\bin`（已添加到用户 PATH）链接到它。macOS/Linux 将 `cua-driver` 符号链接到 `~/.local/bin`（可用 `--bin-dir <path>` 覆盖）。
- `-NoAutoStart` 跳过注册 `cua-driver-serve` 登录守护进程——Hermes 测试不需要它（参见备注）。

然后打开一个新的 shell（以便 PATH 更改可见），并确认：

```
cua-driver --version                 # 本地构建报告 0.0.0-local-release
# Windows:      (Get-Command cua-driver).Source
# macOS/Linux:  which cua-driver
```

### 选项 B — 将 Hermes 直接指向构建的二进制文件（最快循环）

完全跳过安装步骤：`cargo build` 并设置 `HERMES_CUA_DRIVER_CMD` 指向生成的二进制文件。最适合快速编辑/构建/测试。

```bash
cargo build -p cua-driver            # 添加 --release 进行 release 构建；从 libs/cua-driver/rust 运行
```

```
# Windows (.env)
HERMES_CUA_DRIVER_CMD=C:\path\to\cua\libs\cua-driver\rust\target\debug\cua-driver.exe
# macOS / Linux (.env)
HERMES_CUA_DRIVER_CMD=/path/to/cua/libs/cua-driver/rust/target/debug/cua-driver
```

### 确认 Hermes 正在使用你的构建

- `hermes computer-use status` 打印解析的二进制路径和版本。
- `hermes computer-use doctor` 确认二进制文件可达，并完整执行 MCP 路径的端到端测试。
- 在会话中，`computer_use(action="capture")` 会执行衍生出的 `cua-driver mcp` 子进程。

### 备注与陷阱

- **Hermes 通过 stdio 生成自己的 `cua-driver mcp` 子进程**——它 *不* 附加到长时间运行的 `cua-driver serve` 自启动守护进程或其命名管道。因此，计划任务 / LaunchAgent 对于测试并非必需（`-NoAutoStart` 可以)。自启动守护进程和 Windows UIAccess 工作器（`cua-driver-uia.exe`）仅对某些应用程序（例如 WPF）的前台安全输入重要；标准工具表面通过 stdio 子进程工作。在 Windows SSH 会话上，则需要自启动模式——请参见限制部分。
- **Windows 上的二进制文件锁定。** 正在运行的 `cua-driver-serve` 守护进程可能会持有 `cua-driver.exe` 并阻止重建时的覆盖。`install-local.ps1` 会自动将锁定的二进制文件重命名以腾出空间；如果你手动执行 `cargo build`（选项 B），请先使用 `cua-driver autostart disable`（或 `schtasks /End /TN cua-driver-serve`）停止它。
- **重建循环。** 编辑 cua-driver 源代码后，对于选项 A，重新运行 `install-local`（重建、重新部署、翻转 `current` 符号链接）；对于选项 B，只需重新 `cargo build`——两种方式都不需要更改 Hermes。
- **本地构建跳过版本检查。** Hermes 会在安装的 cua-driver 早于其针对操作系统测试的基线时发出警告，但会豁免 `0.0.0-local-*` 开发构建——因此你的本地构建永远不会触发该警告。

## 故障排除

**当出现任何问题时，首要操作：运行 `hermes computer-use doctor`。** 结构化的逐项检查矩阵会告诉你（以及任何帮你调试的代理）确切的问题所在。

以下是一些 doctor 无法捕获的特定失败模式：

**`computer_use backend unavailable: cua-driver is not installed`** ——
运行 `hermes computer-use install` 获取 cua-driver 二进制文件，或运行 `hermes tools` 并启用 Computer Use 工具集。

**点击似乎没有效果** —— 捕获并验证。你可能没注意到的模态框可能正在阻止输入。使用 `escape` 或关闭按钮将其关闭。

**元素索引已过期** —— SOM 索引仅在下次 `capture` 之前有效。在任何状态更改操作后重新捕获。包装器带有不透明的 `element_token`，用于过期检测——你会看到明确的错误消息，而不是错误的点击。

**"blocked pattern in type text"** —— 你尝试 `type` 的文本与危险 shell 模式列表匹配。请拆分命令或重新考虑。

**Linux 上捕获结果为空** —— `DISPLAY` 未设置，或者你处于纯 Wayland 环境而没有 XWayland 桥接。`hermes computer-use doctor` 会将其标记为 `ax_capability: fail`，并附带 `Set DISPLAY (X11)…` 提示。

**通过 SSH 在 Windows 上捕获结果为空** —— 你在 Session 0（服务会话）中。请直接从 RDP / 控制台驱动，或设置自启动模式——参见 [cua.ai/docs/how-to-guides/driver/windows-ssh](https://cua.ai/docs/how-to-guides/driver/windows-ssh)。

## 另请参阅

- **Hermes 端技能** —— `skills/computer-use/SKILL.md` —— 介绍 Hermes `computer_use` 动作词汇；这是代理加载的内容。
- **cua-driver 技能包** —— 针对平台特定深度剖析（macOS 无前台约定、Windows UIA + Session 0、Linux AT-SPI + X11/Wayland、录制、浏览器页面），运行 `cua-driver skills install` 并阅读 `MACOS.md` / `WINDOWS.md` / `LINUX.md` / `RECORDING.md` / `WEB_APPS.md`。一旦 `cua-driver skills install` 能自动检测到 Hermes（计划中的后续跟进），这将在安装时自动完成。
- **cua.ai/docs** —— cua-driver 项目的文档：
  - [什么是计算机使用？](https://cua.ai/docs/explanation/what-is-computer-use) —— 概念介绍
  - [无前台约定](https://cua.ai/docs/explanation/the-no-foreground-contract) —— *为什么* 后台模式很重要
  - [安装参考](https://cua.ai/docs/how-to-guides/driver/install) —— 跨平台安装详情
  - [个性化代理光标](https://cua.ai/docs/how-to-guides/driver/personalize-cursor) —— 内置形状、自定义资源、运行时覆盖
  - [通过 SSH 驱动 Windows](https://cua.ai/docs/how-to-guides/driver/windows-ssh) —— Session 0 → Session 1+ 自启动模式
  - [保持 cua-driver 运行](https://cua.ai/docs/how-to-guides/driver/keep-running) —— 自启动 / 守护进程生命周期
  - [连接你的代理](https://cua.ai/docs/how-to-guides/driver/connect-your-agent) —— 将 cua-driver 注册到各种工具（包括 Hermes）
- [cua-driver 源代码 (trycua/cua)](https://github.com/trycua/cua)
- [浏览器自动化](./browser.md) 用于不需要驱动本地应用程序的跨平台 Web 任务。