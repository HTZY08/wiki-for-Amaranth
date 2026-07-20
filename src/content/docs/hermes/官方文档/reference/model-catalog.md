---
title: 模型目录
---

# 模型目录

Hermes 从托管在文档站点旁的 JSON 清单中获取 **OpenRouter** 和 **Nous Portal** 的精选模型列表。这使得维护者无需发布新的 `hermes-agent` 版本即可更新选择器列表。

当清单无法访问时（离线、网络阻塞、托管故障），Hermes 会静默回退到随 CLI 一起发布的仓库内快照。

## 实时清单 URL

https://hermes-agent.nousresearch.com/docs/api/model-catalog.json

每次合并到 `main` 分支时，通过现有的 `deploy-site.yml` GitHub Pages 流水线发布。

## 模式（Schema）

```json
{
  "version": 1,
  "updated_at": "2026-04-25T22:00:00Z",
  "metadata": {},
  "providers": {
    "openrouter": { "metadata": {}, "models": [...] },
    "nous": { "metadata": {}, "models": [...] }
  }
}
```

字段说明：`version`、`metadata`、`description`、`default`、定价/上下文长度。

## 获取行为

| 条件 | 发生情况 |
|------|----------|
| `/model` 或 `hermes model` | 如果磁盘缓存过期则获取 |
| 磁盘缓存未过期（< TTL） | 无网络请求 |
| 网络失败但有缓存 | 静默回退到缓存 |
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

### 按提供者覆盖 URL

第三方可以自行托管自己的精选列表。

## 更新清单

维护者：

```bash
python scripts/build_model_catalog.py
```

然后 PR 到 `main` 分支。文档站点在合并后自动部署。
