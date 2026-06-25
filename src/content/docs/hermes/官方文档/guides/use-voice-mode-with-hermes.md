---
title: Use Voice Mode With Hermes
---

sidebar_position: 8
title: "使用Hermes语音模式"
description: "关于在CLI、Telegram、Discord以及Discord语音频道中设置和使用Hermes语音模式的实用指南"
---

--- body ---
# 使用Hermes语音模式

本指南是[语音模式功能参考文档](/user-guide/features/voice-mode)的实践伴侣。

如果功能页面解释了语音模式能做什么，那么本指南将展示如何实际有效地使用它。

:::tip
[Nous Portal](/integrations/nous-portal) 通过一个OAuth同时捆绑了LLM和TTS——语音模式无需额外凭证即可端到端工作。
:::

## 语音模式适合什么场景

语音模式在以下情况下特别有用：
- 你想要免提的CLI工作流
- 你想要在Telegram或Discord中获得语音回复
- 你想要Hermes坐在Discord语音频道中进行实时对话
- 你想要在走动时快速捕捉想法、调试或来回交流，而不是打字

## 选择你的语音模式设置

Hermes实际上有三种不同的语音体验。

| 模式 | 最适合 | 平台 |
|---|---|---|
| 交互式麦克风循环 | 编码或研究时的个人免提使用 | CLI |
| 聊天中的语音回复 | 普通消息旁边的语音回复 | Telegram, Discord |
| 实时语音频道机器人 | 语音频道中的群组或个人实时对话 | Discord语音频道 |

一个好的路径是：
1. 先让文本模式正常工作
2. 其次启用语音回复
3. 最后如果你想要完整体验，再移动到Discord语音频道

## 第一步：确保普通Hermes先正常工作

在接触语音模式之前，验证：
- Hermes 启动
- 你的提供商已配置
- 代理（Agent）能够正常回答文本提示

```bash
hermes
```

询问一些简单的问题：

```text
你有什么可用的工具？
```

如果这还不稳定，先修复文本模式。

## 第二步：安装正确的额外依赖

### CLI 麦克风 + 回放

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[voice]"
```

### 消息平台

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[messaging]"
```

### 高级 ElevenLabs TTS

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[tts-premium]"
```

### 本地 NeuTTS（可选）

```bash
python -m pip install -U neutts[all]
```

### 全部

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"
```

## 第三步：安装系统依赖

### macOS

```bash
brew install portaudio ffmpeg opus
brew install espeak-ng
```

### Ubuntu / Debian

```bash
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng
```

为什么这些重要：
- `portaudio` → CLI语音模式的麦克风输入/回放
- `ffmpeg` → 音频转换用于TTS和消息投递
- `opus` → Discord语音编解码器支持
- `espeak-ng` → NeuTTS的音素化后端

## 第四步：选择STT和TTS提供商

Hermes同时支持本地和云端语音堆栈。

### 最简单/最便宜的设置

使用本地STT和免费的Edge TTS：
- STT提供商：`local`
- TTS提供商：`edge`

这通常是最好的起点。

### 环境文件示例

添加到 `~/.hermes/.env`：

```bash
# 云端STT选项（本地无需密钥）
GROQ_API_KEY=***
VOICE_TOOLS_OPENAI_KEY=***

# 高级TTS（可选）
ELEVENLABS_API_KEY=***
```

### 提供商推荐

#### 语音转文本（Speech-to-text）

- `local` → 最佳默认选项，保护隐私且零成本
- `groq` → 非常快的云端转录
- `openai` → 不错的付费备选

#### 文本转语音（Text-to-speech）

- `edge` → 免费且对大多数用户足够好
- `neutts` → 免费的本地/设备端TTS
- `elevenlabs` → 最佳质量
- `openai` → 不错的折中选择
- `mistral` → 多语言，原生Opus

### 如果你使用 `hermes setup`

如果在设置向导中选择NeuTTS，Hermes会检查 `neutts` 是否已安装。如果缺失，向导会告知NeuTTS需要Python包 `neutts` 和系统包 `espeak-ng`，并提供安装选项，使用你的平台包管理器安装 `espeak-ng`，然后运行：

```bash
python -m pip install -U neutts[all]
```

如果你跳过安装或安装失败，向导会回退到Edge TTS。

## 第五步：推荐配置

```yaml
voice:
  record_key: "ctrl+b"
  max_recording_seconds: 120
  auto_tts: false
  beep_enabled: true
  silence_threshold: 200
  silence_duration: 3.0

stt:
  provider: "local"
  local:
    model: "base"

tts:
  provider: "edge"
  edge:
    voice: "en-US-AriaNeural"
```

这对大多数人来说是一个不错的保守默认配置。

如果你想要本地TTS，可以将 `tts` 块切换为：

