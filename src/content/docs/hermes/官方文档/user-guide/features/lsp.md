---
sidebar_position: 16
title: "LSP — 语义诊断 (Semantic Diagnostics)"
description: "真正的语言服务器（pyright、gopls、rust-analyzer 等）接入 `write_file` 和 `patch` 使用的写入后 lint 检查。"
---

--- body ---
# 语言服务器协议 (Language Server Protocol, LSP)

Hermes 以后台子进程运行完整的语言服务器 —— pyright、gopls、rust-analyzer、typescript-language-server、clangd 以及约 20 个其他语言服务器 —— 并将其语义诊断结果提供给 `write_file` 和 `patch` 使用的写入后 lint 检查。当智能体（Agent）编辑文件时，它能看到该编辑引入的确切错误 —— 不仅是语法错误，还包括语言服务器检测到的**类型错误、未定义的名称、缺失的导入以及项目级语义问题**。

这与顶级编码智能体使用的架构相同。Hermes 自带完整功能：无需编辑器宿主、无需安装插件、无需管理单独的守护进程。

## LSP 运行时机

LSP 的运行以 **git 工作区检测**为条件。当智能体的工作目录（或正在编辑的文件）位于 git 仓库内时，LSP 会针对该工作区运行。当两者都不在 git 仓库时，LSP 保持静默 —— 这对消息网关场景很有用，例如当前工作目录是用户的主目录且没有项目需要诊断。

检查是分层进行的：首先进行进程内语法检查（微秒级），语法通过后再进行 LSP 诊断。不稳定的或缺失的语言服务器永远不会中断写入 —— 每个 LSP 失败路径都会静默回退到仅语法检查的结果。

具体来说，每次成功执行 `write_file` 或 `patch` 时：

1. Hermes 捕获当前文件诊断结果的基线。
2. 执行写入操作。
3. 重新查询语言服务器，过滤掉基线上已有的诊断结果，只呈现新的诊断结果。

智能体会看到类似如下的输出：

```
{
  "bytes_written": 42,
  "dirs_created": false,
  "lint": {"status": "ok", "output": ""},
  "lsp_diagnostics": "LSP diagnostics introduced by this edit:\n<diagnostics file=\"/path/to/foo.py\">\nERROR [42:5] Cannot find name 'foo' [reportUndefinedVariable] (Pyright)\nERROR [50:1] Argument of type \"str\" is not assignable to \"int\" [reportArgumentType] (Pyright)\n</diagnostics>"
}
```

`lint` 字段携带语法检查结果（通过 `ast.parse`、`json.loads` 等进行的微秒级进程内解析）；`lsp_diagnostics` 字段携带来自真实语言服务器的语义诊断结果。两个通道，独立的信号 —— 智能体会看到一个语法正确的文件但存在语义问题，表现为 ``lint: ok`` 加上一个包含内容的 ``lsp_diagnostics``。

## 支持的语言

| 语言 | 服务器 | 自动安装 |
|----------|--------|--------------|
| Python | `pyright-langserver` | npm |
| TypeScript / JavaScript / JSX / TSX | `typescript-language-server` | npm |
| Vue | `@vue/language-server` | npm |
| Svelte | `svelte-language-server` | npm |
| Astro | `@astrojs/language-server` | npm |
| Go | `gopls` | `go install` |
| Rust | `rust-analyzer` | 手动 (rustup) |
| C / C++ | `clangd` | 手动 (LLVM) |
| Bash / Zsh | `bash-language-server` | npm |
| YAML | `yaml-language-server` | npm |
| Lua | `lua-language-server` | 手动 (GitHub releases) |
| PHP | `intelephense` | npm |
| OCaml | `ocaml-lsp` | 手动 (opam) |
| Dockerfile | `dockerfile-language-server-nodejs` | npm |
| Terraform | `terraform-ls` | 手动 |
| Dart | `dart language-server` | 手动 (dart sdk) |
| Haskell | `haskell-language-server` | 手动 (ghcup) |
| Julia | `julia` + LanguageServer.jl | 手动 |
| Clojure | `clojure-lsp` | 手动 |
| Nix | `nixd` | 手动 |
| Zig | `zls` | 手动 |
| Gleam | `gleam lsp` | 手动 (gleam install) |
| Elixir | `elixir-ls` | 手动 |
| Prisma | `prisma language-server` | 手动 |
| Kotlin | `kotlin-language-server` | 手动 |
| Java | `jdtls` | 手动 |

对于标记为“手动”的条目，请通过该语言合适的工具链管理器（rustup、ghcup、opam、brew 等）安装服务器。Hermes 会自动检测 PATH 或 `<HERMES_HOME>/lsp/bin/` 中的二进制文件。

少数服务器与 npm 无法自动拉取的同级依赖项一起安装。当前的情况是 `typescript-language-server`，它要求 `typescript` SDK 可以从同一个 `node_modules` 树中导入 —— 当您运行 `hermes lsp install typescript` 或首次使用时自动安装触发，Hermes 会同时安装这两个包。

## 命令行

