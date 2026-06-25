---
title: "Llm Wiki"
---

```markdown
---
source_url: https://example.com/article   # 原始 URL（如适用）
ingested: YYYY-MM-DD
sha256: &lt;原始内容的十六进制数字摘要（位于 frontmatter 下方）>
```

--- body ---
```

`sha256:` 使得将来对同一 URL 重新收录时，若内容未变更则跳过处理，并在内容发生变化时标记偏差。仅对正文（结束 `---` 之后的部分）计算哈希，不包含 frontmatter 本身。

## 标签分类（Tag Taxonomy）
[为领域定义 10-20 个顶级标签。在使用新标签之前，先在此处添加。]

AI/ML 示例：
- 模型（Models）：模型、架构（architecture）、基准（benchmark）、训练（training）
- 人/组织（People/Orgs）：人物（person）、公司（company）、实验室（lab）、开源（open-source）
- 技术（Techniques）：优化（optimization）、微调（fine-tuning）、推理（inference）、对齐（alignment）、数据（data）
- 元标签（Meta）：比较（comparison）、时间线（timeline）、争议（controversy）、预测（prediction）

规则：页面上使用的每个标签都必须出现在此分类中。如果需要新标签，先在此处添加，然后使用。这可防止标签泛滥。

## 页面创建阈值（Page Thresholds）
- **创建一个页面**：当一个实体/概念出现在 2 个以上来源中，或者是一个来源的核心内容时。
- **添加到现有页面**：当某个来源提及已覆盖的内容时。
- **不要创建页面**：对于提及一次、次要细节或领域外的事物。
- **拆分页面**：当页面超过约 200 行时——拆分为子话题并添加交叉链接。
- **归档页面**：当页面内容完全被取代时——移至 `_archive/`，从索引中移除。

## 实体页面（Entity Pages）
每个显著实体一个页面。包括：
- 概述 / 它是什么
- 关键事实和日期
- 与其他实体的关系（[[维基链接]]）
- 来源引用

## 概念页面（Concept Pages）
每个概念或主题一个页面。包括：
- 定义 / 解释
- 当前知识状态
- 未解决问题或争议
- 相关概念（[[维基链接]]）

## 比较页面（Comparison Pages）
并排分析。包括：
- 比较的内容和原因
- 比较维度（首选表格格式）
- 结论或综合
- 来源

## 更新策略（Update Policy）
当新信息与现有内容冲突时：
1. 检查日期——较新的来源通常取代较旧的来源
2. 如果确实矛盾，则同时记录两种立场，并注明日期和来源
3. 在 frontmatter 中标记矛盾：`contradictions: [page-name]`
4. 在 lint 报告中标记以供用户审查

### index.md 模板

索引按类型分区。每个条目为一行：维基链接 + 摘要。

```markdown
# 维基索引

> 内容目录。每个维基页面列在其类型下，并带有一行摘要。
> 首先阅读此文件以查找任何查询的相关页面。
> 最后更新：YYYY-MM-DD | 总页面数：N

## 实体（Entities）
<!-- 按字母顺序排列，分区内 -->

## 概念（Concepts）

## 比较（Comparisons）

## 查询（Queries）
```

**扩展规则：** 当任何分区超过 50 个条目时，按首字母或子领域拆分为子分区。当索引总计超过 200 个条目时，创建一个 `_meta/topic-map.md`，按主题对页面进行分组以实现更快导航。

### log.md 模板

```markdown
# 维基日志

> 所有维基操作的时间线记录。仅可追加。
> 格式：`## [YYYY-MM-DD] 操作 | 主题`
> 操作：ingest, update, query, lint, create, archive, delete
> 当此文件超过 500 个条目时，进行轮转：重命名为 log-YYYY.md，新建一个。

