---
title: Updating
---

# 更新与卸载

## 更新

通过一条命令即可更新到最新版本：

```bash
hermes update
```

此命令从 `main` 分支拉取最新代码、更新依赖项，并提示你配置自上次更新以来新增的任何选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示你添加。如果你跳过了该提示，可以手动运行 `hermes config check` 查看缺失的选项，然后运行 `hermes config migrate` 以交互方式添加它们。
:::

### 更新期间发生了什么

运行 `hermes update` 时，将执行以下步骤：

1. **配对（Pairing）数据快照** — 保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则以及在运行时被修改的其他状态文件）。可通过[快照与回滚](../user-guide/checkpoints-and-rollback.md)中描述的快照恢复流程进行恢复，或解压 Hermes 在 `~/.hermes/` 目录旁写入的最新快速快照 zip 文件。
2. **Git 拉取** — 从 `main` 分支拉取最新代码并更新子模块。
3. **拉取后语法验证 + 自动回滚** — 拉取后，Hermes 会编译每次 `hermes` 调用启动时导入的八个关键文件。如果其中任何一个解析失败（例如，孤立的合并冲突标记、意外截断的文件），Hermes 将执行 `git reset --hard <pre-pull-sha>` 回滚安装，以便你的 shell 保持可启动状态。等待上游修复完成后重新运行 `hermes update`。
4. **依赖安装** — 运行 `uv pip install -e ".[all]"` 以安装新增或更改的依赖项。
5. **配置迁移** — 检测自你版本以来新增的配置选项，并提示你进行设置。
6. **网关（Gateway）自动重启** — 更新完成后，正在运行的网关会被刷新，以便新代码立即生效。服务管理的网关（Linux 上的 systemd，macOS 上的 launchd）会通过服务管理器重启。当 Hermes 能将运行中的 PID 映射回某个配置文件时，手动网关会自动重新启动。

### 针对非默认分支进行更新：`--branch`

默认情况下，`hermes update` 跟踪 `origin/main`。通过 `--branch <name>` 参数可以针对不同分支进行更新——这对 QA 渠道、功能分支或候选版本测试很有用：

```bash
hermes update --branch release-candidate
hermes update --check --branch experimental   # 仅预览落后程度
```

如果你的本地检出位于另一个分支，Hermes 会自动暂存任何未提交的工作，将 HEAD 切换到目标分支，然后拉取。本地不存在的分支会自动从 `origin/<name>` 跟踪（`git checkout -B <name> origin/<name>`）。任何地方都不存在的分支会干净地失败——退出前会恢复你的暂存更改，这样你就不会卡在奇怪的状态中。仅限 `main` 分支的上游同步逻辑会自动跳过非 `main` 分支。

### 非交互式更新中的本地更改

当你在终端中运行 `hermes update` 时，Hermes 会暂存任何未提交的源码树更改、拉取，然后**询问**是否恢复这些更改——与以往完全一样。交互式更新没有任何变化。

当更新**在没有终端**的情况下运行时——通过桌面/聊天应用的“更新”按钮或由网关触发的更新——则没有提示可供回答。`updates.non_interactive_local_changes` 设置决定了你的暂存更改如何处理：

```yaml
# ~/.hermes/config.yaml
updates:
  non_interactive_local_changes: stash   # 默认：保留并自动恢复
  # non_interactive_local_changes: discard  # 丢弃本地源编辑
```

- `stash`（默认）— 自动暂存、拉取，然后在更新后的代码之上自动恢复你的更改。不会丢失任何内容；如果恢复时遇到冲突，它们会保留在 git 暂存中以供手动恢复。
- `discard` — 自动暂存并在拉取后丢弃暂存内容，这样更新始终落在干净的树中。仅在你永远不希望保留对 Hermes 源码的本地编辑的机器上使用此选项。它会执行暂存丢弃（而非 `git reset --hard` + `git clean -fd`），因此 `node_modules`、`venv` 和构建输出等被忽略的路径永远不会被触及。

在桌面应用中，此选项位于 **设置 → 高级 → 应用内更新本地更改**。

### 仅预览：`hermes update --check`

想在拉取之前知道是否有可用更新？运行 `hermes update --check`——它会获取并与 `origin/main` 比较提交。不会修改任何文件，也不会重启任何网关。在基于“是否有更新”进行判断的脚本和 cron 作业中很有用。

### 完整的更新前备份：`--backup`

对于高价值配置文件（生产网关、团队共享安装），你可以选择在拉取前对整个 `HERMES_HOME`（配置、认证、会话、技能（Skill）、配对）进行完整备份：

```bash
hermes update --backup
```

或者将其设为每次运行的默认行为：

```yaml
# ~/.hermes/config.yaml
updates:
  pre_update_backup: true
```

`--backup` 在早期版本中是始终开启的行为，但在大型 home 目录上每次更新会增加几分钟时间，因此现在改为可选项。上述轻量级配对数据快照仍然无条件运行。

### Windows：另一个 `hermes.exe` 正在运行

在 Windows 上，如果 `hermes update` 检测到另一个 `hermes.exe` 进程占用了虚拟环境入口点可执行文件（最常见的是 Hermes 桌面应用生成的后端、另一个终端中打开的 `hermes` REPL，或正在运行的网关），则会拒绝运行：

