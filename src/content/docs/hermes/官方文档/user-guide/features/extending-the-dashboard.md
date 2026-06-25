---
title: "Extending The Dashboard"
---

# API 参考

## 主题端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/themes` | GET | 列出可用主题及当前活动主题名称。内置主题返回 `{name, label, description}`；用户主题额外包含 `definition` 字段，提供完整的规范化主题对象。 |
| `/api/dashboard/theme` | PUT | 设置活动主题。请求体：`{"name": "midnight"}`。持久化到 `config.yaml` 中的 `dashboard.theme` 下。 |

## 插件端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/api/dashboard/plugins` | GET | 列出已发现的插件（包含清单，已去除内部字段）。 |
| `/api/dashboard/plugins/rescan` | GET | 强制重新扫描插件目录，无需重启。 |
| `/dashboard-plugins/<name>/<path>` | GET | 提供插件 `dashboard/` 目录下的静态资源。路径遍历已被阻止。 |
| `/api/plugins/<name>/*` | * | 插件注册的后端路由。 |

## 窗口上的 SDK

| 全局变量 | 类型 | 提供者 |
|--------|------|----------|
| `window.__HERMES_PLUGIN_SDK__` | object | `registry.ts` — 包含 React、钩子、UI 组件、API 客户端、工具函数。 |
| `window.__HERMES_PLUGINS__.register(name, Component)` | function | 注册插件的主组件。 |
| `window.__HERMES_PLUGINS__.registerSlot(name, slot, Component)` | function | 注册到指定的壳插槽（shell slot）中。 |

---

# 故障排除

**我的主题没有出现在选择器中。**
检查文件是否位于 `~/.hermes/dashboard-themes/` 并以 `.yaml` 或 `.yml` 结尾。刷新页面。运行 `curl http://127.0.0.1:9119/api/dashboard/themes` — 你的主题应出现在响应中。如果 YAML 存在解析错误，控制台日志会记录到 `~/.hermes/logs/errors.log`。

**插件的选项卡没有显示。**
1. 检查清单文件是否位于 `~/.hermes/plugins/<name>/dashboard/manifest.json`（注意 `dashboard/` 子目录）。
2. 执行 `curl http://127.0.0.1:9119/api/dashboard/plugins/rescan` 强制重新发现。
3. 打开浏览器开发者工具 → 网络 — 确认 `manifest.json`、`index.js` 以及任何 CSS 加载成功，无 404 错误。
4. 打开浏览器开发者工具 → 控制台 — 查找 IIFE 期间的错误或 `window.__HERMES_PLUGINS__ is undefined`（表示 SDK 未初始化，通常是由于更早的 React 渲染崩溃）。
5. 确认你的打包文件使用与 `manifest.json:name` **相同** 的名称调用了 `window.__HERMES_PLUGINS__.register(...)`。

**注册到插槽的组件没有渲染。**
`sidebar` 插槽仅在当前主题的 `layoutVariant` 为 `cockpit` 时渲染。其他插槽始终渲染。如果你注册到一个没有命中的插槽，请在 `registerSlot` 内部添加 `console.log` 以确认插件包确实运行了。

**插件后端路由返回 404。**
1. 确认清单中的 `"api": "plugin_api.py"` 指向 `dashboard/` 目录下存在的文件。
2. 重启 `hermes dashboard` — 插件 API 路由只在启动时挂载，**不会**在重新扫描时挂载。
3. 检查 `plugin_api.py` 是否导出了模块级别的 `router = APIRouter()`。其他导出名称不会被识别。
4. 查看 `~/.hermes/logs/errors.log` 末尾的 `Failed to load plugin <name> API routes` — 导入错误会记录在那里。

**切换主题会丢失我的颜色覆盖设置。**
`colorOverrides` 作用于当前活动主题，并在主题切换时被清除 — 这是设计如此。如果你希望覆盖设置持久保留，请将其放入主题的 YAML 文件中，而不是使用实时切换器。

**主题的 customCSS 被截断了。**
`customCSS` 块每个主题最大限制为 32 KiB。将大型样式表拆分到多个主题中，或者改用通过其 `css` 字段注入完整样式表的插件（无大小限制）。

**我想在 PyPI 上发布一个插件。**
控制台插件是通过目录布局安装的，而不是通过 pip 入口点。目前最简洁的分发方式是提供一个 git 仓库，用户将其克隆到 `~/.hermes/plugins/`。基于 pip 的控制台插件安装程序目前尚未实现。