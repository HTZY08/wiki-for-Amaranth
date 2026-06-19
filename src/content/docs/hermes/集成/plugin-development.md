---
title: "Hermes Agent 插件开发：从论文概念到可运行工具"
description: "基于 4 个实际插件的完整开发流程——plugin.yaml、register()、工具注册、踩坑记录"
---

# Hermes Agent 插件开发教程

Hermes Agent 的插件系统允许你通过标准接口注入自定义工具。本文以 4 个已上线的插件为例，从 `plugin.yaml` 到 `__init__.py` 完整讲解开发流程。

这些插件的特殊之处在于：每个都来自一篇 AI 论文的架构思想，映射到了 Agent 工具中。不是"论文复现"，而是"论文概念→Agent 模式"的转换。

---

## 一、插件系统基础

### 目录结构

```
$HERMES_HOME/plugins/<plugin-name>/
├── plugin.yaml      # 元信息：名称、版本、注册的工具
└── __init__.py      # 核心逻辑 + register() 入口
```

目录名就是插件名。放在 `$HERMES_HOME/plugins/`（你的环境下是 `/opt/data/plugins/`）。

### plugin.yaml

```yaml
name: plugin-name
version: 1.0.0
description: 一句话描述
tools:
  - tool_name_1    # 提供给 Hermes 的工具名
  - tool_name_2
```

`tools` 列表里的名称对应你要注册的工具。Hermes 框架根据这个列表知道这个插件提供了哪些能力。

### __init__.py 结构

```python
def register(ctx):
    """插件入口，在加载时被 Hermes 调用。"""
    ctx.register_tool(
        "tool_name",      # 工具名（agent 对话中可见）
        ["web"],          # 工具集（toolset，决定可用工具范围）
        schema,           # JSON Schema 定义参数
        handler,          # 处理函数
        "描述文字",
        emoji="🔧"        # 显示用的 emoji
    )
```

**关键点：** `ctx.register_tool()` 接受**位置参数**，不是字典。很多新手在这里翻车。

### 在 config.yaml 中启用

```yaml
plugins:
  enabled:
    - plugin-name
  disabled: []
```

配置后重启 Hermes（或新会话）即可生效。

---

## 二、四个实战插件

以下是 4 个已上线的插件，全部来自论文概念映射。

### 2.1 flyroute — 隐式技能路由

**论文参考：** FlyLoRA (NeurIPS 2025) — 受果蝇嗅觉回路启发的低秩适应

**功能：** 根据用户输入，自动匹配最合适的技能。不需要用户手动指定"我要用哪个工具"。

**核心逻辑：**

```python
# 预定义 N 个技能类别，每个有名称、关键词和描述
SKILLS = [
    {"name": "code-review",   "keywords": ["code review", "审查", "review pr"]},
    {"name": "debugging",     "keywords": ["debug", "fix", "bug", "报错"]},
    {"name": "writing",       "keywords": ["write", "撰写", "draft"]},
    # ...
]

def _route_skills(user_input, top_k=3):
    # 用关键词匹配 + 余弦相似度找到 top-k 技能
    return sorted_skills[:top_k]
```

**工具签名：** `flyroute_select()` — 无参数，返回路由结果。

**代码量：** 77 行。

### 2.2 lori-selector — 稀疏工具选择

**论文参考：** LoRI (COLM 2025) — 冻结 A + 稀疏 B 掩码

**功能：** 根据用户输入，只激活部分工具子集，减少上下文噪音。

**核心逻辑：**

```python
# 按优先级排列的任务类型
TASKS = {
    "code_dev":     r"code|代码|implement|def |class |function|refactor",
    "file_ops":     r"file|文件|read|write|save|保存",
    "web_research": r"research|search|find|查|搜索|调研",
    "agent_orch":   r"plan|schedule|安排|协调",
    "knowledge":    r"what is|explain|什么是|解释",
}

def classify(text):
    for task, pattern in TASKS.items():
        if re.search(pattern, text, re.I):
            return task
    return "agent_orch"
```

**工具签名：** `lori_select()` — 无参数，返回选中的任务类型和工具子集。

**代码量：** 72 行。

### 2.3 mudd-orchestrator — 多路工作流编排

**论文参考：** MUDDFormer (ICML 2025) — Q/K/V/R 四路动态连接

**功能：** 将用户输入路由到四条工作流路径之一：execute（执行）、interact（交互）、query（查询）、knowledge（知识）。

