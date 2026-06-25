--- frontmatter ---
---
title: "Airtable — 通过 curl 使用 Airtable REST API"
sidebar_label: "Airtable"
description: "通过 curl 使用 Airtable REST API"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能（Skill）的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Airtable

通过 curl 使用 Airtable REST API。支持记录（Records）的增删改查、筛选（Filters）、更新或插入（Upserts）。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 捆绑（默认安装） |
| 路径 | `skills/productivity/airtable` |
| 版本 | `1.1.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Airtable`, `Productivity`, `Database`, `API` |

## 参考：完整的 SKILL.md

:::info
以下是当此技能（Skill）被触发时 Hermes 加载的完整技能定义。当技能（Skill）激活时，代理（Agent）会将此视为指令。
:::

# Airtable — 基础（Bases）、表（Tables）与记录（Records）

使用 `terminal` 工具通过 `curl` 直接操作 Airtable 的 REST API。无需 MCP 服务器、OAuth 流程或 Python SDK——只需 `curl` 和一个个人访问令牌（Personal Access Token）。

## 先决条件

1. 在 https://airtable.com/create/tokens 创建一个 **个人访问令牌（Personal Access Token, PAT）**（令牌以 `pat...` 开头）。
2. 授予以下作用域（Scope）（最低要求）：
   - `data.records:read` — 读取行
   - `data.records:write` — 创建/更新/删除行
   - `schema.bases:read` — 列出基础（Bases）和表（Tables）
3. **重要：** 在同一令牌 UI 中，将你要访问的每个基础（Base）添加到令牌的**访问**列表。PAT 是基于基础（Base）的作用域——一个有效的令牌在错误的基础（Base）上会返回 `403`。
4. 将令牌存储在 `${HERMES_HOME:-~/.hermes}/.env`（或通过 `hermes setup` 设置）：
   ```
   AIRTABLE_API_KEY=pat_your_token_here
   ```

> 注意：传统的 `key...` API 密钥已于 2024 年 2 月弃用。目前仅支持 PAT 和 OAuth 令牌。

## API 基础

- **端点（Endpoint）：** `https://api.airtable.com/v0`
- **认证头（Auth header）：** `Authorization: Bearer $AIRTABLE_API_KEY`
- **所有请求** 使用 JSON（任何 POST/PATCH/PUT 的请求体需要 `Content-Type: application/json`）。
- **对象 ID：** 基础（Base）以 `app...` 开头，表（Table）以 `tbl...` 开头，记录（Record）以 `rec...` 开头，字段（Field）以 `fld...` 开头。ID 永远不会改变；名称可以。在自动化中优先使用 ID。
- **速率限制：** 每个基础（Base）每秒 5 个请求。`429` → 退避。对单个基础（Base）的突发请求会被限制。

基础 curl 模式：
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=5" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

`-s` 隐藏 curl 的进度条——每次调用都保持此设置，以使工具输出保持干净，供 Hermes 使用。通过 `python3 -m json.tool`（始终存在）或 `jq`（如果已安装）管道输出可读的 JSON。

## 字段类型（请求体形状）

| 字段类型 | 写入形状 |
|---|---|
| 单行文本 | `"Name": "hello"` |
| 长文本 | `"Notes": "multi\nline"` |
| 数字 | `"Score": 42` |
| 复选框 | `"Done": true` |
| 单选 | `"Status": "Todo"`（除非 `typecast: true`，否则名称必须已存在） |
| 多选 | `"Tags": ["urgent", "bug"]` |
| 日期 | `"Due": "2026-04-01"` |
| 日期时间（UTC） | `"At": "2026-04-01T14:30:00.000Z"` |
| URL / 电子邮件 / 电话 | `"Link": "https://…"` |
| 附件 | `"Files": [{"url": "https://…"}]`（Airtable 获取并重新托管） |
| 链接记录 | `"Owner": ["recXXXXXXXXXXXXXX"]`（记录 ID 数组） |
| 用户 | `"AssignedTo": {"id": "usrXXXXXXXXXXXXXX"}` |

