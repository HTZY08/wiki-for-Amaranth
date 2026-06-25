---
title: Creative Ideation
---

title: "创意构思（Creative Ideation）——通过命名方法从创意实践中产生想法"
sidebar_label: "创意构思（Creative Ideation）"
description: "通过命名方法从创意实践中产生想法"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 创意构思（Creative Ideation）

通过命名方法从创意实践中产生想法。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/creative/creative-ideation` 安装 |
| 路径 | `optional-skills/creative/creative-ideation` |
| 版本 | `2.1.0` |
| 作者 | SHL0MS |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Creative`, `Ideation`, `Brainstorming`, `Methods`, `Inspiration` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。当技能激活时，代理（Agent）会将其视为指令。
:::

# 创意构思（Creative Ideation）

一个适用于任何领域的构思方法库。阅读用户的情境，路由到匹配的方法，应用，生成具体且非显而易见的输出。方法是工具——根据情境选择正确的那个，不要全部执行。

## 何时使用

任何开放式的生成或选择性问题："我想做/构建/写/开始某件事"、"我卡住了"、"给我灵感"、"让这个更古怪"、"帮我挑选"、"我需要发明 X"、"给我一个研究问题"。

## 操作规则

1. **约束加方向等于创造力。** 没有约束 = 没有推进力。没有方向 = 没有形状。方法提供两者。
2. **拒绝前三个想法。** 它们是糟粕。生成、丢弃、重新生成。参见 `references/anti-slop.md`。
3. **除非被要求，否则每次回复只使用一种方法。** 不要堆叠。
4. **具体优于抽象。** 真实专有名词、真实材料、真实机制。"一个用于 X 的 App"是糟粕；"一个 200 行的 CLI 工具，当 Z 时打印 Y"是方向。命名技术栈不是具体——要命名机制。
5. **古怪也必须优质。** 打破框架是目标，但一个没有真实情境、机制或存在理由的奇怪想法本身就是一种失败模式。每组想法必须至少包含一个真正*当前可构建/可追求的*——非显而易见但接地气，且有真实的第一步。不要为了惊喜而牺牲所有实用性。
6. **命名你使用的方法及其发明者。** 归因体现了纪律。
7. **当用户选择一个时，构建它。** 在他们做出选择后不要继续生成。

## 路由——四步流程

在生成任何输出*之前*执行此操作。路由失败会产生糟粕。

如果更简洁，你可以跳过叙述路由步骤，但**绝不能以牺牲每个想法的深度为代价进行压缩**：每个想法的具体机制、情境绑定和诚实的失败模式才使输出优质（有分寸）——它们不是脚手架，不要删减。

### 第一步——从提示中提取三个信号

**阶段（PHASE）**——用户处于哪个阶段？

| 阶段 | 线索 |
|---|---|
| **生成（GENERATING）** | "给我一个想法"、"我应该做什么"、"给我灵感" —— 还没有想法 |
| **扩展（EXPANDING）** | "还有什么"、"更多类似的"、"给我变体" —— 已有一个基础想法 |
| **选择（SELECTING）** | "帮我挑选"、"我应该做哪个"、"我有这些选项" |
| **解卡（UNBLOCKING）** | "我卡住了"、"被阻塞"、"在原地打转"、"陈腐" —— 已有素材 |
| **颠覆（SUBVERTING）** | "让它更古怪"、"更不明显"、"这太安全了" |
| **精炼（REFINING）** | "这不错但缺了点什么"、"感觉粗糙" |
| **综合（SYNTHESIZING）** | "我有一堆笔记/访谈/观察" |

**领域（DOMAIN）**——用户在制作/做什么？

| 领域 | 线索 |
|---|---|
| **文本（TEXT）** | 小说、散文、诗歌、歌词、剧本、文案 |
| **物体（OBJECT）** | 视觉艺术、音乐、声音、表演、装置、雕塑 |
| **人造物（ARTIFACT）** | 软件、硬件、机制、设备 |
| **系统（SYSTEM）** | 组织、公民、机构、生态、社区 |
| **自我（SELF）** | 人生决策、职业、个人实践 |
| **研究（RESEARCH）** | 论文、学位论文、学术问题 |
| **产品（PRODUCT）** | 商业、市场、服务 |

**具体度（SPECIFICITY）**——提示中有多少约束？

| 等级 | 线索 |
|---|---|
| **无（NONE）** | "我很无聊"、"给我灵感" —— 无领域、无项目 |
| **领域（DOMAIN）** | "我想写点东西" —— 知道领域，无项目 |
| **项目（PROJECT）** | "我正在做一个特定的 X" |
| **问题（PROBLEM）** | "我在 X 中遇到了这个特定的摩擦点" |

### 第二步——应用覆盖规则（最高优先级，优先触发）

覆盖规则优于路由表：

