---
title: X (推特) 搜索
description: 通过 xAI 内置的 x_search 响应工具，让代理搜索 X (推特) 帖子和讨论串——支持 SuperGrok OAuth 登录或 XAI_API_KEY 两种方式。
sidebar_label: X (推特) 搜索
sidebar_position: 7
---

# X (推特) 搜索

`x_search` 工具让代理能够直接搜索 X (推特) 上的帖子、个人资料和讨论串。它基于 xAI 在 Responses API (网址为 `https://api.x.ai/v1/responses`) 上内置的 `x_search` 工具——Grok 本身在服务端运行搜索，并返回带有原始帖子引用的合成结果。

当您特别想要查看 **X 上** 当前的讨论、反应或声明时，**请使用此工具代替 `web_search`**。对于一般网页，请继续使用 `web_search` / `web_extract`。

:::tip
如果您已经为 Portal 上的 xAI 模型付费，那么 Live Search 调用会计入为聊天配置的同一个 xAI 密钥。请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 身份验证

当 **任一** xAI 凭证路径可用时，`x_search` 工具会注册：

| 凭证 | 来源 | 设置 |
|------------|--------|-------|
| **SuperGrok / X Premium+ OAuth**（推荐） | 在 `accounts.x.ai` 通过浏览器登录，自动刷新 | `hermes auth add xai-oauth` — 请参阅 [xAI Grok OAuth (SuperGrok / X Premium+)](../../guides/xai-grok-oauth.md) |
| **`XAI_API_KEY`** | 付费的 xAI API 密钥 | 在 `~/.hermes/.env` 中设置 |

两者都使用相同的负载访问同一个端点——唯一的区别是 bearer 令牌。**当两个都配置时，SuperGrok OAuth 优先**，因此 x_search 会使用您的订阅配额而非付费 API 消费。

该工具的 `check_fn` 会在每次重新构建模型工具列表时运行 xAI 凭证解析器。返回 `True` 表示 bearer 可获取、非空，并且（如果已过期）已成功刷新。已撤销且刷新失败的令牌会从架构中隐藏该工具；模型根本无法看到它。

## 启用工具

当存在 xAI 凭证（OAuth 令牌或 `XAI_API_KEY`）时自动启用。如果您不希望使用，可以通过 `hermes tools` → Search → x_search 显式禁用。

```bash
hermes tools
# → 🐦 X (推特) 搜索   (按空格键切换为启用)
```

选择器提供两种凭证选择：

1. **xAI Grok OAuth (SuperGrok / Premium+)** — 如果您尚未登录，则打开浏览器转到 `accounts.x.ai`
2. **xAI API 密钥** — 提示输入 `XAI_API_KEY`

任一种选择都能满足准入要求。您可以选择已有的任何一种凭证；该工具在两者下功能完全相同。如果最终两个都配置了，调用时 OAuth 优先。

## 配置

```yaml
# ~/.hermes/config.yaml
x_search:
  # 用于 Responses 调用的 xAI 模型。
  # grok-4.20-reasoning 是推荐的默认值；任何具有 x_search 工具访问权限的 Grok 模型均可。
  model: grok-4.20-reasoning

  # 请求超时时间（秒）。对于复杂查询，x_search 可能需要 60–120 秒——默认值已足够宽松。最小值：30。
  timeout_seconds: 180

  # 在 5xx / ReadTimeout / ConnectionError 错误时的自动重试次数。
  # 每次重试都会回退（尝试次数 × 1.5 秒，上限为 5 秒）。
  retries: 2
```

## 工具参数

代理使用以下参数调用 `x_search`：

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `query` | string (必需) | 在 X 上要查找的内容。 |
| `allowed_x_handles` | string array | 可选，要 **仅** 包含的句柄列表（最多 10 个）。开头的 `@` 会被去除。 |
| `excluded_x_handles` | string array | 可选，要排除的句柄列表（最多 10 个）。与 `allowed_x_handles` 互斥。 |
| `from_date` | string | 可选的 `YYYY-MM-DD` 起始日期。 |
| `to_date` | string | 可选的 `YYYY-MM-DD` 结束日期。 |
| `enable_image_understanding` | boolean | 要求 xAI 分析匹配帖子中附加的图片。 |
| `enable_video_understanding` | boolean | 要求 xAI 分析匹配帖子中附加的视频。 |