在创建/更新请求体的顶层传递 `"typecast": true`，让 Airtable 自动强制转换值（例如，即时创建新的选择选项，将 `"42"` 转换为 `42`）。

## 常见查询

### 列出令牌可以访问的基础（Bases）
```bash
curl -s "https://api.airtable.com/v0/meta/bases" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 列出一个基础（Base）的表（Tables）+ 模式（Schema）
```bash
curl -s "https://api.airtable.com/v0/meta/bases/$BASE_ID/tables" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
在进行修改前使用此命令——确认确切的字段名称和 ID，显示选择字段的 `options.choices`，并显示主字段名称。

### 列出记录（前 10 条）
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 获取单条记录
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 筛选记录（filterByFormula）
Airtable 公式必须进行 URL 编码。让 Python 标准库完成——切勿手动编码：
```bash
FORMULA="{Status}='Todo'"
ENC=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$FORMULA")
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?filterByFormula=$ENC&maxRecords=20" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

有用的公式模式：
- 精确匹配：`{Email}='user@example.com'`
- 包含：`FIND('bug', LOWER({Title}))`
- 多个条件：`AND({Status}='Todo', {Priority}='High')`
- 或：`OR({Owner}='alice', {Owner}='bob')`
- 非空：`NOT({Assignee}='')`
- 日期比较：`IS_AFTER({Due}, TODAY())`

### 排序 + 选择特定字段
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?sort%5B0%5D%5Bfield%5D=Priority&sort%5B0%5D%5Bdirection%5D=asc&fields%5B%5D=Name&fields%5B%5D=Status" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
查询参数中的方括号必须进行 URL 编码（`%5B` / `%5D`）。

### 使用命名视图（View）
```bash
curl -s "https://api.airtable.com/v0/$BASE_ID/$TABLE?view=Grid%20view&maxRecords=50" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```
视图会在服务端应用其保存的筛选和排序。

## 常见修改操作

### 创建一条记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Name":"New task","Status":"Todo","Priority":"High"}}' | python3 -m json.tool
```

### 一次调用创建最多 10 条记录
```bash
curl -s -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "typecast": true,
    "records": [
      {"fields": {"Name": "Task A", "Status": "Todo"}},
      {"fields": {"Name": "Task B", "Status": "In progress"}}
    ]
  }' | python3 -m json.tool
```
批量端点每个请求最多**10 条记录**。对于更大的插入操作，每 10 条记录为一个批次循环，并短暂休眠以遵守每秒 5 个请求/基础（Base）的限制。

### 更新一条记录（PATCH — 合并，保留未更改的字段）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"Status":"Done"}}' | python3 -m json.tool
```

### 通过合并字段进行更新或插入（Upsert）（无需 ID）
```bash
curl -s -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "performUpsert": {"fieldsToMergeOn": ["Email"]},
    "records": [
      {"fields": {"Email": "user@example.com", "Status": "Active"}}
    ]
  }' | python3 -m json.tool
```
`performUpsert` 会创建合并字段值为新的记录，并修补合并字段值已存在的记录。非常适合幂等同步。

### 删除一条记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

### 一次调用删除最多 10 条记录
```bash
curl -s -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE?records%5B%5D=rec1&records%5B%5D=rec2" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | python3 -m json.tool
```

## 分页（Pagination）

列表端点每页最多返回 **100 条记录**。如果响应包含 `"offset": "..."`，则在下次调用中将其传回。循环直到该字段不存在：

```bash
OFFSET=""
while :; do
  URL="https://api.airtable.com/v0/$BASE_ID/$TABLE?pageSize=100"
  [ -n "$OFFSET" ] && URL="$URL&offset=$OFFSET"
  RESP=$(curl -s "$URL" -H "Authorization: Bearer $AIRTABLE_API_KEY")
  echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(r["id"], r["fields"].get("Name","")) for r in d["records"]]'
  OFFSET=$(echo "$RESP" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("offset",""))')
  [ -z "$OFFSET" ] && break
