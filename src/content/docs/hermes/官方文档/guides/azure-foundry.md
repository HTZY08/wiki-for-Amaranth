---
title: Azure Foundry
---

sidebar_position: 15
title: "微软 Foundry"
description: "使用 Hermes Agent 与 Microsoft Foundry — OpenAI 风格和 Anthropic 风格的端点，自动检测传输方式和已部署的模型"
---

--- body ---
# Microsoft Foundry

Hermes Agent 的 `azure-foundry` 提供商支持 Microsoft Foundry（原 Azure AI Foundry）和 Azure OpenAI。单个 Foundry 资源可以托管两种不同交互格式的模型：

- **OpenAI 风格** — 在类似 `https://<resource>.openai.azure.com/openai/v1` 的端点上使用 `POST /v1/chat/completions`。适用于 GPT-4.x、GPT-5.x、Llama、Mistral 以及大多数开源权重模型。
- **Anthropic 风格** — 在类似 `https://<resource>.services.ai.azure.com/anthropic` 的端点上使用 `POST /v1/messages`。当 Microsoft Foundry 通过 Anthropic Messages API 格式提供 Claude 模型时使用。

设置向导会探测你的端点，自动检测它使用哪种传输方式、哪些部署可用，以及每个模型的上下文长度。

## 先决条件

- 一个 Microsoft Foundry 或 Azure OpenAI 资源，至少包含一个部署
- 该部署的端点 URL
- **或者** 一个 API 密钥（来自 Azure Portal 中的 "Keys and Endpoint"），**或者** 如果你计划使用 Microsoft Entra ID（微软推荐的无密钥路径），则需要在 Foundry 资源上具有 **Azure AI User** RBAC 角色。在微软重命名推广期间，某些租户可能将该角色显示为 **Foundry User**。

## 快速开始

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入你的端点 URL
# → 选择认证方式：
#     1. API 密钥
#     2. Microsoft Entra ID（托管标识 / 工作负载标识 / az login）
# → (Entra) Hermes 探测 DefaultAzureCredential；成功时不再询问密钥
# → (API 密钥) 输入你的 API 密钥
# → Hermes 探测端点并自动检测传输方式 + 模型
# → 从列表中选择一个模型（或手动输入部署名称）
```

该向导将：

1. **嗅探 URL 路径** — 以 `/anthropic` 结尾的 URL 被识别为 Microsoft Foundry Claude 路由。
2. **探测 `GET <base>/models`** — 如果端点返回 OpenAI 风格的模型列表，Hermes 切换为 `chat_completions` 并用返回的部署 ID 预填选择器。
3. **探测 Anthropic Messages 格式** — 针对未暴露 `/models` 但接受 Anthropic Messages 格式的端点的回退。
4. **回退到手动输入** — 拒绝所有探测的私有/受限端点仍可正常工作；你手动选择 API 模式并输入部署名称。

所选模型的上下文长度通过 Hermes 的标准元数据链（`models.dev`、提供商元数据和硬编码的系列回退）解析，并存储在 `config.yaml` 中，以便模型能够正确调整其上下文窗口大小。

## Microsoft Entra ID（无密钥，基于 RBAC）— 推荐

微软建议对生产环境中的 Foundry 工作负载使用[基于 Microsoft Entra ID 的无密钥认证](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id)。Hermes 支持 **两种** API 接口的 Entra ID：

- **OpenAI 风格**（`api_mode: chat_completions` / `codex_responses`）— GPT-4/5、Llama、Mistral、DeepSeek 等。
- **Anthropic 风格**（`api_mode: anthropic_messages`）— Microsoft Foundry 上的 Claude 模型。

Foundry 的 RBAC 是按资源划分的（`Azure AI User` 授权两种接口；某些租户可能显示 `Foundry User`），微软为两者记录了相同的推理范围（`https://ai.azure.com/.default`）。在底层：

- OpenAI 风格使用 OpenAI Python SDK 的原生可调用 `api_key=` 契约——SDK 自动为每个请求生成一个全新的 JWT。
- Anthropic 风格使用一个带有 `agent.azure_identity_adapter.build_bearer_http_client` 安装的请求事件钩子的 `httpx.Client`，因为 Anthropic SDK 本身不接受可调用的 `auth_token`。该钩子会为每个出站请求重写 `Authorization: Bearer <fresh-jwt>`。相同的 Microsoft RBAC，相同的 Foundry 范围——唯一区别在于 SDK 契约。

### 为什么使用 Entra ID？

