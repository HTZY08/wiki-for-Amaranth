---
title: Bitwarden 集成
description: Hermes Agent 官方文档汉化版
---

# Bitwarden Secrets Manager

在进程启动时从 [Bitwarden Secrets Manager](https://bitwarden.com/products/secrets-manager/) 拉取 API 密钥，而不是将它们以明文形式存储在 `~/.hermes/.env` 中。一个引导密钥（机器账户访问令牌）取代了 N 个提供者密钥，轮换凭据只需在 Bitwarden Web 应用中更改一次。

## 工作原理

1.  你在 Bitwarden Secrets Manager 中创建一个 **机器账户（machine account）**，授予其对某个项目的读取权限，并生成一个 **访问令牌（access token）**。
2.  Hermes 将该单一令牌存储在 `~/.hermes/.env` 中，作为 `BWS_ACCESS_TOKEN`。
3.  每次 `hermes`（或网关、cron 作业）启动时，在加载 `~/.hermes/.env` 后，Hermes 会调用 `bws secret list <project_id>`，并将返回的密钥设置到 `os.environ` 中。
4.  默认情况下，Hermes **覆盖（overrides）** 环境中已有的值，因此 Bitwarden 是权威来源——在 Web 应用中轮换一个密钥，所有 Hermes 进程会在下次启动时获取到。如果你希望 `.env` 优先，可以在配置中将 `override_existing: false`。

`bws` 二进制文件在首次使用时会被自动下载到 `~/.hermes/bin/` — 无需 `apt`、`brew` 或 `sudo`。

## 为什么使用机器账户（以及为什么没有 2FA 提示）

Bitwarden Secrets Manager 专为非交互式工作负载设计：机器账户不能受 2FA 限制，因为流程中没有人参与。访问令牌就是凭据。任何拥有它的人都可以读取机器账户有权访问的所有秘密，因此请将其视为高价值的承载令牌——存储在 `.env` 中（而不是 `config.yaml` 中），如果泄露，请在 Bitwarden Web 应用中撤消并重新生成。

你需要在 Web 应用中设置机器账户（此时会应用你正常的 2FA）。之后令牌就是自主的。

## 设置

### 1. 创建机器账户和访问令牌

在 [Bitwarden Web 应用](https://vault.bitwarden.com)（或欧洲账户使用 [vault.bitwarden.eu](https://vault.bitwarden.eu)）：

1.  从产品切换器切换到 **Secrets Manager**。
2.  创建或选择一个 **项目（Project）**（例如 "Hermes keys"）。
3.  将你的提供者密钥添加为秘密。秘密的 **名称（Name）** 将成为环境变量名——使用 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等。
4.  **机器账户（Machine accounts）→ 新建机器账户 → My Hermes machine** → **项目（Projects）** 选项卡 → 授予对你项目的读取权限。
5.  **访问令牌（Access tokens）** 选项卡 → **创建访问令牌 → 永不（Never）** 过期（或选择一个日期）→ 复制令牌（以 `0.` 开头）。Bitwarden 无法再次检索它——请保留副本。

Secrets Manager 包含在 Bitwarden 免费套餐中，有一定限制；无需付费计划即可尝试。

### 2. 运行向导

```bash
hermes secrets bitwarden setup
```

它将：

1.  将 `bws v2.0.0` 下载并验证到 `~/.hermes/bin/bws` 中。
2.  提示你输入访问令牌（输入隐藏）。存储在 `~/.hermes/.env` 中作为 `BWS_ACCESS_TOKEN`。
3.  询问你的机器账户属于哪个 Bitwarden 区域——**US Cloud**、**EU Cloud**，或 **自托管（self-hosted）/自定义 URL**。存储在 `config.yaml` 中作为 `secrets.bitwarden.server_url`，并作为 `BWS_SERVER_URL` 传递给 `bws`。
4.  列出机器账户可以看到的项目；选择一个。存储在 `config.yaml` 中作为 `secrets.bitwarden.project_id`。
5.  测试获取项目的秘密，并显示哪些环境变量将被解析。
6.  将 `secrets.bitwarden.enabled` 设置为 `true`。

也支持通过标志进行非交互式设置：

```bash
hermes secrets bitwarden setup \
  --access-token "$BWS_ACCESS_TOKEN" \
  --server-url https://vault.bitwarden.eu \
  --project-id <project-uuid>
```

### 3. 确认

```bash
hermes secrets bitwarden status
```

从现在开始，每次 `hermes` 调用都会在启动时拉取最新秘密。你将在进程首次应用秘密时在 stderr 中看到一行摘要。

## CLI

| 命令 | 功能 |
|---|---|
| `hermes secrets bitwarden setup` | 交互式向导（安装二进制文件、提示输入令牌、选择项目、测试获取） |
| `hermes secrets bitwarden status` | 显示配置 + 二进制版本 + 令牌是否存在 |
| `hermes secrets bitwarden sync` | 试运行：立即拉取秘密并显示将应用哪些 |
| `hermes secrets bitwarden sync --apply` | 拉取并导出到当前 shell 的环境中 |
| `hermes secrets bitwarden install` | 仅下载固定的 `bws` 二进制文件（无需认证） |
| `hermes secrets bitwarden disable` | 将 `enabled` 设置为 `false`；保留令牌 + 项目 ID |

## 配置

`~/.hermes/config.yaml` 中的默认值：

```yaml
secrets:
  bitwarden:
    enabled: false
    access_token_env: BWS_ACCESS_TOKEN
    project_id: ""
    server_url: ""
    cache_ttl_seconds: 300
    override_existing: true
    auto_install: true
```

| 键 | 默认值 | 作用 |
|---|---|---|
| `enabled` | `false` | 总开关。为 false 时，绝不联系 Bitwarden。 |
| `access_token_env` | `BWS_ACCESS_TOKEN` | 存放引导令牌的环境变量名。如果你已经将 `BWS_ACCESS_TOKEN` 用于其他目的，可更改此项。 |
| `project_id` | `""` | 要同步的项目 UUID。 |
| `server_url` | `""` | Bitwarden 区域或自托管端点。为空时使用 `bws` 默认值（US Cloud，`https://vault.bitwarden.com`）。设为 `https://vault.bitwarden.eu` 用于 EU Cloud，或自托管 URL。作为 `BWS_SERVER_URL` 传递给 `bws` 子进程。 |
| `cache_ttl_seconds` | `300` | 进程内获取结果被重复使用的时间。设为 `0` 禁用缓存。缓存是进程级的；新的 `hermes` 调用会重新开始。 |
| `override_existing` | `true` | 为 true 时，Bitwarden 的值会覆盖环境中已有的内容（因此 Web 应用中的轮换实际生效）。设为 `false` 如果你希望 `.env` / shell 导出在本地优先。 |
| `auto_install` | `true` | 为 true 时，首次使用会自动将 `bws` 下载到 `~/.hermes/bin/`。 |

## 故障模式

Bitwarden 从不会阻止 Hermes 启动。如果出现问题，你会在 stderr 中看到一行警告，Hermes 会继续使用 `.env` 中已有的凭据：

| 症状 | 原因 | 解决方法 |
|---|---|---|
| `BWS_ACCESS_TOKEN is not set` | 已在配置中启用，但令牌已从 `.env` 中清除 | 重新运行 `hermes secrets bitwarden setup` |
| `bws exited 1: invalid access token` | 令牌已被撤销或错误 | 生成新令牌，重新运行 setup |
| `[400 Bad Request] {"error":"invalid_client"}` | 令牌属于与 `bws` 调用的 Bitwarden 区域不同的区域（例如 EU 令牌访问美国身份端点） | 重新运行 setup 并选择正确区域，或将 `secrets.bitwarden.server_url` 设为 `https://vault.bitwarden.eu`（或你的自托管 URL） |
| `bws timed out` | 网络被阻断或 Bitwarden API 缓慢 | 检查与 `api.bitwarden.com`（或你的 `server_url`）的连接 |
| `bws binary not available` | `auto_install: false` 且 `bws` 不在 PATH 中 | 从 [github.com/bitwarden/sdk-sm/releases](https://github.com/bitwarden/sdk-sm/releases) 手动安装，或将 `auto_install` 重新设为 true |
| `Checksum mismatch` | 下载损坏或被篡改 | 重新运行，会重试；如果持续出现，请提交 issue |

## 安全说明

-   引导令牌（`BWS_ACCESS_TOKEN`）本身是敏感的——任何拥有它的人都可以读取机器账户有权访问的所有秘密。请像对待其他 API 密钥一样对待它。
-   Hermes 会拒绝让 Bitwarden 覆盖引导令牌本身，即使设置了 `override_existing: true`。如果你在项目中存储了 `BWS_ACCESS_TOKEN` 作为秘密，它会在应用时被静默跳过。
-   `bws` 二进制文件下载会根据同一 GitHub 发布的 SHA-256 校验和进行验证。不匹配将中止安装。
-   固定版本（撰写本文时为 `bws v2.0.0`）通过对此仓库的 PR 进行更新——Hermes 不会自动将 `bws` 升级到“最新”，因为上游发布形式可能会发生变化。

## 何时不使用此功能

-   **单机个人设置**，其中 `~/.hermes/.env` 已足够。你只是在用一种凭据交换另一种凭据，并在启动时增加网络依赖。
-   **无法访问 `api.bitwarden.com` 的气隙环境（air-gapped environments）**。
-   **CI/CD**，其中现有的秘密注入机制（GitHub Actions secrets、Vault 等）已经设置——选择一条路径，不要两条都走。

此功能适用的情况是：多机集群、共享开发机、网关 VPS，或任何希望在多个 Hermes 安装之间实现集中轮换和撤销的设置。