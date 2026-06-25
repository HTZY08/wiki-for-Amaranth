--- frontmatter ---
---

## 工作流与模式（Workflows & Patterns）

### 为不同任务使用不同模型（多模型工作流）

**场景：** 你日常使用 GPT-5.4，但 Gemini 或 Grok 更适合写社交媒体内容。每次手动切换模型很繁琐。

**解决方案：** 委托配置（Delegation config）。Hermes 可以自动将子代理（subagents）路由到不同模型。在 `~/.hermes/config.yaml` 中设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # 子代理使用此模型
  provider: "openrouter"                    # 子代理的提供商
```

现在，当你告诉 Hermes “帮我写一条关于 X 的 Twitter 推文”时，它会生成一个 `delegate_task` 子代理，该子代理在 Gemini 上运行，而不是你的主模型。你的主要对话仍保留在 GPT-5.4 上。

你也可以在提示语中明确说明：*“委托一个任务来撰写关于我们产品发布的社交媒体帖子。让子代理实际写作。”* 代理将使用 `delegate_task`，它会自动采用委托配置。

如需单次模型切换而不使用委托，可在 CLI 中使用 `/model` 命令：

```bash
/model google/gemini-3-flash-preview    # 切换当前会话的模型
# ... 撰写内容 ...
/model openai/gpt-5.4                   # 切换回来
```

更多关于委托的工作原理，请参见 [子代理委托](../user-guide/features/delegation.md)。

### 在同一个 WhatsApp 号码上运行多个代理（按聊天绑定）

**场景：** 在 OpenClaw 中，你将多个独立代理绑定到特定的 WhatsApp 聊天——一个用于家庭购物清单群组，另一个用于私人聊天。Hermes 也能实现吗？

**当前限制：** Hermes 的每个配置文件（profile）都需要独立的 WhatsApp 号码/会话。你不能在同一个 WhatsApp 号码上将多个配置文件绑定到不同的聊天——WhatsApp 桥接（Baileys）每个号码只使用一个已认证的会话。

**变通方法：**

1. **使用单个配置文件，通过人格切换。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令按聊天更改行为。代理会识别它在哪个聊天中，并相应调整。

2. **使用 cron 任务处理特定任务。** 对于购物清单追踪器，设置一个 cron 任务来监控特定聊天并管理清单——无需单独的代理。

3. **使用不同的号码。** 如果你需要真正独立的代理，请为每个配置文件配对其自己的 WhatsApp 号码。Google Voice 等服务的虚拟号码可以用于此目的。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按聊天绑定——每个 Telegram 群组或 Discord 频道都有自己的会话，你可以在同一个账户上运行多个机器人令牌（每个配置文件一个）。

更多详情，请参见 [配置文件](../user-guide/profiles.md) 和 [WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中显示的内容（隐藏日志和推理过程）

**场景：** 你在 Telegram 中看到了网关执行日志、Hermes 推理过程和工具调用细节，而不是最终输出。

**解决方案：** `config.yaml` 中的 `display.tool_progress` 设置控制工具活动的显示程度：

```yaml
display:
  tool_progress: "off"   # 选项： off, new, all, verbose
```

- **`off`** — 仅显示最终响应。无工具调用、无推理过程、无日志。
- **`new`** — 显示新的工具调用（简短的一行摘要）。
- **`all`** — 显示所有工具活动，包括结果。
- **`verbose`** — 完整详细信息，包括工具参数和输出。

对于消息平台，通常使用 `off` 或 `new`。编辑 `config.yaml` 后，重启网关以使更改生效。

你也可以使用 `/verbose` 命令（如果启用）按会话切换此设置：

```yaml
display:
  tool_progress_command: true   # 在网关中启用 /verbose 命令
```

### 在 Telegram 上管理技能（斜杠命令限制）

**场景：** Telegram 有 100 个斜杠命令的限制，而你的技能数量正在超过这个限制。你想在 Telegram 上禁用不需要的技能，但 `hermes skills config` 设置似乎没有生效。

**解决方案：** 使用 `hermes skills config` 按平台禁用技能。这会写入 `config.yaml`：

```yaml
skills:
  disabled: []                    # 全局禁用的技能
  platform_disabled:
    telegram: [skill-a, skill-b]  # 仅在 Telegram 上禁用
