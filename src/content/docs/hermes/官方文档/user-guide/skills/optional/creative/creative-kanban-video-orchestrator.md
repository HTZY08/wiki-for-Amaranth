# Kanban Video Orchestrator（看板视频编排器）

规划、设置并监控一个由 Hermes Kanban 支持的多智能体视频制作流水线。（Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban.）当用户想要制作任何类型的视频——叙事电影、产品/营销视频、音乐视频、解说视频、ASCII/终端艺术、抽象/生成循环、漫画、3D、实时/装置艺术——且工作量需要分解为通过看板协调的专门角色（编剧、设计师、动画师、渲染师、配音、剪辑等）时使用。该技能执行自适应发现以界定概要，为请求的风格设计合适的团队，生成创建 Hermes 角色 + 初始看板任务的设置脚本，然后帮助监控执行并在任务停滞或失败时进行干预。它将场景路由到适合每个节拍的任何 Hermes 渲染/音频/设计技能（`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`pixel-art`、`baoyu-comic`、`claude-design`、`excalidraw`、`songsee`、`heartmula`……），以及根据需要的外部 API（TTS、图像生成、图像转视频）。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选——使用 `hermes skills install official/creative/kanban-video-orchestrator` 安装 |
| 路径（Path） | `optional-skills/creative/kanban-video-orchestrator` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | ['SHL0MS', 'alt-glitch'] |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `video`, `kanban`, `multi-agent`, `orchestration`, `production-pipeline` |
| 相关技能（Related skills） | [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js), [`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui), [`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp), [`blender-mcp`](/docs/user-guide/skills/optional/creative/creative-blender-mcp), [`pixel-art`](/docs/user-guide/skills/optional/creative/creative-pixel-art), [`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art), [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music), [`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula), [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee), `spotify`, [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram), [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams), [`baoyu-comic`](/docs/user-guide/skills/optional/creative/creative-baoyu-comic), [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic), [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer), [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search), [`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# Kanban Video Orchestrator（看板视频编排器）

将任何视频请求——从15秒的产品预告片到5分钟的叙事短片，再到音乐视频甚至 ASCII 循环——都包装在 Hermes Kanban 流水线中，将工作分解给专门的代理角色。

该技能**本身不执行任何渲染**。它是一个元流水线，负责：

1. **界定范围（Scopes）**：通过有针对性的发现来界定请求
2. **设计团队（Designs）**：根据风格设计合适的团队（哪些角色，每个角色使用哪些工具）
3. **生成设置脚本（Generates）**：生成一个创建 Hermes 角色、项目工作区和初始看板任务的设置脚本
4. **移交给导演角色（Hands off）**：移交给导演角色，后者通过看板进行分解
5. **监控执行（Monitors）**：监控执行，在任务停滞或失败时提供帮助

实际的渲染在看板运行后发生，通过任何适合场景的现有技能和工具——`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`songwriting-and-ai-music`、`heartmula`、外部 API 或使用 PIL + ffmpeg 的普通 Python。

## 何时不使用该技能（When NOT to use this skill）

- 视频是一个连续的、程序化的项目，不需要专家。直接编写代码即可。
- 用户想要快速的单次转换（例如“将此 mp4 转换为 GIF”）——直接使用 ffmpeg。
- 输出是静态图像、GIF 或仅音频的制品——使用匹配的特定技能（`ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）。
- 工作可以干净地适配单个现有技能（例如纯 ASCII 视频——只需使用 `ascii-video`）。

## 工作流（Workflow）

```
发现（DISCOVER） → 概要（BRIEF） → 团队设计（TEAM DESIGN） → 设置（SETUP） → 执行（EXECUTE） → 监控（MONITOR）
```

### 步骤 1 — 发现（Discover）（提出正确的问题）

发现过程是**自适应的**：只问实际需要的问题。始终从三个问题开始，以确定大致的形态：

- **视频是什么？**（一句话概要）
- **时长？**（5-30秒预告片 / 30-90秒短片 / 90秒-3分钟解说 / 3-10分钟影片 / 更长）
- **纵横比和目标平台？**（1:1 / 9:16 / 16:9；X、Ins、YouTube、内部等）

根据回答，对风格类别进行分类。风格决定了接下来要提出哪些后续问题。**不要一次性问所有问题。** 一次问2-4个，倾听，然后继续。当用户暗示了答案时，做出合理的假设。

完整的输入模式和各风格的问题库，请参阅 **[references/intake.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/intake.md)**。

### 步骤 2 — 概要（Brief）

一旦获得足够的信息，使用 `assets/brief.md.tmpl` 中的模板生成结构化的 `brief.md`。阶段包括：

1. **概念（Concept）**——一句话推介 + 情感北极星
2. **范围（Scope）**——时长、纵横比、平台、截止日期
3. **风格（Style）**——视觉参考、品牌约束、基调
4. **场景（Scenes）**——逐节拍分解（时长、内容、目标工具）
5. **音频（Audio）**——旁白 / 音乐 / 音效 / 静音（如果需要，按场景说明）
6. **交付物（Deliverables）**——文件格式、分辨率、可选替代版本（竖版、GIF 等）

在设计团队之前向用户展示概要以待确认。**概要就是合约**——每个下游任务都引用它。

### 步骤 3 — 团队设计（Team design）

从库中选择适合此视频的角色原型。**组合，而非复制。** 大多数视频需要4-7个角色。导演始终在场；其余角色根据概要的实际需求选取。

角色库和各风格团队组成，请参阅 **[references/role-archetypes.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/role-archetypes.md)**。

关于角色→加载哪些 Hermes 技能和工具集的映射，请参阅 **[references/tool-matrix.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/tool-matrix.md)**。

### 步骤 4 — 设置（Setup）

生成设置脚本（`setup.sh`）并运行它。该脚本：

1. 创建项目工作区（`~/projects/video-pipeline/<slug>/`）
2. 将任何提供的资源复制到 `taste/`、`audio/`、`assets/`
3. 通过 `hermes profile create --clone` 创建每个 Hermes 角色
4. 为每个角色编写 `SOUL.md`（个性 + 角色定义）
5. 配置角色 YAML（工具集、always_load 技能、cwd）
6. 编写 `brief.md`、`TEAM.md` 和 `taste/` 内容
7. 触发分配给导演的初始 `hermes kanban create` 任务

使用 `scripts/bootstrap_pipeline.py` 从概要 + 团队设计 JSON 生成 setup.sh。关于设置脚本结构、角色配置模式以及关键的“共享工作区”规则，请参阅 **[references/kanban-setup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/kanban-setup.md)**。

### 步骤 5 — 执行（Execute）

运行 `setup.sh`。然后为用户提供监控命令：

```bash
hermes kanban watch --tenant <project-tenant>     # 实时事件
hermes kanban list  --tenant <project-tenant>     # 看板快照
hermes dashboard                                   # 可视化看板 UI
```

导演角色从此时接管，通过看板工具集分解工作并将任务路由给专业角色。

### 步骤 6 — 监控和干预（Monitor and intervene）

保持参与——看板自主运行，但卡住的任务或糟糕的输出需要人工（或 AI）判断。

监控模式：定期轮询 `kanban list`，用 `kanban show <id>` 检查任何超出预期持续时间的 RUNNING 任务，并检查心跳。当工作者的输出未通过审核时，标准干预措施包括：

1. 在工作者的任务上添加带有具体反馈的评论（`kanban_comment`）
2. 创建一个以原任务为父任务的重运行任务
3. 调整概要的范围，让导演重新分解

关于诊断模式、干预策略以及“任务卡住”的操作手册，请参阅 **[references/monitoring.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/monitoring.md)**。

## 参考：工作示例（worked examples）

六个具体的流水线，涵盖非常不同的视频风格——叙事电影、产品/营销、音乐视频、数学/算法解说、ASCII 视频、实时装置——展示了相同的工作流程如何产生截然不同的团队和任务图。请参阅 **[references/examples.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/examples.md)**。

## 关键规则（Critical rules）

1. **先发现，后行动。** 切勿在未至少提出三个基本问题的情况下开始生成概要或团队。糟糕的概要会影响整个流水线。

2. **团队与视频匹配。** 不要为每个工作重复使用相同的4角色设置。一个没有节拍分析角色的音乐视频会失败。一个没有编剧角色的叙事电影会产生不连贯的场景。请参阅 `references/role-archetypes.md`。

3. **每个项目一个工作区。** 给定视频的所有角色共享同一个 `dir:` 工作区。任务通过共享文件系统和结构化的交接传递制品。**每个** `kanban_create` 调用都传递 `workspace_kind="dir"` + `workspace_path="<绝对项目路径>"`。

4. **每个项目一个租户。** 使用项目特定的租户（`--tenant <project-slug>`）。保持仪表盘范围清晰，防止与正在进行的其他看板交叉污染。

5. **尊重现有技能。** 当场景适合现有技能时，相关渲染器应在其任务上通过 `--skill <name>` 或在其角色配置中使用 `always_load` 加载该技能。不要重新推导技能已提供的功能。

6. **导演从不执行。** 即使拥有完整的 `kanban + terminal + file` 工具集，导演的 `SOUL.md` 规则也禁止其自行执行工作。它只负责分解和路由——每个具体任务都转变为对专业角色的 `hermes kanban create` 调用。自动注入的看板编排指南进一步说明了这一点。

7. **不要过度分解。** 一个30秒的产品视频不需要20个任务。目标是尽可能小的任务图，同时仍能良好并行化并暴露适当的人工审核关卡。

8. **在触发之前验证 API 密钥。** 外部 API（TTS、图像生成、图像转视频）需要将密钥放入 `${HERMES_HOME:-~/.hermes}/.env` 或用户的密钥存储中。遇到缺少密钥错误的工作者会浪费一个任务槽。设置脚本中的 `check_key` 辅助函数会在缺少所需密钥时干净地中止。

## 文件映射（File map）

```
SKILL.md                            ← 本文件（工作流 + 规则）
references/
  intake.md                         ← 按风格的发现问题库
  role-archetypes.md                ← 角色库（编剧、设计师、动画师……）
  tool-matrix.md                    ← 按角色的技能 + 工具集映射
  kanban-setup.md                   ← 设置脚本结构和角色配置
  monitoring.md                     ← 监控 + 干预模式
  examples.md                       ← 六个工作流水线
assets/
  brief.md.tmpl                     ← 概要模板
  setup.sh.tmpl                     ← 设置脚本模板
  soul.md.tmpl                      ← 角色个性模板
scripts/
  bootstrap_pipeline.py             ← 从概要 + 团队设计 JSON 生成 setup.sh
  monitor.py                        ← 轮询 + 干预辅助函数
```