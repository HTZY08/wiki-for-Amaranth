---
title: "Spike — 在构建前验证想法的可丢弃实验"
sidebar_label: "Spike"
description: "在构建前验证想法的可丢弃实验"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# 尖峰实验（Spike）

在构建前验证想法的可丢弃实验。

## 技能元数据

| | |
|---|---|
| 来源 | 内建（默认安装） |
| 路径 | `skills/software-development/spike` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent（改编自 gsd-build/get-shit-done） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `spike`, `prototype`, `experiment`, `feasibility`, `throwaway`, `exploration`, `research`, `planning`, `mvp`, `proof-of-concept` |
| 相关技能 | [`sketch`](/docs/user-guide/skills/bundled/creative/creative-sketch), [`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development), [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是代理在技能激活时所看到的指令。
:::

# 尖峰实验（Spike）

当用户想要在真正构建前**试探某个想法**——验证可行性、比较不同方法、或揭示仅靠研究无法回答的未知因素时，使用此技能。尖峰实验本质上是可丢弃的。一旦它们完成了使命，就将其抛弃。

当用户说出类似“让我试试这个”“我想看看X是否可行”“把这个做成尖峰实验”“在我投入Y之前”“快速原型Z”“这到底可行吗？”或“比较A和B”时，加载此技能。

## 何时不使用此技能

- 答案可以通过文档或阅读代码得知——只需做研究，不要构建
- 工作是生产路径——改用 `plan` 技能
- 想法已验证——直接跳到实现

## 如果用户安装了完整的 GSD 系统

如果 `gsd-spike` 作为同级技能出现（通过 `npx get-shit-done-cc --hermes` 安装），当用户需要完整的 GSD 工作流时，**优先使用 `gsd-spike`**：包括持久的 `.planning/spikes/` 状态、跨会话的 MANIFEST 追踪、Given/When/Then 裁决格式，以及与 GSD 其余部分集成的提交模式。本技能是轻量级独立版本，适用于没有（或不想要）完整系统的用户。

## 核心方法（Core method）

无论规模如何，每个尖峰实验都遵循以下循环：

```
分解（decompose）  →  研究（research）  →  构建（build）  →  裁决（verdict）
   ↑__________________________________________↓
                根据发现进行迭代（iterate on findings）
```

### 1. 分解（Decompose）

将用户的想法分解成 **2-5 个独立的可行性问题**。每个问题就是一个尖峰实验。以表格形式呈现，使用 Given/When/Then 框架：

| # | 尖峰实验（Spike） | 验证内容（Given/When/Then） | 风险 |
|---|--------------------|------------------------------|------|
| 001 | websocket-streaming | 给定一个 WS 连接，当 LLM 流式传输 token 时，客户端接收到的块时间 < 100ms | 高 |
| 002a | pdf-parse-pdfjs | 给定一个多页 PDF，当使用 pdfjs 解析时，可提取出结构化文本 | 中 |
| 002b | pdf-parse-camelot | 给定一个多页 PDF，当使用 camelot 解析时，可提取出结构化文本 | 中 |

**尖峰实验类型：**
- **标准实验（standard）** — 用一种方法回答一个问题
- **比较实验（comparison）** — 同一个问题，用不同的方法（共享编号，字母后缀 `a`/`b`/`c`）

**好的尖峰实验问题：** 具有可观察输出的具体可行性。
**不好的尖峰实验问题：** 过于宽泛、没有可观察输出、或仅仅是“阅读关于 X 的文档”。

**按风险排序。** 最可能扼杀想法的尖峰实验先进行。如果困难部分行不通，那么对简单部分进行原型设计就没有意义。

**跳过分解** 仅在用户已经确切知道他们想要尖峰实验什么并明确说明的情况下。此时直接将他们的想法视为一个单独的尖峰实验。

### 2. 对齐（Align）（针对多尖峰实验的想法）

呈现尖峰实验表格。询问：“按此顺序全部构建，还是需要调整？” 在你写任何代码之前，让用户进行删除、重新排序或重新框架。

### 3. 研究（Research）（每个尖峰实验，在构建前）

尖峰实验并非不做研究——你进行足够的研究以选择正确的方法，然后再进行构建。每个尖峰实验：

1. **简要说明（Brief it）。** 2-3 句话：这个尖峰实验是什么，为什么重要，关键风险。
2. **列出竞争方法（Surface competing approaches）** 如果确实存在多种选择：

   | 方法（Approach） | 工具/库（Tool/Library） | 优点（Pros） | 缺点（Cons） | 状态（Status） |
   |------------------|-------------------------|--------------|--------------|----------------|
   | ... | ... | ... | ... | 维护中 / 废弃 / 测试版 |

3. **选择一个。** 说明理由。如果有 2 个或以上方法可信，则在尖峰实验内部构建快速变体。
4. **跳过研究** 针对没有外部依赖的纯逻辑。

研究步骤使用 Hermes 工具：

- `web_search("python websocket streaming libraries 2025")` — 查找候选库
- `web_extract(urls=["https://websockets.readthedocs.io/..."])` — 阅读实际文档（返回 markdown）
- `terminal("pip show websockets | grep Version")` — 检查项目虚拟环境中已安装的内容

对于没有文档页面的库，通过 `read_file` 克隆并阅读它们的 `README.md` / `examples/`。如果用户配置了 Context7 MCP，这也是一个很好的信息来源——`mcp_*_resolve-library-id` 然后 `mcp_*_query-docs`。

### 4. 构建（Build）

每个尖峰实验一个目录。保持独立。

<!-- ascii-guard-ignore -->
```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
├── 002a-pdf-parse-pdfjs/
│   ├── README.md
│   └── parse.js
└── 002b-pdf-parse-camelot/
    ├── README.md
    └── parse.py
```
<!-- ascii-guard-ignore-end -->

**优先选择用户能够与之交互的内容。** 当唯一的输出是一行“它成功了”的日志时，尖峰实验就失败了。用户想要*感受到*尖峰实验在起作用。默认选择，按偏好顺序：

1. 一个可运行的 CLI，接受输入并打印可观察输出
2. 一个演示行为的最小 HTML 页面
3. 一个具有一个端点的小型 Web 服务器
4. 一个单元测试，用可识别的断言来验证问题

**深度优先于速度。** 永远不要在运行一次快乐路径后就声明“它成功了”。测试边缘情况。追踪意外的发现。只有当调查是诚实的时，裁决才是可信的。

**避免** 除非尖峰实验特别需要：复杂的包管理、构建工具/bundler、Docker、环境变量文件、配置系统。硬编码一切——它只是一个尖峰实验。

**构建单个尖峰实验** —— 典型的工具序列：

```
terminal("mkdir -p spikes/001-websocket-streaming")
write_file("spikes/001-websocket-streaming/README.md", "# 001: websocket-streaming\n\n...")
write_file("spikes/001-websocket-streaming/main.py", "...")
terminal("cd spikes/001-websocket-streaming && python3 main.py")
# 观察输出，迭代。
```

**并行比较尖峰实验（002a / 002b）—— 委派（delegate）。** 当两种方法可以并行运行并且两者都需要真正的工程工作（而不是 10 行的原型）时，使用 `delegate_task` 进行委派：

```
delegate_task(tasks=[
    {"goal": "构建 002a-pdf-parse-pdfjs: ...", "toolsets": ["terminal", "file", "web"]},
    {"goal": "构建 002b-pdf-parse-camelot: ...", "toolsets": ["terminal", "file", "web"]},
])
```

每个子代理返回自己的裁决；你撰写正面对比。

### 5. 裁决（Verdict）

每个尖峰实验的 `README.md` 以以下内容结尾：

```markdown
## 裁决：已验证 | 部分验证 | 无效

### 有效部分
- ...

### 无效部分
- ...

### 意外发现
- ...

### 对实际构建的建议
- ...
```

**已验证（VALIDATED）** = 核心问题得到了肯定的回答，并有证据。
**部分验证（PARTIAL）** = 在约束条件 X, Y, Z 下可用——记录这些约束。
**无效（INVALIDATED）** = 因这个原因不可行。这是一个成功的尖峰实验。

## 比较尖峰实验（Comparison spikes）

当两种方法回答同一个问题（002a / 002b）时，**接连构建**它们，然后最后做一个正面对比：

```markdown
## 正面对比：pdfjs vs camelot

| 维度 | pdfjs (002a) | camelot (002b) |
|-------|--------------|----------------|
| 提取质量 | 结构化 9/10 | 仅表格 7/10 |
| 搭建复杂度 | npm install, 1 行 | pip + ghostscript |
| 对 100 页 PDF 的性能 | 3 秒 | 18 秒 |
| 处理旋转文本 | 否 | 是 |

**胜者：** 对于我们的用例，pdfjs 胜出。如果将来需要优先从表格提取，则使用 camelot。
```

## 前沿模式（Frontier mode）（决定下一步进行哪个尖峰实验）

如果已经存在尖峰实验，用户问“接下来我应该尖峰实验什么？”，遍历现有目录并寻找：

- **集成风险** — 两个已验证的尖峰实验触及同一资源，但独立测试
- **数据交接** — 尖峰实验 A 的输出被假定与尖峰实验 B 的输入兼容，但从未证实
- **愿景中的空白** — 假定但未经证明的能力
- **替代方法** — 针对部分验证或无效尖峰实验的不同角度

以 Given/When/Then 形式提出 2-4 个候选。让用户选择。

## 输出（Output）

- 在仓库根目录创建 `spikes/` 目录（如果用户使用 GSD 约定，则创建 `.planning/spikes/`）
- 每个尖峰实验一个目录：`NNN-descriptive-name/`
- 每个尖峰实验的 `README.md` 记录问题、方法、结果和裁决
- 保持代码可丢弃——一个需要 2 天“清理以用于生产”的尖峰实验是一个糟糕的尖峰实验

## 归属（Attribution）

改编自 GSD（Get Shit Done）项目的 `/gsd-spike` 工作流 — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done))。完整的 GSD 系统提供持久的尖峰实验状态、MANIFEST 追踪以及与更广泛的规范驱动开发管线的集成；使用 `npx get-shit-done-cc --hermes --global` 安装。