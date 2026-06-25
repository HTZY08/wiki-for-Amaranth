## 配置参考

### config.yaml

```yaml
# 语音录制 (CLI)
voice:
  record_key: "ctrl+b"            # 开始/停止录制的按键
  max_recording_seconds: 120       # 最大录制时长
  auto_tts: false                  # 语音模式启动时自动启用 TTS
  beep_enabled: true               # 播放录制开始/停止提示音
  silence_threshold: 200           # RMS 电平 (0-32767)，低于此值视为静音
  silence_duration: 3.0            # 自动停止前的静音秒数

# 语音转文字
stt:
  enabled: true                     # 设为 false 可跳过自动转录 —
                                    # 网关仍会缓存音频文件，并将其路径作为入站消息的一部分传递给代理（Agent），
                                    # 适用于自定义流水线（说话人分离、对齐、存档等）
  provider: "local"                  # "local" (免费) | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # 旧版：当未设置 provider 时使用

# 文字转语音
tts:
  provider: "edge"                 # "edge" (免费) | "elevenlabs" | "openai" | "neutts" | "minimax" | "mistral" | "gemini" | "xai" | "kittentts" | "piper"
  edge:
    voice: "en-US-AriaNeural"      # 322 种语音，74 种语言
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"    # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"                 # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 可选：覆盖用于自托管或 OpenAI 兼容端点
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### 环境变量

```bash
# 语音转文字提供商（本地无需密钥）
# pip install faster-whisper        # 免费本地 STT — 无需 API 密钥
GROQ_API_KEY=...                    # Groq Whisper（快速，免费额度）
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper（付费）

# STT 高级覆盖（可选）
STT_GROQ_MODEL=whisper-large-v3-turbo    # 覆盖默认 Groq STT 模型
STT_OPENAI_MODEL=whisper-1               # 覆盖默认 OpenAI STT 模型
GROQ_BASE_URL=https://api.groq.com/openai/v1     # 自定义 Groq 端点
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # 自定义 OpenAI STT 端点

# 文字转语音提供商（Edge TTS 和 NeuTTS 无需密钥）
ELEVENLABS_API_KEY=***             # ElevenLabs（优质质量）
# 上述 VOICE_TOOLS_OPENAI_KEY 也可启用 OpenAI TTS

# Discord 语音频道
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```

### STT 提供商对比

| 提供商（Provider） | 模型（Model） | 速度（Speed） | 质量（Quality） | 成本（Cost） | API 密钥（API Key） |
|----------|-------|-------|---------|------|---------|
| **本地（Local）** | `base` | 快（取决于 CPU/GPU） | 良好 | 免费 | 否 |
| **本地（Local）** | `small` | 中等 | 更佳 | 免费 | 否 |
| **本地（Local）** | `large-v3` | 慢 | 最佳 | 免费 | 否 |
| **Groq** | `whisper-large-v3-turbo` | 非常快（约0.5秒） | 良好 | 免费额度 | 是 |
| **Groq** | `whisper-large-v3` | 快（约1秒） | 更佳 | 免费额度 | 是 |
| **OpenAI** | `whisper-1` | 快（约1秒） | 良好 | 付费 | 是 |
| **OpenAI** | `gpt-4o-transcribe` | 中等（约2秒） | 最佳 | 付费 | 是 |
| **Mistral** | `voxtral-mini-latest` | 快 | 良好 | 付费 | 是 |
| **xAI** | `grok-stt` | 快 | 良好 | 付费 | 是 |

提供商优先级（自动回退）：**本地（local）** > **groq** > **openai**

### TTS 提供商对比

| 提供商（Provider） | 质量（Quality） | 成本（Cost） | 延迟（Latency） | 需密钥（Key Required） |
|----------|---------|------|---------|-------------|
| **Edge TTS** | 良好 | 免费 | 约1秒 | 否 |
| **ElevenLabs** | 优秀 | 付费 | 约2秒 | 是 |
| **OpenAI TTS** | 良好 | 付费 | 约1.5秒 | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于 CPU/GPU | 否 |

NeuTTS 使用上方 `tts.neutts` 配置块。

---

## 故障排除

### "未找到音频设备" (CLI)

PortAudio 未安装：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

如果在 Linux 桌面上的 Docker 内运行 Hermes，容器也需要访问主机音频套接字。请参阅 [Docker 音频桥](/user-guide/docker#optional-linux-desktop-audio-bridge) 说明以获取兼容 PulseAudio/PipeWire 的配置。

### 机器人在 Discord 服务器频道中无响应

默认情况下，机器人在服务器频道中需要 @提及。请确保：

1. 输入 `@` 并选择 **机器人用户**（带 #discriminator），而不是同名 **角色**
2. 或改用私信 — 无需提及
3. 或在 `~/.hermes/.env` 中设置 `DISCORD_REQUIRE_MENTION=false`

### 机器人加入语音频道但听不到我说话

- 检查您的 Discord 用户 ID 是否在 `DISCORD_ALLOWED_USERS` 中
- 确保您在 Discord 中没有静音
- 机器人需要从 Discord 收到 SPEAKING 事件才能映射您的音频 — 请在加入后几秒钟内开始说话

### 机器人听到我说话但无响应

- 确认 STT 可用：安装 `faster-whisper`（无需密钥）或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查 LLM 模型是否已配置并可访问
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

### 机器人以文本回复但在语音频道中无声

- TTS 提供商可能失败 — 检查 API 密钥和配额
- Edge TTS（免费，无需密钥）是默认回退方案
- 检查日志中的 TTS 错误

### Whisper 返回乱码文本

幻觉过滤器（hallucination filter）会自动捕获大多数情况。如果仍然出现虚假转录：

- 使用更安静的环境
- 调整配置中的 `silence_threshold`（数值越高 = 灵敏度越低）
- 尝试不同的 STT 模型