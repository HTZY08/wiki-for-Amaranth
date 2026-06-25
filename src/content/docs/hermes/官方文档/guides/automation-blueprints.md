--- frontmatter ---
---

## 多技能工作流（Multi-Skill Workflows）

### 安全审计流水线

组合多项技能进行全面的每周安全审查。

**触发方式：** 按计划（每周）

```bash
hermes cron create "0 3 * * 0" \
  "Run a comprehensive security audit of the hermes-agent codebase.

1. Check for dependency vulnerabilities (pip audit, npm audit)
2. Search the codebase for common security anti-patterns:
   - Hardcoded secrets or API keys
   - SQL injection vectors (string formatting in queries)
   - Path traversal risks (user input in file paths without validation)
   - Unsafe deserialization (pickle.loads, yaml.load without SafeLoader)
3. Review recent commits (last 7 days) for security-relevant changes
4. Check if any new environment variables were added without being documented

Write a security report with findings categorized by severity (Critical, High, Medium, Low).
If nothing found, report a clean bill of health." \
  --skill codebase-security-audit \
  --name "Weekly security audit" \
  --deliver telegram
```

### 内容流水线

按计划进行调研、起草并准备内容。

**触发方式：** 按计划（每周）

```bash
hermes cron create "0 10 * * 3" \
  "Research and draft a technical blog post outline about a trending topic in AI agents.

1. Search the web for the most discussed AI agent topics this week
2. Pick the most interesting one that's relevant to open-source AI agents
3. Create an outline with:
   - Hook/intro angle
   - 3-4 key sections
   - Technical depth appropriate for developers
   - Conclusion with actionable takeaway
4. Save the outline to ~/drafts/blog-$(date +%Y%m%d).md

Keep the outline to ~300 words. This is a starting point, not a finished post." \
  --name "Blog outline" \
  --deliver local
```

---

--- body ---
--- body ---
## 快速参考

### Cron 计划语法

| 表达式 | 含义 |
|--------|------|
| `every 30m` | 每30分钟 |
| `every 2h` | 每2小时 |
| `0 2 * * *` | 每天凌晨2:00 |
| `0 9 * * 1` | 每周一上午9:00 |
| `0 9 * * 1-5` | 工作日上午9:00 |
| `0 3 * * 0` | 每周日凌晨3:00 |
| `0 */6 * * *` | 每6小时 |

### 投递目标

| 目标 | 标志 | 说明 |
|------|------|------|
| 同一聊天 | `--deliver origin` | 默认 — 投递到创建任务的位置 |
| 本地文件 | `--deliver local` | 保存输出，不发送通知 |
| Telegram | `--deliver telegram` | 家庭频道，或指定 `telegram:CHAT_ID` |
| Discord | `--deliver discord` | 家庭频道，或指定 `discord:CHANNEL_ID` |
| Slack | `--deliver slack` | 家庭频道 |
| 短信 | `--deliver sms:+15551234567` | 直接发送到手机号码 |
| 特定话题 | `--deliver telegram:-100123:456` | Telegram 论坛主题 |

### Webhook 模板变量

| 变量 | 描述 |
|------|------|
| `{pull_request.title}` | 拉取请求标题 |
| `{issue.number}` | Issue 编号 |
| `{repository.full_name}` | `owner/repo` |
| `{action}` | 事件动作（opened、closed 等） |
| `{__raw__}` | 完整 JSON 负载（截断至 4000 字符） |
| `{sender.login}` | 触发事件的 GitHub 用户 |

### [SILENT] 模式

当 cron 任务的响应中包含 `[SILENT]` 时，投递会被抑制。用于在静默运行时避免通知轰炸：

```
如果没有什么值得注意的事情，请回复 [SILENT]。
```

这意味着只有当代理（Agent）有内容需要报告时你才会收到通知。