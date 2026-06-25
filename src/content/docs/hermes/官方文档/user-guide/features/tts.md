---
title: Tts
---

sidebar_position: 9
title: "语音与TTS"
description: "跨所有平台的文本转语音和语音消息转录"
---

--- body ---
# 语音与TTS

Hermes 代理（Agent）支持在所有消息平台上进行文本转语音输出和语音消息转录。

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅，可通过 **[工具网关（Tool Gateway）](tool-gateway.md)** 使用 OpenAI TTS，无需单独的 OpenAI API 密钥。新安装可通过 `hermes setup --portal` 登录并一次性启用所有网关工具；现有安装可通过 `hermes model` 或 `hermes tools` 选择 **Nous Subscription** 仅用于 TTS。
:::

## 文本转语音 (Text-to-Speech)

通过十个提供商（Provider）将文本转换为语音：

| 提供商 | 质量 | 费用 | API 密钥 |
|--------|------|------|----------|
| **Edge TTS** (默认) | 良好 | 免费 | 无需 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **Mistral (Voxtral TTS)** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费额度 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 (本地) | 无需 |
| **KittenTTS** | 良好 | 免费 (本地) | 无需 |
| **Piper** | 良好 | 免费 (本地) | 无需 |

### 平台投递 (Platform Delivery)

| 平台 | 投递方式 | 格式 |
|------|----------|------|
| Telegram | 语音气泡（内联播放） | Opus `.ogg` |
| Discord | 语音气泡（Opus/OGG），回退为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` | MP3 |

### 配置

```yaml
# In ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper"
  speed: 1.0                    # 全局速度倍率（提供商特定设置会覆盖此值）
  edge:
    voice: "en-US-AriaNeural"   # 322 种声音，74 种语言
    speed: 1.0                  # 转换为速率百分比 (+/-%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # 覆盖 OpenAI 兼容 TTS 端点
    speed: 1.0                  # 0.25 - 4.0
  minimax:
    model: "speech-2.8-hd"     # speech-2.8-hd (默认), speech-2.8-turbo
    voice_id: "English_Graceful_Lady"  # 参见 https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - 中性（默认）
  gemini:
    model: "gemini-2.5-flash-preview-tts"  # 或 gemini-3.1-flash-tts-preview
    voice: "Kore"               # 30 个预置声音：Zephyr, Puck, Kore, Enceladus, Gacrux 等
    audio_tags: false           # 启用隐藏的 Gemini 3.1 TTS 音频标签插入
    persona_prompt_file: ""      # 可选的 Markdown/文本文件，用于描述 Gemini 声音角色
  xai:
    voice_id: "eve"             # 或自定义声音 ID — 参见下文文档
    language: "en"              # ISO 639-1 代码
    sample_rate: 24000          # 22050 / 24000 (默认) / 44100 / 48000
    bit_rate: 128000            # MP3 比特率；仅适用于 codec=mp3
    # base_url: "https://api.x.ai/v1"   # 通过 XAI_BASE_URL 环境变量覆盖
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
  kittentts:
    model: KittenML/kitten-tts-nano-0.8-int8   # 25MB int8；另有：kitten-tts-micro-0.8 (41MB), kitten-tts-mini-0.8 (80MB)
    voice: Jasper                               # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
    speed: 1.0                                  # 0.5 - 2.0
    clean_text: true                            # 扩展数字、货币、单位
  piper:
    voice: en_US-lessac-medium                  # 声音名称（自动下载）或 .onnx 的绝对路径
    # voices_dir: ''                            # 默认: ~/.hermes/cache/piper-voices/
    # use_cuda: false                           # 需要 onnxruntime-gpu
    # length_scale: 1.0                         # 2.0 = 慢两倍
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = 音量减半
    # normalize_audio: true
