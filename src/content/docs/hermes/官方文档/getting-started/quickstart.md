--- frontmatter ---
---

## 常见故障模式（Common Failure Modes）

以下是浪费最多时间的问题：

| 症状（Symptom） | 可能原因（Likely cause） | 修复方法（Fix） |
|---|---|---|
| Hermes 打开但返回空或错误的回复 | 提供者认证（Provider auth）或模型选择错误 | 重新运行 `hermes model` 并确认提供者（provider）、模型和认证（auth） |
| 自定义端点“正常工作”但返回垃圾信息 | 基础 URL、模型名称错误，或实际上不兼容 OpenAI | 先在单独客户端中验证端点 |
| 网关启动但无人可向其发送消息 | 机器人令牌（Bot token）、允许列表（allowlist）或平台设置不完整 | 重新运行 `hermes gateway setup` 并检查 `hermes gateway status` |
| `hermes --continue` 找不到旧会话 | 切换了配置文件（profiles）或会话从未保存 | 检查 `hermes sessions list` 并确认你处于正确的配置文件中 |
| 模型不可用或出现奇怪的默认回退行为 | 提供者路由（Provider routing）或回退设置过于激进 | 在基础提供者稳定之前保持路由关闭 |
| `hermes doctor` 标记配置问题 | 配置值缺失或过期 | 修复配置，在添加功能前重新测试普通聊天 |

## 恢复工具包（Recovery Toolkit）

当感觉有问题时，按此顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

该序列能让你从“异常状态”快速回到已知状态。

---

--- body ---
--- body ---
## 快速参考（Quick Reference）

| 命令（Command） | 描述（Description） |
|---|---|
| `hermes` | 开始聊天 |
| `hermes model` | 选择你的 LLM 提供者（provider）和模型 |
| `hermes tools` | 配置每个平台启用的工具（tools） |
| `hermes setup` | 完整设置向导（一次性配置所有内容） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 更新到最新版本 |
| `hermes gateway` | 启动消息网关（messaging gateway） |
| `hermes --continue` | 恢复上次会话 |

## 下一步（Next Steps）

- **[CLI 指南（CLI Guide）](../user-guide/cli.md)** — 掌握终端界面
- **[配置（Configuration）](../user-guide/configuration.md)** — 自定义你的设置
- **[消息网关（Messaging Gateway）](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant、Teams 等
- **[工具与工具集（Tools & Toolsets）](../user-guide/features/tools.md)** — 探索可用能力
- **[AI 提供者（AI Providers）](../integrations/providers.md)** — 完整提供者列表及设置详情
- **[技能系统（Skills System）](../user-guide/features/skills.md)** — 可重用工作流与知识
- **[技巧与最佳实践（Tips & Best Practices）](../guides/tips.md)** — 高级用户技巧