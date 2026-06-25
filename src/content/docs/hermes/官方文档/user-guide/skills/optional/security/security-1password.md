--- frontmatter ---
---
title: "1Password — 设置并使用 1Password CLI (op)"
sidebar_label: "1Password"
description: "设置并使用 1Password CLI (op)"
---

--- body ---
--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能（Skill）的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 1Password

设置并使用 1Password CLI (op)。当安装 CLI、启用桌面应用集成、登录以及为命令读取/注入机密（secrets）时使用此技能。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源（Source） | 可选（Optional） — 使用 `hermes skills install official/security/1password` 安装 |
| 路径（Path） | `optional-skills/security/1password` |
| 版本（Version） | `1.0.0` |
| 作者（Author） | arceus77-7，由 Hermes Agent 增强 |
| 许可证（License） | MIT |
| 平台（Platforms） | linux, macos, windows |
| 标签（Tags） | `security`, `secrets`, `1password`, `op`, `cli` |

## 参考：完整 SKILL.md

:::info
以下是在此技能被触发时 Hermes 加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# 1Password CLI

当用户希望机密（secrets）通过 1Password 管理而不是纯文本环境变量或文件时，使用此技能。

## 要求（Requirements）

- 1Password 账户
- 已安装 1Password CLI (`op`)
- 以下之一：桌面应用集成、服务账号令牌（Service Account Token）（`OP_SERVICE_ACCOUNT_TOKEN`）、或 Connect 服务器
- 在 Hermes 终端调用期间（桌面应用流程），需要 `tmux` 以保持稳定的已认证会话

## 何时使用（When to Use）

- 安装或配置 1Password CLI
- 使用 `op signin` 登录
- 读取类似于 `op://Vault/Item/field` 的机密引用（secret references）
- 使用 `op inject` 将机密注入配置/模板中
- 通过 `op run` 使用机密环境变量运行命令

## 认证方法（Authentication Methods）

### 服务账号（Service Account）（推荐用于 Hermes）

在 `${HERMES_HOME:-~/.hermes}/.env` 中设置 `OP_SERVICE_ACCOUNT_TOKEN`（首次加载时技能会提示您设置）。无需桌面应用。支持 `op read`、`op inject`、`op run`。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"
op whoami  # 验证 — 应显示 Type: SERVICE_ACCOUNT
```

### 桌面应用集成（Desktop App Integration）（交互式）

1. 在 1Password 桌面应用中启用：设置 → 开发者 → 与 1Password CLI 集成
2. 确保应用已解锁
3. 运行 `op signin` 并批准生物识别提示

### Connect 服务器（自托管）

```bash
export OP_CONNECT_HOST="http://localhost:8080"
export OP_CONNECT_TOKEN="your-connect-token"
```

## 设置（Setup）

1. 安装 CLI：

```bash
# macOS
brew install 1password-cli

# Linux（官方包/安装文档）
# 请参阅 references/get-started.md 获取各发行版的具体链接。

# Windows (winget)
winget install AgileBits.1Password.CLI
```

2. 验证：

```bash
op --version
```

3. 选择上述一种认证方法并进行配置。

## Hermes 执行模式（桌面应用流程）

Hermes 终端命令默认是非交互式的，可能在多次调用之间丢失认证上下文。为了在桌面应用集成中可靠地使用 `op`，请在专用的 tmux 会话中运行登录和机密操作。

注意：使用 `OP_SERVICE_ACCOUNT_TOKEN` 时**无需**此操作——令牌会自动在终端调用之间保持有效。

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/hermes-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/hermes-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# 登录（在提示时于桌面应用中批准）
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "eval \"\$(op signin --account my.1password.com)\"" Enter

# 验证认证
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter

# 示例读取
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op read 'op://Private/Npmjs/one-time password?attribute=otp'" Enter

# 在需要时捕获输出
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# 清理
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## 常用操作（Common Operations）

### 读取一个机密（Read a secret）

```bash
op read "op://app-prod/db/password"
```

### 获取一次性密码（OTP）

```bash
op read "op://app-prod/npm/one-time password?attribute=otp"
```

### 注入到模板（Inject into template）

```bash
echo "db_password: {{ op://app-prod/db/password }}" | op inject
```

### 使用机密环境变量运行命令

```bash
export DB_PASSWORD="op://app-prod/db/password"
op run -- sh -c '[ -n "$DB_PASSWORD" ] && echo "DB_PASSWORD is set" || echo "DB_PASSWORD missing"'
```

## 防护措施（Guardrails）

- 除非用户明确请求值，否则绝不要将原始机密打印给用户。
- 优先使用 `op run` / `op inject`，而不是将机密写入文件。
- 如果命令失败并显示“account is not signed in”，请在同一个 tmux 会话中再次运行 `op signin`。
- 如果桌面应用集成不可用（无头/CI 环境），请使用服务账号令牌流程。

## CI / 无头环境说明

对于非交互式使用，请使用 `OP_SERVICE_ACCOUNT_TOKEN` 进行认证，避免交互式 `op signin`。服务账号需要 CLI v2.18.0+。

## 参考（References）

- `references/get-started.md`
- `references/cli-examples.md`
- https://developer.1password.com/docs/cli/
- https://developer.1password.com/docs/service-accounts/