```

**速度控制**：全局 `tts.speed` 值默认应用于所有提供商。每个提供商可以通过自己的 `speed` 设置覆盖该值（例如 `tts.openai.speed: 1.5`）。提供商特定的速度优先级高于全局值。默认值为 `1.0`（正常速度）。

### Gemini 角色提示 (Persona Prompts)

Gemini TTS 可以遵循自然语言的表演指示。将 `tts.gemini.persona_prompt_file` 设置为描述声音角色的本地 Markdown 或文本文件。该文件可以包含 Gemini 风格的章节，例如 `AUDIO PROFILE`、`SCENE`、`DIRECTOR'S NOTES`、`SAMPLE CONTEXT`和`TRANSCRIPT`。

如果文件包含 `{transcript}` 或 `{{ transcript }}`，Hermes 会将该占位符替换为实时 TTS 文本。否则，Hermes 会自动追加一个带标签的 `TRANSCRIPT` 章节。角色提示保留在本地，不会显示在聊天回复中。

```yaml
tts:
  provider: gemini
  gemini:
    voice: Algieba
    persona_prompt_file: ~/.hermes/tts/butler-voice.md
```

### Gemini 音频标签 (Audio Tags)

Gemini 3.1 Flash TTS 支持自由形式的方括号音频标签，例如 `[whispers]`、`[excitedly]`、`[very slow]`、`[laughs]` 以及其他表达性交付注释。启用 `tts.gemini.audio_tags` 后，Hermes 会在 Gemini TTS 之前运行一个隐藏的重写过程。重写仅在 TTS 脚本中插入内联标签；可见的聊天回复保持不变。

```yaml
tts:
  provider: gemini
  gemini:
    model: gemini-3.1-flash-tts-preview
    audio_tags: true
```

重写使用 `auxiliary.tts_audio_tags`，默认使用您的主聊天模型。如果您希望由更便宜或更快的模型处理标签插入，可以覆盖该辅助任务。

### 输入长度限制

每个提供商都有记录的每次请求输入字符上限。Hermes 在调用提供商之前会截断文本，以确保请求不会因长度错误而失败：

| 提供商 | 默认上限 (字符数) |
|--------|-------------------|
| Edge TTS | 5000 |
| OpenAI | 4096 |
| xAI | 15000 |
| MiniMax | 10000 |
| Mistral | 4000 |
| Google Gemini | 32000 |
| ElevenLabs | 模型感知 (见下文) |
| NeuTTS | 2000 |
| KittenTTS | 2000 |
| Piper | 5000 |

**ElevenLabs** 从配置的 `model_id` 中选择上限：

| `model_id` | 上限 (字符数) |
|------------|---------------|
| `eleven_flash_v2_5` | 40000 |
| `eleven_flash_v2` | 30000 |
| `eleven_multilingual_v2` (默认), `eleven_multilingual_v1`, `eleven_english_sts_v2`, `eleven_english_sts_v1` | 10000 |
| `eleven_v3`, `eleven_ttv_v3` | 5000 |
| 未知模型 | 回退到提供商默认 (10000) |

**每个提供商可通过** `max_text_length:` 在 TTS 配置的提供商部分下覆盖：

```yaml
tts:
  openai:
    max_text_length: 8192   # 提高或降低提供商上限
```

仅接受正整数。零、负数、非数字或布尔值将回退到提供商默认值，因此错误的配置不会意外禁用截断。

### Telegram 语音气泡与 ffmpeg

Telegram 语音气泡需要 Opus/OGG 音频格式：

- **OpenAI、ElevenLabs 和 Mistral** 原生输出 Opus — 无需额外设置
- **Edge TTS**（默认）输出 MP3，需要 **ffmpeg** 进行转换
- **MiniMax TTS** 输出 MP3，需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **Google Gemini TTS** 输出原始 PCM，并使用 **ffmpeg** 直接编码为 Opus 用于 Telegram 语音气泡
- **xAI TTS** 输出 MP3，需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **NeuTTS** 输出 WAV，也需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **KittenTTS** 输出 WAV，也需要 **ffmpeg** 转换以用于 Telegram 语音气泡
- **Piper** 输出 WAV，也需要 **ffmpeg** 转换以用于 Telegram 语音气泡

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

