--- frontmatter ---
---
title: 工具搜索（Tool Search）
sidebar_position: 95
---

--- body ---
# 工具搜索（Tool Search）

当会话中附加了许多 MCP 服务器或非核心插件工具时，它们的 JSON 模式（JSON schemas）会在每一轮中消耗相当一部分上下文窗口（context window）——即便其中只有少数几个与用户实际请求相关。

**工具搜索（Tool Search）** 是 Hermes 为应对此问题提供的可选渐进式披露（progressive-disclosure）层。激活后，MCP 和插件工具会被三个桥接工具（bridge tools）替换到模型可见的工具数组（tools array）中，模型则按需加载每个特定工具的模式。

:::info 内置 Hermes 工具从不延迟
构成 Hermes 核心能力集的工具（`terminal`、`read_file`、`write_file`、`patch`、`search_files`、`todo`、`memory`、`browser_*`、`web_search`、`web_extract`、`clarify`、`execute_code`、`delegate_task`、`session_search`、`send_message` 以及其余 `_HERMES_CORE_TOOLS`）*始终*直接加载。只有 MCP 工具和非核心插件工具才符合延迟条件。
:::

## 工作原理

当工具搜索在某一轮中激活时，模型会看到三个新工具来代替被延迟的工具：

```
tool_search(query, limit?)     — 搜索延迟工具目录
tool_describe(name)            — 加载某个工具的完整模式
tool_call(name, arguments)     — 调用一个延迟工具
```

典型的交互过程如下：

```
模型：tool_search("创建一个 GitHub issue")
  → { matches: [{ name: "mcp_github_create_issue", ... }, ...] }
模型：tool_describe("mcp_github_create_issue")
  → { parameters: { type: "object", properties: { ... } } }
模型：tool_call("mcp_github_create_issue", { title: "...", body: "..." })
  → { ok: true, issue_number: 42 }
```

当模型调用 `tool_call` 时，Hermes **解开桥接**并将底层工具分派出去，就像模型直接调用它一样。预工具调用钩子（pre-tool-call hooks）、防护措施（guardrails）、审批提示（approval prompts）和后工具调用钩子（post-tool-call hooks）均针对真实工具名称运行——而非针对 `tool_call`。CLI 和网关中的活动馈送（activity feed）也会解开桥接，以便你看到底层工具，而不是桥接工具。

## 何时激活？

默认情况下，工具搜索以 `auto` 模式运行：仅当可延迟工具模式（deferrable tool schemas）消耗活动模型上下文窗口至少 10% 时才会激活。低于该阈值时，工具数组的组装是纯粹的直通（pass-through），你不会产生任何开销。

此决策在每次构建工具数组时都会重新评估，因此：

- 仅有少量 MCP 工具且使用长上下文模型的会话，永远不会激活工具搜索。
- 附加了许多 MCP 服务器（通常 15 个以上工具）的会话会开始激活它。
- 在会话中间移除 MCP 服务器，下次组装时会正确地恢复到直接暴露。

## 配置

```yaml
tools:
  tool_search:
    enabled: auto       # auto（默认）、on 或 off
    threshold_pct: 10   # 上下文百分比——仅在 auto 模式下使用
    search_default_limit: 5
    max_search_limit: 20
```

| 键 | 默认值 | 含义 |
| --- | --- | --- |
| `enabled` | `auto` | `auto` 在超过阈值时激活；`on` 只要存在至少一个可延迟工具就始终激活；`off` 完全禁用。 |
| `threshold_pct` | `10` | `auto` 模式触发的上下文长度百分比。范围 0–100。 |
| `search_default_limit` | `5` | 模型调用 `tool_search` 且未提供 `limit` 时返回的命中数。 |
| `max_search_limit` | `20` | 模型可通过 `limit` 请求的硬上限。范围 1–50。 |

你也可以使用传统的布尔形式：

```yaml
tools:
  tool_search: true   # 等同于 {enabled: auto}
```

## 何时不使用

工具搜索用固定的每轮令牌成本（三个桥接工具模式，约 300 个令牌）以及至少一次额外的往返（搜索→描述→调用）来换取延迟模式上的节省。当你拥有许多工具且每轮使用较少时，它显然是赢家；当工具总数很少时，它就成了开销。

`auto` 默认值会为你处理这一点。如果你无条件设置 `enabled: on`，预计在小工具集上会产生轻微的每轮成本。

## 无法消除的权衡

这些源于提示缓存完整性不变性（prompt-cache integrity invariant）——它们是任何渐进式披露设计所固有的，并非此实现特有：

- **冷工具上的额外一次往返。** 模型首次需要延迟工具时，会多花费一两次模型调用来查找并加载模式。静态侧的令牌节省是真实的，但一部分会在运行时被偿还。
- **延迟模式无缓存收益。** 加载后的 `tool_describe` 结果会进入对话历史（因此会在后续轮次中被缓存），但从未受益于系统提示缓存前缀（system-prompt cache prefix）。
- **模型质量依赖。** 工具搜索假设模型能够为所需工具编写合理的搜索查询。较小的模型在这方面表现较差；已发布的 Anthropic 数据（使用工具搜索与不使用相比，Opus 4 上从 49% 提升至 74%）显示了优势，但也表明约 26 个百分点的准确率仍然存在检索失败。
- **工具集编辑会使缓存失效。** 在会话中间添加或移除工具会改变桥接工具的描述（其中包含延迟工具的数量）以及目录，因此提示缓存会失效。这与任何工具集编辑的权衡相同。

## 实现细节

- **检索：** 对分词后的工具名称 + 描述 + 参数名称进行 BM25。当 BM25 返回零正分命中时，回退到工具名称的字面子串匹配，这可以防止零 IDF 的退化情况（例如，在目录中每个工具名称都包含 "github" 时搜索 `"github"`）。
- **目录在轮次之间是无状态的。** 每次组装时，它都会从当前工具定义列表重新构建——没有会话键控的 `Map`。这避免了存储的目录与实时工具注册表不同步的错误类别。
- **目录限定于会话的工具集。** `tool_search`、`tool_describe` 和 `tool_call` 只能看到并调用会话实际被授予的工具。被限制到工具集子集的子代理（subagent）、看板工作器（kanban worker）或网关会话，无法使用桥接来发现或调用该子集之外的工具——延迟目录是会话自身启用/禁用工具集的延迟切片，而非整个进程注册表。
- **无 JS 沙箱。** Hermes 使用更简单的"结构化工具"模式（search / describe / call 作为普通函数）。其他一些实现提供的 JS 沙箱"代码模式"攻击面较大；我们选择跳过它。

## 另请参阅

- `tools/tool_search.py` — 实现
- `tests/tools/test_tool_search.py` — 回归测试套件
- 原始实现 PR 中的 `openclaw-tool-search-report` PDF，其中包含塑造设计的研究