```
hermes lsp status          # 服务状态 + 每个服务器的安装状态
hermes lsp list            # 注册表，可选 --installed-only
hermes lsp install <id>    # 主动安装一个服务器
hermes lsp install-all     # 尝试安装所有有已知安装方法的服务器
hermes lsp restart         # 关闭正在运行的客户端
hermes lsp which <id>      # 打印已解析的二进制文件路径
```

`hermes lsp status` 是最好的起点 —— 它会显示哪些语言今天可以获得语义诊断，哪些需要安装二进制文件。

## 配置

默认配置适用于典型设置；如果二进制文件在 PATH 中，则无需设置任何内容。

```yaml
# config.yaml
lsp:
  # 总开关。禁用后将跳过整个子系统 —— 不会启动任何服务器，不会运行后台事件循环。
  enabled: true

  # 每次写入后等待诊断结果的时间。
  wait_mode: document      # "document" 或 "full"
  wait_timeout: 5.0

  # 如何处理缺失的服务器二进制文件。
  #   auto    — 通过 npm/pip/go install 安装到 <HERMES_HOME>/lsp/bin
  #   manual  — 只使用已经在 PATH 上的二进制文件
  install_strategy: auto

  # 每个服务器的覆盖设置（全部可选）。
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      env: { PYRIGHT_LOG_LEVEL: "info" }
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true       # 即使扩展名匹配也跳过 TypeScript
```

### 每个服务器的键

* `disabled: true` —— 即使扩展名匹配文件，也完全跳过此服务器。
* `command: [bin, ...args]` —— 指定自定义二进制文件路径。绕过自动安装。
* `env: {KEY: value}` —— 传递给生成进程的额外环境变量。
* `initialization_options: {...}` —— 合并到 LSP `initialize` 握手时发送的 `initializationOptions` 负载中。服务器特定；请查阅语言服务器的文档。

## 安装位置

当 `install_strategy: auto` 时，Hermes 将二进制文件安装到 `<HERMES_HOME>/lsp/bin/`。npm 包位于 `<HERMES_HOME>/lsp/node_modules/`，bin 符号链接位于上一级目录。Go 二进制文件通过 `go install` 安装，`GOBIN` 指向暂存目录。

任何内容都不会安装到 `/usr/local/`、`~/.local/` 或其他共享位置 —— 暂存目录完全由 Hermes 拥有，当您重置配置文件时会被删除。

## 性能特征

LSP 服务器在首次使用时被**延迟生成**。在之前没有 `.py` 流量的项目中编辑 Python 文件会生成 pyright；大多数服务器的生成需要 1-3 秒（rust-analyzer 在冷项目上可能需要 10 秒以上）。同一工作区中的后续编辑会重用正在运行的服务器。

当没有发出诊断结果时，LSP 层为干净写入增加几毫秒时间。当发出诊断结果时，等待预算为 `wait_timeout` 秒 —— 通常 pyright/tsserver 在几十毫秒内响应，rust-analyzer 在索引处理中间需要几秒钟。

服务器在 Hermes 进程的生命周期内保持活动状态。没有空闲超时回收机制 —— 在每次写入时重启服务器索引的成本远高于保持守护进程。

## 禁用

在 `config.yaml` 中设置 `lsp.enabled: false` 以禁用整个子系统。写入后检查会回退到进程内语法检查（Python 使用 `ast.parse`，JSON 使用 `json.loads` 等），这与早期版本保持不变。

要禁用单个语言而不禁用整个层：

```yaml
lsp:
  servers:
    rust-analyzer:
      disabled: true
```

## 故障排除

**`hermes lsp status` 显示服务器为 "missing"**

二进制文件不在 PATH 上，也不在 `<HERMES_HOME>/lsp/bin/` 中。运行 `hermes lsp install <server_id>` 尝试自动安装，或通过该语言的正常工具链手动安装二进制文件。

**`hermes lsp status` 中的 `Backend warnings` 部分**

某些服务器作为一个薄包装器，实际诊断依赖于外部命令行工具 —— 它们正常启动并接受请求，但当 sidecar 二进制文件缺失时从不发出错误。最常见的情况是 `bash-language-server`，它将诊断委托给 `shellcheck`。当 `hermes lsp status` 显示 `Backend warnings` 部分时，通过您的操作系统包管理器安装列出的工具：

```
apt install shellcheck      # Debian / Ubuntu
brew install shellcheck     # macOS
scoop install shellcheck    # Windows
```

在服务器生成时，相同的警告会记录一次到 `~/.hermes/logs/agent.log`。

**服务器启动但从不返回诊断结果**

检查 `~/.hermes/logs/agent.log` 中的 `[agent.lsp.client]` 条目 —— 语言服务器的标准错误输出和协议错误都会记录在那里。某些服务器（尤其是 rust-analyzer）需要在发出每个文件的诊断结果之前完成项目范围的索引；服务器启动后的第一次编辑可能没有诊断结果完成，后续编辑会接续上。

**服务器崩溃**

崩溃的服务器会被添加到故障集合中，在本次会话期间不会重试。运行 `hermes lsp restart` 以清除该集合；下一次编辑会重新生成服务器。

**在 git 仓库外编辑文件**

根据设计，LSP 仅在 git 仓库内运行。如果项目尚未初始化，运行 `git init` 以启用 LSP 诊断。否则，会应用进程内仅语法检查的回退方案。