没有 ffmpeg 时，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 和 Piper 的音频将作为普通音频文件发送（可播放，但显示为矩形播放器而不是语音气泡）。

:::tip
如果您希望在不安装 ffmpeg 的情况下获得语音气泡，请切换到 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

### xAI 自定义声音（声音克隆）

xAI 支持克隆您的声音并将其用于 TTS。在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义声音，然后将生成的 `voice_id` 设置到您的配置中：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # 您的自定义声音 ID
```

有关录音、支持的格式和限制的详细信息，请参阅 [xAI 自定义声音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper (本地, 44种语言)

Piper 是 Open Home Foundation（Home Assistant 维护者）开发的一款快速、本地的神经 TTS 引擎。它完全在 CPU 上运行，支持 **44 种语言**，带有预训练声音，无需 API 密钥。

**通过 `hermes tools` 安装** → 语音与 TTS → Piper — Hermes 会为您运行 `pip install piper-tts`。或手动安装：`pip install piper-tts`。

**切换到 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

首次调用本地未缓存的声音时，Hermes 会运行 `python -m piper.download_voices <name>` 并将模型（约 20-90MB，取决于质量等级）下载到 `~/.hermes/cache/piper-voices/`。后续调用会重用缓存的模型。

**选择声音。**[完整声音目录](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md) 涵盖英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等 — 每种都有 `x_low` / `low` / `medium` / `high` 质量等级。在 [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/) 试听示例声音。

**使用预下载的声音。** 将 `tts.piper.voice` 设置为以 `.onnx` 结尾的绝对路径：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级旋钮** (`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`、`use_cuda`) 与 Piper 的 `SynthesisConfig` 一一对应。它们会被较旧的 `piper-tts` 版本忽略。

### 自定义命令提供商 (Custom command providers)

如果您想要的 TTS 引擎不受原生支持（VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本等任何暴露 CLI 的工具），您可以将其作为**命令类型提供商**接入，无需编写任何 Python 代码。Hermes 将输入文本写入一个临时 UTF-8 文件，运行您的 shell 命令，然后读取命令生成的音频文件。

在 `tts.providers.<name>` 下声明一个或多个提供商，并通过 `tts.provider: <name>` 在它们之间切换 — 就像在内置提供商（如 `edge` 和 `openai`）之间切换一样。

```yaml
tts:
  provider: voxcpm                 # 在 tts.providers 下选择任意名称
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      timeout: 180
      voice_compatible: true       # 尝试以 Telegram 语音气泡形式投递

    mlx-kokoro:
      type: command
      command: "python -m mlx_kokoro --in {input_path} --out {output_path} --voice {voice}"
      voice: af_sky
      output_format: wav

    piper-custom:                  # 原生 Piper 也支持通过 tts.piper.voice 使用自定义 .onnx
      type: command
      command: "piper -m /path/to/custom.onnx -f {output_path} < {input_path}"
      output_format: wav
```

#### 示例：豆包 (Chinese seed-tts-2.0)

对于通过字节跳动 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流 API 实现的高质量中文 TTS，安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) PyPI 包并将其作为命令提供商接入：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
```

```yaml
tts:
  provider: doubao
  providers:
    doubao:
      type: command
      command: "doubao-speech say --text-file {input_path} --out {output_path}"
      output_format: mp3
      max_text_length: 1024
      timeout: 30
```