- 无需轮换或吊销长期有效的 API 密钥。
- 基于 RBAC 的访问——在 Foundry 资源上授予或移除 `Azure AI User` 即可，无需重写配置。
- 访问和审计日志按分配者区分，而不是所有调用者共享一个静态密钥。
- 对于 Azure 虚拟机、AKS Pod、App Service、Functions、Container Apps 和 Foundry Agent Service，可通过托管标识使用单一的认证接口。
- 用于 CI/CD 流水线的工作负载标识和服务主体流程。

### 一次性设置（Azure 端）

1. 在 Azure Portal 中，打开你的 Foundry 资源 → **访问控制 (IAM)** → **添加 → 添加角色分配**。
2. 选择 **Azure AI User** 角色（如果你的租户使用了重命名后的角色，则选择 **Foundry User**）。
3. 将其分配给：
   - **你的用户账户** 用于本地开发（配合 `az login`）。
   - **托管标识或工作负载标识** 用于 Azure 托管的计算资源（生产环境推荐）。
   - **当 Hermes 在托管代理内部运行时，分配给 Foundry Agent Service 托管代理的代理标识**。
   - **用于 CI/CD 流水线的服务主体**（当工作负载标识不可用时）。
4. 等待约 5 分钟以便角色生效。

Azure CLI 等效命令：

```bash
az role assignment create \
  --assignee <principal-or-agent-identity-client-id> \
  --role "Azure AI User" \
  --scope <foundry-resource-id>
```

### 一次性设置（Hermes 端）

```bash
hermes model
# → 选择 "Azure Foundry"
# → 输入你的端点 URL
# → 认证：2 (Microsoft Entra ID)
# → (可选) 用户分配的托管标识客户端 ID
# → (可选) Azure 租户 ID
# → Hermes 探测 DefaultAzureCredential() 并报告哪个内部凭据成功
#    例如 AzureCliCredential、ManagedIdentityCredential
```

该向导会运行一次有限的预检探测（10 秒超时）。若失败，会提供“仍然保存，稍后验证”的选项——适用于在尚未具备凭据但运行时将会具备的机器上配置（例如为托管标识部署准备配置）。

`azure-identity` 会在首次使用时通过 Hermes 的延迟安装路径自动安装。若要预安装：

```bash
pip install azure-identity
```

### 写入 `config.yaml` 的配置

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  auth_mode: entra_id
  default: gpt-4o
  context_length: 128000
  entra:
    scope: https://ai.azure.com/.default        # 仅在覆盖默认值时使用
```

Hermes 在 `config.yaml` 中只管理一个与 Entra 相关的参数：

- **`scope`** — OAuth 资源范围。默认为微软记录的推理范围（`https://ai.azure.com/.default`）。仅当你的资源针对非标准受众进行配置时才需要覆盖。

