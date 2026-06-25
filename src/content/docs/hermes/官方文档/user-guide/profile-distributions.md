---
title: Profile Distributions
---

## 配方（Recipes）

### 固定到特定版本

:::note
Git引用固定（`#v1.2.0`）已规划但尚未在初始版本中提供——当前安装会跟踪默认分支。通过`hermes profile info <name>`跟踪你所安装的版本，并在准备好之前暂缓更新。
:::

### 检查你所使用的版本与最新版本

```bash
# 你已安装的版本
hermes profile info research-bot | grep Version

# 上游最新版本（不安装的情况）
git ls-remote --tags https://github.com/you/research-bot | tail -5
```

### 通过更新保留本地配置自定义

默认更新行为已经做到这一点：`config.yaml`会被保留。为了安全起见，将你的本地调整写入分发版不会触及的文件中：

```yaml
# ~/.hermes/profiles/research-bot/local/my-overrides.yaml
# （分发版永远不会触及 local/ 目录）
```

…然后根据需要从 `config.yaml` 或你的 SOUL 中引用它。

### 强制完全重新安装

```bash
# 彻底删除并从头重新安装（也会丢失记忆/会话）
hermes profile delete research-bot --yes
hermes profile install github.com/you/research-bot --alias

# 更新到当前主分支，但将 config.yaml 重置为分发版的默认配置
hermes profile update research-bot --force-config --yes
```

### 分叉（Fork）并定制

标准的 git 工作流——分发版就是仓库：

```bash
# 在 GitHub 上分叉该仓库，然后安装你的分叉版本
hermes profile install github.com/yourname/forked-research-bot --alias

# 在 ~/.hermes/profiles/forked-research-bot/ 中本地迭代
# 编辑 SOUL.md，提交，推送到你的分叉版本
# 上游变更：按照常规方式拉取到你的分叉版本中
```

### 在推送前测试分发版

在作者机器上：

```bash
# 从本地目录安装（无需推送 git）
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test --alias

# 调整、删除、重新安装，直到正确为止
hermes profile delete research-bot-test --yes
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test
```

---

--- body ---
## 分发版中永远不包含的内容

即使作者意外包含了这些路径，安装程序也会硬性排除它们。没有配置选项可以覆盖此限制——此安全防护是一个经过回归测试的不变量：

- `auth.json` —— OAuth 令牌、平台凭证
- `.env` —— API 密钥、机密信息
- `memories/` —— 对话记忆
- `sessions/` —— 对话历史
- `state.db`、`state.db-shm`、`state.db-wal` —— 会话元数据
- `logs/` —— 代理（Agent）和错误日志
- `workspace/` —— 生成的工作文件
- `plans/` —— 临时计划
- `home/` —— Docker 后端中用户的主目录挂载点
- `*_cache/` —— 图片/音频/文档缓存
- `local/` —— 用户保留的自定义命名空间

当你作为安装者克隆一个分发版时，这些文件根本就不会被复制到你的配置文件目录中。当你更新时，你的副本保持不变。如果你在五台机器上安装了同一个分发版，你会得到五组完全独立的数据——每台机器一组。

:::caution
此排除操作在**安装/更新时，在安装者机器上**执行。它**不会**阻止作者提交敏感或不必要的文件。作者必须使用 [`.gitignore`](#step-3--create-a-gitignore-before-the-first-commit) 来将机密信息排除在仓库之外。
:::

## 安全与信任

配置文件分发版默认是未签名的。你信任的是：

- **Git 托管平台**（GitHub / GitLab / 其他）提供作者推送的字节内容。
- **作者**不会发布恶意的 SOUL、技能（Skill）或定时任务（cron job）。

来自分发版的定时任务**不会自动调度**——安装程序会打印 `hermes -p <name> cron list`，你需要明确启用它们。SOUL.md 和技能（Skill）在你开始与该配置文件对话时立即生效，因此如果你从你信任的人那里安装，请在首次运行前阅读它们。

粗略类比：安装分发版就像安装浏览器扩展或 VS Code 扩展。低摩擦、高能力、信任来源。对于公司内部分发版，请使用私有仓库和常规的 git 认证——无需额外配置。

未来版本可能会增加签名、带有已解析提交 SHA 的锁文件（`.distribution-lock.yaml`），以及在应用更新前打印差异的 `--dry-run` 标志。这些功能目前都尚未发布。

## 底层实现

有关实现细节、精确的 CLI 行为以及所有标志，请参阅[配置文件命令参考](../reference/profile-commands.md#distribution-commands)。

简要说明：

- `install`、`update`、`info` 位于 `hermes profile` 之下——而不是一个并行的命令树。
- 清单格式为 YAML，带有极小的必要模式（仅需要 `name`）。
- 安装程序使用你本地的 `git` 二进制文件进行克隆，因此你的 shell 已经处理的任何认证（SSH 密钥、凭据助手）都可以透明地工作。
- 克隆后，会剥离 `.git/` 目录——安装后的配置文件本身不是一个 git 检出，从而避免“哎呀，我不小心把 `.env` 提交到分发版的 git 历史中了”这种陷阱。
- 保留的配置文件名称（`hermes`、`test`、`tmp`、`root`、`sudo`）在安装时会被拒绝，以避免与常见二进制文件冲突。

## 另请参阅

- [配置文件：运行多个代理](./profiles.md) —— 基本概念
- [配置文件命令参考](../reference/profile-commands.md) —— 所有标志和选项
- [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) —— 本地备份/恢复（非分发版）
- [在 Hermes 中使用 SOUL](../guides/use-soul-with-hermes.md) —— 创作个性
- [个性与 SOUL](./features/personality.md) —— SOUL 如何融入代理
- [技能目录](../reference/skills-catalog.md) —— 你可以捆绑的技能