## [YYYY-MM-DD] create | 维基已初始化
- 领域：[领域]
- 已创建结构：SCHEMA.md, index.md, log.md
```

## 核心操作（Core Operations）

### 1. 收录（Ingest）

当用户提供来源（URL、文件、粘贴文本）时，将其整合到维基中：

① **捕获原始来源：**
   - URL → 使用 `web_extract` 获取 markdown，保存到 `raw/articles/`
   - PDF → 使用 `web_extract`（可处理 PDF），保存到 `raw/papers/`
   - 粘贴的文本 → 保存到合适的 `raw/` 子目录
   - 文件命名要有描述性：`raw/articles/karpathy-llm-wiki-2026.md`
   - **添加原始 frontmatter**（`source_url`、`ingested`、正文的 `sha256`）。
     重新收录同一 URL 时：重新计算 sha256，与存储值比较——
     如果相同则跳过，如果不同则标记偏差并更新。这在每次重新收录时成本足够低，
     并且能捕获来源的静默变化。

② **与用户讨论要点**——哪些内容有趣，哪些对该领域重要。（在自动化/定时任务环境中跳过此步——直接进入下一步。）

③ **检查已有内容**——搜索 index.md 并使用 `search_files` 查找提及的实体/概念的现有页面。这是构建增量维基与堆积重复内容的区别。

④ **编写或更新维基页面：**
   - **新实体/概念：** 仅当它们满足 SCHEMA.md 中的页面创建阈值（2 个以上来源提及，或是一个来源的核心内容）时才创建页面。
   - **现有页面：** 添加新信息，更新事实，更新 `updated` 日期。当新信息与现有内容矛盾时，遵循更新策略。
   - **交叉引用：** 每个新建或更新的页面必须通过 `[[wikilinks]]` 链接到至少 2 个其他页面。检查现有页面是否有反向链接。
   - **标签：** 仅使用 SCHEMA.md 分类中的标签。
   - **溯源：** 在综合 3 个以上来源的页面上，对段落中的主张添加 `^[raw/articles/source.md]` 标记，以追踪到具体来源。
   - **置信度：** 对于观点性强、快速变化或单一来源的主张，在 frontmatter 中设置 `confidence: medium` 或 `low`。除非主张在多个来源中得到良好支持，否则不要标记为 `high`。

⑤ **更新导航：**
   - 将新页面添加到 `index.md` 的正确分区，按字母顺序排列
   - 更新索引头部的“总页面数”和“最后更新”日期
   - 追加到 `log.md`：`## [YYYY-MM-DD] ingest | 来源标题`
   - 在日志条目中列出每个创建或更新的文件

⑥ **报告变更内容**——向用户列出每个创建或更新的文件。

单个来源可能触发 5-15 个维基页面的更新。这是正常且期望的——这是累积效应。

### 2. 查询（Query）

当用户询问关于维基领域的问题时：

① **读取 `index.md`** 以识别相关页面。
② **对于超过 100 页的维基**，还需在所有 `.md` 文件中 `search_files` 搜索关键术语——仅靠索引可能会遗漏相关内容。
③ **使用 `read_file` 读取相关页面。**
④ **根据汇总的知识综合答案。** 引用你使用的维基页面：“根据 [[page-a]] 和 [[page-b]]...”
⑤ **将有价值的答案归档**——如果答案是一个重要的比较、深入分析或新颖的综合，则在 `queries/` 或 `comparisons/` 中创建一个页面。不要归档琐碎的查询——仅归档那些重新推导会很痛苦的答案。
⑥ **更新 log.md**，记录查询内容以及是否已归档。

### 3. 检查（Lint）

当用户要求对维基进行检查、健康审计或审核时：

① **孤立页面：** 查找没有来自其他页面的入站 `[[wikilinks]]` 的页面。
```python
# 使用 execute_code 进行此操作——在所有维基页面中编程扫描
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# 扫描 entities/, concepts/, comparisons/, queries/ 中的所有 .md 文件
# 提取所有 [[wikilinks]] —— 构建入站链接映射
# 入站链接为零的页面即为孤立页面
```

② **损坏的维基链接：** 查找指向不存在页面的 `[[links]]`。

③ **索引完整性：** 每个维基页面应出现在 `index.md` 中。将文件系统与索引条目进行比较。

④ **Frontmatter 验证：** 每个维基页面必须包含所有必填字段（title, created, updated, type, tags, sources）。标签必须属于分类。

⑤ **过时内容：** 页面的 `updated` 日期比提及相同实体的最新来源晚 90 天以上。

⑥ **矛盾：** 同一主题的页面存在冲突的主张。查找共享标签/实体但陈述不同事实的页面。将所有具有 `contested: true` 或 `contradictions:` frontmatter 的页面提交给用户审查。

⑦ **质量信号：** 列出 `confidence: low` 的页面以及任何仅引用单一来源但未设置 confidence 字段的页面——这些页面要么需要寻找佐证，要么降级为 `confidence: medium`。

⑧ **来源漂移：** 对于 `raw/` 中具有 `sha256:` frontmatter 的每个文件，重新计算哈希并标记不匹配。不匹配表示原始文件被编辑（不应发生——raw/ 是不可变的）或收录自一个后来发生变化的 URL。这不是硬性错误，但值得报告。

⑨ **页面大小：** 标记超过 200 行的页面——这些页面适合拆分。

⑩ **标签审计：** 列出所有正在使用的标签，标记任何不在 SCHEMA.md 分类中的标签。

⑪ **日志轮转：** 如果 log.md 超过 500 个条目，则轮转它。

⑫ **报告发现结果**，包含具体文件路径和建议的操作，按严重性分组（损坏链接 > 孤立页面 > 来源漂移 > 有争议页面 > 过时内容 > 风格问题）。

⑬ **追加到 log.md**：`## [YYYY-MM-DD] lint | 发现 N 个问题`

## 使用维基（Working with the Wiki）

### 搜索

