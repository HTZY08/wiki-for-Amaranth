---
title: Memento Flashcards
---

title: "Memento Flashcards — 间隔重复抽认卡系统"
sidebar_label: "Memento Flashcards"
description: "间隔重复抽认卡系统"
---

--- body ---

{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Memento Flashcards

间隔重复（spaced-repetition）抽认卡系统。根据事实或文本创建卡牌，通过由代理评分的自由文本答案与抽认卡聊天，从 YouTube 字幕生成测验，通过自适应调度复习到期卡牌，并以 CSV 格式导出/导入牌组。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/memento-flashcards` 安装 |
| 路径 | `optional-skills/productivity/memento-flashcards` |
| 版本 | `1.0.0` |
| 作者 | Memento AI |
| 许可证 | MIT |
| 平台 | macos, linux |
| 标签 | `教育`, `抽认卡`, `间隔重复`, `学习`, `测验`, `YouTube` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Memento Flashcards — 间隔重复抽认卡技能

## 概述

Memento 为您提供一个基于本地文件的抽认卡系统，并带有间隔重复调度功能。
用户可以通过自由文本回答问题，并由代理评估回答后再安排下次复习，从而与抽认卡进行交互。
在以下情况下使用它：

- **记住一个事实** — 将任何陈述转化为问答抽认卡
- **通过间隔重复学习** — 使用自适应间隔和代理评分的自由文本答案复习到期卡牌
- **基于 YouTube 视频进行测验** — 获取字幕并生成 5 题测验
- **管理牌组** — 将卡牌组织到集合中，导出/导入 CSV

所有卡牌数据都存储在一个 JSON 文件中。不需要外部 API 密钥 — 您（代理）直接生成抽认卡内容和测验题目。

Memento Flashcards 面向用户的响应风格：
- 仅使用纯文本。在回复用户时不要使用 Markdown 格式。
- 保持复习和测验反馈简洁且中立。避免额外的表扬、鼓励或冗长解释。

## 使用时机

当用户想要以下操作时使用此技能：
- 将事实保存为抽认卡以备后续复习
- 使用间隔重复复习到期卡牌
- 从 YouTube 视频字幕生成测验
- 导入、导出、查看或删除抽认卡数据

不要将此技能用于一般问答、编程帮助或非记忆性任务。

## 快速参考

| 用户意图 | 操作 |
|---|---|
| "记住那件事" / "将其保存为抽认卡" | 生成问答卡，调用 `memento_cards.py add` |
| 用户发送一个事实但未提及抽认卡 | 询问"是否要将此保存为 Memento 抽认卡？" — 仅在确认后创建 |
| "创建一张抽认卡" | 询问问题、答案、集合；调用 `memento_cards.py add` |
| "复习我的卡牌" | 调用 `memento_cards.py due`，逐张展示卡牌 |
| "通过 [YouTube URL] 对我进行测验" | 调用 `youtube_quiz.py fetch VIDEO_ID`，生成 5 个问题，调用 `memento_cards.py add-quiz` |
| "导出我的卡牌" | 调用 `memento_cards.py export --output PATH` |
| "从 CSV 导入卡牌" | 调用 `memento_cards.py import --file PATH --collection NAME` |
| "显示我的统计信息" | 调用 `memento_cards.py stats` |
| "删除一张卡牌" | 调用 `memento_cards.py delete --id ID` |
| "删除一个集合" | 调用 `memento_cards.py delete-collection --collection NAME` |

## 卡牌存储

卡牌存储在以下路径的 JSON 文件中：

```
~/.hermes/skills/productivity/memento-flashcards/data/cards.json
```

**切勿直接编辑此文件。** 始终使用 `memento_cards.py` 子命令。该脚本处理原子写入（先写入临时文件，再重命名）以防止损坏。

该文件在首次使用时自动创建。

## 流程

### 从事实创建卡牌

### 激活规则

并非每个事实性陈述都应成为抽认卡。使用此三级检查：

1. **明确意图** — 用户提到"memento"、"抽认卡"、"记住这个"、"保存这张卡"、"添加卡"或类似明确请求抽认卡的措辞 → **直接创建卡牌**，无需确认。
2. **隐含意图** — 用户发送事实性陈述但未提及抽认卡（例如："光速是 299,792 km/s"） → **先询问**："是否要将此保存为 Memento 抽认卡？"仅在用户确认后创建卡牌。
3. **无意图** — 消息是编程任务、问题、指令、正常对话或任何明显不是需要记忆的事实 → **完全不激活此技能**。让其他技能或默认行为处理。

当激活确定后（第一级直接，第二级确认后），生成抽认卡：

**步骤 1：** 将陈述转换为问答对。内部使用此格式：

```
将事实性陈述转换为正面-背面配对。
返回恰好两行：
Q: <问题文本>
A: <答案文本>

陈述: "{statement}"
```

规则：
- 问题应测试关键事实的回忆
- 答案应简洁直接

**步骤 2：** 调用脚本存储卡牌：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add \
  --question "第二次世界大战在哪一年结束？" \
  --answer "1945" \
  --collection "历史"
```

如果用户未指定集合，则使用 `"General"` 作为默认值。

脚本输出 JSON 确认创建的卡牌。

### 手动创建卡牌

当用户明确要求创建抽认卡时，询问他们：
1. 问题（卡正面）
2. 答案（卡背面）
3. 集合名称（可选 — 默认为 `"General"`）

然后如上所述调用 `memento_cards.py add`。

### 复习到期卡牌

当用户想要复习时，获取所有到期卡牌：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

返回一个 JSON 数组，其中包含 `next_review_at <= 当前时间` 的卡牌。如果需要集合筛选：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due --collection "历史"
```

**复习流程（自由文本评分）：**

以下是您必须遵循的精确交互模式示例。用户回答，您为他们评分，告诉他们正确答案，然后评价卡牌。

**示例交互：**

> **代理：** 柏林墙是哪一年倒塌的？
>
> **用户：** 1991
>
> **代理：** 不太对。柏林墙于 1989 年倒塌。下次复习在明天。
> *(代理调用：memento_cards.py rate --id ABC --rating hard --user-answer "1991")*
>
> 下一个问题：谁是第一个在月球上行走的人？

**规则：**

1. 仅显示问题。等待用户回答。
2. 收到他们的回答后，将其与预期答案进行比较并评分：
   - **correct** — 用户答对了关键事实（即使措辞不同）
   - **partial** — 方向正确但缺少核心细节
   - **incorrect** — 错误或跑题
3. **您必须告诉用户正确答案以及他们的表现。** 保持简短并使用纯文本。使用以下格式：
   - correct："正确。答案：&#123;答案&#125;。7 天后下次复习。"
   - partial："接近。答案：&#123;答案&#125;。&#123;他们遗漏的内容&#125;。3 天后下次复习。"
   - incorrect："不太对。答案：&#123;答案&#125;。明天下次复习。"
4. 然后调用评分命令：correct→easy, partial→good, incorrect→hard。
5. 然后显示下一个问题。

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "用户所说的内容"
```

**切勿跳过步骤 3。** 用户必须始终在看到正确回答和反馈后，您才能继续。

如果没有到期卡牌，告诉用户："当前没有到期复习的卡牌。请稍后再来！"

**退役覆盖：** 用户可以随时说"退役这张卡"，以将其从复习中永久移除。使用 `--rating retire` 来实现。

### 间隔重复算法

评分决定下次复习间隔：

| 评分 | 间隔 | ease_streak | 状态变化 |
|---|---|---|---|
| **hard** | +1 天 | 重置为 0 | 保持学习 |
| **good** | +3 天 | 重置为 0 | 保持学习 |
| **easy** | +7 天 | +1 | 如果 ease_streak >= 3 → 退役 |
| **retire** | 永久 | 重置为 0 | → 退役 |

- **learning**: 卡牌正在活跃轮换中
- **retired**: 卡牌不会出现在复习中（用户已掌握或手动退役）
- 连续三次"easy"评分会自动使卡牌退役

### YouTube 测验生成

当用户发送 YouTube URL 并想要测验时：

**步骤 1：** 从 URL 中提取视频 ID（例如：从 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 中提取 `dQw4w9WgXcQ`）。

**步骤 2：** 获取字幕：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/youtube_quiz.py fetch VIDEO_ID
```

返回 `{"title": "...", "transcript": "..."}` 或错误信息。

如果脚本报告 `missing_dependency`，告诉用户安装：
```bash
pip install youtube-transcript-api
```

**步骤 3：** 从字幕生成 5 个测验问题。使用这些规则：

```
您正在为播客剧集创建一个 5 题测验。
仅返回一个包含恰好 5 个对象的 JSON 数组。
每个对象必须包含 'question' 和 'answer' 键。

选择标准：
- 优先选择重要、令人惊讶或基础性的事实。
- 跳过填充内容、明显细节以及需要大量上下文的事实。
- 绝不返回 true/false 问题。
- 绝不只问日期。

问题规则：
- 每个问题必须测试恰好一个独立的事实。
- 使用清晰、无歧义的措辞。
- 优先使用 What、Who、How many、Which。
- 避免开放式的 Describe 或 Explain 提示。

答案规则：
- 每个答案必须少于 240 个字符。
- 以答案本身开头，而非前言。
- 如有必要，仅添加最少的澄清细节。
```

使用字幕的前 15,000 个字符作为上下文。自己生成问题（您就是 LLM）。

**步骤 4：** 验证输出是有效的 JSON，且恰好有 5 个项目，每个项目都有非空的 `question` 和 `answer` 字符串。如果验证失败，重试一次。

**步骤 5：** 存储测验卡牌：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add-quiz \
  --video-id "VIDEO_ID" \
  --questions '[{"question":"...","answer":"..."},...]' \
  --collection "测验 - 剧集标题"
```

脚本通过 `video_id` 去重 — 如果该视频的卡牌已存在，则跳过创建并报告现有卡牌。

**步骤 6：** 一次一个问题地呈现，使用相同的自由文本评分流程：
1. 显示"问题 1/5: ..."并等待用户回答。切勿包含答案或任何关于揭示答案的提示。
2. 等待用户用自己的话回答
3. 使用评分提示（参见"复习到期卡牌"部分）对答案进行评分
4. **重要：您必须先向用户回复反馈，然后再执行其他操作。** 显示评分、正确答案以及卡牌的下次到期时间。切勿静默跳到下一个问题。保持简短纯文本。示例："不太对。答案：&#123;答案&#125;。明天下次复习。"
5. **显示反馈后**，调用评分命令，然后在同一条消息中显示下一个问题：
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py rate \
  --id CARD_ID --rating easy --user-answer "用户所说的内容"
```
6. 重复。每个答案在下一个问题之前必须收到可见的反馈。

### 导出/导入 CSV

**导出：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py export \
  --output ~/flashcards.csv
```

生成一个三列的 CSV：`question,answer,collection`（无标题行）。

**导入：**
```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py import \
  --file ~/flashcards.csv \
  --collection "Imported"
```

读取一个包含列 question、answer 以及可选 collection（第 3 列）的 CSV。如果缺少 collection 列，则使用 `--collection` 参数。

### 统计信息

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
```

返回 JSON，包含：
- `total`: 卡牌总数
- `learning`: 活跃轮换中的卡牌
- `retired`: 已掌握的卡牌
- `due_now`: 当前到期待复习的卡牌
- `collections`: 按集合名称分类的细分

## 注意事项

- **切勿直接编辑 `cards.json`** — 始终使用脚本子命令以避免损坏
- **字幕获取失败** — 部分 YouTube 视频没有英文字幕或禁用了字幕；告知用户并建议另一个视频
- **可选依赖** — `youtube_quiz.py` 需要 `youtube-transcript-api`；如果缺少，告诉用户运行 `pip install youtube-transcript-api`
- **大量导入** — 数千行的 CSV 导入可以正常工作，但 JSON 输出可能冗长；为用户总结结果
- **视频 ID 提取** — 支持 `youtube.com/watch?v=ID` 和 `youtu.be/ID` 两种 URL 格式

## 验证

直接验证辅助脚本：

```bash
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py stats
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py add --question "法国的首都是？" --answer "巴黎" --collection "General"
python3 ~/.hermes/skills/productivity/memento-flashcards/scripts/memento_cards.py due
```

如果您从仓库检出进行测试，请运行：

```bash
pytest tests/skills/test_memento_cards.py tests/skills/test_youtube_quiz.py -q
```

代理级别验证：
- 开始一次复习，确认反馈是纯文本、简短，并且在下张卡牌之前始终包含正确答案
- 运行一次 YouTube 测验流程，确认每个答案在下一个问题之前收到可见反馈