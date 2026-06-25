---
sidebar_position: 3
title: "桌面应用（Desktop App）"
description: "原生 Hermes 桌面应用——提供与 Hermes 聊天的精致体验，支持流式工具输出、并排预览、文件浏览器、语音、定时任务、配置文件、技能（Skill）和设置。支持 macOS、Windows 和 Linux。"
---

# 桌面应用（Desktop App）

Hermes 桌面应用是一款原生应用，基于与 CLI 和网关（Gateway）**相同**的代理（Agent）构建——相同的配置、相同的 API 密钥、相同的会话（Session）、相同的技能（Skill）、相同的内存。它不是一个独立的产品或轻量级克隆；它使用相同的 Hermes 代理核心和设置，并通过一个现代且精心设计的 UI 驱动。如果你在终端中使用过 `hermes`，那么你在那里设置的所有内容都已在这里，而在这里所做的任何操作也会在那里显示。

它支持 **macOS、Windows 和 Linux**。

:::tip 哪个界面是什么？
Hermes 有多个前端，它们都与同一个代理通信：

- **桌面应用**（本页）—— 一个原生应用，带有专为聊天、配置和管理量身定制的 UI。
- **CLI** (`hermes`) 和 **[TUI](./tui.md)** (`hermes --tui`) —— 终端界面。
- **[Web 仪表板](./features/web-dashboard.md)** (`hermes dashboard`) —— 一个浏览器管理面板；其可选的 **聊天** 标签页通过伪终端嵌入了 TUI。

根据场景选择合适的工具。它们共享状态，因此你可以在一个界面中启动会话，然后在另一个界面中继续。
:::

## 安装

按照 [Hermes 桌面版安装说明](../getting-started/installation.md) 进行安装。

如果你已经安装了 Hermes，只需运行：

```bash
hermes desktop
```

这会使用你当前的配置、密钥、会话和技能。

## 应用包含的内容

桌面应用以一个聊天优先的窗口组织，左侧边栏用于导航。它旨在允许管理多个并发的代理对话、配置消息提供者、创建工件（Artifact）、浏览项目的文件夹结构，并同时处理多个项目。

### 聊天

应用的中心。你将获得：

- **流式响应（Streaming responses）**——在代理工作时显示实时的工具活动以及结构化的工具调用摘要。
- **与所有其他 Hermes 界面相同的对话历史**——在此处开始的会话可以在 CLI/TUI 中恢复，反之亦然。
- **拖放文件**——将文件拖放到聊天区域的任意位置，以附加到你的下一条消息中。
- **右侧预览栏**——在继续聊天的同时，并排渲染网页、文件和工具输出。
- **编写器历史与队列编辑**——在空白编写器中按上/下箭头键可调用并重复使用之前的提示，并在发送之前编辑已排队待发送的消息。

#### 状态栏

聊天窗口底部的状态栏显示实时的会话状态，并提供快速控件，无需打开设置：

