--- frontmatter ---
---
title: "电话功能（Telephony）— 无需更改核心工具即可为 Hermes 添加电话能力"
sidebar_label: "电话功能（Telephony）"
description: "无需更改核心工具即可为 Hermes 添加电话能力"
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非本页面。 */}

# 电话功能（Telephony）

无需更改核心工具即可为 Hermes 添加电话能力。配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，进行直接通话，并通过 Bland.ai 或 Vapi 发起 AI 驱动的外呼。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/telephony` 安装 |
| 路径 | `optional-skills/productivity/telephony` |
| 版本 | `1.0.0` |
| 作者 | Nous Research |
| 许可协议 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `telephony`, `phone`, `sms`, `mms`, `voice`, `twilio`, `bland.ai`, `vapi`, `calling`, `texting` |
| 相关技能 | [`maps`](/docs/user-guide/skills/bundled/productivity/productivity-maps)，[`google-workspace`](/docs/user-guide/skills/bundled/productivity/productivity-google-workspace)，[`agentmail`](/docs/user-guide/skills/optional/email/email-agentmail) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时智能体（Agent）看到的指令。
:::

# 电话功能（Telephony）— 无需更改核心工具的号码、通话和短信

此可选技能为 Hermes 提供了实用的电话功能，同时将电话功能排除在核心工具列表之外。

它附带一个辅助脚本 `scripts/telephony.py`，可以：
- 将提供商凭证保存到 `${HERMES_HOME:-~/.hermes}/.env`
- 搜索并购买 Twilio 电话号码
- 在后续会话中记住该拥有的号码
- 从拥有的号码发送 SMS / MMS
- 轮询该号码的入站 SMS，无需 webhook 服务器
- 使用 TwiML `<Say>` 或 `<Play>` 发起直接 Twilio 通话
- 将拥有的 Twilio 号码导入 Vapi
- 通过 Bland.ai 或 Vapi 发起外呼 AI 通话

## 解决的问题

此技能旨在涵盖用户实际需要的实用电话任务：
- 外呼
- 短信
- 拥有一个可重复使用的智能体号码
- 稍后检查发送到该号码的消息
- 在会话之间保留该号码及相关 ID
- 为入站 SMS 轮询和其他自动化提供面向未来的电话身份

它**不会**将 Hermes 变成实时入站电话网关。入站 SMS 通过轮询 Twilio REST API 处理。这对于许多工作流（包括通知和某些一次性代码检索）来说已经足够，且无需添加核心 webhook 基础设施。

## 安全规则 — 必须遵守

1. 在拨打电话或发送短信前务必确认。
2. 切勿拨打紧急号码。
3. 切勿将电话功能用于骚扰、垃圾信息、冒充他人或任何非法活动。
4. 将第三方电话号码视为敏感操作数据：
   - 不要将其保存到 Hermes 记忆（Memory）中
   - 不要将其包含在技能文档、摘要或后续笔记中，除非用户明确要求
5. 可以持久化**智能体拥有的 Twilio 号码**，因为它是用户配置的一部分。
6. **不能保证** VoIP 号码适用于所有第三方 2FA 流程。谨慎使用，并明确告知用户预期。

## 决策树 — 使用哪种服务？

使用此逻辑而非硬编码的提供商路由：

### 1) "我希望 Hermes 拥有一个真实的电话号码"
使用 **Twilio**。

原因：
- 购买和保留号码的最简单途径
- 最佳的 SMS / MMS 支持
- 最简单的入站 SMS 轮询方案
- 未来实现入站 webhook 或通话处理的最清晰路径

使用场景：
- 稍后接收短信
- 发送部署告警 / 定时通知
- 维护智能体的可重复使用的电话身份
- 稍后尝试基于电话的认证流

### 2) "我现在只需要最简单的 AI 外呼电话"
使用 **Bland.ai**。

原因：
- 设置最快
- 只需一个 API 密钥
- 无需先自行购买/导入号码

权衡：
- 灵活性较低
- 语音质量尚可，但非最佳

### 3) "我想要最好的对话式 AI 语音质量"
使用 **Twilio + Vapi**。

原因：
- Twilio 提供你拥有的号码
- Vapi 提供更好的对话式 AI 通话质量和更多语音/模型灵活性

推荐流程：
1. 购买/保存一个 Twilio 号码
2. 将其导入 Vapi
3. 保存返回的 `VAPI_PHONE_NUMBER_ID`
4. 使用 `ai-call --provider vapi`

### 4) "我想用自定义预录音频消息打电话"
使用 **Twilio 直接通话**，配合公共音频 URL。

原因：
- 播放自定义 MP3 的最简单方式
- 与 Hermes 的 `text_to_speech` 配合良好，再加上公共文件托管或隧道

## 文件和持久化状态

该技能在两个位置持久化电话状态：

### `${HERMES_HOME:-~/.hermes}/.env`
用于长期存在的提供商凭证和拥有的号码 ID，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER`（AI 通话提供商：bland 或 vapi）

