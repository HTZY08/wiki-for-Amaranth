--- frontmatter ---
---
version: alpha
name: Heritage
description: 建筑极简主义与新闻庄重感的结合。
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
---

--- body ---
## 概述

建筑极简主义与新闻庄重感的结合……

## 色彩

- **主要色彩 (#1A1C1E):** 用于标题和核心文本的深墨色。
- **第三色彩 (#B8422E):** “波士顿陶土色” — 交互的唯一驱动力。

## 字体排印

所有内容均使用 Public Sans，除小型全大写标签外……

## 组件

`button-primary` 是页面上唯一的高强调动作……

## 令牌（Token）类型

| 类型 | 格式 | 示例 |
|------|--------|---------|
| 色彩 | `#` + 十六进制 (sRGB) | `"#1A1C1E"` |
| 尺寸 | 数字 + 单位 (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| 令牌引用 | `{路径.到.令牌}` | `{colors.primary}` |
| 字体排印 | 包含 `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` 的对象 | 见上 |

组件属性白名单：`backgroundColor`, `textColor`, `typography`,
`rounded`, `padding`, `size`, `height`, `width`。变体（hover, active,
pressed）是**独立的组件条目**，带有相关键名
（`button-primary-hover`），而非嵌套。

## 规范章节顺序

章节为可选，但存在的章节**必须**按此顺序出现。重复的标题会拒绝该文件。

1. 概述（别名：品牌与风格）
2. 色彩
3. 字体排印
4. 布局（别名：布局与间距）
5. 高度与深度（别名：高度）
6. 形状
7. 组件
8. 应做与不应做

未知章节会被保留，不会报错。如果值类型有效，未知的令牌名称也会被接受。未知的组件属性会产生警告。

## 工作流：编写新的 DESIGN.md

1. **询问用户**（或推断）品牌基调、强调色和字体排印方向。如果用户提供了网站、图片或氛围，将其转换为上述令牌形状。
2. **在项目根目录下**使用 `write_file` 编写 `DESIGN.md`。始终包含 `name:` 和 `colors:`；其他章节可选但鼓励包含。
3. **使用令牌引用**（`{colors.primary}`）在 `components:` 章节中，而不是重复编写十六进制值。保持调色板单一来源。
4. **进行 lint 检查**（见下方）。在返回前修复任何损坏的引用或 WCAG 失败。
5. **如果用户已有项目**，还要在同一文件旁边编写 Tailwind 或 DTCG 导出文件（`tailwind.theme.json`、`tokens.json`）。

## 工作流：lint / diff / 导出

CLI 为 `@google/design.md`（Node）。使用 `npx` — 无需全局安装。

```bash
# 验证结构 + 令牌引用 + WCAG 对比度
npx -y @google/design.md lint DESIGN.md

# 比较两个版本，回归时失败（退出码 1 = 回归）
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# 导出为 Tailwind 主题 JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# 导出为 W3C DTCG（设计令牌格式模块）JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# 打印规范本身 — 在注入到代理提示时有用
npx -y @google/design.md spec --rules-only --format json
```

所有命令都接受 `-` 作为标准输入。`lint` 在出现错误时返回退出码 1。如果需要结构化地报告结果，使用 `--format json` 标志并解析输出。

### Lint 规则参考（7 条规则捕捉的内容）

- `broken-ref` （错误）— `{colors.missing}` 指向不存在的令牌
- `duplicate-section` （错误）— 同一 `## 标题` 出现两次
- `invalid-color`, `invalid-dimension`, `invalid-typography` （错误）
- `wcag-contrast` （警告/信息）— 组件 `textColor` 与 `backgroundColor` 的对比度比率，针对 WCAG AA （4.5:1）和 AAA （7:1）
- `unknown-component-property` （警告）— 超出上述白名单

当用户关心无障碍性时，在你的总结中明确提及这一点 — WCAG 发现是使用 CLI 的最重要原因。

## 陷阱

- **不要嵌套组件变体。** `button-primary.hover` 是错误的；应使用同级键 `button-primary-hover`。
- **十六进制颜色必须用引号括起来。** 否则 YAML 会在 `#` 处出错，或奇怪地截断像 `#1A1C1E` 的值。
- **负尺寸也需要引号。** `letterSpacing: -0.02em` 会被解析为 YAML 流 — 应写为 `letterSpacing: "-0.02em"`。
- **章节顺序是强制的。** 如果用户以任意顺序提供了散文，在保存前重新排序以匹配规范列表。
- **`version: alpha` 是当前规范版本**（截至2026年4月）。该规范标记为 alpha — 请注意破坏性变更。
- **令牌引用通过点路径解析。** `{colors.primary}` 有效；`{primary}` 无效。

## 规范来源真相

- 仓库：https://github.com/google-labs-code/design.md （Apache-2.0）
- CLI：npm 上的 `@google/design.md`
- 生成的 DESIGN.md 文件的许可：使用用户项目的许可；规范本身为 Apache-2.0。