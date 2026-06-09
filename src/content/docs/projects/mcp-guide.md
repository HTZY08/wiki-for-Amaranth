---
title: MCP 详解
description: Model Context Protocol——外部工具接入系统
---

> MCP（Model Context Protocol）是一个开放协议，让 AI 代理通过标准接口调用外部工具。
> 简单说：这是 Hermes 的"插件系统"。

---

## 概念

```
MCP Server（工具提供方）       MCP Client（Hermes）
      │                              │
      │  ——— list_tools() ——————→    │
      │  ←—— 返回工具列表 —————      │
      │                              │
      │  ——— call_tool("xxx") ——→    │
      │  ←—— 返回结果 ————————      │
```

MCP Server 是一个独立进程（或远程服务），注册到 Hermes 后，它的工具就跟内置工具（`terminal`、`read_file` 等）一样可以直接调用。

---

## 当前配置的 MCP Servers

```yaml
# `~/.hermes/config.yaml` 中的 `mcp_servers` 配置（示例路径，实际以部署为准）
mcp_servers:
  mcp_search:          # 统一搜索（自动 fallback 多个后端）
    command: "python3"
    args: ["/opt/data/scripts/mcp_search_server.py"]

  perplexity:          # Perplexity AI 搜索（通过 OpenRouter）
    command: "python3"
    args: ["/opt/data/scripts/perplexity_mcp_server.py"]
    env:
      OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}"
      HTTP_PROXY: "http://127.0.0.1:7890"
      HTTPS_PROXY: "http://127.0.0.1:7890"
```

每次 Hermes 启动时自动连接这些服务器，发现它们的工具后注册到系统中。

---

## 注册的工具

MCP 工具以 `mcp_{服务器名}_{工具名}` 格式命名：

| 工具名 | 来自 | 做什么 |
|--------|------|--------|
| `mcp_mcp_search_mcp_search` | mcp_search | 统一网页搜索（多后端 fallback） |
| `mcp_perplexity_perplexity_search` | perplexity | Perplexity 搜索（附引用来源） |

这些工具对 AI 来说是透明的——她不需要知道哪些是内置工具、哪些是 MCP 工具，直接调用就行。

---

## 配置方式

### 添加一个新的 MCP Server

在 `/opt/data/config.yaml` 的 `mcp_servers` 下添加：

```yaml
mcp_servers:
  服务器名:
    command: "npx"                    # 启动命令
    args: ["-y", "包名"]              # 参数
    env:                              # 环境变量
      变量名: "值"
    timeout: 60                       # 超时（秒）
```

两种连接方式：

| 方式 | 适用 | 配置 |
|------|------|------|
| **stdio** | 本地进程 | `command` + `args` |
| **HTTP** | 远程服务 | `url` + `headers` |

### 重启生效

添加或修改后，重启 Hermes 即可：

```bash
# 或者直接告诉 Amaranth "重启一下"
```

### 环境变量安全

MCP 子进程**不会继承**宿主机的全部环境变量——只传递 `PATH`、`HOME` 等基础变量。API Key 等敏感信息必须通过 `env:` 显式传入，或使用 `${VAR}` 语法从 `.env` 插值。

---

## 常见 MCP Server 示例

### 文件系统访问

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### GitHub

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### 时间

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

---

## 和 Skill 的区别

| | Skill | MCP Tool |
|------|-------|----------|
| **本质** | 给 AI 读的文本指令 | 可执行的代码函数 |
| **做什么** | 告诉 AI"怎么做" | AI 直接调用"帮你做" |
| **输入** | 自然语言指令 | 结构化参数（JSON） |
| **输出** | 无（只是 context） | 返回数据结构 |
| **典型场景** | 微信排障步骤、生图 prompt | 搜索网页、读取文件、调 API |

---

## 故障排查

### MCP 工具没出现

```bash
# ① MCP SDK 装了没？
pip list | grep mcp

# ② 配置文件有 mcp_servers 吗？
grep -A5 "mcp_servers" /opt/data/config.yaml

# ③ 启动日志里有错误吗？
tail -20 /opt/data/logs/errors.log | grep -i mcp
```

### "Failed to connect to MCP server"

常见原因：

- **命令不存在**——`npx` / `uvx` 没装
- **网络问题**——npx 下载包时需要联网，代理可能拦截
  - 修复：在 MCP server 的 `env` 里加 `HTTP_PROXY` / `HTTPS_PROXY`
- **超时**——服务器启动太慢，增加 `connect_timeout`

---

*PS：MCP 是一个相对新的协议，生态还在快速变化。如果某个社区 MCP server 不稳定，删掉就好，不影响其他部分。*