### `~/.hermes/telephony_state.json`
用于仅技能相关的状态，这些状态应在会话之间持久化，例如：
- 记住的默认 Twilio 号码 / SID
- 记住的 Vapi 电话号码 ID
- 最后入站消息 SID/日期，用于收件箱轮询检查点

这意味着：
- 下次加载技能时，`diagnose` 可以告诉你已经配置了哪个号码
- `twilio-inbox --since-last --mark-seen` 可以从上一个检查点继续

## 定位辅助脚本

安装此技能后，按如下方式定位脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 为空，则表示尚未安装该技能。

## 安装

这是一个官方可选技能，因此从 Skills Hub 安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

## 提供商设置

### Twilio — 拥有的号码、SMS/MMS、直接通话、入站 SMS 轮询

在以下地址注册：
- https://www.twilio.com/try-twilio

然后将凭证保存到 Hermes：

```bash
python3 "$SCRIPT" save-twilio ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_auth_token_here
```

搜索可用号码：

```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 5
```

购买并记住一个号码：

```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

列出拥有的号码：

```bash
python3 "$SCRIPT" twilio-owned
```

稍后将其中的一个设为默认：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# 或
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

### Bland.ai — 最简单的 AI 外呼

在以下地址注册：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

### Vapi — 更好的对话式语音质量

在以下地址注册：
- https://dashboard.vapi.ai

首先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将你拥有的 Twilio 号码导入 Vapi，并持久化返回的电话号码 ID：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果你已经知道 Vapi 电话号码 ID，直接保存：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

## 诊断当前状态

在任何时候，检查技能已知的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，首先使用此命令。

## 常见工作流

### A. 购买智能体号码并在以后继续使用

1. 保存 Twilio 凭证：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买它并保存到 `${HERMES_HOME:-~/.hermes}/.env` + 状态：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 下次会话时运行：
```bash
python3 "$SCRIPT" diagnose
```
这将显示记住的默认号码和收件箱检查点状态。

### B. 从智能体号码发送短信

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "你的部署已成功完成。"
```

带媒体文件：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "这是图表。" --media-url "https://example.com/chart.png"
```

### C. 无需 webhook 服务器，稍后检查入站短信

轮询默认 Twilio 号码的收件箱：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示上次检查点之后到达的消息，并在阅读完毕后推进检查点：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这是回答“下次加载技能时如何访问该号码收到的消息？”的主要方法。

### D. 使用内置 TTS 发起直接 Twilio 通话

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "你好！这是 Hermes 给你打来的状态更新电话。" --voice Polly.Joanna
```

### E. 使用预录音频/自定义语音消息通话

这是重用 Hermes 现有 `text_to_speech` 支持的主要路径。

