---
title: Codex 接入指南
description: 将 OpenAI Codex CLI 接入 Hermes Agent——安装、认证、代理、配置、使用
---

[Codex CLI](https://github.com/openai/codex) 是 OpenAI 的自主编码 Agent，在 Hermes 中作为**执行层**使用。

## 架构

```
你提需求 → Hermes (骨架模型) → 分析/规划 → Codex CLI → 执行/编码 → 返回结果
                ↑                            ↑
          DeepSeek/Gemini/...          GPT-5.5 (ChatGPT OAuth)
```

**分工：**
- **Hermes 骨架模型**（DeepSeek V4 Flash 等）负责分析、规划、决策
- **Codex** 负责执行——写代码、改文件、跑命令
- Codex 底层用的是 **GPT-5.5**，通过 ChatGPT Plus 订阅的 OAuth 鉴权，不走 OpenAI API 计费

## 两种接入方式

| 方式 | 原理 | 费用 | 推荐场景 |
|------|------|------|---------|
| **`openai-codex` provider** | Hermes 原生内置，通过 ChatGPT 后端 API 调用 GPT-5.5 | 消耗 ChatGPT Plus 额度 | 日常对话、轻量编码 |
| **Codex CLI 二进制** | 独立命令行工具，`npx @openai/codex` 运行 | 同上 | 批量任务、文件操作、PR 审查 |

本教程主要覆盖 **Codex CLI** 的接入。

## 前置条件

- Hermes Agent 已部署运行
- ChatGPT Plus 或 API key 认证（Codex 优先走 OAuth，但也支持 API key 直接认证）
- 代理（mihomo/Clash）已运行——Codex 连接 chatgpt.com 需要代理

## 第一步：安装 Codex CLI

```bash
# 全局安装（推荐）
npm install -g @openai/codex

# 验证
codex --version
# 输出: 0.x.y
```

或用 `npx` 免安装运行（首次稍慢）：

```bash
npx -y @openai/codex --version
```

## 第二步：认证

Codex CLI 通过 OAuth 设备认证登录你的 ChatGPT Plus 账户。

### 方式 A：直接登录 Codex CLI

```bash
# 确保代理正在运行
pgrep -a mihomo || echo "代理未运行"

# 启动设备认证
npx -y @openai/codex login --device-auth

# 终端会输出一个 10 位验证码和一个 URL
# 在浏览器打开 URL，输入验证码，完成登录
# 认证信息存储在 ~/.codex/auth.json
```

### 方式 B：通过 Hermes auth 系统

```bash
# Hermes 内置的 openai-codex provider 认证
hermes auth add openai-codex

# ⚠️ 注意：此命令超时时间为 300 秒
# 如果浏览器验证流程较长，可能超时
# 可靠做法：先用方式 A 登录，然后将 token 导入 Hermes
```

### 故障排除：认证超时

如果 `hermes auth add openai-codex` 超时，可用以下方法手动导入：

```bash
# 1. 直接登录 Codex CLI
npx -y @openai/codex login --device-auth
# 完成浏览器验证

# 2. 提取 token
cat ~/.codex/auth.json
# 复制 token 内容

# 3. 导入到 Hermes
# 编辑 ~/.hermes/auth.json，按格式添加 openai-codex 条目
```

## 第三步：代理配置

Codex CLI 通过 WebSocket 连接 `wss://chatgpt.com/backend-api/codex/responses`，**必须经过代理**。

```bash
# 验证代理可用
curl -s --proxy http://127.0.0.1:7890 --connect-timeout 5 \
  https://chatgpt.com -o /dev/null -w "%{http_code}"
# 200 = 正常；000 = 代理挂了

# 如果代理挂了，重启
pkill -f mihomo 2>/dev/null
mihomo -d /opt/data/mihomo-config &
sleep 3
# 再次验证
```

> **代理挂了的表现**：Codex 启动时报 `Failed to refresh token` 和 `Connection refused (os error 111)`。不只是登录，每次使用都依赖代理。

## 第四步：在 Hermes 中配置 openai-codex provider

在 Hermes 配置中启用 Codex 作为模型 provider：

```yaml
# ~/.hermes/config.yaml
providers:
  openai-codex:
    # 使用从 Codex CLI 导入的 OAuth token
    # 或通过 hermes auth add openai-codex 配置
    models:
      gpt-5.5:
        # 默认模型
```

然后在模型路由中指定使用：

```yaml
models:
  - name: codex-coding
    provider: openai-codex
    model: gpt-5.5
```

## 使用方式

### 在对话中委托任务

Hermes 会自动将编码任务委托给 Codex 执行。典型流程：

```
你：帮我写一个 Python 脚本，批量重命名某个目录下的文件

Hermes：我先分析需求...
        → 调用 Codex CLI → 执行 → 返回结果
```

### 手动调 Codex CLI

通过终端直接运行：

```bash
# 一对一任务（推荐用 --yolo 跳过确认）
codex exec --sandbox danger-full-access "写一个脚本，..."

# 后台长任务
codex exec --full-auto "重构 auth 模块..."
```

### 并行工作流

```bash
# 批量处理多个 issue
cd /tmp/issue-1 && git init && codex exec "Fix issue 1" --background &
cd /tmp/issue-2 && git init && codex exec "Fix issue 2" --background &
```

## 关键参数

| 参数 | 效果 | 适用场景 |
|------|------|---------|
| `exec "prompt"` | 执行完退出 | 单次任务 |
| `--sandbox danger-full-access` | 跳过沙箱（Docker 内必须） | 所有 WSL/Docker 环境 |
| `--yolo` | 无沙箱无确认 | 已审过的计划执行 |
| `--full-auto` | 沙箱内自动批准 | 构建任务 |

> ⚠️ Docker/WSL 环境下 bubblewrap 沙箱会因 user namespace 限制失败，**必须用 `--sandbox danger-full-access`**。`--sandbox none` 是无效参数。

## 常见问题

### Codex 拒绝运行："Not a git repository"

Codex 要求必须在 git 仓库内运行。临时方案：

```bash
cd $(mktemp -d) && git init && codex exec "你的需求"
```

### 连接失败

检查：
```
1. 代理是否运行 → curl 测试 chatgpt.com
2. OAuth token 是否过期 → codex login --device-auth 重新登录
3. 网络是否通畅
```

### Codex 一直卡住不动

PTY 模式下偶尔会等待输入。用 `process(action="log")` 查看输出。如果卡在询问用户确认，用 `process(action="submit", data="yes")` 放行。

### 提示"升级 ChatGPT 计划"

Codex 需要 ChatGPT Plus 或更高计划。免费版用户无法使用。

## 限制

- **必须联网**：Codex 是云端服务，离线不可用
- **必须翻墙**：`wss://chatgpt.com` 被封锁，需要代理
- **沙箱在 Docker 内受限**：必须用 `danger-full-access` 跳过
- **Git 仓库依赖**：即使处理无关文件的任务也需要 `.git` 目录
- **OAuth token 有过期时间**，需要定期重新登录

## 关联 Skills

- `codex` — Codex CLI 完整操作指南（含 PR 审查、并行修复、概念评审等高级用法）
- `hermes-agent` — Hermes Agent 配置管理
