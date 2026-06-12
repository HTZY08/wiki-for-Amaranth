---
name: paper-figure-mapper
description: >-
  扫读论文/综述全文，识别需配图的关键数据/机理/概念，
  按 baoyu-article-illustrator 格式输出每张图的 prompt（YAML frontmatter + hex 色板 + 类型模板）。
  不生成图片。产出 prompt 文件后由用户选定平台批量出图。
---

# Paper Figure Mapper

## 与 baoyu-article-illustrator 的关系

```
论文/综述全文
  → 本 skill（paper-figure-mapper）：扫读 → 识别图位 → 产出 prompt 文件
  → baoyu-article-illustrator / mcp_meigen_generate_image / Codex CLI image2 → 出图
```

本 skill 负责「从文中提取数据和结构」，产出格式与 baoyu-article-illustrator 完全兼容。

## 适应图片模型

prompt 中不指定后端。以下均可：
- **MeiGen**: `mcp_meigen_generate_image`（GPT Image 2.0 / Nanobanana / Seedream）
- **Codex CLI**: 通过 OpenAI API 用 image2
- **ComfyUI**: 本地 SDXL/Flux

## 输入

论文/综述的章节文件列表。

## 输出

```
paper-figures/{paper-slug}/prompts/
├── _test-timeline-concept.md     # 测试图（先产1张）
├── 01-timeline-concept.md        # 批量产出
├── 02-comparison-data.md
└── ...
```

## 工作流

### Step 0：定义风格体系（一次性）

用户指定色板 + 渲染规则。之后所有图用同一套。

```yaml
palette:
  primary: "#XXXXXX"      # 主色
  secondary: "#XXXXXX"    # 辅色
  accent: "#XXXXXX"       # 亮色
  contrast: "#XXXXXX"     # 对比色
  emphasis: "#XXXXXX"     # 强调色（用于矛盾/缺口/警告节点）
  background: "#XXXXXX"   # 底色
  text: "#XXXXXX"         # 文字色
  line: "#XXXXXX"         # 线条/网格色

render_rules:
  - Flat vector. Clean outlines (1.5-2px).
  - Solid color fills, no gradients.
  - Sans-serif labels.
  - Rounded rectangles for process cards.
  - Thick triangular arrows (3-4px).
  - No 3D perspective.
  - Small annotation boxes for data values.
```

### Step 1：扫读 → 识别图位

逐节扫描，识别以下 8 类必须配图的信号：

| 信号 | 例子 |
|:-----|:------|
| 时间线/序列 | 1857→1908→1951→1994→… |
| 多路对比 | 方法 A vs 方法 B、两种模型 |
| 定量关系 | 线性拟合、定标公式、散布范围 |
| 结构拆解 | 分子/界面/晶面的放大对比 |
| 决策分歧 | 当 X 走路径 A，当 Y 走路径 B |
| 分层框架 | 第一层…第二层…第三层… |
| 数据矛盾 | A 组报告 35 nm 红移，B 组报告 20 nm 蓝移 |
| 时空范围 | 不同技术的分辨率/灵敏度对比 |

每节产出：`(类型, 图名, 数据摘要, 位置)`

### Step 2：归类 → 排序

| 优先级 | 标准 |
|:-----:|------|
| P0 | 无图就讲不清楚的核心概念（≤5 张） |
| P1 | 支撑关键论证的机理图解（5–8 张） |
| P2 | 深化数据展示（不限） |

### Step 3：测试一图 → 迭代确认风格（不可跳过的步骤）

**不要批量产出全部 prompt。** 一次性写全部 prompt 的结果是风格不对全白写。

1. 从 P0 选 **1 张最典型**的图（推荐时间线或对比图——结构清晰，好坏一眼可辨）
2. 写测试 prompt，保存为 `prompts/_test-{type}-{description}.md`
3. 用户用自己选定的平台/模型生成测试图
4. 用户审核：色板准确度、描边一致性、标签清晰度、数值标注格式、整体风格是否对
5. 根据反馈修改 prompt（COLORS/ELEMENTS/STYLE/LAYOUT 等节）
6. 重新生成→再审核→再改→迭代直到用户确认「风格 OK」
7. **只有风格确认后，才按该模板批量产出剩余全部 prompt**

**迭代原则：** 先产 1 张 → 看效果 → 调 prompt → 再产 1 张 → 确认 → 批量。不要跳过这一步。

### Step 4：批量产出剩余 prompt

#### Frontmatter

```yaml
---
illustration_id: "01"
type: timeline                     # timeline / comparison / infographic / flowchart / framework
style: vector-illustration         # baoyu 风格
palette: custom                    # 自定义色板名
palette_colors:
  primary: "#C5851A"
  secondary: "#D4A843"
  accent: "#E8C36A"
  contrast: "#1A6B6B"
  emphasis: "#8B2252"
  background: "#FAF6F0"
  text: "#2C1810"
  line: "#8B7355"
render_rules:
  - Flat vector. Clean outlines (1.5-2px).
  - Solid fills, no gradients.
  - Sans-serif labels. Rounded cards. Thick arrows (3-4px).
  - No 3D perspective. Annotation boxes for data values.
aspect: 16:9
complexity: medium
---
```

#### 内容体模板（5 种类型）

