---
title: Page Agent
---

title: "页面代理（Page Agent）"
sidebar_label: "页面代理"
description: "将 alibaba/page-agent 嵌入到你自己的 Web 应用程序中 —— 一个纯 JavaScript 的页面内 GUI 代理，以单个 <script> 标签或 npm 包形式交付，让你的网站最终用户能够用自然语言驱动界面（“点击登录，填入用户名 John”）。无需 Python、无头浏览器或扩展。当用户是一位希望给自己的 SaaS / 管理面板 / B2B 工具添加 AI 助手、让传统 Web 应用支持自然语言交互、或基于本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，使用此技能。不适用于服务端浏览器自动化 —— 这类用户应指向 Hermes 内置的浏览器工具。"
---

--- body ---
--- body ---
{/* 此页面由技能目录中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# 页面代理（Page Agent）

将 alibaba/page-agent 嵌入到你自己的 Web 应用程序中 —— 一个纯 JavaScript 的页面内 GUI 代理（Agent），以单个 &lt;script&gt; 标签或 npm 包形式交付，让你的网站最终用户能够用自然语言驱动界面（“点击登录，填入用户名 John”）。无需 Python、无头浏览器或扩展。当用户是一位希望给自己的 SaaS / 管理面板 / B2B 工具添加 AI 助手（Copilot）、让传统 Web 应用支持自然语言交互、或基于本地（Ollama）或云端（Qwen / OpenAI / OpenRouter）LLM 评估 page-agent 的 Web 开发者时，使用此技能。不适用于服务端浏览器自动化 —— 这类用户应指向 Hermes 内置的浏览器工具。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 使用 `hermes skills install official/web-development/page-agent` 安装 |
| 路径 | `optional-skills/web-development/page-agent` |
| 版本 | `1.0.0` |
| 作者 | Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `web`, `javascript`, `agent`, `browser`, `gui`, `alibaba`, `embed`, `copilot`, `saas` |

## 参考：完整 SKILL.md

:::info
以下是当该技能被触发时 Hermes 加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# page-agent

alibaba/page-agent（https://github.com/alibaba/page-agent，17k+ star，MIT）是一个用 TypeScript 编写的页面内 GUI 代理。它存在于网页内部，将 DOM 读取为文本（无需截图，无需多模态 LLM），并根据当前页面执行自然语言指令，如“点击登录按钮，然后将用户名填写为 John”。纯客户端 —— 宿主网站只需包含一个脚本并传递一个兼容 OpenAI 的 LLM 端点。

## 何时使用此技能

当用户想要以下功能时加载此技能：

- **在自己的 Web 应用中交付 AI 助手**（SaaS、管理面板、B2B 工具、ERP、CRM）——“我的仪表盘用户应该能输入‘为 Acme Corp 创建发票并通过邮件发送’，而不是点击五个页面”
- **改造传统 Web 应用**，无需重写前端 —— page-agent 直接叠加在现有 DOM 之上
- **通过自然语言增强无障碍性** —— 语音 / 屏幕阅读器用户通过描述所需操作来驱动界面
- **演示或评估 page-agent**，基于本地（Ollama）或托管（Qwen、OpenAI、OpenRouter）LLM
- **构建交互式培训 / 产品演示** —— 让 AI 在真实 UI 中引导用户完成“如何提交费用报告”的流程

## 何时不使用此技能

- 用户希望 **Hermes 自身来驱动浏览器** → 使用 Hermes 内置的浏览器工具（Browserbase / Camofox）。page-agent 是*相反*的方向。
- 用户希望 **无需嵌入即可进行跨标签页自动化** → 使用 Playwright、browser-use 或 page-agent 的 Chrome 扩展
- 用户需要 **视觉定位/截图** → page-agent 仅基于文本 DOM；应改用多模态浏览器代理

## 前提条件

- Node 22.13+ 或 24+，npm 10+（文档声称需要 11+，但 10.9 也能正常工作）
- 兼容 OpenAI 的 LLM 端点：Qwen（DashScope）、OpenAI、Ollama、OpenRouter 或任何支持 `/v1/chat/completions` 的服务
- 带有开发者工具的浏览器（用于调试）

## 方式 1 —— 通过 CDN 进行 30 秒演示（无需安装）

最快看到效果的方式。使用阿里巴巴的免费测试 LLM 代理 —— **仅供评估使用**，需遵守其条款。

添加到任意 HTML 页面（或作为书签小工具粘贴到开发者工具控制台中）：

```html
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js" crossorigin="true"></script>
```

面板出现。输入一条指令。完成。

书签小工具形式（拖入书签栏，点击任意页面运行）：

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/page-agent@1.8.0/dist/iife/page-agent.demo.js';document.head.appendChild(s);})();
```

## 方式 2 —— 通过 npm 安装到自己的 Web 应用中（生产使用）

在现有的 Web 项目（React / Vue / Svelte / 原生）中：

```bash
npm install page-agent
```

使用你自己的 LLM 端点进行配置 —— **切勿将演示 CDN 交付给真实用户**：

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: process.env.LLM_API_KEY,   // 切勿硬编码
    language: 'en-US',
})

// 为最终用户显示面板：
agent.panel.show()

// 或通过编程方式驱动：
await agent.execute('提交按钮，然后将用户名改为 John')
```

提供商示例（任何兼容 OpenAI 的端点均可工作）：

| 提供商 | `baseURL` | `model` |
|----------|-----------|---------|
| Qwen / DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen3.5-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen3:14b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4.6` |

**关键配置项**（传递给 `new PageAgent({...})`）：

- `model`、`baseURL`、`apiKey` —— LLM 连接
- `language` —— UI 语言（`en-US`、`zh-CN` 等）
- 用于限制代理可操作范围的白名单和数据脱敏钩子 —— 完整选项列表请参见 https://alibaba.github.io/page-agent/

**安全**。在生产部署中，不要在客户端代码中放置 `apiKey` —— 通过你的后端代理 LLM 调用，并将 `baseURL` 指向你的代理。演示 CDN 之所以存在，是因为阿里巴巴运行该代理用于评估。

## 方式 3 —— 克隆源代码仓库（贡献或自行修改）

当用户想要修改 page-agent 本身、通过本地 IIFE 包在任意网站上测试，或开发浏览器扩展时使用此方式。

```bash
git clone https://github.com/alibaba/page-agent.git
cd page-agent
npm ci              # 精确锁文件安装（或 `npm i` 允许更新）
```

在仓库根目录下创建 `.env` 文件，填入 LLM 端点。示例：

```
LLM_MODEL_NAME=gpt-4o-mini
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
```

Ollama 风格：

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=NA
LLM_MODEL_NAME=qwen3:14b
```

常用命令：

```bash
npm start           # 文档/网站开发服务器
npm run build       # 构建所有包
npm run dev:demo    # 在 http://localhost:5174/page-agent.demo.js 提供 IIFE 包
npm run dev:ext     # 开发浏览器扩展（WXT + React）
npm run build:ext   # 构建扩展
```

**使用本地 IIFE 包在任何网站上测试**。添加以下书签小工具：

```javascript
javascript:(function(){var s=document.createElement('script');s.src=`http://localhost:5174/page-agent.demo.js?t=${Math.random()}`;s.onload=()=>console.log('PageAgent ready!');document.head.appendChild(s);})();
```

然后执行：`npm run dev:demo`，在任何页面上点击书签小工具，本地构建的包就会注入。保存时自动重新构建。

**警告：** 在开发构建过程中，你的 `.env` 中的 `LLM_API_KEY` 会被内联到 IIFE 包中。不要分享这个包。不要提交它。不要将 URL 粘贴到 Slack 中。（已验证：在公共开发包中搜索，能直接得到 `.env` 中的原始值。）

## 仓库布局（方式 3）

npm workspaces 管理的单体仓库（Monorepo）。关键包：

| 包 | 路径 | 用途 |
|---------|------|------|
| `page-agent` | `packages/page-agent/` | 主入口，带 UI 面板 |
| `@page-agent/core` | `packages/core/` | 核心代理逻辑，无 UI |
| `@page-agent/mcp` | `packages/mcp/` | MCP 服务器（测试版） |
| — | `packages/llms/` | LLM 客户端 |
| — | `packages/page-controller/` | DOM 操作 + 视觉反馈 |
| — | `packages/ui/` | 面板 + 国际化 |
| — | `packages/extension/` | Chrome/Firefox 扩展 |
| — | `packages/website/` | 文档 + 落地网站 |

## 验证是否正常工作

在方式 1 或方式 2 之后：
1. 在浏览器中打开页面，同时打开开发者工具
2. 你应该会看到一个浮动的面板。如果没有，请检查控制台是否有错误（最常见原因：LLM 端点的 CORS 问题、错误的 `baseURL` 或无效的 API 密钥）
3. 输入一条与页面上可见元素匹配的简单指令（“点击 Login 链接”）
4. 观察网络（Network）标签页 —— 你应该看到向你的 `baseURL` 发起的请求

在方式 3 之后：
1. `npm run dev:demo` 会输出 `Accepting connections at http://localhost:5174`
2. `curl -I http://localhost:5174/page-agent.demo.js` 返回 `HTTP/1.1 200 OK` 及 `Content-Type: application/javascript`
3. 在任何网站上点击书签小工具，面板出现

## 常见陷阱

- **在生产中使用演示 CDN** —— 不要这样做。它有限流、使用阿里巴巴的免费代理，并且其条款禁止生产使用。
- **API 密钥暴露** —— 传递给 `new PageAgent({apiKey: ...})` 的任何密钥都会包含在你的 JS 包中。对于真实部署，始终通过你自己的后端代理。
- **非 OpenAI 兼容端点**会静默失败或出现难以理解的错误。如果你的提供商需要使用原生 Anthropic/Gemini 格式，请在前面使用 OpenAI 兼容代理（LiteLLM、OpenRouter）。
- **CSP 拦截** —— 具有严格内容安全策略（Content-Security-Policy）的网站可能拒绝加载 CDN 脚本或禁止内联 eval。在这种情况下，请从你的源站自托管。
- **在方式 3 中编辑 `.env` 后需要重启开发服务器** —— Vite 仅在启动时读取环境变量。
- **Node 版本** —— 仓库声明为 `^22.13.0 || >=24`。Node 20 在 `npm ci` 时会因引擎错误而失败。
- **npm 10 vs 11** —— 文档说需要 npm 11+；实际上 npm 10.9 也能正常工作。

## 参考

- 仓库：https://github.com/alibaba/page-agent
- 文档：https://alibaba.github.io/page-agent/
- 许可证：MIT（基于 browser-use 的 DOM 处理内部实现，版权所有 2024 Gregor Zunic）