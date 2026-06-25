---
title: Memory Providers
---

### Supermemory

具有语义化长期记忆（Semantic long-term memory）功能，支持画像召回（profile recall）、语义搜索、显式记忆工具，并通过 Supermemory 图 API 在会话结束时进行对话接入。

| | |
|---|---|
| **最佳适用场景** | 结合用户画像和会话级图构建的语义召回 |
| **依赖** | `pip install supermemory` + [API 密钥](https://supermemory.ai) |
| **数据存储** | Supermemory 云服务 |
| **成本** | Supermemory 定价 |

**工具：** `supermemory_store`（保存显式记忆），`supermemory_search`（语义相似性搜索），`supermemory_forget`（按 ID 或最佳匹配查询遗忘），`supermemory_profile`（持久画像 + 近期上下文）

**设置：**
```bash
hermes memory setup    # 选择 "supermemory"
# 或手动设置：
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置：** `$HERMES_HOME/supermemory.json`

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持 `{identity}` 模板，用于画像作用域的标签。 |
| `auto_recall` | `true` | 在轮次前自动注入相关记忆上下文 |
| `auto_capture` | `true` | 每次响应后存储清理后的用户-助手对话轮次 |
| `max_recall_results` | `10` | 格式化为上下文的最大召回结果数 |
| `profile_frequency` | `50` | 首次轮次和每 N 轮次包含画像事实 |
| `capture_mode` | `all` | 默认跳过微小或琐碎的轮次 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents` |
| `api_timeout` | `5.0` | 用于 SDK 和接入请求的超时时间 |

**环境变量：** `SUPERMEMORY_API_KEY`（必需），`SUPERMEMORY_CONTAINER_TAG`（覆盖配置）。

**主要特性：**
- 自动上下文隔离（context fencing）——从捕获的轮次中剥离被召回的记忆，防止递归记忆污染
- 全会话接入——在会话边界一次性发送整个对话
- 会话结束的对话接入（至 `/v4/conversations`），用于在 Supermemory 中构建更丰富的画像和图表
- 在首次轮次和可配置间隔注入画像事实
- **画像作用域容器**——在 `container_tag` 中使用 `{identity}`（例如 `hermes-{identity}` → `hermes-coder`），按 Hermes 画像隔离记忆
- **多容器模式**——启用 `enable_custom_container_tags` 并设置 `custom_containers` 列表，让代理可跨命名容器读取和写入。自动操作保持在主容器上。

<details>
<summary>多容器示例</summary>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "为编码上下文使用 project-alpha。"
}
```

</details>

**支持：** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

### Memori

使用 Memori 云的结构化长期记忆，具备后台已完成轮次捕获、工具感知的轮次上下文，以及用于事实、摘要、配额、注册和反馈的显式召回工具。

| | |
|---|---|
| **最佳适用场景** | 代理控制的召回，具有结构化项目和会话归属 |
| **依赖** | `pip install hermes-memori` + `hermes-memori install` + [Memori API 密钥](https://app.memorilabs.ai/signup) |
| **数据存储** | Memori 云服务 |
| **成本** | Memori 定价 |

**工具：** `memori_recall`（搜索长期记忆），`memori_recall_summary`（汇总上下文），`memori_quota`（使用量/配额），`memori_signup`（请求注册邮件），`memori_feedback`（发送集成反馈）

**设置：**
```bash
pip install hermes-memori
hermes-memori install
hermes config set memory.provider memori
hermes memory setup
```

---

--- body ---
## 提供商对比

| 提供商 | 存储 | 成本 | 工具数 | 依赖项 | 独特特性 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云服务 | 付费 | 5 | `honcho-ai` | 辩证用户建模 + 会话作用域上下文 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层级 + 分级加载 |
| **Mem0** | 云/自托管 | 免费/付费 | 5 | `mem0ai` | 服务端 LLM 提取 + 开源模式 |
| **Hindsight** | 云/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反思合成 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR 代数 + 信任评分 |
| **RetainDB** | 云服务 | 20美元/月 | 5 | `requests` | 增量压缩 |
| **ByteRover** | 本地/云 | 免费/付费 | 3 | `brv` CLI | 预压缩提取 |
| **Supermemory** | 云服务 | 付费 | 4 | `supermemory` | 上下文隔离 + 会话图接入 + 多容器 |
| **Memori** | 云服务 | 免费/付费 | 5 | `hermes-memori` | 工具感知记忆 + 结构化召回 |

## 画像隔离

每个提供商的数据根据[画像](/user-guide/profiles)被隔离：

- **本地存储提供商**（Holographic, ByteRover）使用每个画像不同的 `$HERMES_HOME/` 路径
- **配置文件提供商**（Honcho, Mem0, Hindsight, Supermemory）将配置存储在 `$HERMES_HOME/` 中，因此每个画像拥有自己的凭据
- **云提供商**（RetainDB）自动推导画像作用域的项目名称
- **环境变量提供商**（OpenViking）通过每个画像的 `.env` 文件进行配置

## 构建记忆提供商

请参阅[开发者指南：记忆提供商插件](/developer-guide/memory-provider-plugin)了解如何创建自己的插件。