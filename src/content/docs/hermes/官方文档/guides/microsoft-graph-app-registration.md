---
title: "注册 Microsoft Graph 应用程序"
description: "Azure 门户操作指南，用于创建支持 Teams 会议管道的应用注册"
---

# 注册 Microsoft Graph 应用程序

Teams 会议管道使用**仅应用**（守护程序）身份验证从 Microsoft Graph 读取会议转录、录制和相关工件——无需用户登录，每个会议无需交互式同意。这需要一个具有管理员同意的应用程序权限的 Azure AD 应用注册。

本指南逐步介绍：

1. 创建应用注册
2. 创建客户端机密
3. 授予管道所需的 Graph API 权限
4. 管理员同意这些权限
5. （可选）使用应用程序访问策略将应用限定于特定用户

你需要**租户管理员权限**（或由管理员代你授予同意）才能完成此操作。请收藏你收集的值——最后它们会被写入 `~/.hermes/.env`。

## 先决条件

- 一个具有 Teams Premium 或 Teams 许可证（可生成会议转录和录制）的 Microsoft 365 租户
- 对 Azure 门户 [entra.microsoft.com](https://entra.microsoft.com) 的管理员访问权限
- 一个可公开访问的 HTTPS 端点，用于接收 Graph 变更通知（稍后在 webhook 监听步骤中设置）

## 第 1 步：创建应用注册

1. 以租户管理员身份登录 [entra.microsoft.com](https://entra.microsoft.com)。
2. 导航至 **标识 → 应用程序 → 应用注册**。
3. 单击 **新注册**。
4. 填写：
   - **名称：** `Hermes Teams Meeting Pipeline`（或任何你能识别的名称）。
   - **支持的账户类型：** *仅限此组织目录中的账户（单租户）*。
   - **重定向 URI：** 留空——仅应用身份验证不需要。
5. 单击 **注册**。

你将进入应用的概览页面。复制两个值：

- **应用程序（客户端）ID** → `MSGRAPH_CLIENT_ID`
- **目录（租户）ID** → `MSGRAPH_TENANT_ID`

## 第 2 步：创建客户端机密

1. 在左侧导航中，打开 **证书和机密**。
2. 单击 **新建客户端机密**。
3. **说明：** `hermes-graph-secret`。**过期：** 选择一个符合轮换策略的值（通常为 6-24 个月）。
4. 单击 **添加**。
5. 立即复制 **值** 列——它只显示一次。该值就是 `MSGRAPH_CLIENT_SECRET`。

> **机密 ID** 列不是机密。你需要的是 **值** 列。

## 第 3 步：授予 Graph API 权限

管道使用最小可行的一组应用程序权限。只添加你需要的权限；每个权限都会扩大应用在租户范围内的读取能力。

1. 在左侧导航中，打开 **API 权限**。
2. 单击 **添加权限** → **Microsoft Graph** → **应用程序权限**。
3. 从下表添加与你希望管道执行的操作匹配的权限。
4. 添加后，单击 **为 `<your tenant>` 授予管理员同意**。每个权限的“状态”列应变为绿色复选标记。

### 转录优先摘要所需

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `OnlineMeetings.Read.All` | 读取 Teams 在线会议元数据（主题、参与者、加入 URL）。 |
| `OnlineMeetingTranscript.Read.All` | 读取 Teams 生成的会议转录。 |

### 录制回退所需（当转录不可用时）

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `OnlineMeetingRecording.Read.All` | 下载 Teams 会议录制内容，用于离线语音转文本处理。 |
| `CallRecords.Read.All` | 当只知道加入 URL 时，从通话记录中解析会议。 |

### 出站摘要投递所需（仅限 Graph 模式）

如果 `platforms.teams.extra.delivery_mode` 为 `graph`，则管道通过 Graph API 将摘要发布到 Teams 频道或聊天。如果使用 `incoming_webhook` 投递模式，则跳过这些权限。

| 权限 | 允许应用执行的操作 |
|------------|--------------------------|
| `ChannelMessage.Send` | 代表应用向 Teams 频道发布消息。 |
| `Chat.ReadWrite.All` | 向 1:1 和群聊发布消息（仅当将 `chat_id` 设置为投递目标时）。 |

### 不推荐

- `OnlineMeetings.ReadWrite.All` / `Chat.ReadWrite`（不带 `.All`）—— 比管道需要的更宽泛。
- 委派权限 —— 管道使用仅应用（客户端凭据）流程；没有用户登录，委派权限将无法工作。

## 第 4 步：（推荐）使用应用程序访问策略限定应用范围

默认情况下，像 `OnlineMeetings.Read.All` 这样的应用程序权限允许应用访问租户中的**每个**会议。对于合作伙伴演示和开发租户来说，这没问题；但对于生产环境，你几乎肯定要限制应用可以读取哪些用户的会议。

Microsoft 为此提供了 Teams 的**应用程序访问策略**。该策略仅通过 PowerShell 管理；门户中没有 UI。

在安装了 MicrosoftTeams 模块并已连接（`Connect-MicrosoftTeams`）的管理员 PowerShell 中运行：

```powershell
# 创建一条限定于 Hermes 应用的策略
New-CsApplicationAccessPolicy `
  -Identity "Hermes-Meeting-Pipeline-Policy" `
  -AppIds "<MSGRAPH_CLIENT_ID>" `
  -Description "将 Hermes 会议管道限制在允许列表中的用户"

# 将策略授予管道可以读取其会议的特定用户
Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "alice@example.com"

Grant-CsApplicationAccessPolicy `
  -PolicyName "Hermes-Meeting-Pipeline-Policy" `
  -Identity "bob@example.com"
```

策略传播最多可能需要 30 分钟。验证方法：

```powershell
Test-CsApplicationAccessPolicy -Identity "alice@example.com" -AppId "<MSGRAPH_CLIENT_ID>"
```

如果没有该策略，**任何**用户的会议都是可读的——这是权限在技术上的授予范围。请不要在生产租户上跳过此步骤。

## 第 5 步：将凭据写入环境文件

将你收集的三个值放入 `~/.hermes/.env`：

```bash
MSGRAPH_TENANT_ID=<directory-tenant-id>
MSGRAPH_CLIENT_ID=<application-client-id>
MSGRAPH_CLIENT_SECRET=<client-secret-value>
```

设置文件权限，使得只有你可以读取机密：

```bash
chmod 600 ~/.hermes/.env
```

## 第 6 步：验证令牌流程

Hermes 附带一个 Graph 身份验证冒烟测试。从你的 Hermes 安装目录运行：

```python
python -c "
import asyncio
from tools.microsoft_graph_auth import MicrosoftGraphTokenProvider
provider = MicrosoftGraphTokenProvider.from_env()
token = asyncio.run(provider.get_access_token())
print('Token acquired, length:', len(token))
print(provider.inspect_token_health())
"
```

成功运行会打印一个长令牌字符串和一个健康字典，显示 `cached: True` 和 `expires_in_seconds` 值接近 3600。失败会产生一个 `MicrosoftGraphTokenError`，并附带 Azure 错误代码——最常见的如下：

| Azure 错误 | 含义 | 修复方法 |
|-------------|---------|-----|
| `AADSTS7000215: Invalid client secret` | 机密值不匹配或已过期。 | 在第 2 步中生成一个新机密；更新 `.env`。 |
| `AADSTS700016: Application not found` | `MSGRAPH_CLIENT_ID` 错误或租户错误。 | 再次核对第 1 步中的值是否来自同一个应用。 |
| `AADSTS90002: Tenant not found` | `MSGRAPH_TENANT_ID` 有拼写错误。 | 从应用概览页面重新复制目录（租户）ID。 |
| 调用时出现 `insufficient_claims`（非令牌获取时） | 令牌已获取，但 Graph 返回 401/403。 | 你跳过了第 3 步的管理员同意，或者添加了权限但未重新同意。重新访问 API 权限并再次单击 **授予管理员同意**。 |

## 轮换客户端机密

Azure 客户端机密有硬性到期时间。在到期前，请执行以下操作：

1. 在第 2 步中创建第二个客户端机密，但不要删除第一个。
2. 使用新值更新 `~/.hermes/.env` 中的 `MSGRAPH_CLIENT_SECRET`。
3. 重启网关以使新机密生效：`hermes gateway restart`。
4. 使用上面的冒烟测试进行验证。
5. 从 Azure 门户中删除旧机密。

## 后续步骤

凭据验证通过后，继续执行：

- **Webhook 监听设置** —— 启动接收 Graph 变更通知的 `msgraph_webhook` 网关平台。
- **管道配置** —— 配置 Teams 会议管道运行时和操作员 CLI。
- **出站投递** —— 将摘要回送到 Teams 频道或聊天。

这些页面将与添加相应运行时的 PR 一起发布。本凭据设置是一个独立的先决条件，可以提前完成。