---
title: 视觉与图像粘贴
description: 将剪贴板中的图像粘贴到 Hermes CLI 中，以进行多模态视觉分析。
sidebar_label: 视觉与图像粘贴
sidebar_position: 7
---

# 视觉与图像粘贴

Hermes Agent 支持**多模态视觉（multimodal vision）**——你可以将剪贴板中的图像直接粘贴到 CLI 中，让智能体分析、描述或处理这些图像。图像会以 base64 编码的内容块发送给模型，因此任何支持视觉的模型（vision-capable model）都能处理它们。

:::tip
门户订阅者可以在同一目录中获得支持视觉的模型（Claude、GPT-5、Gemini），无需额外凭证。请参阅 [Nous 门户](/integrations/nous-portal)。
:::

## 工作原理

1. 将图像复制到剪贴板（截图、浏览器图片等）
2. 使用以下方法之一附加图像
3. 输入你的问题并按 Enter
4. 图像会以 `[📎 图像 #1]` 标记出现在输入框上方
5. 提交时，图像会作为视觉内容块发送给模型

你可以在发送前附加多张图像——每张图像都会获得自己的标记。按 `Ctrl+C` 清除所有已附加的图像。

图像会以 PNG 格式保存到 `~/.hermes/images/`，文件名带时间戳。

## 粘贴方法

附加图像的方式取决于你的终端环境。并非所有方法在所有地方都有效——以下是完整说明：

### `/paste` 命令

**最可靠的显式图像附加回退方法。**

```
/paste
```

输入 `/paste` 并按 Enter。Hermes 会检查剪贴板中是否有图像并进行附加。当你的终端重写了 `Cmd+V`/`Ctrl+V`，或者你只复制了图像且没有可供检查的带括号粘贴文本负载时，这是最安全的选择。

### Ctrl+V / Cmd+V

Hermes 现在将粘贴视为分层流程：
- 首先进行普通文本粘贴
- 如果终端未能清晰地传递文本，则使用原生剪贴板 / OSC52 文本回退
- 当剪贴板或粘贴负载解析为图像或图像路径时，附加图像

这意味着粘贴的 macOS 截图临时路径和 `file://...` 图像 URI 可以立即附加，而不会作为原始文本停留在编辑器中。

:::warning
如果你的剪贴板中**只有图像**（没有文本），终端仍然无法直接发送二进制图像字节。请使用 `/paste` 作为显式的图像附加回退方法。
:::

### VS Code / Cursor / Windsurf 的 `/terminal-setup`

如果你在 macOS 的本地 VS Code 系列集成终端中运行 TUI，Hermes 可以安装推荐的 `workbench.action.terminal.sendSequence` 绑定，以获得更好的多行和撤销/重做支持：

```text
/terminal-setup
```

当 `Cmd+Enter`、`Cmd+Z` 或 `Shift+Cmd+Z` 被 IDE 拦截时，这尤其有用。仅在本地机器上运行，不要通过 SSH 会话运行。

## 平台兼容性

| 环境 | `/paste` | Cmd/Ctrl+V | `/terminal-setup` | 备注 |
|---|:---:|:---:|:---:|---|
| **macOS Terminal / iTerm2** | ✅ | ✅ | 不适用 | 最佳体验——原生剪贴板 + 截图路径恢复 |
| **Apple Terminal** | ✅ | ✅ | 不适用 | 如果 Cmd+←/→/⌫ 被重写，请使用 Ctrl+A / Ctrl+E / Ctrl+U 回退键 |
| **Linux X11 桌面** | ✅ | ✅ | 不适用 | 需要 `xclip`（`apt install xclip`） |
| **Linux Wayland 桌面** | ✅ | ✅ | 不适用 | 需要 `wl-paste`（`apt install wl-clipboard`） |
| **WSL2（Windows Terminal）** | ✅ | ✅ | 不适用 | 使用 `powershell.exe`——无需额外安装 |
| **VS Code / Cursor / Windsurf（本地）** | ✅ | ✅ | ✅ | 建议使用以获得更好的 Cmd+Enter / 撤销 / 重做支持 |
| **VS Code / Cursor / Windsurf（SSH）** | ❌² | ❌² | ❌³ | 改为在本地机器上运行 `/terminal-setup` |
| **SSH 终端（任何）** | ❌² | ❌² | 不适用 | 远程剪贴板无法访问 |

