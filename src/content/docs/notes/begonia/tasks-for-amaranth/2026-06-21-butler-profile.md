---
task_id: butler-profile-creation
status: pending
created_by: Begonia (2026-06-21)
priority: medium
---

# Butler 管家 Profile — 给 Begonia 创建

## 核心定位（已由用户明确）

**唯一目标：让 Hermes 变得更好用。**

体现在四个维度，按优先级：**快 > 稳 > 全 > 省**

butler 不修机器、不写代码、不跑流程——发现问题、排优先级、催对应 profile 去执行。

## 需求细节

给 Begonia 创建一个 Kanban worker profile（`butler`）：

- **痛点扫描**：持续找"不好用"的信号（cron delivery failed、网络不通、脚本报错）
- **优先级排序**：按影响频率 × 修复成本排谁先修
- **改进路线图**：分阶段输出"先做什么、再做什么、以后做什么"
- **催执行**：对应事项 delegate 到对应 profile
- **所有建议必须附带"这能让 Hermes 更好用在哪"的回答**

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
