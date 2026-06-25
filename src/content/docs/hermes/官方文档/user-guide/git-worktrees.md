---
title: Git Worktrees
---

sidebar_position: 3
sidebar_label: "Git 工作树"
title: "Git 工作树"
description: "使用 Git 工作树和隔离检出，在同一仓库中安全运行多个 Hermes 代理"
---

--- body ---
# Git 工作树

Hermes 代理常用于大型、长期存在的仓库。当你想要：

- 在同一个项目上**并行运行多个代理**，或者
- 将实验性重构与主分支隔离，

Git **工作树（worktrees）** 是为每个代理提供独立检出而不复制整个仓库的最安全方式。

本页介绍如何将工作树与 Hermes 结合使用，使每个会话拥有干净、隔离的工作目录。

## 为何要在 Hermes 中使用工作树？

Hermes 将**当前工作目录**视为项目根目录：

- CLI：运行 `hermes` 或 `hermes chat` 的目录
- 消息网关：由 `~/.hermes/config.yaml` 中 `terminal.cwd` 设置的目录

如果你在**同一个检出**中运行多个代理，它们的更改可能会相互干扰：

- 一个代理可能删除或重写另一个代理正在使用的文件。
- 更难理解哪些更改属于哪个实验。

使用工作树后，每个代理获得：

- 它**自己的分支和工作目录**
- 它**自己的检查点管理器历史记录**，用于 `/rollback`

另请参阅：[检查点与 /rollback](./checkpoints-and-rollback.md)。

## 快速开始：创建工作树

从主仓库（包含 `.git/`）中，为功能分支创建一个新工作树：

```bash
# 在主仓库根目录下
cd /path/to/your/repo

# 创建新分支和工作树，位于 ../repo-feature
git worktree add ../repo-feature feature/hermes-experiment
```

这将创建：

- 一个新目录：`../repo-feature`
- 一个在该目录中签出的新分支：`feature/hermes-experiment`

现在你可以 `cd` 进入新的工作树并在此运行 Hermes：

```bash
cd ../repo-feature

# 在工作树中启动 Hermes
hermes
```

Hermes 将：

- 将 `../repo-feature` 视为项目根目录。
- 使用该目录作为上下文文件、代码编辑和工具的工作目录。
- 使用**独立的检查点历史记录**，并限定在此工作树范围内，用于 `/rollback`。

## 并行运行多个代理

你可以创建多个工作树，每个都有独立的分支：

```bash
cd /path/to/your/repo

git worktree add ../repo-experiment-a feature/hermes-a
git worktree add ../repo-experiment-b feature/hermes-b
```

在独立的终端中：

```bash
# 终端 1
cd ../repo-experiment-a
hermes

# 终端 2
cd ../repo-experiment-b
hermes
```

每个 Hermes 进程：

- 在其自己的分支上工作（`feature/hermes-a` vs `feature/hermes-b`）。
- 在（由工作树路径派生的）不同影子仓库哈希下写入检查点。
- 可以独立使用 `/rollback`，不影响另一个。

这在以下场景中特别有用：

- 运行批量重构。
- 对同一任务尝试不同方法。
- 针对同一个上游仓库，同时使用 CLI 和网关会话。

## 安全清理工作树

当某个实验完成后：

1. 决定是保留还是丢弃工作。
2. 如果要保留：
   - 像往常一样将分支合并到主分支。
3. 移除工作树：

```bash
cd /path/to/your/repo

# 移除工作树目录及其引用
git worktree remove ../repo-feature
```

注意：

- 除非强制，否则 `git worktree remove` 将拒绝移除含有未提交更改的工作树。
- 移除工作树**不会**自动删除分支；你可以使用常规 `git branch` 命令删除或保留分支。
- 移除工作树时，`~/.hermes/checkpoints/` 下的 Hermes 检查点数据不会自动清理，但通常数据量很小。

## 最佳实践

- **每个 Hermes 实验一个工作树**
  - 为每个实质性更改创建独立的分支/工作树。
  - 这能保持差异集中，PR 小而可审阅。
- **根据实验命名分支**
  - 例如 `feature/hermes-checkpoints-docs`、`feature/hermes-refactor-tests`。
- **频繁提交**
  - 使用 git 提交记录高级里程碑。
  - 使用[检查点与 /rollback](./checkpoints-and-rollback.md) 作为工具驱动编辑的保险网。
- **使用工作树时，避免从裸仓库根目录运行 Hermes**
  - 优先使用工作树目录，这样每个代理都有清晰的范围。

## 使用 `hermes -w`（自动工作树模式）

Hermes 有一个内置的 `-w` 标志，可以**自动创建一个带有独立分支的一次性 git 工作树**。你无需手动设置工作树——只需 `cd` 进入仓库并运行：

```bash
cd /path/to/your/repo
hermes -w
```

Hermes 将：

- 在你的仓库内的 `.worktrees/` 下创建一个临时工作树。
- 签出一个隔离的分支（例如 `hermes/hermes-<hash>`）。
- 在该工作树内运行完整的 CLI 会话。

这是获得工作树隔离的最简单方式。你也可以将其与单个查询结合使用：

```bash
hermes -w -z "修复问题 #123"
```

对于并行代理，打开多个终端并在每个终端中运行 `hermes -w`——每次调用都会自动获得自己的工作树和分支。

## 汇总

- 使用 **git 工作树**为每个 Hermes 会话提供自己干净的检出。
- 使用**分支**捕获实验的高级历史。
- 在每个工作树内部使用**检查点 + `/rollback`** 从错误中恢复。

这种组合带来：

- 强保证：不同代理和实验不会相互干扰。
- 快速迭代周期，易于从错误编辑中恢复。
- 干净、可审阅的拉取请求。