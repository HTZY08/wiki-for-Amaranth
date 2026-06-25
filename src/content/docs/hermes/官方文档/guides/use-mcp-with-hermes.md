---
sidebar_position: 6
title: "使用 MCP 与 Hermes"
description: "一份实用指南，介绍如何将 MCP 服务器连接到 Hermes Agent，过滤其工具，并在实际工作流中安全使用它们"
---

# 使用 MCP 与 Hermes

本指南介绍如何在实际日常工作流中使用 MCP 与 Hermes Agent。

如果特性页面解释了 MCP 是什么，那么本指南则侧重于如何快速且安全地从 MCP 中获得价值。

## 何时应该使用 MCP？

在以下情况下使用 MCP：
- 某个工具已经以 MCP 形式存在，而你不想构建原生的 Hermes 工具
- 你希望通过一个干净的 RPC 层让 Hermes 操作本地或远程系统
- 你需要对每个服务器的暴露范围进行精细控制
- 你想让 Hermes 连接到内部 API、数据库或公司系统，而无需修改 Hermes 核心

在以下情况下不应使用 MCP：
- 内置的 Hermes 工具已经很好地解决了问题
- 服务器暴露了大量危险的工具接口，而你尚未准备好进行过滤
- 你只需要一个非常狭窄的集成，而原生工具会更简单、更安全

## 思维模型

将 MCP 视为一个适配层：

- Hermes 仍然是代理（Agent）
- MCP 服务器贡献工具
- Hermes 在启动或重载时发现这些工具
- 模型可以像使用普通工具一样使用它们
- 你可以控制每个服务器的可见范围

最后一点很重要。好的 MCP 使用方式不仅仅是“连接一切”，而是“连接正确的东西，且暴露最小的有用表面”。

## 步骤 1：安装 MCP 支持

如果你通过标准安装脚本安装了 Hermes，那么 MCP 支持已经包含在内（安装程序会运行 `uv pip install -e ".[all]"`）。

如果你没有附带 extras 安装，需要单独添加 MCP：

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[mcp]"
```

对于基于 npm 的服务器，请确保 Node.js 和 `npx` 可用。

对于许多 Python MCP 服务器，`uvx` 是一个不错的默认选择。

## 步骤 2：首先添加一个服务器

从单个安全的服务器开始。

示例：仅访问一个项目目录的文件系统。

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

然后启动 Hermes：

```bash
hermes chat
```

现在问一些具体的问题：

```text
检查这个项目，总结一下仓库的布局。
```

## 步骤 3：验证 MCP 已加载

你可以通过几种方式验证 MCP：

- Hermes 的横幅/状态应在配置后显示 MCP 集成
- 询问 Hermes 有哪些工具可用
- 配置文件更改后使用 `/reload-mcp`
- 如果服务器连接失败，检查日志

一个实用的测试提示：

```text
告诉我现在有哪些 MCP 支持的工具可用。
```

## 步骤 4：立即开始过滤

如果服务器暴露了大量工具，不要等到以后再做。

### 示例：仅白名单你想要的

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
```

对于敏感系统，这通常是最好的默认设置。

## WSL2：将 WSL 中的 Hermes 桥接到 Windows 上的 Chrome

这是实际设置，当：

- Hermes 在 WSL2 内部运行
- 你想要控制的浏览器是你正常登录的 Windows 上的 Chrome
- 从 WSL 使用 `/browser connect` 很别扭或不可靠

在这种设置中，Hermes **不**直接连接 Chrome。取而代之的是：

- Hermes 在 WSL 中运行
- Hermes 启动一个本地 stdio MCP 服务器
- 该 MCP 服务器通过 Windows 互操作（`cmd.exe` 或 `powershell.exe`）启动
- MCP 服务器连接到你正在运行的 Windows Chrome 会话

思维模型：

```text
Hermes (WSL) -> MCP stdio 桥接 -> Windows Chrome
```

### 为什么这种模式有用

- 你保留真实的 Windows 浏览器配置文件、cookies 和登录状态
- Hermes 保持在其支持的 Unix 环境（WSL2）中
- 浏览器控制作为 MCP 工具暴露，而不是依赖 Hermes 核心的浏览器传输

### 推荐的服务器

使用 `chrome-devtools-mcp`。

如果你的 Windows Chrome 已经通过 `chrome://inspect/#remote-debugging` 启用了实时远程调试，可以从 WSL 这样添加：

