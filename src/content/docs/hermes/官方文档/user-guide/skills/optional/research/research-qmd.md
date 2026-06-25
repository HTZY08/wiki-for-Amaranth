---
title: "Qmd"
sidebar_label: "Qmd"
description: "使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录——qmd 是一个混合检索引擎，结合了 BM25、向量搜索和 LLM 重排序。"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Qmd

使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录——qmd 是一个混合检索引擎，结合了 BM25、向量搜索和 LLM 重排序。支持 CLI 和 MCP 集成（Integration）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/research/qmd` 安装 |
| 路径 | `optional-skills/research/qmd` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent + Teknium |
| 许可协议 | MIT |
| 平台 | macos, linux |
| 标签 | `搜索`, `知识库`, `RAG`, `笔记`, `MCP`, `本地AI` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian), `native-mcp`, [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# QMD — 查询标记文档（Query Markup Documents）

用于个人知识库的本地设备端搜索引擎。为 Markdown 笔记、会议记录、文档以及任何基于文本的文件建立索引，然后提供结合关键词匹配、语义理解和 LLM 重排序的混合搜索——所有操作均在本地运行，无需依赖云端。

由 [Tobi Lütke](https://github.com/tobi/qmd) 创建。采用 MIT 许可协议。

## 何时使用

- 用户要求搜索其笔记、文档、知识库或会议记录
- 用户希望在大规模 Markdown/文本文件中查找内容
- 用户需要语义搜索（“查找关于 X 概念的笔记”），而不仅仅是关键词 grep
- 用户已经设置了 qmd 集合（Collection）并希望进行查询
- 用户要求建立本地知识库或文档搜索系统
- 关键词：“搜索我的笔记”、“在我的文档中查找”、“知识库”、“qmd”

## 前提条件

### Node.js >= 22（必须）

```bash
# 检查版本
node --version  # 必须 >= 22

# macOS —— 通过 Homebrew 安装或升级
brew install node@22

# Linux —— 使用 NodeSource 或 nvm
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
# 或使用 nvm：
nvm install 22 && nvm use 22
```

### 支持扩展的 SQLite（仅 macOS）

macOS 系统自带的 SQLite 缺少扩展加载功能。通过 Homebrew 安装：

```bash
brew install sqlite
```

### 安装 qmd

```bash
npm install -g @tobilu/qmd
# 或使用 Bun：
bun install -g @tobilu/qmd
```

首次运行时会自动下载 3 个本地 GGUF 模型（共约 2GB）：

| 模型 | 用途 | 大小 |
|-------|---------|------|
| embeddinggemma-300M-Q8_0 | 向量嵌入（Vector embeddings） | ~300MB |
| qwen3-reranker-0.6b-q8_0 | 结果重排序（Result reranking） | ~640MB |
| qmd-query-expansion-1.7B | 查询扩展（Query expansion） | ~1.1GB |

### 验证安装

```bash
qmd --version
qmd status
```

## 快速参考

| 命令 | 功能 | 速度 |
|---------|-------------|-------|
| `qmd search "query"` | BM25 关键词搜索（无需模型） | ~0.2s |
| `qmd vsearch "query"` | 语义向量搜索（需加载 1 个模型） | ~3s |
| `qmd query "query"` | 混合搜索 + 重排序（需加载全部 3 个模型） | 已预热 ~2-3s，冷启动 ~19s |
| `qmd get <docid>` | 检索完整文档内容 | 即时 |
| `qmd multi-get "glob"` | 批量检索多个文件 | 即时 |
| `qmd collection add <path> --name <n>` | 添加目录作为集合 | 即时 |
| `qmd context add <path> "description"` | 添加上下文元数据以提升检索质量 | 即时 |
| `qmd embed` | 生成/更新向量嵌入 | 视情况而定 |
| `qmd status` | 显示索引健康状态和集合信息 | 即时 |
| `qmd mcp` | 启动 MCP 服务器（stdio 模式） | 持久运行 |
| `qmd mcp --http --daemon` | 启动 MCP 服务器（HTTP，模型已预热） | 持久运行 |

## 设置工作流

### 1. 添加集合

将 qmd 指向包含文档的目录：

```bash
# 添加笔记目录
qmd collection add ~/notes --name notes

# 添加项目文档
qmd collection add ~/projects/myproject/docs --name project-docs

# 添加会议记录
qmd collection add ~/meetings --name meetings