- **情绪信号**——用户说"古怪"、"奇怪"、"令人惊讶"、"更不明显"、"更有趣" → 使用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md`，无论领域如何。
- **用户命名了一个方法**——使用它。
- **用户要求推荐方法**（"哪种方法"）→ 列出 2–3 个候选及其一行描述，询问应用哪个。不要静默默认。
- **高糟粕地形**——"AI 想法"、"创业想法"、"习惯追踪器"、"生产力/健康/健身/食物/旅游 App" → 强制使用 `references/methods/lateral-provocations.md` 或 `references/methods/pataphysics.md` 覆盖明显的方法。拒绝前 **5** 个想法，而不是 3 个。

### 第三步——先按阶段路由，再按领域路由

**按阶段（无论领域如何均适用）：**

| 阶段 | 默认路由 |
|---|---|
| 生成（GENERATING） + 具体度=无 | `references/full-prompt-library.md` **通用（General）** 部分（约束调度） |
| 生成（GENERATING） + 领域已知 | 按领域路由（下一表） |
| 扩展（EXPANDING） | `references/methods/scamper.md` |
| 选择（SELECTING） | `references/methods/premortem-and-inversion.md`（若关注上升潜力则用 `references/methods/compression-progress.md`） |
| 解卡（UNBLOCKING） | `references/methods/oblique-strategies.md` |
| 颠覆（SUBVERTING） | `references/methods/lateral-provocations.md`（后备 `references/methods/pataphysics.md`） |
| 精炼（REFINING）（文本） | `references/methods/defamiliarization.md` |
| 精炼（REFINING）（其他） | `references/methods/creative-discipline.md`（Tharp 的脊柱） |
| 综合（SYNTHESIZING） | `references/methods/affinity-diagrams.md` |
| 需要快速大量产出 | `references/methods/volume-generation.md` |

**按领域（当生成（GENERATING）且领域已知时）：**

| 领域 | 默认路由 |
|---|---|
| 文本——正式/诗歌 | `references/methods/oulipo.md` |
| 文本——叙事 | `references/methods/story-skeletons.md` |
| 文本——有源材料可混搭 | `references/methods/chance-and-remix.md` |
| 物体（音乐、视觉、表演） | `references/methods/oblique-strategies.md` |
| 物体——实体制作者/想要一个起始约束 | `references/full-prompt-library.md` **物理/物体（Physical / object）** 部分 |
| 人造物——想要一个起始约束 | `references/full-prompt-library.md` **软件/人造物（Software / artifact）** 部分 |
| 人造物——参数冲突的工程发明 | `references/methods/triz-principles.md` |
| 人造物——软件架构 | `references/methods/pattern-languages.md` |
| 人造物——有自然系统类比 | `references/methods/biomimicry.md` |
| 人造物——积累了需要质疑的假设 | `references/methods/first-principles.md` |
| 系统（公民、组织、机构） | `references/methods/leverage-points.md` |
| 系统——集体/参与式 | `references/full-prompt-library.md` **社会/集体（Social / collective）** 部分 |
| 自我（人生、职业、学什么） | `references/methods/derive-and-mapping.md` |
| 研究——选择问题 | `references/methods/compression-progress.md` |
| 研究——攻克已知问题 | `references/methods/polya.md` |
| 产品（商业、服务） | `references/methods/jobs-to-be-done.md` |
| 需要打破框架/寻找类比 | `references/methods/analogy-and-blending.md` |

### 第四步——处理模糊性和矛盾

- **多条路径都合理** → 选择最接近用户实际表述的那条。不要为了显得高深而选择最有趣的方法。
- **确实模糊** → 问一个澄清性问题，不要静默猜测。例如："你是在生成想法，还是在已有的想法中做选择？" / "这是用于小说、散文，还是其他？"
- **信号矛盾**（例如"古怪的创业想法"→ 产品领域 + 古怪情绪）→ **显式堆叠两种方法**。说明你的做法："使用 `jobs-to-be-done` 做产品框架 + `lateral-provocations` 打破显而易见的形状。"
- **无匹配** → 约束调度（`references/full-prompt-library.md`）是安全的后备。
- **同一问题再次被问** → 切换方法。方法的变化 = 想法分布的变化。

### 反默认检查（在生成前运行）

- 即将写出"这里有 5 个想法："或裸编号列表？→ 停止。先选择一种方法。
- 即将默认为通用的 LLM 模式头脑风暴？→ 停止。选择上面的一个路径。
- 输出看起来像未路由的 LLM 会产生的？→ 路由失败，重做。

默认的 LLM 模式正是此技能要取代的东西。如果你不经过路由就生成，你就让技能失效了。

有关更深入的边界情况（情绪信号、堆叠、反模式），请参见 `references/heuristics.md`。

## 输出格式

对于约束调度的默认路径：

```
## 约束：[名称] —— 来自 [来源]
> [约束，一句话]

### 想法

1. **[一行简介]**
   [2–3 句 —— 具体制作了什么，为什么有趣]
   ⏱ [周末/周/月]  •  🔧 [技术栈/媒介/材料]

2. ...
3. ...
```

对于其他方法，使用方法指定的格式（TRIZ 产生矛盾分析；OuLiPo 产生受约束的文本；Oblique Strategies 产生一张应用卡片 → 下一步行动）。不要强制每种方法都使用约束模板。

**每组想法，无论使用何种方法：**
- 命名使用的方法。在糟粕地形上，命名你拒绝的显而易见想法。
- 为每个想法提供其具体机制及其诚实的失败模式/权衡/适用对象。这种深度让想法落地——有分寸，而非装饰性。
- 标记至少一个想法为**接地气的（grounded）** ——当前可构建/可追求，非显而易见但有真实的第一步。其他想法可以走得更偏向古怪；这个必须真正可行。不要让整组都变得古怪而不切实际。

## 文件地图

- `references/full-prompt-library.md` —— 约束库，按领域分节（通用、软件、物理、社会、列表）。具体度=无时的默认路径。
- `references/method-catalog.md` —— 每种方法的一行摘要 + 何时使用
- `references/heuristics.md` —— 针对边界情况的扩展决策树
- `references/anti-slop.md` —— 反糟粕规则；应用于每个输出
- `references/exercises.md` —— 限时练习（5 分钟 / 30 分钟 / 1 小时 / 天 / 周）
- `references/methods/` —— 22 种命名方法，每个文件一种，只加载你正在使用的那一个

## 归属

约束调度核心改编自 [wttdotm.com/prompts.html](https://wttdotm.com/prompts.html)。方法源自每个方法文件中引用的主要来源。