--- frontmatter ---
---
title: "Canvas — Canvas LMS集成 — 使用API令牌认证获取已注册课程和作业"
sidebar_label: "Canvas"
description: "Canvas LMS集成 — 使用API令牌（API token）认证获取已注册课程和作业"
---

--- body ---
{/* 本页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而不是本页面。 */}

# Canvas

Canvas LMS（Canvas学习管理系统）集成——使用API令牌（API token）认证获取已注册的课程和作业。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/productivity/canvas` 安装 |
| 路径 | `optional-skills/productivity/canvas` |
| 版本 | `1.0.0` |
| 作者 | community |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Canvas`, `LMS`, `Education`, `Courses`, `Assignments` |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理（Agent）所看到的指令内容。
:::

# Canvas LMS — 课程与作业访问

对 Canvas LMS 的只读访问，用于列出课程和作业。

## 脚本

- `scripts/canvas_api.py` — 用于 Canvas API 调用的 Python CLI

## 设置

1. 在浏览器中登录你的 Canvas 实例
2. 前往 **账号 → 设置**（点击个人资料图标，然后点击设置）
3. 滚动到 **已批准的集成**，点击 **+ 新建访问令牌**
4. 为令牌命名（例如 "Hermes Agent"），设置可选过期时间，点击 **生成令牌**
5. 复制令牌并添加到 `${HERMES_HOME:-~/.hermes}/.env`：

```
CANVAS_API_TOKEN=your_token_here
CANVAS_BASE_URL=https://yourschool.instructure.com
```

基础 URL 即你在浏览器中登录 Canvas 时看到的 URL（末尾不要加斜杠）。

## 用法

```bash
CANVAS="python $HERMES_HOME/skills/productivity/canvas/scripts/canvas_api.py"

# 列出所有活跃课程
$CANVAS list_courses --enrollment-state active

# 列出所有课程（任意状态）
$CANVAS list_courses

# 列出特定课程的作业
$CANVAS list_assignments 12345

# 按截止日期排序列出作业
$CANVAS list_assignments 12345 --order-by due_at
```

## 输出格式

**list_courses** 返回：
```json
[{"id": 12345, "name": "Intro to CS", "course_code": "CS101", "workflow_state": "available", "start_at": "...", "end_at": "..."}]
```

**list_assignments** 返回：
```json
[{"id": 67890, "name": "Homework 1", "due_at": "2025-02-15T23:59:00Z", "points_possible": 100, "submission_types": ["online_upload"], "html_url": "...", "description": "...", "course_id": 12345}]
```

注意：作业描述会被截断为 500 个字符。`html_url` 字段链接到 Canvas 中的完整作业页面。

## API 参考（curl）

```bash
# 列出课程
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses?enrollment_state=active&per_page=10"

# 列出某门课程的作业
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses/COURSE_ID/assignments?per_page=10&order_by=due_at"
```

Canvas 使用 `Link` 头进行分页。Python 脚本会自动处理分页。

## 规则

- 本技能为**只读**——仅获取数据，绝不修改课程或作业
- 首次使用时，通过运行 `$CANVAS list_courses` 验证认证——若返回 401 错误，请引导用户完成设置
- Canvas 的速率限制约为每 10 分钟 700 次请求；若遇到限制，请检查 `X-Rate-Limit-Remaining` 头

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| 401 未授权 | 令牌无效或已过期——在 Canvas 设置中重新生成 |
| 403 禁止访问 | 令牌缺乏该课程的权限 |
| 课程列表为空 | 尝试 `--enrollment-state active` 或省略该标志以查看所有状态 |
| 机构错误 | 确认 `CANVAS_BASE_URL` 与浏览器中的 URL 一致 |
| 超时错误 | 检查到 Canvas 实例的网络连接 |