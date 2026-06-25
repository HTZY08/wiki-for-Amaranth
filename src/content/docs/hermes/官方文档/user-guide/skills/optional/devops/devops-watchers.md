---
title: Watchers
---

title: "Watchers — 带水印去重的 RSS、JSON API 和 GitHub 轮询"
sidebar_label: "Watchers"
description: "使用水印去重技术轮询 RSS、JSON API 和 GitHub"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能（Skill）的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Watchers（观察器）

通过水印去重（watermark dedup）轮询 RSS、JSON API 和 GitHub。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/devops/watchers` 安装 |
| 路径 | `optional-skills/devops/watchers` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos |
| 标签 | `cron`, `polling`, `rss`, `github`, `http`, `automation`, `monitoring` |

## 参考：完整的 SKILL.md

:::info
以下是当此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# Watchers（观察器）

按时间间隔轮询外部源，仅对新项目做出反应。提供了三个现成的脚本以及一个共享的水印辅助工具；可将它们配置到 cron 任务中（或从终端临时运行）。

## 何时使用

- 用户希望监视 RSS/Atom 订阅源，并在有新条目时获得通知
- 用户希望监视 GitHub 仓库的议题（issues）/拉取请求（pulls）/发布（releases）/提交（commits）
- 用户希望轮询任意 JSON 端点，并在出现新项目时获得通知
- 用户要求“为 X 设置一个观察器”或“在 X 发生变化时通知我”

## 思维模型

观察器（Watcher）只是一个脚本，其工作流程如下：

1. 从外部源获取数据
2. 与之前见过的 ID 的水印文件（watermark file）进行比较
3. 将新的水印写回
4. 将新项目输出到标准输出（无变化则无输出）

下面的脚本处理了上述所有步骤。代理通过终端工具运行这些脚本（通过 cron 任务、webhook 或交互式聊天），并报告新内容。

## 现成脚本

安装技能后，所有三个脚本都位于 `$HERMES_HOME/skills/devops/watchers/scripts/`。每个脚本读取 `WATCHER_STATE_DIR`（默认值为 `$HERMES_HOME/watcher-state/`）中的状态文件，以 `--name` 参数作为键。

| 脚本 | 监视对象 | 去重键（Dedup key） |
|---|---|---|
| `watch_rss.py` | RSS 2.0 或 Atom 订阅源 URL | `<guid>` / `<id>` |
| `watch_http_json.py` | 返回对象列表的任意 JSON 端点 | 可配置的 id 字段 |
| `watch_github.py` | 仓库的 GitHub 议题/拉取请求/发布/提交 | `id` / `sha` |

所有三个脚本：

- 首次运行记录基线（baseline）——不会重播已有订阅源
- 水印是一个有界 ID 集合（最多 500 个），以控制内存使用
- 输出格式：每项为 `## <标题>\n<URL>\n\n<可选正文>`
- 无新项目时标准输出为空——调用者将其视为静默
- 获取错误时返回非零退出码

## 使用方法

直接从终端工具运行观察器：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_rss.py \
  --name hn --url https://news.ycombinator.com/rss --max 5
```

监视 GitHub 仓库（在 `${HERMES_HOME:-~/.hermes}/.env` 中设置 `GITHUB_TOKEN` 以避免匿名速率限制 60 次/小时）：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_github.py \
  --name hermes-issues --repo NousResearch/hermes-agent --scope issues
```

轮询任意 JSON API：

```bash
python $HERMES_HOME/skills/devops/watchers/scripts/watch_http_json.py \
  --name api --url https://api.example.com/events \
  --id-field event_id --items-path data.events
```

## 配置到 cron 中

请代理以类似以下提示安排一个 cron 任务：

> 每 15 分钟运行一次 `watch_rss.py --name hn --url https://news.ycombinator.com/rss`。如果有输出，请总结标题并交付。如果没有输出，则保持静默。

代理通过终端工具在 cron 任务的代理循环中调用脚本；无需对 cron 内置的 `--script` 标志进行任何更改。

## 状态文件

每个观察器都会写入 `$HERMES_HOME/watcher-state/<name>.json`。可查看：

```bash
cat $HERMES_HOME/watcher-state/hn.json
```

强制重播（下次运行视为首次轮询）：

```bash
rm $HERMES_HOME/watcher-state/hn.json
```

## 编写你自己的观察器

所有三个脚本都使用相同的模板：加载水印、获取、比较、保存、输出。`scripts/_watermark.py` 是共享的辅助工具；导入它即可获得原子写入 + 有界 ID 集合 + 首次运行基线。参考三个脚本中的任何一个，了解只需极少的样板代码。

## 常见陷阱

1. **每次运行时都输出“无新项目”标题。** 调用者依赖空的标准输出来表示静默。如果在空的变化上输出了任何内容，就会在频道中产生垃圾信息。附带的脚本已处理此问题；自定义脚本也必须如此。
2. **期望首次运行就能输出项目。** 不会——首次运行会记录基线。如果需要初始摘要，请在首次运行后删除状态文件，或在自定义脚本中添加 `--prime-with-latest N` 标志。
3. **水印无界增长。** 共享辅助工具将 ID 上限设为 500。对于高变化率的订阅源，可以提高该值；在文件系统受限的环境下可以降低。
4. **将状态目录放在代理沙箱无法写入的位置。** `$HERMES_HOME/watcher-state/` 始终可写。Docker/Modal 后端可能无法访问任意主机路径。