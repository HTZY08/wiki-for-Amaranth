--- frontmatter ---
---
title: "Parallel Cli 命令行工具"
sidebar_label: "Parallel Cli"
description: "Parallel CLI 的可选供应商技能——代理原生（agent-native）的网络搜索、提取、深度研究、丰富化（enrichment）、FindAll 和监控"
---

--- body ---
{/* 本页面由技能目录下的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Parallel Cli

Parallel CLI 的可选供应商技能——代理原生（agent-native）的网络搜索、提取、深度研究、丰富化（enrichment）、FindAll 和监控。优先使用 JSON 输出和非交互式流程。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——通过 `hermes skills install official/research/parallel-cli` 安装 |
| 路径 | `optional-skills/research/parallel-cli` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Research`, `Web`, `Search`, `Deep-Research`, `Enrichment`, `CLI` |
| 相关技能 | [`duckduckgo-search`](/docs/user-guide/skills/optional/research/research-duckduckgo-search), [`mcporter`](/docs/user-guide/skills/optional/mcp/mcp-mcporter) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Parallel CLI

当用户明确要求使用 Parallel，或者终端原生工作流需要利用 Parallel 的供应商专有堆栈进行网络搜索、提取、深度研究、丰富化（enrichment）、实体发现或监控时，请使用 `parallel-cli`。

这是一个可选的第三方工作流，并非 Hermes 核心功能。

重要预期：
- Parallel 是一项付费服务（提供免费套餐），并非完全免费的本地工具。
- 它与 Hermes 原生 `web_search` / `web_extract` 功能存在重叠，因此普通查询时不要默认推荐它。
- 当用户明确提及 Parallel，或需要 Parallel 特有的丰富化（enrichment）、FindAll、监控等工作流时，才优先使用此技能。

`parallel-cli` 专为代理设计：
- 通过 `--json` 输出 JSON
- 非交互式命令执行
- 使用 `--no-wait`、`status` 和 `poll` 进行异步长时间运行任务
- 使用 `--previous-interaction-id` 进行上下文链接
- 在一个 CLI 中完成搜索、提取、研究、丰富化（enrichment）、实体发现和监控

## 何时使用

在以下情况下优先使用此技能：
- 用户明确提及 Parallel 或 `parallel-cli`
- 任务需要比简单一次性搜索/提取更丰富的工作流
- 需要异步深度研究任务（可启动后稍后轮询）
- 需要结构化丰富化（enrichment）、FindAll 实体发现或监控

当用户未特别要求 Parallel 时，优先使用 Hermes 原生 `web_search` / `web_extract` 进行快速一次性查询。

## 安装

根据环境选择侵入性最小的安装路径。

### Homebrew

```bash
brew install parallel-web/tap/parallel-cli
```

### npm

```bash
npm install -g parallel-web-cli
```

### Python 包

```bash
pip install "parallel-web-tools[cli]"
```

### 独立安装程序

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

如果需要隔离的 Python 安装，也可以使用 `pipx`：

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

## 认证

交互式登录：

```bash
parallel-cli login
```

无头/SSH/CI 环境：

```bash
parallel-cli login --device
```

API 密钥环境变量：

```bash
export PARALLEL_API_KEY="***"
```

验证当前认证状态：

```bash
parallel-cli auth
```

如果认证需要浏览器交互，请使用 `pty=true` 运行。

## 核心规则集

1. 当需要机器可读输出时，始终优先使用 `--json`。
2. 优先使用显式参数和非交互式流程。
3. 对于长时间运行的任务，使用 `--no-wait`，然后使用 `status` / `poll`。
4. 仅引用 CLI 输出中返回的 URL。
5. 当可能后续追问时，将较大的 JSON 输出保存到临时文件。
6. 仅对真正长时间运行的工作流使用后台进程；否则在前台运行。
7. 优先使用 Hermes 原生工具，除非用户明确要求 Parallel 或需要 Parallel 特有的工作流。

## 快速参考

<!-- ascii-guard-ignore -->
```text
parallel-cli
├── auth
├── login
├── logout
├── search
├── extract / fetch
├── research run|status|poll|processors
├── enrich run|status|poll|plan|suggest|deploy
├── findall run|ingest|status|poll|result|enrich|extend|schema|cancel
└── monitor create|list|get|update|delete|events|event-group|simulate
```
<!-- ascii-guard-ignore-end -->

## 常用标志和模式

常用标志：
- `--json` 用于结构化输出
- `--no-wait` 用于异步任务
- `--previous-interaction-id <id>` 用于复用之前上下文的后续任务
- `--max-results <n>` 用于搜索结果数量
- `--mode one-shot|agentic` 用于搜索行为
- `--include-domains domain1.com,domain2.com`
- `--exclude-domains domain1.com,domain2.com`
- `--after-date YYYY-MM-DD`

方便时从标准输入读取：

```bash
echo "Anthropic 的最新融资情况如何？" | parallel-cli search - --json
echo "研究问题" | parallel-cli research run - --json
```

## 搜索

用于获取当前网络上的结构化结果。

```bash
parallel-cli search "Anthropic 最新的 AI 模型是什么？" --json
parallel-cli search "Apple 的 SEC 文件" --include-domains sec.gov --json
parallel-cli search "比特币价格" --after-date 2026-01-01 --max-results 10 --json
parallel-cli search "最新浏览器基准测试" --mode one-shot --json
parallel-cli search "AI 编码代理企业版评测" --mode agentic --json
```

有用的约束条件：
- `--include-domains` 限定可信来源
- `--exclude-domains` 排除噪音域名
- `--after-date` 按时间过滤
- `--max-results` 需要更广覆盖时使用

如果预期会有后续问题，请保存输出：

```bash
parallel-cli search "最新 React 19 变更" --json -o /tmp/react-19-search.json
```

汇总结果时：
- 先给出答案
- 包含日期、名称和具体事实
- 仅引用返回的源
- 不要虚构 URL 或源标题

## 提取

用于从 URL 中提取干净的内容或 Markdown。

```bash
parallel-cli extract https://example.com --json
parallel-cli extract https://company.com --objective "查找定价信息" --json
parallel-cli extract https://example.com --full-content --json
parallel-cli fetch https://example.com --json
```

当页面内容广泛且只需要某一类信息时，使用 `--objective`。

## 深度研究

用于可能耗时较长的多步研究任务。

常见处理器层级：
- `lite` / `base` 用于更快、更便宜的扫描
- `core` / `pro` 用于更全面的综合分析
- `ultra` 用于最繁重的研究任务

### 同步

```bash
parallel-cli research run \
  "比较领先的 AI 编码代理在定价、模型支持和企业级控制方面的差异" \
  --processor core \
  --json
```

### 异步启动 + 轮询

```bash
parallel-cli research run \
  "比较领先的 AI 编码代理在定价、模型支持和企业级控制方面的差异" \
  --processor ultra \
  --no-wait \
  --json

parallel-cli research status trun_xxx --json
parallel-cli research poll trun_xxx --json
parallel-cli research processors --json
```

### 上下文链接 / 后续提问

```bash
parallel-cli research run "顶级的 AI 编码代理有哪些？" --json
parallel-cli research run \
  "排名第一的代理提供了哪些企业级控制？" \
  --previous-interaction-id trun_xxx \
  --json
```

推荐的 Hermes 工作流：
1. 使用 `--no-wait --json` 启动
2. 捕获返回的 run/task ID
3. 如果用户希望继续其他工作，则继续执行
4. 稍后调用 `status` 或 `poll`
5. 使用返回源中的引用汇总最终报告

## 丰富化（Enrichment）

当用户拥有 CSV/JSON/表格输入，并希望根据网络研究推断出额外的列时使用。

### 建议列

```bash
parallel-cli enrich suggest "查找 CEO 和年度营收" --json
```

### 规划配置

```bash
parallel-cli enrich plan -o config.yaml
```

### 内联数据

```bash
parallel-cli enrich run \
  --data '[{"company": "Anthropic"}, {"company": "Mistral"}]' \
  --intent "查找总部和员工数量" \
  --json
```

### 非交互式文件运行

```bash
parallel-cli enrich run \
  --source-type csv \
  --source companies.csv \
  --target enriched.csv \
  --source-columns '[{"name": "company", "description": "公司名称"}]' \
  --intent "查找 CEO 和年度营收"
```

### YAML 配置运行

```bash
parallel-cli enrich run config.yaml
```

### 状态 / 轮询

```bash
parallel-cli enrich status <task_group_id> --json
parallel-cli enrich poll <task_group_id> --json
```

在非交互式操作时，使用显式的 JSON 数组定义列。在报告成功前验证输出文件。

## FindAll

当用户希望获得一个发现的数据集而非简短答案时，用于网络规模的实体发现。

```bash
parallel-cli findall run "查找提供企业产品的 AI 编码代理初创公司" --json
parallel-cli findall run "医疗保健领域的 AI 初创公司" -n 25 --json
parallel-cli findall status <run_id> --json
parallel-cli findall poll <run_id> --json
parallel-cli findall result <run_id> --json
parallel-cli findall schema <run_id> --json
```

当用户希望获得一组可后续查看、过滤或丰富化（enrichment）的发现实体时，此功能比普通搜索更合适。

## 监控

用于持续检测随时间变化的内容。

```bash
parallel-cli monitor list --json
parallel-cli monitor get <monitor_id> --json
parallel-cli monitor events <monitor_id> --json
parallel-cli monitor delete <monitor_id> --json
```

创建通常是最敏感的部分，因为频率和交付方式很重要：

```bash
parallel-cli monitor create --help
```

当用户希望定期跟踪某个页面或来源（而非一次性获取）时使用。

## 推荐的 Hermes 使用模式

### 快速回答并附带引用
1. 运行 `parallel-cli search ... --json`
2. 解析标题、URL、日期、摘要
3. 仅使用返回 URL 的引用进行汇总

### URL 调查
1. 运行 `parallel-cli extract URL --json`
2. 如有需要，使用 `--objective` 或 `--full-content` 重新运行
3. 引用或汇总提取的 Markdown

### 长研究工作流
1. 运行 `parallel-cli research run ... --no-wait --json`
2. 存储返回的 ID
3. 继续其他工作或定期轮询
4. 汇总最终报告并附带引用

### 结构化丰富化（Enrichment）工作流
1. 检查输入文件及其列
2. 使用 `enrich suggest` 或提供显式的丰富化列
3. 运行 `enrich run`
4. 如有需要轮询完成状态
5. 在报告成功前验证输出文件

## 错误处理和退出码

CLI 记录了以下退出码：
- `0` 成功
- `2` 输入错误
- `3` 认证错误
- `4` API 错误
- `5` 超时

如果遇到认证错误：
1. 检查 `parallel-cli auth`
2. 确认 `PARALLEL_API_KEY` 已设置，或运行 `parallel-cli login` / `parallel-cli login --device`
3. 验证 `parallel-cli` 在 `PATH` 中

## 维护

检查当前认证/安装状态：

```bash
parallel-cli auth
parallel-cli --help
```

更新命令：

```bash
parallel-cli update
pip install --upgrade parallel-web-tools
parallel-cli config auto-update-check off
```

## 陷阱

- 除非用户明确要求人类可读的输出，否则不要省略 `--json`。
- 不要引用 CLI 输出中不存在的来源。
- `login` 可能需要 PTY/浏览器交互。
- 对于短任务，优先前台执行；不要过度使用后台进程。
- 对于大型结果集，将 JSON 保存到 `/tmp/*.json`，而不是将所有内容塞入上下文。
- 当 Hermes 原生工具已足够时，不要默默选择 Parallel。
- 请记住这是一个供应商工作流，通常需要账户认证，并且超出免费套餐后需付费使用。