# 列出所有集合
qmd collection list
```

### 2. 添加上下文描述

上下文元数据（Context metadata）可帮助搜索引擎理解每个集合的内容，显著提升检索质量：

```bash
qmd context add qmd://notes "个人笔记、想法和日记条目"
qmd context add qmd://project-docs "主项目的技术文档"
qmd context add qmd://meetings "团队同步会议的记录和待办事项"
```

### 3. 生成嵌入

```bash
qmd embed
```

该命令会处理所有集合中的所有文档，生成向量嵌入。添加新文档或新集合后，需重新运行此命令。

### 4. 验证

```bash
qmd status   # 显示索引健康状态、集合统计和模型信息
```

## 搜索模式

### 快速关键词搜索（BM25）

最适合：精确术语、代码标识符、名称、已知短语。
无需加载模型——几乎即时返回结果。

```bash
qmd search "authentication middleware"
qmd search "handleError async"
```

### 语义向量搜索（Semantic Vector Search）

最适合：自然语言问题、概念性查询。
需加载嵌入模型（首次查询约 3s）。

```bash
qmd vsearch "how does the rate limiter handle burst traffic"
qmd vsearch "ideas for improving onboarding flow"
```

### 混合搜索 + 重排序（最佳质量）

最适合：对质量要求较高的关键查询。
使用全部 3 个模型——查询扩展、并行 BM25+向量搜索、重排序。

```bash
qmd query "what decisions were made about the database migration"
```

### 结构化多模式查询

在同一查询中组合不同搜索类型以实现精确性：

```bash
# BM25 用于精确术语 + 向量用于概念
qmd query $'lex: rate limiter\nvec: how does throttling work under load'

# 带查询扩展
qmd query $'expand: database migration plan\nlex: "schema change"'
```

### 查询语法（lex/BM25 模式）

| 语法 | 效果 | 示例 |
|--------|--------|---------|
| `term` | 前缀匹配 | `perf` 匹配 "performance" |
| `"phrase"` | 精确词组 | `"rate limiter"` |
| `-term` | 排除术语 | `performance -sports` |

### HyDE（假设性文档嵌入，Hypothetical Document Embeddings）

对于复杂主题，编写您期望看到的答案形式：

```bash
qmd query $'hyde: The migration plan involves three phases. First, we add the new columns without dropping the old ones. Then we backfill data. Finally we cut over and remove legacy columns.'
```

### 限定集合范围

```bash
qmd search "query" --collection notes
qmd query "query" --collection project-docs
```

### 输出格式

```bash
qmd search "query" --json        # JSON 输出（最适合解析）
qmd search "query" --limit 5     # 限制结果数量
qmd get "#abc123"                # 按文档 ID 获取
qmd get "path/to/file.md"       # 按文件路径获取
qmd get "file.md:50" -l 100     # 获取指定行范围
qmd multi-get "journals/*.md" --json  # 按 glob 模式批量检索
```

## MCP 集成（推荐）

qmd 提供了一个 MCP 服务器，可通过 Hermes Agent 的本地 MCP 客户端直接使用搜索工具。这是首选的集成方式——配置完成后，代理无需加载本技能即可自动获得 qmd 工具。

### 选项 A：Stdio 模式（简单）

添加到 `~/.hermes/config.yaml`：

```yaml
mcp_servers:
  qmd:
    command: "qmd"
    args: ["mcp"]
    timeout: 30
    connect_timeout: 45
```

这将注册以下工具：`mcp_qmd_search`、`mcp_qmd_vsearch`、`mcp_qmd_deep_search`、`mcp_qmd_get`、`mcp_qmd_status`。

**权衡：** 模型在首次搜索调用时加载（冷启动约 19s），之后在该会话期间保持预热。适合偶尔使用。

### 选项 B：HTTP 守护进程模式（快速，推荐频繁使用）

单独启动 qmd 守护进程——它会在内存中保持模型预热：

```bash
# 启动守护进程（在 Agent 重启后仍持续运行）
qmd mcp --http --daemon

# 默认运行在 http://localhost:8181
```

然后配置 Hermes Agent 通过 HTTP 连接：

```yaml
mcp_servers:
  qmd:
    url: "http://localhost:8181/mcp"
    timeout: 30
```

**权衡：** 运行时占用约 2GB 内存，但每次查询都很快（约 2-3s）。最适合频繁搜索的用户。

### 保持守护进程运行

#### macOS（launchd）

```bash
cat > ~/Library/LaunchAgents/com.qmd.daemon.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.qmd.daemon</string>
  <key>ProgramArguments</key>
  <array>
    <string>qmd</string>
    <string>mcp</string>
    <string>--http</string>
    <string>--daemon</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/qmd-daemon.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/qmd-daemon.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.qmd.daemon.plist
```

#### Linux（systemd 用户服务）

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/qmd-daemon.service << 'EOF'
[Unit]
Description=QMD MCP 守护进程
After=network.target

[Service]
ExecStart=qmd mcp --http --daemon
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now qmd-daemon
systemctl --user status qmd-daemon
```

### MCP 工具参考

