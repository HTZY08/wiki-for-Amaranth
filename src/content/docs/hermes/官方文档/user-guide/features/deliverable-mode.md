---
title: Deliverable Mode
---

title: 交付模式（聊天中的工件）
sidebar_label: 交付模式
description: 智能体如何将生成的图表、PDF、电子表格及其他文件作为消息平台的原生附件交付。
---

# 交付模式

当 Hermes 智能体（Agent）在消息网关（Slack、Discord、Telegram、WhatsApp、Signal 等）内运行时，它可以将生成的文件直接交付到聊天中——不是作为用户需要复制的路径，而是作为原生附件。

图表以内联图片形式显示。PDF 报告以文件下载形式出现。电子表格作为 `.xlsx` 上传。智能体无需编写 `MEDIA:` 标签或做任何特殊操作——它只需生成文件并在响应中提及文件的绝对路径。网关从文本中提取该路径，将其从可见消息中移除，并以原生方式上传文件。

## 工作原理

三个部分协同工作：

1. **智能体拥有生成文件的工具。** `execute_code` 通过 matplotlib 生成图表，`latex-pdf-report` 技能（Skill）生成 PDF，`powerpoint` 技能生成演示文稿，`image_generate` 生成图片，`text_to_speech` 生成音频，等等。

2. **网关扫描智能体响应中的文件路径。** 任何以支持的扩展名结尾的绝对路径（`/tmp/...`）或以 home 开头的相对路径（`~/...`）都会被提取出来。代码块和内联代码中的路径会被忽略，因此代码示例永远不会被破坏。

3. **网关按文件类型分发。** 在平台支持的情况下，图片以内联方式嵌入；视频以内联方式嵌入；音频路由到语音/音频附件；其他所有内容作为文件附件上传。

## 支持的文件扩展名

| 类别 | 扩展名 | 交付方式 |
|---|---|---|
| 图片 | `.png .jpg .jpeg .gif .webp .bmp .tiff .svg` | 内联嵌入 |
| 视频 | `.mp4 .mov .avi .mkv .webm` | 内联嵌入（平台支持时） |
| 音频 | `.mp3 .wav .ogg .m4a .flac` | 语音/音频附件 |
| 文档 | `.pdf .docx .doc .odt .rtf .txt .md` | 文件上传 |
| 数据 | `.xlsx .xls .csv .tsv .json .xml .yaml .yml` | 文件上传 |
| 演示文稿 | `.pptx .ppt .odp` | 文件上传 |
| 压缩包 | `.zip .tar .gz .tgz .bz2 .7z` | 文件上传 |
| 网页 | `.html .htm` | 文件上传 |

`.py`、`.log` 及其他源代码文件扩展名被有意排除，因此智能体不会自动发送任意源代码文件；如果希望向用户发送代码，请使用代码块。

## 鼓励智能体生成工件

默认情况下，智能体不会主动生成工件——它需要知道应该这样做。有两种方式可以引导它：

**按会话：** 明确要求（“将对比结果以图表形式发送给我”、“将数据以 CSV 格式返回”），或编写自定义指令/个性条目，使其在消息平台上偏向于工件风格的回复。

**项目级别：** 在智能体工作的项目中的 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` 中添加偏好，或添加到 `~/.hermes/SOUL.md` 中的全局角色（Persona），或作为 `~/.hermes/config.yaml` 中 `agent.personalities` 下的命名预设（可通过 `/personality` 按会话切换）。

智能体需要使用的机制很简单：将文件渲染为绝对路径（例如 `/tmp/q3-revenue.png`），并在回复中以纯文本形式提及该路径。其余工作由网关完成。围栏代码块或反引号内的路径会被忽略，因此代码示例永远不会被破坏。

## 看板：工件伴随完成通知

如果您使用 Hermes 的看板（Kanban）多智能体工作流，工作人员（Worker）可以将可交付文件附加到其 `kanban_complete` 调用中：

```python
kanban_complete(
    summary="渲染了 Q3 收入图表和报告",
    artifacts=[
        "/tmp/q3-revenue.png",
        "/tmp/q3-report.pdf",
    ],
)
```

当网关通知器向在 Slack/Telegram 等平台上订阅该任务的人发送“任务完成”消息时，它还会将每个工件作为原生附件上传到该聊天中。人类用户将在同一位置获得可交付内容和摘要。

如果通知器运行时文件在磁盘上不存在，则会静默跳过。

## 通过 MCP 连接更多服务

除了工件交付管道之外，智能体还可以通过 MCP（模型上下文协议，Model Context Protocol）访问其他服务。MCP 生态系统为大多数流行工具提供了社区服务器——根据需求安装即可：

| 服务 | 能解锁的功能 |
|---|---|
| **Notion** | 读写 Notion 页面、数据库、查询工作区 |
| **GitHub** | 议题、PR、评论，以及超越 gh CLI 的仓库搜索 |
| **Linear** | 工单、项目、周期 |
| **Slack** | 工作区范围搜索、读取其他频道 |
| **Gmail** | 收件箱分类、发送邮件、标签管理 |
| **Salesforce** | 线索、商机、客户数据 |
| **Snowflake / BigQuery** | 针对数据仓库的 SQL 查询 |
| **Google Drive** | 文件搜索、内容、共享管理 |

通过 `~/.hermes/config.yaml` 的 `mcp_servers` 部分安装 MCP 服务器。完整设置指南请参见 [MCP 集成](./mcp.md)。

## 与 Slack 中 Perplexity Computer 的比较

Perplexity Computer 的 Slack 集成基于同样的理念：智能体生成可交付内容（图表、PDF、幻灯片）并将其作为原生附件发布回线程中。Hermes 智能体的交付模式在本地提供了相同的面向用户模式：

- 生成发生在用户自己的虚拟环境 / 沙箱中（无远程租户）。
- 文件通过相同的 Slack `files.uploadV2` API 进入聊天。
- 连接器的广度通过 MCP 实现，而非由 400 个托管集成的策划目录——安装您实际使用的那些即可。

OAuth 令牌保留在用户的 `auth.json` / `.env` 文件中。无需托管令牌存储。无需多租户微VM。最终结果相同。