**timeline（时间线）**
```
Horizontal/vertical timeline layout. [方向] chronological progression.

EVENTS:
- [Year]: [事件描述 + 关键数据]
- [Year]: [事件描述 + 关键数据]

DIRECTION: [horizontal/vertical]
MARKERS: [标记类型]
LABELS: [年份/事件标注方式]
COLORS: [轴线色 / 标记色 / 卡片色 / 文字色]
STYLE: [渲染细节]
ASPECT: 16:9
```

**comparison（对比）**
```
LEFT SIDE - [选项A]:
- [数据点 + 精确数值]
- [数据点 + 精确数值]

RIGHT SIDE - [选项B]:
- [数据点 + 精确数值]
- [数据点 + 精确数值]

DIVIDER: [分隔方式]
LABELS: [对比标注]
COLORS: [左侧色 / 右侧色 / 底色]
STYLE: [渲染细节]
ASPECT: 16:9
```

**infographic（信息图）**
```
Layout: [grid/radial/hierarchical]

ZONES:
- Zone 1 (主面板): [图表类型 + 核心数据 + 数值]
- Zone 2 (辅面板): [对比/补充数据 + 数值]
- Zone 3 (总结): [关键结论]

LABELS: [原文中的具体数值/术语/公式，逐条列出]
COLORS: [主数据色 / 辅色 / 对比色 / 强调色]
STYLE: [渲染细节]
ASPECT: 16:9
```

**flowchart（流程图/决策树）**
```
Layout: [top-down/left-right/circular]

STEPS:
1. [步骤名] — [描述 + 数据]
2. [步骤名] — [描述 + 数据]
...
Branch A: [条件 → 去向]
Branch B: [条件 → 去向]

CONNECTIONS: [箭头类型 / 决策菱形标注]
LABELS: [分支条件数值 / 时标]
COLORS: [步骤框色 / 决策框色 / 箭头色 / 终点色]
STYLE: [渲染细节]
ASPECT: 16:9
```

**framework（框架图）**
```
STRUCTURE: [hierarchical/network/matrix]

NODES:
- [概念1] — [角色/数据]
- [概念2] — [角色/数据]
- [概念3] — [角色/数据]

RELATIONSHIPS: [连接方式]
LABELS: [节点标注]
COLORS: [层级1色 / 层级2色 / 层级3色 / 连接线色]
STYLE: [渲染细节]
ASPECT: 16:9
```

#### 公共前缀（每张 prompt 的第一段）

```
Flat vector illustration style. Clean outlines (1.5-2px) on all elements.
COLORS: [按实际色板填入].
No gradients. Solid color fills only. Sans-serif labels. Rounded rectangles for process cards.
Thick triangular arrows (3-4px). No 3D perspective. Small annotation boxes for exact data values.
Chinese labels for names. English labels for formulas and numerical data.
Color values (#hex) and color names are rendering guidance only — do NOT display them as visible text in the image.
```

#### Prompt 撰写铁律

1. **数值必须与原文完全一致**，不可概括或改动
2. 中文标签用中文，英文公式/数据用英文
3. 不写「高质量」「逼真」「使用 XX 模型」等元提示
4. 颜色用 hex code 指定 + 标注色名（色名不显示在图上）
5. 始终包含颜色不显示指令

### Step 5：批量生成与风格锚定

生成时采用 **reference image 锚定策略**（适用于 MeiGen / OpenAI image2）：

1. 首张图（测试确认的那张）出完后，保留其图片
2. 后续每张图生成时，把前一张图作为 `referenceImages` 参数传入
3. prompt 中增加一句：`"Match the visual style of the reference image exactly — same line thickness, same color palette, same labeling style"`
4. 每 3-4 张图对比一次风格一致性，发现漂移则重新锚定

这条链路利用了 GPT Image 2.0 模型的**原生跨图一致性**能力和 ConsiStory 的注意力共享原理（详见 reference 文件）。

### Step 6：风格一致性验证

每批次对照检查：
- 色板使用是否一致
- 描边/圆角/箭头风格是否统一
- 中文标签 vs 英文公式的分工是否一致
- 数值标注格式是否一致

发现问题 → 修正后续 prompt → 用参考图重新锚定生成 → 确认后继续。

---

## 模板选择速查

| 数据类型 | 推荐类型 | 推荐 style | 理由 |
|:---------|:---------|:-----------|:------|
| 时间线/发现史 | timeline | elegant / vector-illustration | 左右交替卡片，清晰 |
| 方法对比/机制对比 | comparison | vector-illustration | 左右分割，颜色区分 |
| 多面板数据汇总 | infographic | scientific / vector-illustration | 主图+辅面板 |
| 过程流/决策树 | flowchart | vector-illustration | 步骤框+箭头+决策菱形 |
| 分层框架/架构 | framework | blueprint / vector-illustration | 节点+连接线，上下堆叠 |
| 结构拆解/截面 | structural-breakdown | scientific | 放大镜+标注 |

## 与其他 skill 配合

| 阶段 | 使用 skill | 产出 |
|:-----|:-----------|:------|
| 搜索筛选 | `precision-review-search` | 语料库 |
| 写作 | `review-chem-bio-writing` | .md 章节 |
| **配图** | **本 skill** → **baoyu-article-illustrator** | **prompt 文件** |
| 出图 | `mcp_meigen_generate_image` / Codex CLI | PNG |