```bash
# 按内容查找页面
search_files "transformer" path="$WIKI" file_glob="*.md"

# 按文件名查找页面
search_files "*.md" target="files" path="$WIKI"

# 按标签查找页面
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# 最近活动
read_file "$WIKI/log.md" offset=<最后 20 行>
```

### 批量收录

当一次收录多个来源时，批量处理更新：
1. 先读取所有来源
2. 识别所有来源中的所有实体和概念
3. 一次性地检查所有实体的现有页面（一次搜索，而不是 N 次）
4. 一次性地创建/更新页面（避免冗余更新）
5. 最后更新一次 index.md
6. 写入一条涵盖整个批次的日志条目

### 归档

当内容完全被取代或领域范围发生变化时：
1. 如果 `_archive/` 目录不存在则创建
2. 将页面移动到 `_archive/`，保留原始路径（例如 `_archive/entities/old-page.md`）
3. 从 `index.md` 中移除
4. 更新所有链接到该页面的页面——将维基链接替换为纯文本 + “(已归档)”
5. 记录归档操作

### Obsidian 集成

维基目录可直接作为 Obsidian 库使用：
- `[[wikilinks]]` 呈现为可点击链接
- 图谱视图可视化知识网络
- YAML frontmatter 支持 Dataview 查询
- `raw/assets/` 文件夹存放通过 `![[image.png]]` 引用的图片

为获得最佳效果：
- 将 Obsidian 的附件文件夹设置为 `raw/assets/`
- 在 Obsidian 设置中启用“维基链接”（通常默认开启）
- 安装 Dataview 插件以执行类似 `TABLE tags FROM "entities" WHERE contains(tags, "company")` 的查询

如果同时使用此技能和 Obsidian 技能，请将 `OBSIDIAN_VAULT_PATH` 设置为与维基路径相同的目录。

### Obsidian Headless（服务器和无头机器）

在没有显示器的机器上，使用 `obsidian-headless` 替代桌面应用。它通过 Obsidian Sync 同步库而无需图形界面——非常适合在服务器上运行的代理，它们写入维基，而 Obsidian 桌面在其他设备上读取。

**设置：**
```bash
# 需要 Node.js 22+
npm install -g obsidian-headless

# 登录（需要具有 Sync 订阅的 Obsidian 账户）
ob login --email <email> --password '<password>'

# 为维基创建一个远程库
ob sync-create-remote --name "LLM Wiki"

# 将维基目录连接到该库
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# 初始同步
ob sync

# 持续同步（前台运行——使用 systemd 进行后台运行）
ob sync --continuous
```

**通过 systemd 持续后台同步：**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# 启用 linger 使同步在注销后继续运行：
sudo loginctl enable-linger $USER
```

这使得代理可以在服务器上写入 `~/wiki`，而您可以在笔记本电脑/手机上通过 Obsidian 浏览同一个库——更改会在几秒内出现。

## 常见陷阱（Pitfalls）

- **永远不要修改 `raw/` 中的文件**——来源是不可变的。更正应放在维基页面中。
- **始终先定位**——在新会话中执行任何操作之前，先读取 SCHEMA + index + 最近日志。跳过这一步会导致重复和遗漏交叉引用。
- **始终更新 index.md 和 log.md**——跳过这一步会使维基退化。这些是导航的骨干。
- **不要为提及一次的内容创建页面**——遵循 SCHEMA.md 中的页面创建阈值。一个只在脚注中出现一次的名称不值得创建一个实体页面。
- **不要创建没有交叉引用的页面**——孤立的页面是隐形的。每个页面必须链接到至少 2 个其他页面。
- **Frontmatter 是必需的**——它支持搜索、过滤和过时检测。
- **标签必须来自分类**——自由形式的标签会退化为噪音。先将新标签添加到 SCHEMA.md，然后使用它们。
- **保持页面易于浏览**——一个维基页面应在 30 秒内可读完。超过 200 行的页面应拆分。将详细分析移至专门的深入页面。
- **批量更新前先询问**——如果一次收录会触及 10 个以上现有页面，请先与用户确认范围。
- **轮转日志**——当 log.md 超过 500 个条目时，将其重命名为 `log-YYYY.md` 并新建一个。代理应在 lint 期间检查日志大小。
- **明确处理矛盾**——不要静默覆盖。同时记录两种主张及其日期，在 frontmatter 中标记，并提交给用户审查。

## 相关工具（Related Tools）

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) 是一个 Node.js CLI 工具，它将来源编译成概念维基，灵感同样来自 Karpathy。它与 Obsidian 兼容，因此希望使用调度/CLI 驱动编译管道的用户可将其指向此技能维护的同一个库。权衡：它拥有页面生成权（取代了代理在页面创建上的判断），并且针对小型语料库进行了优化。当您希望进行代理参与的策展时，使用此技能；当您想要对源目录进行批量编译时，使用 llmwiki。
```