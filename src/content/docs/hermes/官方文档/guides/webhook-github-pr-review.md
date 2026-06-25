--- frontmatter ---
---

## 完整配置参考（Full Config Reference）

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"         # 绑定地址（默认：0.0.0.0）
      port: 8644               # 监听端口（默认：8644）
      secret: ""               # 可选的全局回退密钥（optional global fallback secret）
      rate_limit: 30           # 每条路由每分钟的请求数
      max_body_bytes: 1048576  # 负载大小限制（单位：字节，默认：1 MB）

      routes:
        <route-name>:
          secret: "required-per-route"
          events: []            # [] = 接受所有事件；否则列出 X-GitHub-Event 值
          prompt: ""            # {field} / {nested.field} 从负载中解析
          skills: []            # 加载第一个匹配的技能（仅一个）
          deliver: "log"        # log | github_comment | telegram | discord | slack | signal | sms
          deliver_extra: {}     # github_comment 需要 repo + pr_number；其他需要 chat_id
```

---

--- body ---
## 下一步是什么？（What's Next?）

- **[基于定时任务的 PR 审查（Cron-Based PR Reviews）](./github-pr-review-agent.md)** — 按计划轮询 PR，无需公开端点
- **[Webhook 参考（Webhook Reference）](/user-guide/messaging/webhooks)** — Webhook 平台的完整配置参考
- **[构建一个插件（Build a Plugin）](/guides/build-a-hermes-plugin)** — 将审查逻辑打包成可共享的插件
- **[配置文件（Profiles）](/user-guide/profiles)** — 使用专属内存和配置运行专用的审查者配置文件