其他所有设置（租户、服务主体密钥、联合令牌文件、主权云颁发机构、代理首选项）均由 `azure-identity` 直接从标准的 `AZURE_*` 环境变量读取——请参阅下面的[凭据解析顺序](#credential-resolution-order)。将这些设置在 `~/.hermes/.env` 或你的部署环境中，完全按照微软 SDK 参考文档的说明操作。

Entra 模式下，`~/.hermes/.env` 中不会出现任何机密信息——`azure-identity` 会在进程内（如果可用，还会在你的操作系统钥匙串 / `~/.IdentityService` 中）缓存令牌。

### 凭据解析顺序

`azure-identity` 的 `DefaultAzureCredential` 在每个令牌请求时按以下链顺序执行，停在第一个成功返回令牌的凭据上：

1. **环境凭据** — `AZURE_TENANT_ID` + `AZURE_CLIENT_ID` + `AZURE_CLIENT_SECRET`（或 `AZURE_CLIENT_CERTIFICATE_PATH` / `AZURE_FEDERATED_TOKEN_FILE`）。
2. **工作负载标识** — `AZURE_FEDERATED_TOKEN_FILE`（AKS 联合令牌 / OIDC）。
3. **托管标识** — 虚拟机使用 IMDS 端点（`169.254.169.254`）；App Service / Functions / Container Apps 使用 `IDENTITY_ENDPOINT`。Foundry Agent Service 托管代理使用托管代理的代理标识。
4. **Visual Studio Code** — Azure 账户扩展。
5. **Azure CLI** — `az login` 会话。
6. **Azure Developer CLI** — `azd auth login`。
7. **Azure PowerShell** — `Connect-AzAccount`。
8. **代理**（仅限 Windows / WSL）— Web Account Manager。

交互式浏览器凭据默认被排除在无人值守的 Hermes 运行之外；请改用 Azure CLI、Azure Developer CLI、托管标识、工作负载标识或服务主体凭据。

### 部署模式

**本地开发：**
```bash
az login
hermes model   # 选择 Azure Foundry → Entra ID
hermes         # 使用你的 az login 令牌
```

**Azure 虚拟机 / Functions / App Service / Container Apps（系统分配的托管标识）：**
1. 在计算资源上启用系统分配的标识。
2. 在 Foundry 资源上为标识授予 `Azure AI User`（或 `Foundry User`）。
3. 在 config.yaml 中设置 `model.auth_mode: entra_id`——无需环境变量。

**Azure 虚拟机 / Functions / App Service / Container Apps（用户分配的托管标识）：**
- 设置 `AZURE_CLIENT_ID` 为用户分配的托管标识的客户端 ID，以便 `DefaultAzureCredential` 选择正确的标识。

**Foundry Agent Service 托管代理：**
- 创建托管代理，并在 Foundry 资源上为该代理的标识授予 `Azure AI User`（或 `Foundry User`）。Hermes 在托管代理内部使用 `ManagedIdentityCredential`；角色分配属于代理标识，而不仅仅是父项目或你的用户。

**AKS 工作负载标识（替代 AAD Pod Identity）：**
- 为 Pod 的服务账户添加工作负载标识客户端 ID 的注解。
- Pod 的联合令牌文件通过 `AZURE_FEDERATED_TOKEN_FILE` 自动检测。
- `model.auth_mode: entra_id` 无需额外配置更改即可工作。

**CI 中的服务主体：**
- 在运行器环境中设置 `AZURE_TENANT_ID`、`AZURE_CLIENT_ID`、`AZURE_CLIENT_SECRET`。

#### 主权云（政府、中国）

导出 `AZURE_AUTHORITY_HOST`（例如 `https://login.microsoftonline.us` 用于 Azure Government，`https://login.partner.microsoftonline.cn` 用于 Azure China）。`azure-identity` 会直接读取它。

### 健康检查

当 `model.auth_mode: entra_id` 时，`hermes doctor` 会对 `DefaultAzureCredential` 进行一次 10 秒探测，报告哪个内部凭据成功（存在的环境变量、可访问的托管标识端点等）。

`hermes auth` 显示结构化的状态块：

```
azure-foundry (Microsoft Entra ID):
  Endpoint: https://my-resource.openai.azure.com/openai/v1
  Scope: https://ai.azure.com/.default
  Status: configured; live token probe is skipped here
```

### 限制

- **Anthropic 风格端点使用 httpx 事件钩子。** Anthropic Python SDK 本身不接受可调用的 `auth_token`（≤ 0.86.0）。Hermes 在自定义的 `httpx.Client` 上安装一个请求事件钩子，该钩子为每个出站请求生成一个新的 JWT 并重写 `Authorization: Bearer <jwt>`。这在功能上等同于 OpenAI SDK 的原生 `Callable[[], str]` 契约，但增加了一个间接层。如果未来版本的 Anthropic SDK 添加了一流可调用认证支持，Hermes 将透明地切换到它。
- **批处理作业和 `multiprocessing.Pool`。** Entra 令牌提供程序是一个闭包，无法跨进程边界进行序列化。`batch_runner.py` 会自动从工作器配置中删除该可调用对象，并让每个工作器进程从 `config.yaml` 重建自己的提供程序——无需用户操作，但每个工作器会在启动时进行一次链遍历。
- **不在 `auth.json` 中持久化载体 JWT。** Hermes 不会复制 `azure-identity` 的内部令牌缓存；冷启动时会在首次推理时遍历凭据链。

## 配置（写入 `config.yaml`）

运行向导后，你将看到类似以下内容：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions         # 或 "anthropic_messages"
  default: gpt-5.4-mini              # 你的部署/模型名称
  context_length: 400000             # 自动检测
```

以及在 `~/.hermes/.env` 中：

```
AZURE_FOUNDRY_API_KEY=<your-azure-key>
```

## OpenAI 风格端点（GPT、Llama 等）

Azure OpenAI 的 v1 GA 端点接受标准的 `openai` Python 客户端，只需少量更改：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.openai.azure.com/openai/v1
  api_mode: chat_completions
  default: gpt-5.4
```

重要行为：

- **GPT-5.x、codex 和 o 系列自动路由到 Responses API。** Microsoft Foundry 将 GPT-5 / codex / o1 / o3 / o4 模型部署为仅支持 Responses API——对这些模型调用 `/chat/completions` 会返回 `400 "The requested operation is unsupported."`。Hermes 会根据名称检测这些模型系列，并透明地将 `api_mode` 升级为 `codex_responses`，即使 `config.yaml` 中仍写着 `api_mode: chat_completions`。GPT-4、GPT-4o、Llama、Mistral 和其他部署仍使用 `/chat/completions`。
- **自动使用 `max_completion_tokens`。** Azure OpenAI（与直接 OpenAI 一样）对于 gpt-4o、o 系列和 gpt-5.x 模型要求使用 `max_completion_tokens`。Hermes 会根据端点发送正确的参数。
- **需要 `api-version` 的 v1 前端点。** 如果你有一个类似 `https://<resource>.openai.azure.com/openai?api-version=2025-04-01-preview` 的旧版基础 URL，Hermes 会提取查询字符串并通过 `default_query` 在每次请求中转发（否则 OpenAI SDK 在拼接路径时会丢弃它）。

## Anthropic 风格端点（通过 Microsoft Foundry 的 Claude）

对于 Claude 部署，请使用 Anthropic 风格路由：

```yaml
model:
  provider: azure-foundry
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_mode: anthropic_messages
  default: claude-sonnet-4-6
```

重要行为：

- **从基础 URL 中移除 `/v1`。** Anthropic SDK 会向每个请求 URL 追加 `/v1/messages`——Hermes 在将 URL 交给 SDK 之前会移除任何尾部的 `/v1`，以避免出现双 `/v1` 路径。
- **通过 `default_query` 发送 `api-version`，而不是追加到 URL 中。** Azure Anthropic 要求一个 `api-version` 查询字符串。将其嵌入基础 URL 会产生如 `/anthropic?api-version=.../v1/messages` 的错误路径并返回 404。Hermes 转而通过 Anthropic SDK 的 `default_query` 传递 `api-version=2025-04-15`。
- **使用 Bearer 认证而不是 `x-api-key`。** Azure 的 Anthropic 兼容路由要求使用 `Authorization: Bearer <key>`，而不是 Anthropic 原生的 `x-api-key` 头部。Hermes 检测到基础 URL 中包含 `azure.com`，并通过 SDK 的 `auth_token` 字段路由 API 密钥，以便正确的头部到达上游。
- **保留 1M 上下文窗口测试头部。** Azure 仍然将 1M 令牌的 Claude 上下文（Opus 4.6/4.7、Sonnet 4.6）限制在 `anthropic-beta: context-1m-2025-08-07` 头部之后。Hermes 在 Azure 路径上保留该测试头部（在原生 Anthropic OAuth 请求中会去掉，因为某些订阅会拒绝它，但 Azure 要求它）。
- **禁用 OAuth 令牌刷新。** Azure 部署使用静态 API 密钥。应用于 Anthropic Console 的 `~/.claude/.credentials.json` OAuth 令牌刷新循环会被显式跳过，以防止 Claude Code OAuth 令牌在会话中间覆盖你的 Azure 密钥。

## 替代方案：`provider: anthropic` + Azure 基础 URL

如果你已经配置了 `provider: anthropic`，并且只想将其指向 Microsoft Foundry 以用于 Claude，你可以完全跳过 `azure-foundry` 提供商：

```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  key_env: AZURE_ANTHROPIC_KEY
  default: claude-sonnet-4-6
```

并在 `~/.hermes/.env` 中设置 `AZURE_ANTHROPIC_KEY`。Hermes 检测到基础 URL 中包含 `azure.com`，并绕过 Claude Code OAuth 令牌链，以便直接使用 Azure 密钥进行 `x-api-key` 认证。

`key_env` 是规范的蛇形命名 (snake_case) 字段名；`api_key_env`（以及驼峰命名 `keyEnv` / `apiKeyEnv`）作为别名也被接受。如果同时设置了 `key_env` 和 `AZURE_ANTHROPIC_KEY`/`ANTHROPIC_API_KEY`，则 `key_env` 命名的环境变量优先。

## 模型发现

Azure **不** 提供纯 API 密钥端点来列出你的 *已部署* 模型部署。枚举部署需要 Azure Resource Manager 认证（`az cognitiveservices account deployment list`）以及 Azure AD 主体，而非推理 API 密钥。

Hermes 能够做的事情：

- Azure OpenAI v1 端点（`<resource>.openai.azure.com/openai/v1`）暴露 `GET /models`，其中包含资源的 **可用** 模型目录。Hermes 使用此列表来预填模型选择器。
- Microsoft Foundry `/anthropic` 路由：通过 URL 路径检测，模型名称手动输入。
- 私有/防火墙端点：手动输入，并显示友好的“无法探测”消息。

你可以直接输入任意部署名称——Hermes 不会针对返回的列表进行验证。

## 环境变量

| 变量 | 用途 |
|----------|---------|
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI 的主 API 密钥（api_key 模式） |
| `AZURE_FOUNDRY_BASE_URL` | 端点 URL（通过 `hermes model` 设置；环境变量作为回退） |
| `AZURE_ANTHROPIC_KEY` | 由 `provider: anthropic` + Azure 基础 URL 使用（`ANTHROPIC_API_KEY` 的替代） |
| `AZURE_TENANT_ID` | 服务主体流程的 Entra ID 租户 |
| `AZURE_CLIENT_ID` | Entra ID 客户端 ID（服务主体、工作负载标识或用户分配的托管标识） |
| `AZURE_CLIENT_SECRET` | 服务主体密钥 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书（密钥的替代） |
| `AZURE_FEDERATED_TOKEN_FILE` | 工作负载标识联合令牌路径（AKS） |
| `AZURE_AUTHORITY_HOST` | 主权云颁发机构主机覆盖 |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | App Service、Functions 和 Container Apps 的托管标识端点；虚拟机通常使用 IMDS |

Azure SDK 直接读取 `AZURE_*` 环境变量。Hermes 从不检查它们，除非在 `hermes doctor` 输出中报告哪些来源存在。

## 故障排除

**在 gpt-5.x 部署上出现 401 Unauthorized。**
Azure 在 `/chat/completions` 上提供 gpt-5.x，而不是 `/responses`。当 URL 包含 `openai.azure.com` 时，Hermes 会自动处理此问题，但如果你看到带有 `Invalid API key` 正文的 401，请检查 `config.yaml` 中的 `api_mode` 是否为 `chat_completions`。

**在 `/v1/messages?api-version=.../v1/messages` 上出现 404。**
这是修复前 Azure Anthropic 设置中的错误 URL 问题。升级 Hermes——`api-version` 参数现在通过 `default_query` 传递，而不是嵌入基础 URL，因此 SDK 无法在 URL 拼接期间损坏它。

**向导显示“自动检测不完整”。**
端点拒绝了 `/models` 探测和 Anthropic Messages 探测。对于防火墙后面或具有 IP 允许列表的私有端点，这是正常现象。回退到手动 API 模式选择并输入你的部署名称——一切仍可正常工作，只是 Hermes 无法预填选择器。

**选择了错误的传输方式。**
再次运行 `hermes model`，向导将重新探测。如果探测仍然选择错误的模式，你可以直接编辑 `config.yaml`：

```yaml
model:
  provider: azure-foundry
  api_mode: anthropic_messages   # 或 chat_completions
```

**Entra ID：切换到 `auth_mode: entra_id` 后出现“credential chain exhausted”或 401 Unauthorized。**
- 运行 `az login` 以刷新你的开发人员会话（缓存的令牌可能已过期）。
- 验证 `Azure AI User`（或 `Foundry User`）角色分配是否已生效：`az role assignment list --assignee <user-or-identity-id>` 应能在你的 Foundry 资源上列出它。角色传播可能需要最多 5 分钟。
- 对于用户分配的托管标识，请仔细检查 `AZURE_CLIENT_ID` 是否与附加到计算资源的标识匹配。
- 运行 `hermes doctor`——Azure Entra 探测会报告令牌获取是否成功，并包含修复提示。

**Entra ID：向导预检挂起或超时。**
10 秒预检是软检查。选择“仍然保存并稍后验证”，在部署到目标环境后运行 `hermes doctor`。常见原因包括令牌服务不可达或本地登录状态过期——在 CI 中优先使用工作负载标识，使用服务主体时设置 `AZURE_TENANT_ID`+`AZURE_CLIENT_ID`+`AZURE_CLIENT_SECRET`，或在本地开发时运行 `az login`。

**在使用 Entra ID 的 Anthropic 风格端点上出现 401。**
验证是否在 Foundry 资源上分配了相同的 `Azure AI User`（或 `Foundry User`）角色（该角色同时覆盖 `/openai/v1` 和 `/anthropic` 路径）。如果向导期间 OpenAI 风格探测正常工作但 `claude-*` 请求在运行时失败，最常见的原因是早期向导运行遗留的过时 `model.entra.scope`——从 `config.yaml` 中删除 `entra.scope` 行，以便运行时回退到默认范围 `https://ai.azure.com/.default`。

## 相关

- [环境变量](/reference/environment-variables)
- [配置](/user-guide/configuration)
- [AWS Bedrock](/guides/aws-bedrock) — 另一个主要的云提供商集成
- [Microsoft：为 Foundry 配置 Entra ID](https://learn.microsoft.com/azure/ai-foundry/foundry-models/how-to/configure-entra-id) — 无密钥路径的上级文档