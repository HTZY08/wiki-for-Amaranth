--- frontmatter ---
---
title: "Dogfood — 网页应用探索性QA：发现漏洞、证据、报告"
sidebar_label: "Dogfood"
description: "网页应用的探索性QA：发现漏洞、证据、报告"
---

--- body ---
{/* 本页面由网站/scripts/generate-skill-docs.py 从技能的SKILL.md自动生成。请编辑源文件SKILL.md，而非此页面。 */}

# Dogfood

网页应用的探索性QA：发现漏洞、证据、报告。

## 技能元数据(Skill metadata)

| 字段 | 值 |
|------|-----|
| 来源(Source) | 内置（默认安装） |
| 路径(Path) | `skills/dogfood` |
| 版本(Version) | `1.0.0` |
| 平台(Platforms) | linux, macos, windows |
| 标签(Tags) | `qa`, `testing`, `browser`, `web`, `dogfood` |

## 参考：完整SKILL.md

:::info
以下是Hermes在触发此技能时加载的完整技能定义。当技能激活时，代理(Agent)会将其视为指令。
:::

# Dogfood：系统性Web应用QA测试

## 概述(Overview)

本技能指导您使用浏览器工具集对Web应用进行系统性的探索性QA测试。您将导航到应用、与元素交互、捕获问题证据，并生成结构化的漏洞报告。

## 先决条件(Prerequisites)

- 浏览器工具集必须可用（`browser_navigate`、`browser_snapshot`、`browser_click`、`browser_type`、`browser_vision`、`browser_console`、`browser_scroll`、`browser_back`、`browser_press`）
- 用户提供目标URL和测试范围

## 输入(Inputs)

用户提供：
1. **目标URL(Target URL)** — 测试的入口点
2. **范围(Scope)** — 需要重点关注哪些区域/功能（或“全站”进行全面测试）
3. **输出目录(Output directory)**（可选）— 用于保存截图和报告的位置（默认：`./dogfood-output`）

## 工作流(Workflow)

请遵循以下5个阶段的系统化工作流：

### 阶段1：计划(Plan)

1. 创建输出目录结构：
<!-- ascii-guard-ignore -->
   ```
   {output_dir}/
   ├── screenshots/       # 证据截图
   └── report.md          # 最终报告（阶段5生成）
   ```
<!-- ascii-guard-ignore-end -->
2. 根据用户输入确定测试范围。
3. 通过规划要测试的页面和功能来构建粗略的站点地图：
   - 着陆页/首页
   - 导航链接（页眉、页脚、侧边栏）
   - 关键用户流程（注册、登录、搜索、结算等）
   - 表单和交互式元素
   - 边缘情况（空状态、错误页面、404）

### 阶段2：探索(Explore)

对于计划中的每个页面或功能：

1. **导航**到页面：
   ```
   browser_navigate(url="https://example.com/page")
   ```

2. **拍摄快照**以了解DOM结构：
   ```
   browser_snapshot()
   ```

3. **检查控制台**是否有JavaScript错误：
   ```
   browser_console(clear=true)
   ```
   每次导航后和每次重要交互后都要执行此操作。静默的JS错误是高价值发现。

4. **拍摄带注释的截图**以视觉评估页面并识别交互式元素：
   ```
   browser_vision(question="Describe the page layout, identify any visual issues, broken elements, or accessibility concerns", annotate=true)
   ```
   `annotate=true` 标志会在交互式元素上叠加编号为`[N]`的标签。每个`[N]`对应后续浏览器命令中的引用`@eN`。

5. **系统化测试交互式元素**：
   - 点击按钮和链接：`browser_click(ref="@eN")`
   - 填写表单：`browser_type(ref="@eN", text="test input")`
   - 测试键盘导航：`browser_press(key="Tab")`，`browser_press(key="Enter")`
   - 滚动内容：`browser_scroll(direction="down")`
   - 使用无效输入测试表单验证
   - 测试空提交

6. **每次交互后**，检查：
   - 控制台错误：`browser_console()`
   - 视觉变化：`browser_vision(question="What changed after the interaction?")`
   - 预期行为与实际行为

### 阶段3：收集证据(Collect Evidence)

对于发现的每个问题：

1. **拍摄截图**展示问题：
   ```
   browser_vision(question="Capture and describe the issue visible on this page", annotate=false)
   ```
   保存响应中的`screenshot_path` — 你将在报告中引用它。

2. **记录详情**：
   - 问题发生的URL
   - 复现步骤
   - 预期行为
   - 实际行为
   - 控制台错误（如果有）
   - 截图路径

3. **使用问题分类体系(issue taxonomy)**对问题进行归类（参见 `references/issue-taxonomy.md`）：
   - 严重程度(Severity)：严重(Critical) / 高(High) / 中(Medium) / 低(Low)
   - 分类(Category)：功能(Functional) / 视觉(Visual) / 无障碍(Accessibility) / 控制台(Console) / 用户体验(UX) / 内容(Content)

### 阶段4：分类(Categorize)

1. 审查所有收集到的问题。
2. 去重 — 合并在不同位置表现为同一漏洞的问题。
3. 为每个问题分配最终严重程度和分类。
4. 按严重程度排序（严重优先，然后高、中、低）。
5. 按严重程度和分类统计问题数量，用于执行摘要。

### 阶段5：报告(Report)

使用 `templates/dogfood-report-template.md` 中的模板生成最终报告。

报告必须包含：
1. **执行摘要(Executive summary)**，包含问题总数、按严重程度的细分、测试范围
2. **每个问题的章节**，包含：
   - 问题编号和标题
   - 严重程度和分类徽章
   - 观察到问题的URL
   - 问题描述
   - 复现步骤
   - 预期行为与实际行为
   - 截图引用（使用 `MEDIA:<screenshot_path>` 嵌入图片）
   - 控制台错误（如果相关）
3. **所有问题的汇总表**
4. **测试说明(Testing notes)** — 测试内容、未测试内容、任何阻塞项

将报告保存到 `{output_dir}/report.md`。

## 工具参考(Tools Reference)

| 工具(Tool) | 用途(Purpose) |
|------------|---------------|
| `browser_navigate` | 导航到URL |
| `browser_snapshot` | 获取DOM文本快照（无障碍树） |
| `browser_click` | 通过引用(`@eN`)或文本点击元素 |
| `browser_type` | 在输入字段中输入内容 |
| `browser_scroll` | 在页面上向上/向下滚动 |
| `browser_back` | 在浏览器历史中后退 |
| `browser_press` | 按下键盘按键 |
| `browser_vision` | 截图 + AI分析；使用 `annotate=true` 获取元素标签 |
| `browser_console` | 获取JS控制台输出和错误 |

## 提示(Tips)

- **每次导航和重要交互后务必检查 `browser_console()`。** 静默的JS错误是最有价值的问题之一。
- **当你需要判断交互式元素位置或快照引用不清晰时，使用 `browser_vision` 的 `annotate=true`。**
- **同时使用有效和无效输入进行测试** — 表单验证漏洞很常见。
- **滚动长页面** — 折叠区域下方的内容可能存在渲染问题。
- **测试导航流程** — 端到端地点击多步骤流程。
- **检查响应式行为** — 注意截图中可见的任何布局问题。
- **不要忘记边缘情况：** 空状态、非常长的文本、特殊字符、快速点击。
- 向用户报告截图时，请包含 `MEDIA:<screenshot_path>`，以便他们能内联查看证据。