连接成功后，以下工具将以 `mcp_qmd_*` 形式提供：

| MCP 工具 | 对应命令 | 描述 |
|----------|---------|-------------|
| `mcp_qmd_search` | `qmd search` | BM25 关键词搜索 |
| `mcp_qmd_vsearch` | `qmd vsearch` | 语义向量搜索 |
| `mcp_qmd_deep_search` | `qmd query` | 混合搜索 + 重排序 |
| `mcp_qmd_get` | `qmd get` | 按 ID 或路径检索文档 |
| `mcp_qmd_status` | `qmd status` | 索引健康状态和统计 |

MCP 工具接受结构化 JSON 查询以实现多模式搜索：

```json
{
  "searches": [
    {"type": "lex", "query": "authentication middleware"},
    {"type": "vec", "query": "how user login is verified"}
  ],
  "collections": ["project-docs"],
  "limit": 10
}
```

## CLI 使用（无需 MCP）

当未配置 MCP 时，可直接通过终端使用 qmd：

```
terminal(command="qmd query 'what was decided about the API redesign' --json", timeout=30)
```

对于设置和管理任务，始终使用终端：

```
terminal(command="qmd collection add ~/Documents/notes --name notes")
terminal(command="qmd context add qmd://notes '个人研究笔记和想法'")
terminal(command="qmd embed")
terminal(command="qmd status")
```

## 搜索管道工作原理

了解内部机制有助于选择正确的搜索模式：

1. **查询扩展（Query Expansion）** ——一个经过微调的 1.7B 模型生成 2 个备选查询。原始查询在融合中权重为 2 倍。
2. **并行检索（Parallel Retrieval）** ——BM25（SQLite FTS5）和向量搜索在所有查询变体上同时运行。
3. **RRF 融合（Reciprocal Rank Fusion）** ——倒数排名融合（k=60）合并结果。排名加成：第 1 名 +0.05，第 2-3 名 +0.02。
4. **LLM 重排序（LLM Reranking）** ——qwen3-reranker 对前 30 个候选结果评分（0.0-1.0）。
5. **位置感知混合（Position-Aware Blending）** ——排名 1-3：75% 检索分数 / 25% 重排序分数。排名 4-10：60/40。排名 11+：40/60（长尾部分更信任重排序）。

**智能分块（Smart Chunking）：** 文档在自然断点（标题、代码块、空行）处拆分，目标约 900 个 token，重叠 15%。代码块永远不会在块中间拆分。

## 最佳实践

1. **始终添加上下文描述** ——`qmd context add` 能显著提升检索准确性。描述每个集合包含的内容。
2. **添加文档后重新嵌入** ——当集合中添加新文件后，必须重新运行 `qmd embed`。
3. **需要速度时使用 `qmd search`** ——当需要快速关键词查找（代码标识符、精确名称）时，BM25 即时生效，无需模型。
4. **需要质量时使用 `qmd query`** ——当问题是概念性的或用户需要最佳结果时，使用混合搜索。
5. **优先选择 MCP 集成** ——配置完成后，Agent 无需每次加载本技能即可原生调用工具。
6. **频繁用户使用守护进程模式** ——如果用户经常搜索知识库，推荐设置 HTTP 守护进程。
7. **结构化搜索中的第一个查询权重为 2 倍** ——在组合 lex 和 vec 时，将最重要/最确定的查询放在第一位。

## 故障排除

### "首次运行时正在下载模型"
正常现象——qmd 在首次使用时自动下载约 2GB 的 GGUF 模型。这是一次性操作。

### 冷启动延迟（约 19s）
当模型未加载到内存时会发生。解决方案：
- 使用 HTTP 守护进程模式（`qmd mcp --http --daemon`）保持预热
- 当不需要模型时，使用 `qmd search`（仅 BM25）
- MCP stdio 模式在首次搜索时加载模型，并在会话期间保持预热

### macOS："unable to load extension"
安装 Homebrew 版本的 SQLite：`brew install sqlite`，然后确保其位于系统 SQLite 的 PATH 之前。

### "No collections found"
运行 `qmd collection add <path> --name <name>` 添加目录，然后运行 `qmd embed` 建立索引。

### 嵌入模型覆盖（CJK/多语言）
对于非英语内容，设置 `QMD_EMBED_MODEL` 环境变量：
```bash
export QMD_EMBED_MODEL="your-multilingual-model"
```

## 数据存储

- **索引和向量：** `~/.cache/qmd/index.sqlite`
- **模型：** 首次运行时自动下载到本地缓存
- **无云端依赖** ——所有操作均在本地运行

## 参考资料

- [GitHub: tobi/qmd](https://github.com/tobi/qmd)
- [QMD 变更日志](https://github.com/tobi/qmd/blob/main/CHANGELOG.md)