凭据来自您的 shell 环境 (`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`) 或 `~/.doubao-speech/config.yaml`。通过向命令添加 `--voice zh-female-warm`（或 `doubao-speech list-voices` 中的任何其他别名）来选择声音。`doubao-speech` 还捆绑了流式 ASR — 有关 Hermes 集成，请参见下面的 [STT 部分](#example-doubao--volcengine-asr)。源代码和完整文档：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

#### 占位符

您的命令模板可以引用这些占位符。Hermes 在渲染时替换它们，并根据周围上下文（裸、单引号、双引号）对每个值进行 shell 引用，因此包含空格和其他 shell 敏感字符的路径是安全的。

| 占位符          | 含义                                                |
|----------------|------------------------------------------------------|
| `{input_path}`   | Hermes 写入的临时 UTF-8 文本文件的路径                |
| `{text_path}`    | `{input_path}` 的别名                                 |
| `{output_path}`  | 命令必须写入音频的路径                                |
| `{format}`       | `mp3` / `wav` / `ogg` / `flac`                       |
| `{voice}`        | `tts.providers.<name>.voice`，未设置时为空            |
| `{model}`        | `tts.providers.<name>.model`                         |
| `{speed}`        | 解析后的速度倍率（提供商或全局）                      |

使用 `{{` 和 `}}` 表示字面花括号。

#### 可选键

| 键                | 默认   | 含义                                                                                                    |
|-------------------|---------|------------------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 秒；超时后杀死进程树（Unix `killpg`，Windows `taskkill /T`）。                                             |
| `output_format`    | `mp3`   | 可选 `mp3` / `wav` / `ogg` / `flac`。如果 Hermes 选择路径，会从输出扩展名自动推断。                        |
| `voice_compatible` | `false` | 当为 `true` 时，Hermes 通过 ffmpeg 将 MP3/WAV 输出转换为 Opus/OGG，以便 Telegram 显示语音气泡。            |
| `max_text_length`  | `5000`  | 在渲染命令之前，输入文本会被截断到此长度。                                                                  |
| `voice` / `model`  | 空      | 仅作为占位符值传递给命令。                                                                                 |

#### 行为说明

- **内置名称始终优先。** `tts.providers.openai` 条目永远不会掩盖原生的 OpenAI 提供商，因此任何用户配置都不能静默替换内置提供商。
- **默认投递为文档。** 命令提供商在每个平台上都作为常规音频附件投递。通过 `voice_compatible: true` 选择每个提供商的语音气泡投递。
- **命令失败会反馈给代理。** 非零退出码、空输出或超时都会返回错误，并包含命令的 stderr/stdout，以便您从对话中调试提供商。
- **当设置了 `command:` 时，`type: command` 是默认值。** 显式写 `type: command` 是好习惯，但不是必需的；带有非空 `command` 字符串的条目被视为命令提供商。
- **`{input_path}` / `{text_path}` 可互换。** 使用在命令中更易读的一个。

#### 安全性

命令类型提供商以您的用户权限运行您配置的任何 shell 命令。Hermes 引用占位符值并强制执行配置的超时，但命令模板本身是受信任的本地输入 — 请像对待 PATH 上的 shell 脚本一样对待它。

### Python 插件提供商 (TTS)

对于无法表示为单个 shell 命令的 TTS 引擎 — 没有 CLI 的 Python SDK、流式引擎、声音列表 API、需要 OAuth 刷新的认证 — 通过 `ctx.register_tts_provider()` 注册一个 Python 插件。该插件与 [自定义命令提供商](#custom-command-providers) 注册表**共存**（不替换）；选择适合您引擎的接口。

#### 何时选择哪种

| 您的后端有…                                                         | 使用方法 |
|-------------------------------------------------------------------|---------|
| 单个 CLI，从文件/stdin 读取文本并将音频写入文件/stdout               | **命令提供商**（无需 Python） |
| 两个或三个 CLI 通过 shell 管道链接                                  | **命令提供商** |
| 仅有 Python SDK — 没有 CLI                                         | **插件** |
| 流式字节，希望分块投递（生成中语音气泡）                          | **插件**（覆盖 `stream()`） |
| 被 `hermes setup` 使用的声音列表 API                               | **插件**（覆盖 `list_voices()`） |
| OAuth 刷新流程（非静态 bearer token）                              | **插件** |

内置始终优先，命令提供商优于同名插件 — 因此针对任何非内置名称注册插件都是安全的，无需担心隐藏现有配置。

#### 最小插件

将此文件放到 `~/.hermes/plugins/my-tts/` 中：

`plugin.yaml`:
```yaml
name: my-tts
version: 0.1.0
description: "我的自定义 Python TTS 后端"
```

`__init__.py`:
```python
from agent.tts_provider import TTSProvider


class MyTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "my-tts"  # 与 tts.provider 匹配的名称

    @property
    def display_name(self) -> str:
        return "我的自定义 TTS"

    def is_available(self) -> bool:
        # 当缺少凭据/依赖时返回 False — 选择器会跳过此行，
        # 但调度器在显式配置时仍会路由到这里。
        import os
        return bool(os.environ.get("MY_TTS_API_KEY"))

    def synthesize(self, text, output_path, *, voice=None, model=None,
                   speed=None, format="mp3", **extra) -> str:
        # 将音频字节写入 output_path，返回该路径。
        # 失败时引发异常 — 调度器将异常转换为标准错误包。
        import my_tts_sdk
        client = my_tts_sdk.Client()
        audio_bytes = client.synthesize(text=text, voice=voice or "default")
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path


def register(ctx):
    ctx.register_tts_provider(MyTTSProvider())
```

启用它（`hermes plugins enable my-tts`），在 `config.yaml` 中将 `tts.provider` 指向它（`tts.provider: my-tts`），然后 `text_to_speech` 工具将通过您的插件路由。

#### 可选钩子

在您的提供商类上覆盖这些方法以获得更丰富的集成：

- `list_voices()` → 返回 `{id, display, language, gender, preview_url}` 字典列表，显示在 `hermes tools` 中。
- `list_models()` → 返回 `{id, display, languages, max_text_length}` 字典列表。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}`，为 `hermes tools` / `hermes setup` 中的选择器行提供支持。缺少此方法时，插件仍可工作，但选择器中的行信息较少。
- `stream(text, *, voice, model, format, **extra)` → 产生音频字节的迭代器，用于流式投递（默认引发 `NotImplementedError`）。
- `voice_compatible` 属性 → 如果输出与 Opus 兼容，设置为 `True`，网关应将其作为语音气泡投递（默认 `False` = 常规音频附件）。

请参阅 `agent/tts_provider.py` 获取完整的抽象基类，包括文档字符串。

## 语音消息转录 (STT)

在 Telegram、Discord、WhatsApp、Slack 或 Signal 上发送的语音消息会自动转录并作为文本注入到对话中。代理会将转录文本视为普通文本。

| 提供商 | 质量 | 费用 | API 密钥 |
|--------|------|------|---------| 
| **本地 Whisper** (默认) | 良好 | 免费 | 无需 |
| **Groq Whisper API** | 良好–最佳 | 免费额度 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 良好–最佳 | 付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 零配置
当安装了 `faster-whisper` 时，本地转录开箱即用。如果不可用，Hermes 也可以使用来自常见安装位置（如 `/opt/homebrew/bin`）的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 使用自定义命令。
:::

### 配置

```yaml
# In ~/.hermes/config.yaml
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
  xai:
    model: "grok-stt"         # xAI Grok STT
```

### 提供商详情

**本地 (faster-whisper)** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper。默认使用 CPU，如果可用则使用 GPU。模型大小：

| 模型 | 大小 | 速度 | 质量 |
|------|------|------|------|
| `tiny` | ~75 MB | 最快 | 基础 |
| `base` | ~150 MB | 快 | 良好（默认）|
| `small` | ~500 MB | 中等 | 较好 |
| `medium` | ~1.5 GB | 较慢 | 优秀 |
| `large-v3` | ~3 GB | 最慢 | 最佳 |

**Groq API** — 需要 `GROQ_API_KEY`。当您希望使用免费托管的 STT 选项时，这是一个很好的云回退方案。

**OpenAI API** — 首选 `VOICE_TOOLS_OPENAI_KEY`，然后回退到 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe`。

**Mistral API (Voxtral Transcribe)** — 需要 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型。支持 13 种语言、说话人分离和单词级时间戳。安装方式：`cd ~/.hermes/hermes-agent && uv pip install -e ".[mistral]"`。

**xAI Grok STT** — 需要 `XAI_API_KEY`。以 multipart/form-data 形式发送到 `https://api.x.ai/v1/stt`。如果您已经在使用 xAI 进行聊天或 TTS 并希望所有功能使用一个 API 密钥，这是一个不错的选择。自动检测顺序将其放在 Groq 之后 — 显式设置 `stt.provider: xai` 以强制使用。

**自定义本地 CLI 回退** — 如果您希望 Hermes 直接调用本地转录命令，请设置 `HERMES_LOCAL_STT_COMMAND`。命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 占位符。您的命令必须在 `{output_dir}` 下的某处写入一个 `.txt` 转录文件。

#### 示例：豆包 / 火山引擎 ASR

如果您使用 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 进行豆包 TTS（参见上面的 [示例](#example-doubao-chinese-seed-tts-20)），同一包通过本地命令 STT 接口处理语音转文本：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
export HERMES_LOCAL_STT_COMMAND='doubao-speech transcribe {input_path} --out {output_dir}/transcript.txt'
```

```yaml
stt:
  provider: local_command
```

Hermes 将传入的语音消息写入 `{input_path}`，运行命令，并读取在 `{output_dir}` 下生成的 `.txt` 文件。语言由火山引擎大模型端点自动检测。

### 回退行为

如果配置的提供商不可用，Hermes 会自动回退：
- **本地 faster-whisper 不可用** → 尝试本地 `whisper` CLI 或 `HERMES_LOCAL_STT_COMMAND`，然后才尝试云提供商
- **未设置 Groq 密钥** → 回退到本地转录，然后 OpenAI
- **未设置 OpenAI 密钥** → 回退到本地转录，然后 Groq
- **未设置 Mistral 密钥/SDK** → 在自动检测中跳过；回退到下一个可用提供商
- **无可用提供商** → 语音消息会通过，并附带一条准确的注释给用户

### STT 自定义命令提供商

如果您想要的 STT 引擎不受原生支持（豆包 ASR、NVIDIA Parakeet、whisper.cpp 构建、开源 SenseVoice CLI 等任何暴露 shell 命令的工具），您可以将其作为**命令类型提供商**接入，无需编写任何 Python 代码。Hermes 对音频文件运行您的 shell 命令并读取转录结果。

在 `stt.providers.<name>` 下声明一个或多个提供商，并通过 `stt.provider: <name>` 在它们之间切换 — 模式与 TTS [命令提供商注册表](#custom-command-providers) 相同，但方向为输入=音频 → 输出=转录。

```yaml
stt:
  provider: parakeet                # 在 stt.providers 下选择任意名称
  providers:
    parakeet:
      type: command
      command: "parakeet-asr --model nvidia/parakeet-tdt-0.6b-v2 --in {input_path} --out {output_path}"
      format: txt
      language: en
      timeout: 300

    whispercpp:
      type: command
      command: "whisper-cli -m ~/models/ggml-large-v3.bin -f {input_path} -otxt -of {output_dir}/transcript"
      format: txt

    sensevoice:
      type: command
      command: "sensevoice-cli {input_path} --json | tee {output_path}"
      format: json
```

这补充了传统的 `HERMES_LOCAL_STT_COMMAND` 逃生口 — 该环境变量仍可通过内置的 `local_command` 路径原样工作。当您需要**多个** shell 驱动的 STT 引擎、可通过 `stt.provider` 选择的名称或任何需要每个提供商 `language` / `model` / `timeout` 的功能时，请使用 `stt.providers.<name>`。

#### STT 占位符

您的命令模板可以引用这些占位符。Hermes 在渲染时替换它们，并根据周围上下文（裸、单引号、双引号）对每个值进行 shell 引用，因此包含空格的路径是安全的。

| 占位符        | 含义                                                                |
|---------------|----------------------------------------------------------------------|
| `{input_path}`    | 输入音频文件的绝对路径（原始位置，只读）                               |
| `{output_path}`   | 命令应将转录写入的绝对路径                                             |
| `{output_dir}`    | `{output_path}` 的父目录（对 whisper 风格的工具有用）                |
| `{format}`        | 配置的输出格式：`txt` / `json` / `srt` / `vtt`                       |
| `{language}`      | 配置的语言代码（默认为 `en`）                                          |
| `{model}`         | `stt.providers.<name>.model`，未设置时为空                           |

使用 `{{` 和 `}}` 表示字面花括号（在命令中嵌入 JSON 片段时很有用）。

#### 如何读取转录结果

在命令成功退出后：

1. 如果 `{output_path}` 存在且非空 → Hermes 将其作为 UTF-8 文本读取。
2. 否则，如果命令写入 stdout → Hermes 使用 stdout。
3. 否则 → 错误：“命令 STT 提供商未写入输出文件且未产生 stdout”。

这使得注册表既适用于写入文件的 CLI（`whisper-cli`、`parakeet-asr`），也适用于将转录输出到 stdout 的 curl 风格单行命令（`curl … | jq -r .text`）。

对于 `format: json` / `srt` / `vtt`，Hermes 返回原始文件内容作为 `transcript` 字段。从 JSON 中提取 `.text` 超出了运行器的范围 — 要么配置 `format: txt`，要么在下游后处理 JSON。

#### STT 命令提供商可选键

| 键             | 默认   | 含义                                                                                              |
|----------------|---------|------------------------------------------------------------------------------------------------------|
| `timeout`       | `300`   | 秒；超时后杀死进程树（Unix `start_new_session`，Windows `taskkill /T`）。                           |
| `format`        | `txt`   | 可选 `txt` / `json` / `srt` / `vtt`。设置 `{output_path}` 的扩展名。                                |
| `language`      | `en`    | 转发到 `{language}`。默认回退到 `stt.language` 然后是 `en`。                                        |
| `model`         | 空      | 转发到 `{model}`。`transcribe_audio()` 的 `model=` 参数会覆盖此值。                                 |

#### STT 命令提供商行为说明

- **内置始终优先。** 声明 `stt.providers.openai: type: command` 不会覆盖真正的 OpenAI Whisper 处理器。内置名称在命令提供商解析器运行之前就被短路。
- **进程树清理。** 运行超过 `timeout` 的命令会杀死其整个进程树，而不仅仅是 shell 包装器。长时间运行的 ASR 管道（分叉模型加载子进程）会被可靠地回收。
- **Shell 引用是自动的。** 在 `'…'` 内部的占位符会进行单引号安全转义；在 `"…"` 内部的占位符会对 `$`/`` ` ``/`"` 进行转义；在引号外部的占位符使用 `shlex.quote`。不要预先引用占位符值。

#### STT 命令提供商安全性

Shell 命令以与 Hermes 相同的用户身份运行，具有完整的文件系统访问权限 — 与 `tts.providers.<name>: type: command` 和 `HERMES_LOCAL_STT_COMMAND` 相同的信任模型。只声明来自可信源的命令提供商。

### Python 插件提供商 (STT)

对于既不是内置的又无法表示为 shell 命令的 STT 引擎（需要 Python SDK、OAuth 刷新认证、流式块等），请通过 `ctx.register_transcription_provider()` 注册一个 Python 插件。该插件与 6 个内置提供商（`local`、`local_command`、`groq`、`openai`、`mistral`、`xai`）以及 `stt.providers.<name>: type: command` 注册表**共存** — 内置在名称冲突时始终保持其原生实现并获胜；命令提供商在名称相同时优于插件（配置比插件安装更本地化）。

#### 何时选择哪种 (STT)

| 后端有…                                                 | 使用方法                                                          |
|---------------------------------------------------------|-------------------------------------------------------------------|
| 单个 shell 命令，接收音频文件并输出文本                     | `stt.providers.<name>: type: command`（无需 Python）              |
| 仅需要传统的单命令逃生口                                   | `HERMES_LOCAL_STT_COMMAND` 环境变量（为向后兼容保留）             |
| 仅有 Python SDK，没有 CLI                                | `register_transcription_provider()` 插件                          |
| 需要 OAuth 刷新认证、流式块、声音列表元数据               | `register_transcription_provider()` 插件                          |
| 内置已覆盖（`local`、`groq`、`openai` 等）               | 设置 `stt.provider: <name>` — 内置是内联的                        |

#### 解析顺序

1. **`stt.provider` 是内置名称** → 内置调度。**始终优先。**
2. **`stt.provider` 匹配 `stt.providers.<name>` 且设置了 `command:`** → 命令提供商运行器（参见 [STT 自定义命令提供商](#stt-custom-command-providers)）。优于同名插件。
3. **`stt.provider` 匹配插件注册的 `TranscriptionProvider`** → 插件调度：
   - 如果插件的 `is_available()` 返回 `False`（缺少凭据或 SDK），调用会显示一个标识插件的不可用错误包 — **而不是**通用的“无 STT 提供商可用”消息。
   - 否则，插件的 `transcribe()` 会被调用，传入 `model`（来自公开的 `model=` 参数，回退到 `stt.<provider>.model`）和 `language`（来自 `stt.<provider>.language`）。
4. **无匹配** → “无 STT 提供商可用”错误。

#### 每个提供商的配置命名空间

插件从 `config.yaml` 中的 `stt.<provider>` 读取其每个提供商的配置，镜像内置如何读取 `stt.openai.model` / `stt.mistral.model`：

```yaml
stt:
  provider: my-stt
  my-stt:
    model: whisper-large-v3
    language: ja          # 作为 language= 转发到 transcribe()
    # 任何其他插件特定键可以放在这里；通过您自己的
    # config.yaml 访问在 __init__/is_available/transcribe 中读取它们
```

调度器从此部分转发 `model` 和 `language`；其他所有内容，插件可以自行读取。

#### 最小插件

将此文件放到 `~/.hermes/plugins/my-stt/` 中：

`plugin.yaml`:
```yaml
name: my-stt
version: 0.1.0
description: "我的自定义 Python STT 后端"
```

`__init__.py`:
```python
from agent.transcription_provider import TranscriptionProvider


class MySTTProvider(TranscriptionProvider):
    @property
    def name(self) -> str:
        return "my-stt"  # 与 stt.provider 匹配的名称

    @property
    def display_name(self) -> str:
        return "我的自定义 STT"

    def is_available(self) -> bool:
        # 当缺少凭据/依赖时返回 False — 选择器会跳过此行，
        # 但调度器在显式配置时仍会路由到这里。
        import os
        return bool(os.environ.get("MY_STT_API_KEY"))

    def transcribe(self, file_path, *, model=None, language=None, **extra):
        # 返回标准转录包：
        #   {"success": bool, "transcript": str, "provider": str, "error": str}
        # 不要引发异常 — 将异常转换为错误包，以便
        # 网关/CLI 调用者在失败时看到一致的形状。
        try:
            import my_stt_sdk
            client = my_stt_sdk.Client()
            text = client.transcribe(open(file_path, "rb"))
            return {
                "success": True,
                "transcript": text,
                "provider": "my-stt",
            }
        except Exception as exc:
            return {
                "success": False,
                "transcript": "",
                "error": f"my-stt 失败: {exc}",
                "provider": "my-stt",
            }


def register(ctx):
    ctx.register_transcription_provider(MySTTProvider())
```

启用它（`hermes plugins enable my-stt`），在 `config.yaml` 中设置 `stt.provider: my-stt`，语音消息转录将通过您的插件路由。

#### 可选钩子

在您的提供商类上覆盖这些方法以获得更丰富的集成：

- `list_models()` → 返回 `{id, display, languages, max_audio_seconds}` 字典列表。
- `default_model()` → 当用户未覆盖模型时返回的字符串。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}`，为 `hermes tools` / `hermes setup` 中的选择器行提供支持（STT 的选择器类别尚未发布 — 此元数据可用于插件的向前兼容性）。

请参阅 `agent/transcription_provider.py` 获取完整的抽象基类，包括文档字符串。