```bash
hermes mcp add chrome-devtools-win --command cmd.exe --args /c npx -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

保存服务器后：

```bash
hermes mcp test chrome-devtools-win
```

然后启动一个新的 Hermes 会话，或运行：

```text
/reload-mcp
```

### 典型的提示

加载后，Hermes 可以直接使用 MCP 前缀的浏览器工具。例如：

```text
调用 MCP 工具 mcp_chrome_devtools_win_list_pages，列出当前浏览器标签页。
```

### 何时 `/browser connect` 是错误的工具

如果 Hermes 在 WSL 中运行，而 Chrome 在 Windows 上运行，即使 Chrome 已打开且可调试，`/browser connect` 也可能失败。

常见原因：

- WSL 无法访问 Chrome 向 Windows 工具暴露的同一 host-local 端点
- 较新版本的 Chrome 实时调试流程与传统的 `ws://localhost:9222` 不同
- 通过 Windows 端的辅助程序（如 `chrome-devtools-mcp`）更容易附加到浏览器

在这些情况下，将 `/browser connect` 用于同环境设置，并使用 MCP 进行 WSL 到 Windows 的浏览器桥接。

### 已知陷阱

- 当通过 MCP 使用 Windows stdio 可执行文件时，请从 Windows 挂载的路径（如 `/mnt/c/Users/<you>` 或 `/mnt/c/workspace/...`）启动 Hermes。
- 如果你从 `/root` 或 `/home/...` 启动 Hermes，Windows 可能在 MCP 服务器启动前发出 `UNC` 当前目录警告。
- 如果 `chrome-devtools-mcp --autoConnect` 在枚举页面时超时，请减少 Chrome 中的后台/冻结标签页并重试。

### 示例：黑名单危险操作

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 示例：也禁用实用包装器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

## 过滤实际上影响什么？

在 Hermes 中，MCP 暴露的功能分为两类：

1. 服务器原生的 MCP 工具
- 通过以下方式过滤：
  - `tools.include`
  - `tools.exclude`

2. Hermes 添加的实用包装器
- 通过以下方式过滤：
  - `tools.resources`
  - `tools.prompts`

### 你可能看到的实用包装器

资源（Resources）：
- `list_resources`
- `read_resource`

提示（Prompts）：
- `list_prompts`
- `get_prompt`

这些包装器仅在以下情况下出现：
- 你的配置允许它们，并且
- MCP 服务器会话实际支持这些能力

因此，如果服务器不支持资源/提示，Hermes 不会假装其存在。

## 常见模式

### 模式 1：本地项目助手

当你希望 Hermes 在一个受限的工作空间中进行推理时，使用 MCP 为仓库本地文件系统或 git 服务器提供服务。

```yaml
mcp_servers:
  fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]

  git:
    command: "uvx"
    args: ["mcp-server-git", "--repository", "/home/user/project"]
```

好的提示：

```text
检查项目结构，指出配置文件所在位置。
```

```text
查看本地 git 状态，总结最近的变化。
```

### 模式 2：使用 Open Scaffold 的仓库原生工作记录