**核心逻辑：**

```python
ROUTES = {
    "execute":   r"run|执行|deploy|build|install",
    "interact":  r"chat|talk|discuss|讨论",
    "query":     r"search|find|查|lookup",
    "knowledge": r"what|explain|why|how|什么是",
}

def route(text):
    for route_name, pattern in ROUTES.items():
        if re.search(pattern, text, re.I):
            return {"route": route_name, "max_turns": ...}
    return {"route": "knowledge", "max_turns": 3}
```

**工具签名：** `mudd_orchestrate()` — 无参数，返回路由决策。

**代码量：** 59 行。

### 2.4 multiverse-mapreduce — 并行任务分解

**论文参考：** Multiverse (NeurIPS 2025) — MapReduce 并行推理

**功能：** 将复杂目标拆解为可并行执行的子任务，最后合并结果。

**核心逻辑：**

```python
def analyze(goal):
    tasks = []
    # 检测 "X 和 Y"、"对比/比较 A 和 B" 等模式
    parts = re.split(r'和|与|、|跟|还有', goal)
    if len(parts) > 1:
        for p in parts:
            tasks.append({"goal": p.strip(), "toolsets": ["web"]})
    return tasks

def merge(results):
    # 合并多个子任务的结果
    combined = "\n\n".join(r["summary"] for r in results)
    return combined
```

**工具签名：** 两个工具：
- `multiverse_analyze(goal)` — 分析目标，返回子任务列表
- `multiverse_merge(results)` — 合并多路结果

**代码量：** 85 行。

---

## 三、开发流程

### 3.1 脚手架

```
1. 在 plugins/ 下创建目录
2. 写 plugin.yaml
3. 写 __init__.py（register 函数 + 业务逻辑）
4. 加到 config.yaml 的 enabled 列表中
5. 新会话 / 重启 Hermes
6. 测试工具是否出现
```

### 3.2 测试方法

```bash
# 检查插件是否被加载
hermes plugins list

# 在对话中触发——调用你注册的工具名
# 如果工具注册成功，Hermes 会自动选择它
```

### 3.3 调试技巧

- **工具没出现？** 检查 `config.yaml` 拼写和 `plugin.yaml` 中的 `tools` 列表
- **register 报错？** 确认 `ctx.register_tool()` 是**位置参数**，不是关键字字典
- **工具调用了但没反应？** 检查 handler 函数的签名和返回格式
- **类太难写？** 所有 4 个插件都是纯函数，没有 class，没有异步

---

## 四、踩坑记录

| 坑 | 原因 | 修复 |
|----|------|------|
| register() 传了字典 | 文档示例曾用 `**kwargs` 风格 | 改为位置参数：`ctx.register_tool(name, toolset, schema, handler, desc, emoji=emoji)` |
| 插件不生效 | 名称拼写错误或 plugin.yaml 格式不对 | 检查 `config.yaml` 中的名称和插件的目录名、plugin.yaml 中的 `name` 三处一致 |
| 工具不出现但在 enabled 列表 | 未重启 Hermes | 插件需要新会话加载 |
| handler 没被调用 | handler 函数未注册或返回格式不对 | handler 应返回字符串或 dict，不要 print |

---

## 五、从论文到插件的思路

这不是"论文复现"——每个插件只有 60-85 行代码，不可能实现完整的论文算法。

思路是：**提取论文的抽象模式，映射到 Agent 场景**。

| 论文 | 核心概念 | 映射到 Agent |
|------|---------|-------------|
| FlyLoRA | 果蝇嗅觉 → 低秩适应 | 关键词 → 技能路由 |
| LoRI | 冻结 A + 稀疏 B | 关键词优先级 → 工具选择 |
| MUDDFormer | Q/K/V/R 四路连接 | 四类路由 → 工作流路径 |
| Multiverse | MapReduce 并行推理 | 任务分解 → 并行执行 → 合并 |

核心价值不是"实现了论文"，而是"理解了论文的抽象思想，并在 Agnet 系统中找到了它的作用位置"。

---

## 六、参考

- 插件源码：`/opt/data/plugins/`（flyroute、lori-selector、mudd-orchestrator、multiverse-mapreduce）
- Hermes 技能：`hermes-plugin-authoring`
- 项目完整文档：`/opt/data/projects/lau-hermes-improvements/`
