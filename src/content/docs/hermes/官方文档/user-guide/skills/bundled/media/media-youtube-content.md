---
title: "Youtube内容 —— 将YouTube转录文本转化为摘要、推文、博客"
sidebar_label: "Youtube内容"
description: "YouTube转录文本转化为摘要、推文、博客"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# Youtube内容

将YouTube转录文本转化为摘要、推文、博客。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/youtube-content` |
| 平台 | linux, macos, windows |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# YouTube内容工具

## 使用场景

当用户分享 YouTube URL 或视频链接、要求总结视频、请求获取转录文本，或希望从任何 YouTube 视频中提取并重新格式化内容时使用。将转录文本转化为结构化内容（章节、摘要、推文、博客文章）。

从 YouTube 视频中提取转录文本，并将其转化为有用的格式。

## 设置

使用 `uv` 将依赖安装到运行辅助脚本的同一 Hermes 管理环境中：

```bash
uv pip install youtube-transcript-api
```

## 辅助脚本

`SKILL_DIR` 是包含此 SKILL.md 文件的目录。该脚本接受任何标准的 YouTube URL 格式、短链接 (youtu.be)、Shorts、嵌入链接、直播链接或原始 11 字符视频 ID。

```bash
# 带元数据的 JSON 输出
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# 纯文本（适合通过管道进一步处理）
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# 带时间戳
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# 指定语言并带后备链
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## 输出格式

获取转录文本后，根据用户需求进行格式化：

- **章节（Chapters）**：按主题转换分组，输出带时间戳的章节列表
- **摘要（Summary）**：整个视频的简洁概述，5-10句话
- **章节摘要（Chapter summaries）**：每个章节附带一段简短摘要
- **推文（Thread）**：Twitter/X 推文格式——带编号的帖子，每条不超过 280 字符
- **博客文章（Blog post）**：包含标题、章节和关键要点的完整文章
- **引用（Quotes）**：带时间戳的引人注目的引用

### 示例 —— 章节输出

```
00:00 引言 —— 主持人以问题陈述开场
03:45 背景 —— 先前工作及现有解决方案为何不足
12:20 核心方法 —— 所提方法的逐步讲解
24:10 结果 —— 基准比较与关键要点
31:55 问答 —— 观众关于可扩展性和后续步骤的问题
```

## 工作流程

1. **获取（Fetch）**：使用辅助脚本并通过 `uv run python3` 运行 `--text-only --timestamps` 参数获取转录文本。
2. **验证（Validate）**：确认输出非空且为预期语言。如果为空，在不带 `--language` 参数的情况下重试以获取任何可用的转录文本。如果仍然为空，告知用户该视频可能禁用了转录功能。
3. **分块（Chunk if needed）**：如果转录文本超过约 50K 字符，则分割成重叠的块（约 40K 字符，重叠 2K），并在合并前对每个块进行摘要。
4. **转换（Transform）**：转换为请求的输出格式。如果用户未指定格式，默认生成摘要。
5. **验证（Verify）**：重新阅读转换后的输出，检查连贯性、时间戳正确性和完整性，然后再呈现给用户。

## 错误处理

- **转录功能禁用（Transcript disabled）**：告知用户；建议他们检查视频页面是否提供字幕。
- **私密/不可用视频（Private/unavailable video）**：转发错误信息，并要求用户验证 URL。
- **无匹配语言（No matching language）**：在不带 `--language` 参数的情况下重试以获取任何可用的转录文本，然后向用户说明实际语言。
- **依赖缺失（Dependency missing）**：运行 `uv pip install youtube-transcript-api` 并重试。