- **每个会话的 YOLO 开关**——仅为当前会话开启或关闭 YOLO 模式（与 TUI 匹配）。YOLO 模式会跳过危险命令的批准提示，因此请了解你正在关闭什么——参见 [安全 → YOLO 模式](./security.md#yolo-mode)。

正在与另一台机器上的 Hermes 实例聊天，而不是本地捆绑的后端？请参见下面的 [连接到远程后端](#connecting-to-a-remote-backend)——关于远程托管的仪表板连接如何工作（认证网关、`/api/ws` 聊天套接字以及 WebSocket 关闭代码诊断）的完整说明，请参见 [Web 仪表板 → 将 Hermes 桌面连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)。

#### 选择模型

模型选择器位于 **编写器** 中，就在麦克风图标的左侧。点击它可在一个下拉菜单中切换模型、推理难度和快速模式。

- **编写器选择器是粘性 UI 状态，不会触及你的默认设置。** 它在本地（按设备）记住，并在新聊天和重启时 **跟随**，而不会回退到默认值——只需选择一次模型，下次按 `Cmd/Ctrl+N` 打开时就使用它。在实时聊天中，切换模型会将更改范围限定在当前 **聊天** 中；无论哪种方式，选择都会在会话创建/切换时随之生效，并且 **永远不会** 写入配置文件的默认设置。（切换 [配置文件](#sessions--profiles) 会重新使用该配置文件自己的默认值。）
- **在设置 → 模型中设置默认模型。** 那个“主”模型是你的 **每个配置文件的全局默认值**——它是新聊天、定时任务、子代理和辅助任务启动的默认模型，也是唯一写入该默认值的地方。每个 [配置文件](#sessions--profiles) 保留自己的默认值。
- **每个模型的难度/快速预设。** 每个模型在桌面应用中记住自己的推理难度和快速模式选择，当你选择该模型时，它会将预设重新应用到会话中。这些预设是桌面应用的便利功能，不会更改定时任务或子代理。

### 文件浏览器

无需离开应用即可浏览和预览工作目录——这对于在代理读取、写入和编辑文件时跟进非常有用。使用 `hermes desktop --cwd <路径>`（或 `HERMES_DESKTOP_CWD` 环境变量）设置初始项目目录。

### 语音

与 Hermes 对话并听到它的回复，与 [语音模式](./features/voice-mode.md) 相同，其他界面也可用。在 macOS 上，操作系统会提示一次麦克风访问权限。

### 设置与入门引导

通过真实的 UI 管理提供者、模型、工具和凭据，而无需编辑 YAML。首次运行的入门引导可在几秒钟内让你发送第一条消息。设置面板涵盖提供者/密钥、模型选择、工具集配置、MCP 服务器、网关和会话管理。

- **提供者设置面板**——专门管理推理提供者的地方，具有账户/API 密钥的用户体验，用于登录和存储每个提供者的凭据。
- **菜单中的每个提供者和模型**——GUI 显示完整的提供者列表以及 `hermes model` 知道的每个模型，因此你可以从 CLI 看到的相同目录中选择，而不是精选的子集。
- **xAI Grok OAuth**——Grok 是启动器中的一等 OAuth 提供者；像其他 OAuth 提供者一样通过浏览器流程登录。
- **从 GUI 安装工具后端**——直接从应用运行工具后端的安装后步骤，而无需切换到终端。
- **辅助模型警告**——如果你将主模型切换到一个新的提供者，而辅助任务（如标题、摘要等）仍绑定在另一个提供者上，应用会警告你，这样你就不会在无意中将工作分散到两个提供者之间。

首次运行的入门引导已重新设计，采用统一的覆盖层设计系统，你可以选择 **稍后选择提供者** 以跳过提供者设置，先进入应用。

### 管理面板

应用还提供了更广泛的 Hermes 管理界面，这样你就不用切换到终端了：

- **技能（Skills）**——浏览、安装和管理 [技能](./features/skills.md)。
- **定时任务（Cron）**——查看和管理 [定时任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件（Profiles）**——在 [Hermes 配置文件](./profiles.md) 之间切换（隔离的配置/技能/会话）。
- **消息（Messaging）**——设置网关通道。
- **代理（Agents）** 和 **指挥中心（Command Center）**——用于多代理工作的编排界面。

### 键盘与导航

- **命令面板**——按 **Cmd+K**（Windows/Linux 上为 Ctrl+K）可跳转到操作，并用键盘导航应用。
- **可重绑定的快捷键**——设置中的快捷键面板允许你将应用的键盘快捷键重新映射到你自己的按键。
- **自定义缩放快捷键**——以半步增量缩放界面，以更精细地控制文本大小。
- **UI 语言切换器**——在应用内更改界面语言，包括简体中文（zh-Hans）。

### 会话与配置文件

- **会话列表大修**——重新设计的会话列表，支持归档和常规的会话清理，以在列表增长时保持可管理性。
- **按 ID 搜索会话**——直接通过会话 ID 查找特定会话。
- **并发的多配置文件会话**——在多个 [配置文件](./profiles.md) 上同时运行会话，并使用跨配置文件的 `@session` 链接引用另一个配置文件中的会话。

## 更新

应用会在后台检查更新，并在有可用更新时提供一键更新。

[手动更新流程](https://hermes-agent.nousresearch.com/docs/getting-started/updating) 也适用于 GUI。

## 卸载

打开 **设置 → 关于 → 危险区域**，选择要移除的内容：

- **仅卸载聊天 GUI**——移除桌面应用及其数据；Hermes 代理、你的配置和聊天记录保持不变。（等同于 `hermes uninstall --gui`。）
- **卸载 GUI + 代理，保留我的数据**——移除应用和代理，但保留配置、聊天记录和秘密，以便将来重新安装。（等同于 `hermes uninstall`。）
- **卸载所有内容**——移除应用、代理和所有用户数据。（等同于 `hermes uninstall --full`。）

应用会关闭以完成卸载操作（清理工作在退出后运行，以便移除正在运行的应用包及其 venv）。当未安装本地代理时（例如，连接到远程后端的纯 GUI“精简版”客户端），移除代理的选项会自动隐藏。

你也可以从终端执行相同操作——`hermes uninstall --gui` 仅卸载 GUI，或 `hermes uninstall` / `hermes uninstall --full` 同时卸载代理。

:::note
从 **源代码检出**（`hermes desktop` 开发构建）运行 `hermes uninstall --gui` 也会移除工作区的 `node_modules` 和 `apps/desktop/{dist,release}` 构建输出，因为这些是 GUI 构建产物。它们可以通过 `hermes desktop`（或 `npm install` + 重新构建）恢复——但如果你正在积极开发桌面应用，预计之后需要重新安装依赖项。
:::

## CLI 参考：`hermes desktop`

要通过 CLI 启动，只需运行 `hermes desktop`。默认情况下，它会安装工作区的 Node 依赖项，构建当前操作系统的解包 Electron 应用，然后启动该打包的工件。

| 标志                 | 描述                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------- |
| `--skip-build`       | 跳过 npm install/package，从 `apps/desktop/release` 启动现有的解包应用 |
| `--force-build`      | 即使内容戳匹配，也强制进行完整重建                                    |
| `--build-only`       | 构建桌面应用但不启动（由 `hermes update` 使用）                      |
| `--source`           | 通过 `electron .` 从 `apps/desktop/dist` 启动，而不是打包的应用           |
| `--cwd PATH`         | 桌面聊天会话的初始项目目录（设置 `HERMES_DESKTOP_CWD`）           |
| `--hermes-root PATH` | 覆盖应用使用的 Hermes 源代码根目录（设置 `HERMES_DESKTOP_HERMES_ROOT`）          |
| `--ignore-existing`  | 强制应用在后端解析期间忽略 `PATH` 上已有的任何 `hermes` CLI      |
| `--fake-boot`        | 启用确定性的启动延迟，用于验证启动 UI                            |

## 工作原理

打包的应用包含 Electron shell 和一个原生 React 聊天界面。首次启动时，它可以将 Hermes 代理运行时安装到 `HERMES_HOME`（`~/.hermes`，或 Windows 上的 `%LOCALAPPDATA%\hermes`）——**与 CLI 安装使用的布局相同**，这就是为什么两者可以互换。后端解析首先尊重 `HERMES_DESKTOP_HERMES_ROOT`，然后是已完成的受管安装，接着是探测 `PATH` 上的 `hermes`（除非设置了 `--ignore-existing` / `HERMES_DESKTOP_IGNORE_EXISTING=1`），最后是用于打包器（如 Nix）的显式 `HERMES_DESKTOP_HERMES` 命令覆盖。React 渲染器通过 `tui_gateway`/dashboard API 与 `hermes dashboard` 后端通信，并重用代理运行时，而不是嵌入 `hermes --tui`。安装、后端解析和自更新逻辑位于 Electron 主进程中。

## 连接到远程后端

默认情况下，应用启动并管理自己的**本地**后端。你也可以将其指向另一台机器上运行的 Hermes 后端——VPS、家庭服务器或 Tailscale 后面的 Mini。

:::info 远程后端是一个正在运行的 `hermes dashboard` 进程
“远程后端”指的是远程机器上运行的 **`hermes dashboard`** 服务器——这是桌面应用连接到的进程。除非该仪表板实际启动并可访问，否则本节中的任何内容都不起作用。桌面应用不会为你启动它；你需要自己（或通过 `systemd` 服务）在远程主机上保持 `hermes dashboard` 运行，然后应用会附加到它。如果你还使用消息通道（Telegram、Discord 等），**网关** 是一个 *独立的* 长期运行进程，你需要单独启动——参见设置步骤后的说明。
:::

连接包含两部分：在后端，你通过一个 **认证提供者** 保护仪表板；在应用中，你输入后端的 URL 并登录。将仪表板绑定到非回环地址会自动启用其认证网关，你配置的提供者就是允许桌面应用通过的方式。

**根据后端所在位置选择提供者：**

- **OAuth（Nous Portal）——推荐用于任何超出自己机器范围的情况。** 登录信息会根据你的 Nous 账户进行验证，因此适用于 VPS、公共主机或任何远程后端。使用 `hermes dashboard register`（或 Portal 的 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards) 页面）注册仪表板以配置其 OAuth 客户端，然后从应用中使用 **使用 Nous Research 登录** 登录。如果你运行自己的身份提供者，自托管的 OIDC 提供者同样适用。
- **用户名/密码——仅限本地/可信网络使用。** 当后端位于同一个可信 LAN 上或只能通过 VPN（例如 Tailscale）访问时，这是最简单的选项。它用一个共享凭据保护后端，不需要外部身份提供者，因此**不要将其用于暴露在公共互联网上的仪表板**——这种情况请使用 OAuth。

本节的其余部分展示了用户名/密码路径，因为它是在可信网络上设置的最快方式；有关 OAuth 路径，请参见 [Web 仪表板 → 默认提供者：Nous Research](./features/web-dashboard.md#default-provider-nous-research)。

### 在后端（远程机器上）

设置用户名和密码，然后启动绑定到可访问地址的仪表板。凭据保存在 `~/.hermes/.env`（秘密文件，模式 0600）中：

```bash
# 1. 设置仪表板登录凭据。
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=选择一个强密码
# 建议：一个稳定的签名密钥，这样会话可以在重启后继续存在。
# 如果没有它，每次启动都会生成一个随机密钥，你会在每次重启后被登出。
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. 运行绑定到可访问地址的仪表板。非回环绑定会启用认证网关；
#    用户名/密码提供者处理登录。
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

保持 `hermes dashboard` 进程运行，只要你想让桌面应用能够连接到它——如果它停止了，应用就无法再访问后端。在 `systemd`、`tmux` 或你选择的进程管理器下运行它，以便在注销和重启后继续运行。

另外，如果你依赖消息通道，请确保 **网关在远程主机上运行**——桌面应用与仪表板后端通信，但你的 Telegram/Discord/Slack 网关会话是一个不同的进程，你需要自己启动并保持运行。请参见 [消息](./messaging/index.md) 了解网关设置。

不想在静态环境中保留明文密码？可以将 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 设置为 scrypt 哈希——使用 `python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"` 计算。完整的配置面（config.yaml 键、所有环境变量、限速器）：[Web 仪表板 → 用户名/密码提供者](./features/web-dashboard.md#usernamepassword-provider-no-oauth-idp)。

将仪表板作为 systemd 服务运行？为单元提供 `EnvironmentFile=%h/.hermes/.env`，以便凭据在启动时存在于环境中。

:::warning
仪表板会读取和写入你的 `.env`（API 密钥、秘密），并且可以运行代理命令。上面显示的 **用户名/密码** 设置适用于可信网络——切勿将受密码保护的仪表板直接暴露在开放互联网上；请将其放在 VPN 后面。[Tailscale](https://tailscale.com/) 是一个简洁的选择：绑定到机器的 tailscale IP（`--host <tailscale-ip>`）并使用 `http://<tailscale-ip>:9119` 作为远程 URL，这样只有你的 tailnet 可以访问它。要通过公共互联网访问后端，请改用 **OAuth（Nous Portal）** 提供者。
:::

### 在应用中

**设置 → 网关 → 远程网关：**

1. **远程 URL** —— `http://<backend-host>:9119`（如果你用反向代理前置，路径前缀如 `/hermes` 也可以）
2. **登录** —— 应用会检测后端宣传的提供者，并调整按钮。对于用户名/密码后端，它会显示一个 **登录** 按钮，打开一个凭据表单（输入步骤 1 中的凭据）。对于 OAuth 后端，它会显示 **使用 `<提供者>` 登录**（例如 *使用 Nous Research 登录*），然后运行提供者的浏览器登录。无论哪种方式，应用最终都会获得针对后端的认证会话。
3. **保存并重新连接** —— 将桌面 shell 切换到远程后端。会话会自动刷新；当设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 时，你可以在重启后保持登录状态。

你也可以在启动应用之前，通过 `HERMES_DESKTOP_REMOTE_URL` 环境变量设置后端 URL，而无需使用 UI（它会覆盖应用内的设置）；你仍然需要从网关设置面板登录。

:::note 每个配置文件的远程主机
远程网关主机是按 [配置文件](./profiles.md) 配置的，因此每个配置文件可以指向自己的远程后端（或保持在本地后端上）。切换配置文件会切换应用连接到的远程主机。
:::

### 故障排除

- **登录失败并显示 401 / "Invalid credentials"** —— 用户名或密码与后端的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。对于未知用户和错误密码，后端返回相同的通用错误（无枚举漏洞），因此请仔细检查两者。确认网关已启用：`curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` —— 应报告 `true` 并包含 `"basic"`。
- **没有"登录"按钮——它要求输入会话令牌** —— 后端的用户名/密码提供者未激活。`/api/status` 不会在 `auth_providers` 中列出 `"basic"`。确保 `~/.hermes/.env` 中同时设置了用户名和密码（或密码哈希），并且仪表板进程实际加载了它们。
- **每次重启都被登出** —— 将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个稳定值。如果没有它，令牌签名密钥会在每次启动时重新生成，从而使所有会话失效。
- **连接被拒绝 / 超时** —— 后端绑定到 `127.0.0.1`（默认值），或者防火墙/VPN 阻止了端口。绑定到 `0.0.0.0` 或 tailscale IP，并向你的可信网络开放端口。

从 Web 仪表板角度进行相同设置，请参见 [Web 仪表板 → 将 Hermes 桌面连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)；环境变量在 [环境变量 → Web 仪表板和 Hermes 桌面](../reference/environment-variables.md#web-dashboard--hermes-desktop) 中列出。

## 故障排除

启动日志位于 `HERMES_HOME/logs/desktop.log`（包括后端输出和最近的 Python 回溯）——如果应用报告启动失败，请先检查此日志。你也可以从 CLI 跟踪：

```bash
hermes logs gui -f
```

常见重置操作：

```bash
# 强制进行干净的首次启动设置（macOS/Linux）
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"

# 重建损坏的 Python 虚拟环境（macOS/Linux）
rm -rf "$HOME/.hermes/hermes-agent/venv"

# 重置卡住的 macOS 麦克风提示
tccutil reset Microphone com.nousresearch.hermes
```

### "构建桌面应用"卡在 Electron 下载

构建过程会从 `github.com/electron/electron/releases` 下载 Electron 运行时（约 114 MB）。如果安装程序卡在 **构建桌面应用** 步骤，并且实时输出重复出现 `retrying attempt=…`，说明 GitHub 在你的网络上被阻止或限流（防火墙、代理或地区限制）。

安装程序会自动修复此问题：在构建失败时，它会（1）清除损坏的 Electron 缓存 zip 并重试，然后（2）如果仍然失败且你未设置 `ELECTRON_MIRROR`，它会通过 `npmmirror.com`（事实上的 Electron 社区镜像）再重试一次。`@electron/get` 会对下载进行 SHASUM 校验，但校验和也来自同一个镜像——这可以捕获损坏或不完整的下载，但无法检测受损的镜像。如果你宁愿不信任第三方主机，请自行指定 `ELECTRON_MIRROR`（见下文）；构建过程永远不会覆盖你设置的值。

要**选择自己的镜像**（例如企业/受信任的镜像），请在安装前设置 `ELECTRON_MIRROR`，或手动重新构建——构建过程会尊重该设置，不会覆盖它：

```bash
ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ \
  bash -c 'cd "$HOME/.hermes/hermes-agent/apps/desktop" && CSC_IDENTITY_AUTO_DISCOVERY=false npm run pack'
```

手动清除损坏的缓存 zip：

```bash
rm -f "$HOME/Library/Caches/electron"/electron-*.zip   # macOS
rm -f "$HOME/.cache/electron"/electron-*.zip            # Linux
```

## 从源代码构建

如果你想自己修改应用，请从仓库根目录一次安装工作区依赖项，然后从 `apps/desktop` 运行开发服务器：

```bash
npm install          # 从仓库根目录——链接 apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite 渲染器 + Electron，后者会启动 Python 后端
```

将应用指向特定的检出目录，或将其与实际配置隔离：

```bash
HERMES_DESKTOP_HERMES_ROOT=/path/to/clone npm run dev
HERMES_HOME=/tmp/throwaway npm run dev
npm run dev:fake-boot   # 使用确定性延迟测试启动覆盖层
```

构建安装程序：

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # NSIS + MSI
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # 生成 release/ 下的解包应用（无安装程序）
```

macOS/Windows 签名和公证会在环境中存在相应凭据时自动运行（macOS 的 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 的 `WIN_CSC_*`）。

## 另请参阅

- [CLI 指南](./cli.md) —— 终端界面
- [TUI](./tui.md) —— `hermes --tui` 和仪表板聊天标签页使用的现代终端 UI
- [Web 仪表板](./features/web-dashboard.md) —— 带有嵌入式聊天标签页的浏览器管理面板
- [配置](./configuration.md) —— 桌面应用读取和写入的配置
- [Windows（原生）](./windows-native.md) —— 原生 Windows 安装路径