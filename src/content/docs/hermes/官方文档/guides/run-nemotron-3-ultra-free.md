---
sidebar_position: 0
title: "在 Hermes Agent 中免费运行 Nemotron 3 Ultra"
description: "在 Nous Portal 上免费体验 NVIDIA Nemotron 3 Ultra（6月4日至18日），Hermes Agent 提供首发支持"
---

# 在 Hermes Agent 中免费运行 Nemotron 3 Ultra

Nous Research 已入选与 **NVIDIA** 合作推动开放前沿基础模型的顶尖 AI 实验室组成的 **Nemotron 联盟（Nemotron Coalition）**。为庆祝这一成就，我们与 **Nebius** 合作，在 [Nous Portal](https://portal.nousresearch.com) 上免费提供 **Nemotron 3 Ultra** 两周（**6月4日至6月18日**）。请按照以下说明，立即在您的 Hermes Agent 中试用该模型。

:::info 限时优惠
`nvidia/nemotron-3-ultra:free` 层级自 **6月4日至6月18日** 可用。`:free` 标记使其保持免费计划状态——请选择该确切变体。
:::

选择适合您的安装方式。**桌面应用**最简单——无需终端。如果您偏好终端，下面的**命令行**安装更适合您。

## 选项 A — 桌面应用（推荐）

最简单的路径：一键安装，带有引导式的点击设置。无需终端。

### 1. 下载并安装

[下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/)（适用于 macOS 或 Windows），然后打开它。首次启动时会完成自身设置（通常在一分钟内）。

### 2. 连接 Nous Portal

应用打开时，您将看到“Let's get you set up”屏幕。点击 **Nous Portal**（标记为 **推荐**）。浏览器将打开——创建一个 [Nous Portal](https://portal.nousresearch.com) 账户（或登录），选择**免费**计划，并授权 Hermes。应用会自动连接。

### 3. 选择免费的 Nemotron 3 Ultra 模型

连接后，应用会显示一个**默认模型**卡片。点击**更改**，搜索 **nemotron 3 ultra**，并选择标记为**免费层级**的变体：

```
nvidia/nemotron-3-ultra:free
```

`:free` 标记使其保持免费层级状态——请选择该变体。

### 4. 开始聊天

点击**开始聊天**。就这样——您正在免费与 Nemotron 3 Ultra 对话。

## 选项 B — 命令行

偏好终端？

### 1. 安装 Hermes Agent

在 macOS/Linux/WSL2/Android 上运行

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

在 Windows 上运行

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

希望先审查？下载 [`install.sh`](https://hermes-agent.nousresearch.com/install.sh)，检查后运行。

完成后，重新加载 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

### 2. 运行快速设置

```bash
hermes setup
```

选择**快速设置**。Hermes 会打开一个浏览器标签页，等待您完成后续步骤。

### 3. 创建 Nous Portal 账户

在浏览器中，创建一个 [Nous Portal](https://portal.nousresearch.com) 账户（或登录）并选择**免费**计划。

### 4. 连接您的账户

当提示将您的账户连接到 Hermes Agent 时，点击**连接**。连接成功后您会看到确认信息。

### 5. 选择免费的 Nemotron 3 Ultra 模型

返回到终端。从模型列表中，选择：

```
nvidia/nemotron-3-ultra:free
```

`:free` 标记使其保持免费层级状态，因此请确保选择该变体。

### 6. 开始聊天

完成剩余的快速设置提示，然后运行：

```bash
hermes
```

就这样——您正在免费与 Nemotron 3 Ultra 对话。

## 稍后切换到此模型

已用其他模型设置好？

- **桌面应用：** 打开模型选择器，搜索 **nemotron 3 ultra**，并选择**免费层级**变体。
- **CLI / TUI：** 在会话中随时使用 `/model nvidia/nemotron-3-ultra:free` 切换，或者运行 `/model` 打开选择器并从列表中选取。

## 故障排除

- **列表中没有该模型？** 确保您已完成 Nous Portal 连接，并且使用的是**免费**计划。在 CLI 中，`hermes portal info` 可确认您已登录并通过 Nous 路由。
- **选错了变体？** 重新选择 `nvidia/nemotron-3-ultra:free` — 必须使用 `:free` 后缀才能保持免费层级。
- **浏览器未打开/您在使用远程主机（CLI）？** 请参阅 [通过 SSH / 远程主机进行 OAuth](/guides/oauth-over-ssh) 了解端口转发和手动粘贴的解决方法。

## 参见

- **[桌面应用](/user-guide/desktop)** — 原生一键应用（macOS、Windows、Linux）
- **[使用 Nous Portal 运行 Hermes Agent](/guides/run-hermes-with-nous-portal)** — 完整的 Portal 操作指南：模型、工具网关和验证
- **[Nous Portal 集成](/integrations/nous-portal)** — 订阅包含的内容
- **[快速入门](/getting-started/quickstart)** — 安装到聊天只需不到 5 分钟