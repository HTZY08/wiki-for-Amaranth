--- frontmatter ---
---

## 故障排除

### "gh: command not found"
网关运行在极简环境中。请确保 `gh` 在系统 PATH 中，然后重启网关。

### 评审过于泛化
1. 添加 `code-review` 技能（Skill）（步骤3）
2. 通过记忆（Memory）教会 Hermes 你的约定（步骤4）
3. 它对技术栈的了解越多，评审效果就越好

### Cron 任务不运行
```bash
hermes gateway status    # 网关是否在运行？
hermes cron list         # 任务是否已启用？
```

### 速率限制
GitHub 允许已认证用户每小时发起 5,000 次 API 请求。每次 PR 评审大约消耗 3-5 次请求（列表 + diff + 可选的评论）。即使每天评审 100 个 PR，也完全在限制范围内。

---

--- body ---
--- body ---
## 下一步是什么？

- **[基于 Webhook 的 PR 评审](./webhook-github-pr-review.md)** — 在 PR 打开时立即获取评审（需要公共端点）
- **[每日简报机器人](/guides/daily-briefing-bot)** — 将 PR 评审与早间新闻摘要结合
- **[构建插件](/guides/build-a-hermes-plugin)** — 将评审逻辑封装为可分享的插件
- **[配置文件](/user-guide/profiles)** — 运行一个带有独立记忆和配置的专用评审配置文件
- **[备用提供商](/user-guide/features/fallback-providers)** — 确保即使某个提供商出现故障，评审也能正常运行