当你希望 Hermes 读取仓库持久的 AI 工作记录（包括任务、计划、证据笔记、交接包、审查/门控结果）时，使用 [Open Scaffold](https://github.com/graphanov/open-scaffold)。Hermes 仍然是代理（Agent）；Open Scaffold 仍然是仓库本地的记录。

为一个有脚手架的仓库添加服务器：

```bash
hermes mcp add open_scaffold --command npx --args -y open-scaffold@latest mcp serve --repo /absolute/path/to/repo
hermes mcp test open_scaffold
```

然后保持暴露的表面以读取为主。在 `hermes mcp add` 提示中选择 `select`，或者之后编辑 `config.yaml`：

```yaml
mcp_servers:
  open_scaffold:
    command: "npx"
    args: ["-y", "open-scaffold@latest", "mcp", "serve", "--repo", "/absolute/path/to/repo"]
    tools:
      include:
        - list_plans
        - get_plan
        - get_mission
        - list_evidence
        - get_evidence
        - get_status
        - search_plans
        - list_amendments
        - get_handoff
        - analyze_loop
        - gate_loop
      prompts: false
```

好的提示：

```text
使用 Open Scaffold MCP 工具编译当前的交接包，并告诉我下一步的合法操作。
```

```text
检查活跃的计划和证据笔记，然后判断这个仓库是否准备好进行人工审查，还是需要再次尝试。
```

边界说明：

- Open Scaffold MCP 是本地优先的，默认只读。
- 其写入工具需要服务器以 `--allow-write` 启动；在明确希望 Hermes 修改 `.osc` 文件之前不要启用。
- Open Scaffold 记录和门控工作；它并不授权 Hermes 进行合并、发布、部署或启动运行时。
- 如果你需要可复现的工具模式，请将 `open-scaffold@<version>` 固定下来，而不是 `@latest`。

### 模式 3：GitHub 分类助手

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false
```

好的提示：

```text
列出关于 MCP 的开放问题，按主题分类，并为最常见的 bug 起草一个高质量的问题。
```

```text
在仓库中搜索 _discover_and_register_server 的用法，并解释 MCP 工具是如何注册的。
```

### 模式 4：内部 API 助手

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      include: [list_customers, get_customer, list_invoices]
      resources: false
      prompts: false
```

好的提示：

```text
查找客户 ACME Corp，并总结最近的发票活动。
```

这种场景下，严格的白名单远优于排除列表。

### 模式 4：文档/知识服务器

一些 MCP 服务器暴露的提示或资源更像是共享的知识资产，而不是直接的操作。

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: true
      resources: true
```

好的提示：

```text
列出文档服务器上可用的 MCP 资源，然后阅读入手指南并总结内容。
```

```text
列出文档服务器暴露的提示，并告诉我哪些对事件响应有帮助。
```

## 教程：带过滤的端到端设置

这是一个实用的演进过程。

### 第一阶段：添加带有严格白名单的 GitHub MCP

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, search_code]
      prompts: false
      resources: false
```

启动 Hermes 并问：

```text
在代码库中搜索对 MCP 的引用，并总结主要的集成点。
```

### 第二阶段：仅在需要时扩展

如果你之后还需要更新问题：

```yaml
tools:
  include: [list_issues, create_issue, update_issue, search_code]
```

然后重载：

```text
/reload-mcp
```

### 第三阶段：添加第二个具有不同策略的服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      prompts: false
      resources: false

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/project"]
```

现在 Hermes 可以结合它们：

```text
检查本地项目文件，然后创建一个 GitHub 问题总结你发现的 bug。
```

这就是 MCP 强大之处：无需修改 Hermes 核心即可实现多系统工作流。

## 安全使用建议

### 对危险系统优先使用白名单

对于任何涉及财务、面向客户或破坏性的操作：
- 使用 `tools.include`
- 从最小的集合开始

### 禁用未使用的实用程序

如果你不希望模型浏览服务器提供的资源/提示，请关闭它们：

```yaml
tools:
  resources: false
  prompts: false
```

### 保持服务器范围狭窄

示例：
- 文件系统服务器根目录为一个项目目录，而不是整个主目录
- git 服务器指向一个仓库
- 内部 API 服务器默认暴露以读取为主的操作

### 配置更改后重新加载

```text
/reload-mcp
```

在更改以下内容后执行此操作：
- include/exclude 列表
- 启用标志
- resources/prompts 开关
- 认证头 / 环境变量

## 按症状进行故障排除

### "服务器连接成功，但我预期的工具缺失"

可能的原因：
- 被 `tools.include` 过滤
- 被 `tools.exclude` 排除
- 通过 `resources: false` 或 `prompts: false` 禁用了实用包装器
- 服务器实际上不支持资源/提示

### "服务器已配置，但没有任何内容加载"

检查：
- 配置中没有保留 `enabled: false`
- 命令/运行时存在（`npx`、`uvx` 等）
- HTTP 端点可访问
- 认证环境变量或标头正确

### "为什么我看到比 MCP 服务器宣传的少得多的工具？"

因为 Hermes 现在遵循你每服务器的策略和基于能力的注册。这是预期的，通常也是理想的。

### "如何在不删除配置的情况下移除 MCP 服务器？"

使用：

```yaml
enabled: false
```

这将保留配置但阻止连接和注册。

## 推荐的初始 MCP 设置

对于大多数用户来说，好的首个服务器：
- 文件系统
- git
- GitHub
- 获取/文档 MCP 服务器
- 一个狭窄的内部 API

不太好的首个服务器：
- 包含大量破坏性操作且未过滤的大型业务系统
- 任何你不够理解以至于无法约束的东西

## 相关文档

- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [常见问题](/reference/faq)
- [斜杠命令](/reference/slash-commands)