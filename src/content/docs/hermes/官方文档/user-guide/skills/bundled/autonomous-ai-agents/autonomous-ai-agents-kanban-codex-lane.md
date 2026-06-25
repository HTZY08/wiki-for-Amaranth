---
title: "看板 Codex 车道 (Kanban Codex Lane)"
sidebar_label: "看板 Codex 车道"
description: "当 Hermes 看板工作者希望将 Codex CLI 作为独立的实施车道运行，而 Hermes 保留任务生命周期、协调、测试...的所有权时使用。"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# 看板 Codex 车道 (Kanban Codex Lane)

当 Hermes 看板工作者希望将 Codex CLI 作为独立的实施车道运行，而 Hermes 保留任务生命周期、协调、测试和交接的所有权时使用。

## 技能元数据 (Skill metadata)

| | |
|---|---|
| 来源 (Source) | 捆绑（默认安装） |
| 路径 (Path) | `skills/autonomous-ai-agents/kanban-codex-lane` |
| 版本 (Version) | `1.0.0` |
| 作者 (Author) | Hermes 代理 |
| 许可证 (License) | MIT |
| 标签 (Tags) | `kanban`, `codex`, `worktrees`, `autonomous-agents`, `prediction-market-bot` |
| 相关技能 (Related skills) | [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md (Reference: full SKILL.md)

:::info
以下是技能被触发时 Hermes 加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# 看板 Codex 车道 (Kanban Codex Lane)

## 概述 (Overview)

本技能为看板工作者定义了轻量级的 Hermes+Codex 双车道约定。Hermes 始终是任务所有者：它调用 `kanban_show`，判断 Codex 是否合适，创建或选择隔离的工作空间，启动并监控 Codex，协调差异，运行验证，并写入最终的 `kanban_complete` 或 `kanban_block` 交接。Codex 仅为输入车道。Codex 的输出不能作为任务完成信号，不能作为可信的审查者，也不允许直接写入持久的看板状态。

该约定存在的目的是让 Hermes 工作者能够在无需更改调度器的情况下，将 Codex 用于限定范围内的实施帮助。调度器仍必须生成 Hermes 工作者。工作者可以选择在其自身运行中启动 Codex，然后在独立审查和测试后接受、部分接受或拒绝该车道。

## 使用时机 (When to Use)

当满足以下所有条件时，使用 Codex 车道：

- 看板任务属于编码、重构、文档、测试或机械性迁移任务，且具有明确的验收标准。
- Hermes 可以在一次运行中评估限定范围的差异。
- 仓库可以在隔离的 git 工作树/分支上复制或检出。
- Codex 退出后，Hermes 可以自行运行相关测试。
- 提示中可以声明所有安全约束和不得更改的文件。

当满足以下任一条件时，不要使用 Codex 车道：

- 任务需要尚未包含在看板主体中的人工判断。
- 工作者缺乏仓库访问权限、Codex 认证或协调结果的时间。
- 变更涉及密钥、凭据存储、私人用户数据或生产订单录入系统。
- 小而直接的编辑比生成另一个代理更快、更安全。
- 任务仅为研究性质，应产出书面交接而非差异。
- 工作者可能会倾向于仅根据 Codex 的自我报告标记为已完成。

## 所有权规则 (Ownership Rules)

1. Hermes 拥有看板生命周期。Codex 绝不得调用 `kanban_complete`、`kanban_block`、`kanban_create`、网关消息或任何 Hermes 看板 CLI 来替代工作者。
2. Hermes 拥有最终验收权。在审查和验证之前，将 Codex 的提交/差异视为不受信任的补丁。
3. Hermes 拥有测试执行权。Codex 可以运行测试，但这些运行仅供参考；需使用仓库的规范包装器从 Hermes 重复必要的验证。
4. Hermes 拥有安全权。如果 Codex 改变了安全边界、风险门、实时交易行为或密钥处理，即使测试通过也要拒绝该车道。
5. Hermes 拥有清理权。杀死卡住的 Codex 进程，并在不再需要时移除临时工作树。

## 所需的工作树和分支模式 (Required Worktree and Branch Pattern)

切勿直接在共享的脏检出中运行 Codex。使用能将车道与看板任务关联起来并保持不受信任编辑隔离的分支/工作树名称。

推荐变量：

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
BASE="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"
```

创建隔离车道：

```bash
git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
git -C "$WORKTREE" status --short --branch
```

如果当前的看板工作空间已经是为此任务隔离的 git 工作树，你可以仅当 `git status --short` 除了 Hermes 有意编辑之外是干净的情况下，在其中创建一个兄弟 Codex 分支。否则，创建一个单独的临时工作树，并在协调后将接受的提交挑选或复制回来。

协调后清理：

```bash
git -C "$REPO" worktree remove "$WORKTREE"
git -C "$REPO" branch -D "$BRANCH"  # 仅在接受的提交已复制/挑选或有意拒绝后执行
```

如果工作树需要作为审查的工件保留，则保留它；在 `codex_lane.artifacts` 中记录，并在交接中提及。

## Codex 能力检查 (Codex Capability Checks)

在生成 Codex 之前运行这些检查。缺少 Codex 是跳过车道的正常原因，如果 Hermes 可以直接完成任务，则不是任务阻塞因素。

```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

如果需要 `/goal` 支持，仅在检查可用性后启用或使用功能标志启动：

```bash
codex features enable goals || true
codex --enable goals --version
```

身份验证可以通过 `OPENAI_API_KEY` 或 Codex CLI OAuth 状态（通常为 `~/.codex/auth.json`）完成。不要打印令牌文件。缺少 `OPENAI_API_KEY` 并不证明身份验证不可用。

## 模式选择 (Mode Selection)

对于限定范围的一次性编辑（Codex 应自行退出），使用 `codex exec`：

```python
terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

仅当更广泛的多步骤工作受益于持久目标跟踪时，才使用 Codex `/goal`。在 PTY/tmux 会话中以交互方式启动，或者如果该功能默认禁用，则使用 `codex --enable goals` 启动。保持目标自包含：仓库路径、任务 ID、安全约束、允许范围、验收标准、测试和提交期望。

示例 `/goal` 目标文本（粘贴到 Codex 中）：

```text
/goal 仅在此仓库中工作：<WORKTREE>。任务：<TASK_ID> <TITLE>。
Hermes 拥有看板生命周期；请勿调用 Hermes 看板工具或消息传递。
在分支 <BRANCH> 上创建小提交。遵循提示中的 PMB 安全约束。
运行请求的验证命令并报告确切输出。在产生差异和摘要后停止。
```

对于预测市场机器人或安全敏感的仓库，不要使用 `--yolo`。首选在隔离的工作树中使用 `--full-auto`，然后依赖 Hermes 协调。

## 提示构建 (Prompt Construction)

对于预测市场机器人相关工作，使用 `templates/pmb-codex-lane-prompt.md` 中的链接模板。对于其他仓库，保持相同结构，并将 PMB 特定的安全块替换为仓库特定的不变式。

每个 Codex 提示必须包含：

- `task_id`、标题和完整的看板验收标准。
- 仓库路径、工作树路径、分支名称和允许的文件范围。
- 明确声明：Hermes 拥有看板生命周期；Codex 仅为输入车道。
- 所需输出：简洁的摘要、更改的文件、提交、运行的测试和已知风险。
- 禁止的操作：密钥访问、外部消息传递、看板状态变更、无关重构、除非必需的依赖升级。
- Codex 可以运行的验证命令以及 Hermes 之后将运行的命令。

对于 PMB，逐字包含这些强制安全约束：

```text
PMB 安全约束：
- live-SIM 仅限模拟；请勿添加或启用实时 REST 订单录入。
- 不要使用市价单。
- 不要添加绕过价格/风险检查的执行交叉。
- 不要伪造被动成交、成交、盈亏、订单状态或协调证据。
- 不要削弱风险门、限制、紧急停止或故障关闭行为。
- 除非明确要求，否则将研究/选择保留在 C++ 热路径之外。
- 不要读取、打印、写入或要求密钥/令牌/凭据。
```

## 监控、超时和终止行为 (Monitoring, Timeout, and Kill Behavior)

在后台上启动长 Codex 车道，使用 PTY 和完成通知：

```python
result = terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
session_id = result["session_id"]
```

在不干扰的情况下监控：

```python
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)
```

对于超过两分钟的车道，每隔几分钟发送一次看板心跳，例如 `kanban_heartbeat(note="Codex lane running in <WORKTREE>; waiting for tests/diff")`。

终止条件：

- 在任务的剩余运行时间预算内没有有用的输出。
- Codex 请求密钥、生产凭据或外部权限。
- Codex 尝试修改工作树之外的文件。
- Codex 开始无关的重写或依赖变更。
- Codex 仍在工作超时附近运行，且没有安全的部分工件。

终止命令：

```python
process(action="kill", session_id=session_id)
```

终止后，检查 `git status --short`，仅当安全时才保留有用的补丁，并记录 `codex_lane.result: timed_out` 或 `rejected`，并附上具体的 `rejected_reason`。

## 协调检查清单 (Reconciliation Checklist)

在接受任何 Codex 车道结果之前，Hermes 必须执行以下检查清单：

- [ ] `git -C <WORKTREE> status --short --branch` 仅显示预期的文件。
- [ ] `git -C <WORKTREE> diff --stat` 和 `git diff` 已由 Hermes 审查。
- [ ] 没有包含密钥、凭据、生成的缓存、无关的数据或本地工件。
- [ ] PMB 安全约束已保留：没有实时 REST 订单录入、没有市价单、没有执行交叉、没有伪造的被动成交/盈亏、没有风险门削弱、没有密钥。
- [ ] Codex 提交足够小，可以干净地挑选或压缩。
- [ ] Hermes 自行运行了规范测试，对于 Hermes 代理使用 `scripts/run_tests.sh`，对于其他仓库使用仓库文档化的包装器。
- [ ] 任何由 Codex 运行的测试都与 Hermes 运行的测试分开列出。
- [ ] 接受的提交/差异已应用于 Hermes 拥有的工作空间/分支。
- [ ] 被拒绝或部分完成的工作有具体原因，如果工件有用，则包含工件路径。

接受结果：

- `accepted`：Codex 差异/提交已被审查、应用和验证。
- `partial`：某些 Codex 工作经过编辑或挑选后被接受；被拒绝的部分已记录。
- `rejected`：没有接受任何 Codex 更改；原因已记录。
- `timed_out`：Codex 超出了车道预算；可能存在有用的工件，也可能没有。

## kanban_complete 元数据模式 (kanban_complete Metadata Schema)

对于考虑过车道的每个任务，在 `metadata.codex_lane` 下包含此对象。如果未使用 Codex，设置 `used: false` 并在 `rejected_reason` 或同级 `notes` 字段中解释原因。

```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/absolute/path/to/codex/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "command": "codex exec --full-auto ...",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>", "<sha2>"],
    "rejected_reason": "empty when fully accepted; otherwise concrete reason",
    "tests_run": [
      {"command": "scripts/run_tests.sh tests/tools/test_x.py", "exit_code": 0, "owner": "hermes"},
      {"command": "codex-reported: npm test", "exit_code": 0, "owner": "codex"}
    ],
    "artifacts": ["/absolute/path/to/log-or-patch"]
  }
}
```

对于有意跳过 Codex 的任务：

```json
{
  "codex_lane": {
    "used": false,
    "mode": "skipped",
    "worktree": null,
    "branch": null,
    "command": null,
    "result": "rejected",
    "accepted_commits": [],
    "rejected_reason": "Direct Hermes edit was smaller and safer than spawning Codex.",
    "tests_run": [],
    "artifacts": []
  }
}
```

## 常见陷阱 (Common Pitfalls)

1. 将 Codex 的自我报告视为验证。始终检查差异并从 Hermes 重新运行测试。
2. 在用户的脏主检出中运行 Codex。始终在工作树/分支中隔离。
3. 让 Codex 拥有看板所有权。Codex 可以总结进度，但 Hermes 写入看板状态。
4. 在提示中忘记 PMB 安全不变式。缺少安全文本是车道设置失败。
5. 对快速编辑使用 `/goal`。除非需要持久的多步骤延续，否则首选 `codex exec`。
6. 在未记录原因的情况下杀死卡住的车道。`rejected_reason` 必须解释决定。
7. 因为测试通过而接受广泛无关的清理。拒绝或仅挑选范围内的更改。

## 验证检查清单 (Verification Checklist)

- [ ] Codex 被跳过或仅在 `command -v codex`、`codex --version` 和可选的目标功能检查之后才启动。
- [ ] Codex 仅在隔离的工作树/分支中运行。
- [ ] 提示中包含了任务范围、所有权规则、适用于 PMB 的安全约束以及验证命令。
- [ ] Hermes 审查了 `git diff` 和安全敏感文件。
- [ ] Hermes 独立运行了规范测试。
- [ ] `kanban_complete.metadata.codex_lane` 遵循上述模式。
- [ ] 临时进程和不必要的工作树已被清理。