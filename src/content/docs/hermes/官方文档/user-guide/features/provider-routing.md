---
title: Provider Routing
---

title: 提供商路由
description: 配置 OpenRouter 提供商偏好，以优化成本、速度或质量。
sidebar_label: Provider Routing
sidebar_position: 7
---

--- body ---
# 提供商路由 (Provider Routing)

当使用 [OpenRouter](https://openrouter.ai) 作为您的 LLM 提供商时，Hermes Agent 支持 **提供商路由** —— 细粒度控制哪个底层 AI 提供商处理您的请求以及它们的优先级顺序。

OpenRouter 将请求路由到多个提供商（例如 Anthropic、Google、AWS Bedrock、Together AI）。提供商路由让您能够优化成本、速度、质量，或强制执行特定的提供商要求。

:::tip
通过 [Nous Portal](/integrations/nous-portal) 路由的流量仍然遵循每模型路由和优先级配置——并且 Portal 订阅者在使用按 token 计费的提供商时可享受 10% 折扣。
:::

## 配置

在您的 `~/.hermes/config.yaml` 文件中添加 `provider_routing` 部分：

```yaml
provider_routing:
  sort: "price"
  only: []
  ignore: []
  order: []
  require_parameters: false
  data_collection: null
```

:::info
提供商路由仅在使用 OpenRouter 时生效。对于直接连接到提供商（例如直接连接 Anthropic API）的情况无效。
:::

## 选项

### `sort`

控制 OpenRouter 如何为您的请求对可用提供商进行排序。

| 值 | 描述 |
|-------|-------------|
| `"price"` | 最便宜的提供商优先 |
| `"throughput"` | 每秒 token 数最快的优先 |
| `"latency"` | 首个 token 到达时间最短的优先 |

```yaml
provider_routing:
  sort: "price"
```

### `only`

提供商名称的白名单。设置后，**仅**使用这些提供商，其他所有提供商均被排除。

```yaml
provider_routing:
  only:
    - "Anthropic"
    - "Google"
```

### `ignore`

提供商名称的黑名单。这些提供商将**永不**被使用，即使它们提供最便宜或最快的选项。

```yaml
provider_routing:
  ignore:
    - "Together"
    - "DeepInfra"
```

### `order`

显式的优先级顺序。列表中排在前面的提供商优先使用。未列出的提供商作为后备。

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
    - "AWS Bedrock"
```

### `require_parameters`

当设置为 `true` 时，OpenRouter 只会将请求路由到支持您的请求中**所有**参数（如 `temperature`、`top_p`、`tools` 等）的提供商。这可以避免参数被静默丢弃。

```yaml
provider_routing:
  require_parameters: true
```

### `data_collection`

控制提供商是否可以使用您的提示（prompts）进行训练。选项为 `"allow"` 或 `"deny"`。

```yaml
provider_routing:
  data_collection: "deny"
```

## 实际示例

### 优化成本

路由到最便宜的可用提供商。适用于高用量和开发阶段：

```yaml
provider_routing:
  sort: "price"
```

### 优化速度

为交互式使用优先选择低延迟提供商：

```yaml
provider_routing:
  sort: "latency"
```

### 优化吞吐量

最适合长时间生成场景，此时每秒 token 数很重要：

```yaml
provider_routing:
  sort: "throughput"
```

### 锁定到特定提供商

确保所有请求都通过特定提供商以保证一致性：

```yaml
provider_routing:
  only:
    - "Anthropic"
```

### 避免特定提供商

排除您不想使用的提供商（例如出于数据隐私考虑）：

```yaml
provider_routing:
  ignore:
    - "Together"
    - "Lepton"
  data_collection: "deny"
```

### 带有后备的优先顺序

首先尝试您偏好的提供商，若不可用则回退到其他提供商：

```yaml
provider_routing:
  order:
    - "Anthropic"
    - "Google"
  require_parameters: true
```

## 工作原理

提供商路由偏好通过每次 API 调用中的 `extra_body.provider` 字段传递给 OpenRouter API。这适用于：

- **CLI 模式** —— 在 `~/.hermes/config.yaml` 中配置，启动时加载
- **网关模式** —— 使用同一配置文件，在网关启动时加载

路由配置从 `config.yaml` 读取，并在创建 `AIAgent` 时作为参数传递：

```
providers_allowed  ← from provider_routing.only
providers_ignored  ← from provider_routing.ignore
providers_order    ← from provider_routing.order
provider_sort      ← from provider_routing.sort
provider_require_parameters ← from provider_routing.require_parameters
provider_data_collection    ← from provider_routing.data_collection
```

:::tip
您可以组合多个选项。例如，按价格排序，但排除某些提供商并要求参数支持：

```yaml
provider_routing:
  sort: "price"
  ignore: ["Together"]
  require_parameters: true
  data_collection: "deny"
```
:::

## 默认行为

当未配置 `provider_routing` 部分时（默认情况），OpenRouter 使用其自身的默认路由逻辑，通常会自动平衡成本和可用性。

:::tip 提供商路由 vs. 后备模型
提供商路由控制的是 OpenRouter 内部的**子提供商**如何处理您的请求。若要在主模型失败时自动故障切换到完全不同的提供商，请参阅 [后备提供商](/user-guide/features/fallback-providers)。
:::