² 请参阅下面的 [SSH 与远程会话](#ssh-与远程会话)
³ 该命令会写入本地 IDE 键绑定，不应在远程主机上运行

## 特定平台设置

### macOS

**无需设置。** Hermes 使用 macOS 内置的 `osascript` 读取剪贴板。为获得更快的性能，可选择安装 `pngpaste`：

```bash
brew install pngpaste
```

### Linux（X11）

安装 `xclip`：

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Linux（Wayland）

现代 Linux 桌面（Ubuntu 22.04+、Fedora 34+）通常默认使用 Wayland。安装 `wl-clipboard`：

```bash
# Ubuntu/Debian
sudo apt install wl-clipboard

# Fedora
sudo dnf install wl-clipboard

# Arch
sudo pacman -S wl-clipboard
```

:::tip 如何检查你是否在使用 Wayland
```bash
echo $XDG_SESSION_TYPE
# "wayland" = Wayland, "x11" = X11, "tty" = 无显示服务器
```
:::

### WSL2

**无需额外设置。** Hermes 会自动检测 WSL2（通过 `/proc/version`），并使用 `powershell.exe` 通过 .NET 的 `System.Windows.Forms.Clipboard` 访问 Windows 剪贴板。这是 WSL2 的 Windows 互操作内建功能——`powershell.exe` 默认可用。

剪贴板数据会通过标准输出以 base64 编码的 PNG 形式传输，因此不需要文件路径转换或临时文件。

:::info WSLg 说明
如果你正在运行 WSLg（带 GUI 支持的 WSL2），Hermes 会首先尝试 PowerShell 路径，然后回退到 `wl-paste`。WSLg 的剪贴板桥仅支持 BMP 格式的图像——Hermes 会使用 Pillow（如果已安装）或 ImageMagick 的 `convert` 命令自动将 BMP 转换为 PNG。
:::

#### 验证 WSL2 剪贴板访问

```bash
# 1. 检查 WSL 检测
grep -i microsoft /proc/version

# 2. 检查 PowerShell 是否可访问
which powershell.exe

# 3. 复制一张图像，然后检查
powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::ContainsImage()"
# 应输出 "True"
```

## SSH 与远程会话

**通过 SSH 时，剪贴板图像粘贴无法完全工作。** 当你通过 SSH 连接到远程机器时，Hermes CLI 在远程主机上运行。剪贴板工具（`xclip`、`wl-paste`、`powershell.exe`、`osascript`）会读取它们所在机器的剪贴板——即远程服务器，而不是你的本地机器。因此，本地剪贴板中的图像无法从远程端访问。

文本有时仍可通过终端粘贴或 OSC52 桥接，但图像剪贴板访问和本地截图临时路径仍然只与运行 Hermes 的机器绑定。

### SSH 的解决方法

1. **上传图像文件**——将图像保存在本地，通过 `scp`、VSCode 的文件资源管理器（拖放）或任何文件传输方法上传到远程服务器，然后通过路径引用。（计划在未来版本中添加 `/attach <文件路径>` 命令。）

2. **使用 URL**——如果图像可以在线访问，只需在消息中粘贴 URL。智能体可以直接使用 `vision_analyze` 查看任何图像 URL。

3. **X11 转发**——使用 `ssh -X` 连接以转发 X11。这允许远程机器上的 `xclip` 访问你的本地 X11 剪贴板。需要在本地运行 X 服务器（macOS 上为 XQuartz，Linux X11 桌面上内置）。对于大图像速度较慢。

4. **使用消息平台**——通过 Telegram、Discord、Slack 或 WhatsApp 将图像发送给 Hermes。这些平台原生处理图像上传，不受剪贴板/终端限制的影响。

## 为什么终端无法粘贴图像

这是一个常见的混淆点，以下是技术解释：

终端是**基于文本**的界面。当你按 Ctrl+V（或 Cmd+V）时，终端模拟器：

1. 读取剪贴板中的**文本内容**
2. 将其包裹在[带括号粘贴](https://en.wikipedia.org/wiki/Bracketed-paste)转义序列中
3. 通过终端的文本流发送到应用程序

如果剪贴板中只包含图像（没有文本），终端就没有任何内容可发送。没有标准的二进制图像数据终端转义序列。终端只是什么都不做。

这就是为什么 Hermes 使用单独的剪贴板检查——它不通过终端粘贴事件接收图像数据，而是直接通过子进程调用操作系统级别的工具（`osascript`、`powershell.exe`、`xclip`、`wl-paste`）来独立读取剪贴板。

## 支持的模型

图像粘贴适用于任何支持视觉的模型。图像会以 OpenAI 视觉内容格式的 base64 编码数据 URL 形式发送：

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,..."
  }
}
```

大多数现代模型都支持这种格式，包括 GPT-4 Vision、Claude（带视觉）、Gemini 以及通过 OpenRouter 提供的开源多模态模型。

## 图像路由（支持视觉的模型与纯文本模型）

当用户附加图像时——无论来自 CLI 剪贴板、网关（Telegram/Discord 照片）还是其他入口点——Hermes 会根据当前模型是否实际支持视觉进行路由：

| 你的模型 | 图像的处理方式 |
|---|---|
| **支持视觉的模型**（GPT-4V、带视觉的 Claude、Gemini、Qwen-VL、MiMo-VL 等） | 使用上述提供者原生图像内容格式作为**真实像素**发送。无文本摘要层。 |
| **纯文本模型**（DeepSeek V3、较小的开源模型、较旧的仅聊天端点） | 通过 `vision_analyze` 辅助工具路由——辅助视觉模型描述图像，然后将文本描述注入到对话中。 |

你无需配置此项——Hermes 会在提供者元数据中查找当前模型的能力，并自动选择正确的路径。实际效果是：你可以在会话中在半途切换视觉和非视觉模型，图像处理“自动适配”，无需改变你的工作流。纯文本模型会获得关于图像的连贯上下文，而不是它们必须拒绝的无效多模态负载。

处理文本描述路径的辅助模型可在 `auxiliary.vision` 下配置——请参阅 [辅助模型](/user-guide/configuration#辅助模型)。

### `vision_analyze` 具有相同的双重行为

`vision_analyze` 工具本身遵循相同的路由。当活动主模型支持视觉**并且**其提供者支持在工具结果中包含图像内容（目前为 Anthropic、OpenAI、Azure-OpenAI 和 Gemini 3.x 堆栈）时，`vision_analyze` 会绕过辅助描述器，将原始图像像素作为多模态工具结果信封返回。主模型在下一轮推理中直接看到图像——无需调用辅助模型，没有文本摘要信息丢失，没有额外延迟。

对于纯文本主模型（或其工具结果通道不支持图像的提供者），`vision_analyze` 回退到传统路径：它请求配置的辅助视觉模型描述图像，并将描述作为纯文本返回。无论哪种方式，调用的工具签名都是相同的——工具在运行时根据活动模型决定采取哪个路径。