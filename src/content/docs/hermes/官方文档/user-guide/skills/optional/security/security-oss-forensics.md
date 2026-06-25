---
title: Oss Forensics
---

## API 速率限制（Rate Limiting）

GitHub REST API 会强制实施速率限制，如果不加以管理，会中断大型调查。

**已认证请求**：5,000次/小时（需要 `GITHUB_TOKEN` 环境变量或 `gh` CLI 认证）
**未认证请求**：60次/小时（无法用于调查）

**最佳实践**：
- 始终进行身份认证：`export GITHUB_TOKEN=ghp_...` 或使用 `gh` CLI（自动认证）
- 使用条件请求（`If-None-Match` / `If-Modified-Since` 标头）避免对未更改数据消耗配额
- 对于分页端点，按顺序获取所有页面——不要对同一端点进行并行请求
- 检查 `X-RateLimit-Remaining` 标头；如果低于100，则暂停至 `X-RateLimit-Reset` 时间戳
- BigQuery 有自己的配额（免费层为 10 TiB/天）——始终先进行试运行（dry-run）
- Wayback Machine CDX API：无正式速率限制，但应保持礼貌（最大 1-2 请求/秒）

如果在调查过程中遇到速率限制，请将部分结果记录到证据存储中，并在报告中说明该限制。

---

--- body ---
--- body ---
--- body ---
--- body ---
--- body ---
## 参考资料

- [github-archive-guide.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/github-archive-guide.md) — BigQuery 查询、CDX API、12 种事件类型
- [evidence-types.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/evidence-types.md) — IOC 分类法、证据源类型、观察类型
- [recovery-techniques.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/recovery-techniques.md) — 恢复已删除的提交、PR、议题
- [investigation-templates.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/references/investigation-templates.md) — 针对每种攻击类型的预构建假设模板
- [evidence-store.py](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/scripts/evidence-store.py) — 用于管理证据 JSON 存储的 CLI 工具
- [forensic-report.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/oss-forensics/templates/forensic-report.md) — 结构化报告模板