该工具返回 JSON，包含：

- `answer` — Grok 合成的文本响应
- `citations` — Responses API 顶级字段返回的引用
- `inline_citations` — 从消息体中提取的 `url_citation` 注释（每个包含 `url`、`title`、`start_index`、`end_index`）
- `degraded` — 当设置了任何限定过滤器（`allowed_x_handles`、`excluded_x_handles`、`from_date`、`to_date`）并且两个引用通道都返回空时为 `true`。在这种情况下，`answer` 是根据模型自身知识合成的，而非来自 X 索引，因此应将其视为无来源。否则为 `false`（包括“未设置过滤器”的情况——一个宽泛的无来源答案只是答案，而不是过滤失败）
- `degraded_reason` — 简短字符串，说明哪些过滤器处于激活状态；如果 `degraded` 为 `false` 则为 `null`
- `credential_source` — 如果 OAuth 解析成功则为 `"xai-oauth"`，如果使用 API 密钥则为 `"xai"`
- `model`、`query`、`provider`、`tool`、`success`

### 日期验证

`from_date` / `to_date` 会在 HTTP 调用之前在客户端进行验证：

- 如果提供了两者，则必须能够解析为 `YYYY-MM-DD` 格式。
- 如果两者都设置，`from_date` 必须早于或等于 `to_date`。
- `from_date` 不得晚于今天的 UTC 时间——尚未开始的时间窗口中不可能存在帖子，因此调用必然返回零引用。
- 允许 `to_date` 为未来日期（调用方可能会合法地请求“从昨天到明天”以捕获即将到达的帖子）。

验证失败会以结构化的 `{"error": "..."}` 工具结果形式呈现，绝不会触发对 xAI 的 HTTP 调用。

## 示例

与代理对话：

> X 上的人们对新 Grok 图片功能有什么看法？重点关注来自 @xai 的回复。

代理将：

1. 调用 `x_search`，参数为 `query="reactions to new Grok image features"`，`allowed_x_handles=["xai"]`
2. 返回一个合成答案以及指向特定帖子的引用列表
3. 用答案和引用进行回复

## 故障排除

### "No xAI credentials available"

当两个认证路径都失败时，工具会显示此信息。请在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，或运行 `hermes auth add xai-oauth` 并完成浏览器登录。然后重新启动会话，以便代理重新读取工具注册表。

### "`x_search` is not enabled for this model"

配置的 `x_search.model` 没有服务端 `x_search` 工具的访问权限。请切换到 `grok-4.20-reasoning`（默认值）或其他支持该工具的 Grok 模型。查看 [xAI 文档](https://docs.x.ai/) 以获取当前列表。

### 工具未出现在架构中

两种可能原因：

1. **工具集未启用。** 运行 `hermes tools` 并确认 `🐦 X (推特) 搜索` 已选中。
2. **没有 xAI 凭证。** check_fn 返回 False，因此架构保持隐藏。运行 `hermes auth status` 确认 xai-oauth 登录状态，并检查 `XAI_API_KEY` 是否已设置（如果您使用 API 密钥路径）。

### `degraded: true` — 无引用的答案

当您使用了 `allowed_x_handles`、`excluded_x_handles` 或日期范围，并且响应返回了 `degraded: true` 时，xAI 的 X 索引未找到匹配的帖子，但 Grok 仍然根据其训练数据生成了合成答案。该答案无来源——请勿将其视为真实的 X 搜索结果。

值得排查的原因：

- **句柄拼写错误。** 去掉 `@`，仔细检查拼写，并确认该账户存在。
- **日期范围过窄** 或滑过了今天的帖子；请扩大范围重试。
- **xAI 索引缺口。** 某些活跃账户即使定期发帖，也可能间歇性地无法在 `x_search` 中显示。等待几分钟后重试，或者在需要精确句柄时间线时使用 `xurl` 技能进行直接的 X API 读取。

## 另请参阅

- [xAI Grok OAuth (SuperGrok / Premium+)](../../guides/xai-grok-oauth.md) — OAuth 设置指南
- [Web 搜索与提取](web-search.md) — 用于一般（非 X）网页搜索
- [工具参考](../../reference/tools-reference.md) — 完整工具目录