done
```

## 典型 Hermes 工作流程

1. **确认认证。** `curl -s -o /dev/null -w "%{http_code}\n" https://api.airtable.com/v0/meta/bases -H "Authorization: Bearer $AIRTABLE_API_KEY"` — 期望 `200`。
2. **找到基础（Base）。** 列出基础（Bases）（如上一步）或者如果令牌缺少 `schema.bases:read` 权限，直接询问用户 `app...` ID。
3. **检查模式（Schema）。** `GET /v0/meta/bases/$BASE_ID/tables` — 在修改任何内容之前，在会话中本地缓存确切的字段名称和主字段名称。
4. **写入前先读取。** 对于“更新 X 其中 Y”，首先使用 `filterByFormula` 解析出 `rec...` ID，然后 `PATCH /v0/$BASE_ID/$TABLE/$RECORD_ID`。切勿猜测记录 ID。
5. **批量写入。** 将相关的创建操作合并到一次 10 条记录的 POST 中，以保持在 5 个请求/秒的预算内。
6. **破坏性操作。** 删除操作无法通过 API 撤销。如果用户说“删除所有 X”，请回显筛选条件和记录计数，并在执行前确认。

## 陷阱（Pitfalls）

- **`filterByFormula` 必须进行 URL 编码。** 具有空格或非 ASCII 字符的字段名称也需要编码（`{My Field}` → `%7BMy%20Field%7D`）。使用 Python 标准库（上述模式）——切勿手动转义。
- **空字段在响应中被省略。** 缺少 `"Assignee"` 键并不意味着该字段不存在——而是意味着该记录的值是空的。在得出结论认为字段缺失之前，请检查模式（步骤 3）。
- **PATCH 与 PUT。** `PATCH` 将提供的字段合并到记录中。`PUT` 完全替换记录，并清除任何你未包含的字段。默认使用 `PATCH`。
- **单选选项必须存在。** 当 `Shipping` 不在字段的选项列表中时，写入 `"Status": "Shipping"` 会引发 `INVALID_MULTIPLE_CHOICE_OPTIONS` 错误，除非你传递 `"typecast": true`（这会自动创建选项）。
- **基于基础（Base）的令牌作用域。** 在一个基础（Base）上出现 `403` 而在另一个基础（Base）上正常，意味着令牌的访问列表不包含该基础（Base）——不是作用域或认证问题。请用户访问 https://airtable.com/create/tokens 授予权限。
- **速率限制是基于基础（Base）的，而非基于令牌。** 在 `baseA` 上每秒 5 个请求和在 `baseB` 上每秒 5 个请求没问题；但仅在 `baseA` 上每秒 6 个请求就会触发限制。监控 `429` 响应的 `Retry-After` 头。

## 给 Hermes 的重要说明

- **始终使用带有 `curl` 的 `terminal` 工具。** 不要使用 `web_extract`（它无法发送认证头）或 `browser_navigate`（需要 UI 认证且速度慢）。
- **`AIRTABLE_API_KEY` 会自动从 `${HERMES_HOME:-~/.hermes}/.env` 流入子进程**——当此技能（Skill）加载时，无需在每次 `curl` 调用前重新导出。
- **小心转义公式中的花括号。** 在 heredoc 正文中，`{Status}` 是字面量。在 shell 参数中，`{Status}` 在 `{...}` 大括号展开（brace expansion）上下文之外是安全的——但在将动态字符串拼接到 URL 之前，请通过 `python3 urllib.parse.quote` 传递。
- **使用 `python3 -m json.tool`（始终存在）进行漂亮的打印**，而不是 `jq`（可选）。仅在你需要筛选/投影时才使用 `jq`。
- **分页是按页的，不是全局的。** Airtable 的 100 条记录上限是硬限制；无法增加。使用 `offset` 循环直到该字段不存在。
- **阅读非 2xx 响应中的 `errors` 数组**——Airtable 会返回结构化的错误代码，如 `AUTHENTICATION_REQUIRED`、`INVALID_PERMISSIONS`、`MODEL_ID_NOT_FOUND`、`INVALID_MULTIPLE_CHOICE_OPTIONS`，这些代码会准确地告诉你问题所在。