```
$ hermes update
✗ 另一个 hermes.exe 正在运行：
    PID 12345  hermes.exe

  现在更新将无法覆盖 ...\venv\Scripts\hermes.exe，因为
  Windows 阻止替换正在运行的可执行文件。

  关闭 Hermes Desktop，退出所有打开的 `hermes` REPL，并
  停止网关 (`hermes gateway stop`) 后重试。
  如果你已确认这些进程不会写入虚拟环境，可以使用 `hermes update --force` 覆盖。
```

关闭列出的进程并重新运行。如果你确定并发进程不会干扰（这种情况很少见——通常仅在杀毒软件垫片被错误归因时有用），可以传递 `--force` 跳过检查。在这种情况下，更新程序仍会以指数退避重试 `.exe` 重命名，如果锁固执不改，则会通过 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 将替换安排在下次重启时进行，以便更新完成。

预期输出如下：

```
$ hermes update
更新 Hermes 代理（Agent）...
📥 正在拉取最新代码...
已是最新。  (或：正在更新 abc1234..def5678)
📦 正在更新依赖项...
✅ 依赖项已更新
🔍 正在检查新的配置选项...
✅ 配置已是最新  (或：发现 2 个新选项 — 正在运行迁移...)
🔄 正在重启网关...
✅ 网关已重启
✅ Hermes 代理成功更新！
```

### 推荐的更新后验证

`hermes update` 处理了主要的更新路径，但快速验证可以确认一切干净落地：

1. `git status --short` — 如果树意外脏污，请在继续前检查
2. `hermes doctor` — 检查配置、依赖项和服务健康状态
3. `hermes --version` — 确认版本已按预期升级
4. 如果你使用网关：`hermes gateway status`
5. 如果 `doctor` 报告了 npm 审核问题：在标记的目录中运行 `npm audit fix`

:::warning 更新后工作树脏污
如果在 `hermes update` 后 `git status --short` 显示了意外的更改，请停止并在继续前检查它们。这通常意味着本地修改已重新应用于更新后的代码上，或者某个依赖步骤刷新了锁文件。
:::

### 如果更新过程中终端断开连接

`hermes update` 能防止意外的终端丢失：

- 更新会忽略 `SIGHUP`，因此关闭 SSH 会话或终端窗口不会再中断安装过程。`pip` 和 `git` 子进程继承了此保护，因此 Python 环境不会因连接断开而处于半安装状态。
- 更新期间所有输出都会镜像到 `~/.hermes/logs/update.log`。如果你的终端消失了，重新连接并检查日志以查看更新是否完成以及网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT）和系统关机（SIGTERM）仍然会被响应——那些是故意的取消，而非意外。

你不再需要将 `hermes update` 包装在 `screen` 或 `tmux` 中来抵御终端断开。

### 检查当前版本

```bash
hermes version
```

与最新版本进行比较，请访问 [GitHub releases 页面](https://github.com/NousResearch/hermes-agent/releases)。

### 通过消息平台更新

你也可以直接从 Telegram、Discord、Slack、WhatsApp 或 Teams 发送以下命令进行更新：

```
/update
```

这会拉取最新代码、更新依赖项并重启正在运行的网关。机器人会在重启期间短暂离线（通常 5–15 秒），然后恢复。

### 手动更新

如果你是通过手动方式安装的（而非快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# 拉取最新代码
git pull origin main

# 重新安装（获取新的依赖项）
uv pip install -e ".[all]"

# 检查新的配置选项
hermes config check
hermes config migrate   # 以交互方式添加任何缺失的选项
```

### 回滚说明

如果更新引入了问题，你可以回滚到之前的版本：

```bash
cd /path/to/hermes-agent

# 列出最近的版本
git log --oneline -10

# 回滚到特定提交
git checkout <commit-hash>
uv pip install -e ".[all]"

# 如果正在运行，重启网关
hermes gateway restart
```

要回滚到特定发布标签（替换为你的上一个标签——例如最近的版本如 `v2026.5.16`，或从 `git tag --sort=-version:refname` 中看到的任何更早标签）：

```bash
git checkout vX.Y.Z
uv pip install -e ".[all]"
```

:::warning
如果添加了新选项，回滚可能会导致配置不兼容。回滚后运行 `hermes config check`，如果遇到错误，请从 `config.yaml` 中移除任何无法识别的选项。
:::

### 针对 Nix 用户的通知

如果你通过 Nix flake 安装，更新将通过 Nix 包管理器进行管理：

```bash
# 更新 flake 输入
nix flake update hermes-agent

# 或者使用最新版本重建
nix profile upgrade hermes-agent
```

Nix 安装是不可变的——回滚由 Nix 的世代系统处理：

```bash
nix profile rollback
```

更多详情请参阅 [Nix 设置](./nix-setup.md)。

---

--- body ---
## 卸载

```bash
hermes uninstall
```

卸载程序会提供选项，让你保留配置文件（`~/.hermes/`）以便将来重新安装。

### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # 可选——如果计划重新安装则保留
```

:::info
如果你已将网关安装为系统服务，请先停止并禁用它：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::