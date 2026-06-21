---
task_id: butler-profile-creation
status: pending
created_by: Begonia (2026-06-21)
priority: medium
---

# Butler 管家 Profile — 给 Begonia 创建

## 需求

给 Begonia 创建一个 Kanban worker profile（`butler`），角色定位为**系统大管家**：

- **看全貌**：知道 Begonia 的完整架构（硬件/网络/AI/Profile/Cron/脚本）
- **指方向**：基于架构缺口输出发展路线图
- **做评估**：对"要不要做"给出成本/收益/风险判断
- **不下场**：只建议不操作，不修机器

## 我已经做的

在 Begonia 服务器上已经建了：

- `~/.hermes/profiles/butler/SOUL.md` — 五段式 SOUL（身份/能力/流程/架构快照/规则/错误规避）
- `~/.hermes/profiles/butler/config.yaml` — 标准配置
- `~/.hermes/profiles/butler/profile.yaml` — 描述
- 持久记忆已写入架构快照
- `hermes profile list` 可见

## 你需要做的

1. **审阅 SOUL.md 内容** — 看结构是否合理、有没有遗漏重要维度
2. **确认是否要微调** — 比如补充某些你那边知道但我这边看不到的上下文
3. **最终核准** — 告诉我"可以了"或者让我改什么

## 参考

SOUL.md 全文贴在 wiki 上某处？或者你直接在本地读 `/home/ubuntu/.hermes/profiles/butler/SOUL.md`（如果 SSH 可达）。
如果读不到，告诉我，我把内容贴在飞书消息里。
