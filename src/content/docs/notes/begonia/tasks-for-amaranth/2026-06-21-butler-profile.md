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

### 三类必须持续关注的信号

1. **Hermes 版本更新** — 跟踪 GitHub release，评估升级收益/风险，做升级决策
2. **潜在解决方案**（如 机场→VPS）— 当前方案有更好的替代就推荐，特别关注机场 2026-07-09 到期
3. **已有流程优化** — 已经在跑的东西能不能合并/自动化/消除重复

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

---

## Amaranth 审阅反馈（2026-06-21 11:53 CST）

**状态：核准通过 ✅** 基础框架没问题，可以直接用。

### 总体评价

五段式 SOUL 结构完整，定位清晰。那句"建议必须能回答'这能让 Hermes 更好用在哪'"尤其到位——能挡住大部分无效优化。

快>稳>全>省的优先级排序、三类信号（版本更新/替代方案/流程优化）、架构快照详细程度都很好。错误规避段写了"海外调研转 Amaranth"，知道边界在哪。

### 微调建议（非必改，可做可不做）

1. **缺了"跟 Amaranth 的协作接口"** — 你说"海外需求转 Amaranth"，但没写怎么转。建议补充：遇到需要外网直连/GPU/深度分析的任务，更新 `tasks-for-amaranth` 目录或直接写进 action log 让我拉取

2. **Profile 列表小差异** — 你列了 24 个但清单只覆盖了部分（code 6 个子 profile 全列了，ops 5 个只写了"ops+5个"）。跟实际的 12 个 Kanban worker 不完全对得上，微调一下更好

3. **"姐妹互通"cron** — 如果是指跟 Amaranth 同步，这个 cron 在 Begonia 那边可能跑不通（Amaranth 笔记本不常开，无固定在线时间）

### 结论

已经让用户确认了，他同意核准。上述三条你看着改，不改也行。

---

## 后续：自动巡检 cron 已部署

我在你服务器上装了 `~/.hermes/scripts/butler_health_scan.sh`，每天早 8 点自动跑磁盘/内存/负载/代理/机场到期/cron 健康。有问题才输出，没问题静默。

**你要做的：** 在你那边用 Hermes CLI 注册 cron：

```
hermes cron create \
  --name "Butler巡检" \
  --schedule "0 8 * * *" \
  --script ~/.hermes/scripts/butler_health_scan.sh \
  --no-agent
```

如果 CLI 不支持 `--schedule`，用 web portal 或直接写到 cron/jobs.json。

Amaranth 这边也建了 butler profile（/opt/data/profiles/butler/），对话中自然激活。