```

更改后，**重启网关**（`hermes gateway restart` 或关闭后重新启动）。Telegram 机器人命令菜单会在启动时重新生成。

:::tip
描述过长的技能在 Telegram 菜单中会被截断为 40 个字符，以保持在有效载荷大小限制内。如果技能没有出现，可能是总有效载荷大小问题，而不是命令数量限制——禁用未使用的技能对两者都有帮助。
:::

### 共享线程会话（多个用户，一个对话）

**场景：** 你有一个 Telegram 或 Discord 线程，其中多个用户提到机器人。你希望该线程中的所有提及都属于一个共享对话，而不是每个用户独立的会话。

**当前行为：** Hermes 在大多数平台上根据用户 ID 创建会话，因此每个人都有自己的对话上下文。这是为了隐私和上下文隔离而设计的。

**变通方法：**

1. **使用 Slack。** Slack 的会话按线程关联，而不是按用户。同一线程中的多个用户共享一个对话——这正是你描述的行为。这是最自然的匹配。

2. **使用单个用户的群聊。** 如果指定一名“操作员”来转发问题，则会话保持统一。其他人可以旁听。

3. **使用 Discord 频道。** Discord 的会话按频道关联，因此同一频道中的所有用户共享上下文。使用专用频道进行共享对话。

### 将 Hermes 导出到另一台机器

**场景：** 你在一台机器上构建了技能、cron 任务和记忆，现在想将其全部迁移到一台新的专用 Linux 机器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

2. 在**源机器**上创建完整备份：
   ```bash
   hermes backup
   ```
   这将创建整个 `~/.hermes/` 目录的压缩包——包括配置、API 密钥、记忆、技能、会话和配置文件——保存在你的主目录中，文件名为 `~/hermes-backup-<timestamp>.zip`。

3. 将压缩包复制到新机器并导入：
   ```bash
   # 在源机器上
   scp ~/hermes-backup-<timestamp>.zip newmachine:~/

   # 在新机器上
   hermes import ~/hermes-backup-<timestamp>.zip
   ```

4. 在新机器上运行 `hermes setup` 以验证 API 密钥和提供商配置是否正常工作。

### 将单个配置文件移动到另一台机器

**场景：** 你想移动或共享一个特定的配置文件——而不是整个安装。

```bash
# 在源机器上
hermes profile export work ./work-backup.tar.gz

# 将文件复制到目标机器，然后：
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将包含导出的所有配置、记忆、会话和技能。如果新机器设置不同，你可能需要更新路径或重新认证提供商。

### `hermes backup` 与 `hermes profile export` 对比

| 功能 | `hermes backup` | `hermes profile export` |
| :--- | :--- | :--- |
| **使用场景** | **全机器迁移** | **移植/共享特定配置文件** |
| **范围** | 全局（整个 `~/.hermes` 目录） | 本地（单个配置文件目录） |
| **包含内容** | 所有配置文件、全局配置、API 密钥、会话 | 单个配置文件：SOUL.md、记忆、会话、技能 |
| **凭据** | **包含**（`.env` 和 `auth.json`） | **排除**（为安全共享而去除） |
| **格式** | `.zip` | `.tar.gz` |

**手动回退方法（rsync）：** 如果你偏好直接复制文件，请排除代码仓库：
```bash
rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
```

:::tip
即使 Hermes 正在运行，`hermes backup` 也会生成一致的快照。还原的归档会排除机器本地的运行时文件，如 `gateway.pid` 和 `cron.pid`。
:::

### 安装后重新加载 shell 时出现权限拒绝错误

**场景：** 运行 Hermes 安装程序后，执行 `source ~/.zshrc` 出现权限拒绝错误。

**原因：** 这通常是由于 `~/.zshrc`（或 `~/.bashrc`）文件权限不正确，或安装程序无法干净地写入该文件。这不是 Hermes 特有的问题——而是 shell 配置权限问题。

**解决方案：**
```bash
# 检查权限
ls -la ~/.zshrc

# 如有必要进行修复（应为 -rw-r--r-- 或 644）
chmod 644 ~/.zshrc

# 然后重新加载
source ~/.zshrc

# 或直接打开一个新的终端窗口——它会自动加载 PATH 更改
```

如果安装程序添加了 PATH 行但权限错误，你可以手动添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行代理时出现错误 400

**场景：** 设置顺利完成，但第一次聊天尝试失败并返回 HTTP 400 错误。

**原因：** 通常是模型名称不匹配——配置的模型在你的提供商上不存在，或者 API 密钥没有访问该模型的权限。

**解决方案：**
```bash
# 检查配置的模型和提供商
hermes config show | head -20

# 重新运行模型选择
hermes model

# 或者用已知可用的模型进行测试
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```

如果使用 OpenRouter，请确保你的 API 密钥有积分。OpenRouter 返回 400 通常意味着该模型需要付费计划，或者模型 ID 有拼写错误。

---

--- body ---
## 仍然卡住？

如果你的问题未在此处涵盖：

1. **搜索已有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区求助：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请包含你的操作系统、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息。