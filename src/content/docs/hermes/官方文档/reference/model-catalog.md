---
title: Model Catalog
---

sidebar_position: 11
title: 模型目录
description: 通过远程托管的清单驱动 OpenRouter 和 Nous Portal 的精选模型选择列表。
---

--- body ---
# 模型目录

Hermes 从托管在文档站点旁的 JSON 清单中获取 **OpenRouter** 和 **Nous Portal** 的精选模型列表。这使得维护者无需发布新的 `hermes-agent` 版本即可更新选择列表。

当清单无法访问时（离线、网络阻塞、托管故障），Hermes 会静默回退到随 CLI 一起发布的仓库内快照。该清单绝不会破坏选择器——最坏情况下，你会看到与你安装版本捆绑的任何列表。

## 实时清单 URL

```
https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
```

每次合并到 `main` 分支时，通过现有的 `deploy-site.yml` GitHub Pages 流水线发布。事实来源位于仓库的 `website/static/api/model-catalog.json` 中。

## 模式（Schema）

```json
{
  "version": 1,
  "updated_at": "2026-04-25T22:00:00Z",
  "metadata": {},
  "providers": {
    "openrouter": {
      "metadata": {},
      "models": [
        {"id": "moonshotai/kimi-k2.6", "description": "recommended", "metadata": {}},
        {"id": "openai/gpt-5.4",       "description": ""}
      ]
    },
    "nous": {
      "metadata": {},
      "models": [
        {"id": "anthropic/claude-opus-4.7"},
        {"id": "moonshotai/kimi-k2.6"}
      ]
    }
  }
}
```

字段说明：

- **`version`** — 整数模式版本号。未来模式将递增此版本；Hermes 会拒绝其不理解的版本的清单，并回退到硬编码的快照。
- **`metadata`** — 在清单、提供者和模型级别的自由格式字典。任意键。Hermes 会忽略未知字段，因此你可以添加注释条目（如 `"tier": "paid"`、`"tags": [...]` 等），而无需协调模式变更。
- **`description`** — 仅用于 OpenRouter。驱动选择器徽章文本（`"recommended"`、`"free"` 或为空）。Nous Portal 不使用此字段——免费层级的控制由 Portal 的定价端点实时决定。
- **定价和上下文长度**不在清单中。这些信息来自获取时的实时提供者 API（`/v1/models` 端点、models.dev）。

## 获取行为

| 条件 | 发生情况 |
|---|---|
| `/model` 或 `hermes model` | 如果磁盘缓存过期则获取，否则使用缓存 |
| 磁盘缓存未过期（< TTL） | 无网络请求 |
| 网络失败但有缓存 | 静默回退到缓存，输出一行日志 |
| 网络失败且无缓存 | 静默回退到仓库内快照 |
| 清单模式验证失败 | 视为不可达 |

缓存位置：`~/.hermes/cache/model_catalog.json`。

## 配置

```yaml
model_catalog:
  enabled: true
  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json
  ttl_hours: 1
  providers: {}
```

设置 `enabled: false` 可完全禁用远程获取，并始终使用仓库内快照。

### 按提供者覆盖 URL

第三方可以使用相同模式自行托管自己的精选列表。将提供者指向自定义 URL：

```yaml
model_catalog:
  providers:
    openrouter:
      url: https://example.com/my-openrouter-curation.json
```

覆盖清单只需填充它关心的提供者块。其他提供者将继续解析到主 URL。

## 更新清单

维护者：

```bash
# 从仓库内硬编码列表重新生成（编辑 herm_cli/models.py 中的
# OPENROUTER_MODELS 或 _PROVIDER_MODELS["nous"] 后，保持清单同步）
python scripts/build_model_catalog.py
```

然后，将生成的更改 PR 到 `website/static/api/model-catalog.json` 到 `main` 分支。文档站点在合并后自动部署，新清单将在几分钟内生效。

你也可以直接手动编辑 JSON，以进行不适合仓库内快照的精细元数据更改——生成脚本只是一个便利工具，而非唯一事实来源。