```yaml
tts:
  provider: "neutts"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

## 用例一：CLI语音模式

## 开启它

启动Hermes：

```bash
hermes
```

在CLI内部：

```text
/voice on
```

### 录制流程

默认按键：
- `Ctrl+B`

工作流：
1. 按下 `Ctrl+B`
2. 说话
3. 等待静音检测自动停止录制
4. Hermes转录并响应
5. 如果TTS开启，它会说出答案
6. 循环可以自动重新开始以实现连续使用

### 有用的命令

```text
/voice
/voice on
/voice off
/voice tts
/voice status
```

### 好的CLI工作流

#### 临时调试

说：

```text
我一直遇到Docker权限错误。帮我调试一下。
```

然后继续免提：
- "再读一遍最后一条错误"
- "用更简单的术语解释根本原因"
- "现在给我准确的修复方法"

#### 研究/头脑风暴

非常适合：
- 边思考边走动
- 口述半成型的想法
- 让Hermes实时结构化你的思路

#### 无障碍/低打字场景

如果打字不方便，语音模式是保持完整Hermes循环的最快方式之一。

## 调整CLI行为

### 静音阈值

如果Hermes启动/停止过于激进，调整：

```yaml
voice:
  silence_threshold: 250
```

阈值越高 = 越不敏感。

### 静音持续时间

如果你在句子之间停顿较多，增加：

```yaml
voice:
  silence_duration: 4.0
```

### 录制按键

如果 `Ctrl+B` 与你的终端或tmux习惯冲突：

```yaml
voice:
  record_key: "ctrl+space"
```

## 用例二：Telegram或Discord中的语音回复

此模式比完整语音频道更简单。

Hermes保持为普通聊天机器人，但可以语音回复。

### 启动网关

```bash
hermes gateway
```

### 开启语音回复

在Telegram或Discord内：

```text
/voice on
```

或

```text
/voice tts
```

### 模式

| 模式 | 含义 |
|---|---|
| `off` | 仅文本 |
| `voice_only` | 仅当用户发送语音时才回复语音 |
| `all` | 每个回复都说话 |

### 何时使用哪种模式

- 如果你只想对语音来源的消息回复语音，使用 `/voice on`
- 如果你想要一个全天候的语音助手，使用 `/voice tts`

### 好的消息工作流

#### 手机上的Telegram助手

在以下情况使用：
- 你远离电脑
- 你想发送语音笔记并快速获得语音回复
- 你想让Hermes像便携式研究或运维助手一样工作

#### 带语音输出的Discord私信

当你想要私密互动而不使用服务器频道提及行为时很有用。

## 用例三：Discord语音频道

这是最先进的模式。

Hermes加入一个Discord语音频道（VC），聆听用户语音，转录，运行正常的代理管道，然后将语音回复播回频道。

## 所需的Discord权限

除了普通的文本机器人设置外，确保机器人拥有：
- 连接（Connect）
- 说话（Speak）
- 最好使用语音活动（Use Voice Activity）

同时在开发者门户中启用特权意图：
- Presence Intent
- Server Members Intent
- Message Content Intent

## 加入和离开

在机器人所在的Discord文本频道中：

```text
/voice join
/voice leave
/voice status
```

### 加入后会发生什么

- 用户在语音频道中说话
- Hermes检测语音边界
- 转录文本发布在关联的文本频道中
- Hermes以文本和音频形式响应
- 文本频道是发出 `/voice join` 的那个频道

### Discord语音频道使用的最佳实践

- 保持 `DISCORD_ALLOWED_USERS` 严格
- 首先使用专门的机器人/测试频道
- 在尝试语音频道模式之前，先在普通文本聊天语音模式下验证STT和TTS是否正常工作

## 语音质量建议

### 最佳质量设置

- STT: 本地 `large-v3` 或 Groq `whisper-large-v3`
- TTS: ElevenLabs

### 最佳速度/便利性设置

- STT: 本地 `base` 或 Groq
- TTS: Edge

### 最佳零成本设置

- STT: 本地
- TTS: Edge

## 常见失败模式

### "找不到音频设备"

安装 `portaudio`。

### "机器人加入了但听不到声音"

检查：
- 你的Discord用户ID是否在 `DISCORD_ALLOWED_USERS` 中
- 你是否没有静音
- 特权意图是否已启用
- 机器人是否拥有连接/说话权限

### "它转录了但不说话"

检查：
- TTS提供商配置
- ElevenLabs或OpenAI的API密钥/配额
- 用于Edge转换路径的 `ffmpeg` 安装

### "Whisper输出乱码"

尝试：
- 更安静的环境
- 更高的 `silence_threshold`
- 不同的STT提供商/模型
- 更短、更清晰的语句

### "它在私信中正常，但在服务器频道中不行"

这通常是提及策略的问题。

默认情况下，除非另行配置，机器人在Discord服务器文本频道中需要 `@提及`。

## 建议的首周设置

如果你想要最短的成功路径：

1. 让文本模式Hermes工作
2. 安装 `hermes-agent[voice]`
3. 使用本地STT + Edge TTS 的CLI语音模式
4. 然后在Telegram或Discord中启用 `/voice on`
5. 只有在那之后，再尝试Discord语音频道模式

这种渐进方式能保持调试范围很小。

## 接下来阅读什么

- [语音模式功能参考文档](/user-guide/features/voice-mode)
- [消息网关](/user-guide/messaging)
- [Discord 设置](/user-guide/messaging/discord)
- [Telegram 设置](/user-guide/messaging/telegram)
- [配置](/user-guide/configuration)