在以下情况使用：
- 你希望通话使用 Hermes 配置的 TTS 语音，而非 Twilio 的 `<Say>`
- 你需要单向语音传递（简报、警报、笑话、提醒、状态更新）
- 你**不需要**实时对话式电话通话

单独生成或托管音频，然后：

```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS -> Twilio Play 工作流：

1. 使用 Hermes `text_to_speech` 生成音频。
2. 使生成的 MP3 公开可访问。
3. 使用 `--audio-url` 发起 Twilio 通话。

智能体流程示例：
- 要求 Hermes 使用 `text_to_speech` 创建消息音频
- 如果需要，使用临时静态主机/隧道/对象存储 URL 公开文件
- 使用 `twilio-call --audio-url ...` 通过电话发送

MP3 的良好托管选项：
- 临时公共对象/存储 URL
- 到本地静态文件服务器的短时隧道
- 电话提供商可以直接获取的任何现有 HTTPS URL

重要说明：
- Hermes TTS 非常适合预录的外呼消息
- Bland/Vapi 更适合**实时对话式 AI 通话**，因为它们自己处理实时电话音频堆栈
- Hermes STT/TTS 在此处不单独用作全双工电话通话引擎；这需要比本技能尝试引入的更重的流/webhook 集成

### F. 使用 Twilio 直接通话导航电话树/IVR

如果需要在通话连接后按数字键，请使用 `--send-digits`。
Twilio 将 `w` 解释为短等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "正在连接到账单部门。" --send-digits "ww1w2w3"
```

这在到达特定菜单分支（然后再转接给人或传递简短状态消息）时非常有用。

### G. 使用 Bland.ai 进行 AI 外呼

```bash
python3 "$SCRIPT" ai-call "+15551230000" "致电牙科诊所，预约周二下午的洗牙服务。如果周二没有空位，则询问周三或周四。" --provider bland --voice mason --max-duration 3
```

检查状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

通话完成后提出 Bland 分析问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "预约确认了吗？、什么日期和时间？、有任何特别说明吗？"
```

### H. 使用 Vapi 在你拥有的号码上进行 AI 外呼

1. 将你的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2. 发起通话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "你正在致电预订一个双人晚餐，时间为晚上 7:30。如果该时间不可用，请询问晚上 6:30 到 8:30 之间的最近时间。" --provider vapi --max-duration 4
```

3. 检查结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

## 建议的智能体流程

当用户要求打电话或发短信时：

1. 根据决策树确定适合的路径。
2. 如果配置状态不明确，运行 `diagnose`。
3. 收集完整任务详情。
4. 在拨号或发短信前与用户确认。
5. 使用正确的命令。
6. 如果需要，轮询结果。
7. 总结结果，不要将第三方号码持久化到 Hermes 记忆（Memory）中。

## 此技能仍不具备的功能

- 实时入站通话接听
- 基于 webhook 的实时短信推送到智能体循环
- 保证支持任意第三方 2FA 提供商

这些需要比纯可选技能更多的基础设施。

## 陷阱

- Twilio 试用账户和地区规则可能限制你可以拨打电话/发送短信的对象。
- 某些服务拒绝将 VoIP 号码用于 2FA。
- `twilio-inbox` 轮询 REST API；它不是即时推送投递。
- Vapi 外呼仍然依赖于拥有有效的导入号码。
- Bland 最简单，但声音不一定最好。
- 不要将任意第三方电话号码存储在 Hermes 记忆（Memory）中。

## 验证清单

设置完成后，你应该能够仅使用此技能完成以下所有操作：

1. `diagnose` 显示提供商准备情况和记住的状态
2. 搜索并购买 Twilio 号码
3. 将该号码持久化到 `${HERMES_HOME:-~/.hermes}/.env`
4. 从拥有的号码发送 SMS
5. 稍后轮询该号码的入站短信
6. 发起直接 Twilio 通话
7. 通过 Bland 或 Vapi 发起 AI 通话

## 参考

- Twilio 电话号码：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息服务：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai：https://app.bland.ai/