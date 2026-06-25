--- frontmatter ---
---
title: "Heartmula — HeartMuLa：类似Suno的从歌词+标签生成歌曲"
sidebar_label: "Heartmula"
description: "HeartMuLa：类似Suno的从歌词+标签生成歌曲"
---

--- body ---
{/* 此页面由网站的scripts/generate-skill-docs.py根据技能的SKILL.md自动生成。请编辑源文件SKILL.md，而非此页面。 */}

# Heartmula

HeartMuLa：类似Suno的从歌词+标签生成歌曲。

## 技能（Skill）元数据

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/media/heartmula` |
| 版本 | `1.0.0` |
| 平台 | linux, macos, windows |
| 标签（Tags） | `music`, `audio`, `generation`, `ai`, `heartmula`, `heartcodec`, `lyrics`, `songs` |
| 相关技能 | `audiocraft` |

## 参考：完整SKILL.md

:::info
以下是Hermes在触发此技能时加载的完整技能定义。这是技能激活时代理（Agent）看到的指令。
:::

# HeartMuLa - 开源音乐生成

## 概述
HeartMuLa是一系列开源音乐基础模型（Apache-2.0），可根据歌词和标签生成音乐，支持多语言。从歌词+标签生成完整歌曲。可比拟开源版的Suno。包括：
- **HeartMuLa** - 音乐语言模型（3B/7B），用于从歌词+标签生成
- **HeartCodec** - 12.5Hz音乐编解码器，用于高保真音频重建
- **HeartTranscriptor** - 基于Whisper的歌词转录
- **HeartCLAP** - 音频-文本对齐模型

## 何时使用
- 用户想从文本描述生成音乐/歌曲
- 用户想要开源的Suno替代品
- 用户想要本地/离线音乐生成
- 用户询问HeartMuLa、heartlib或AI音乐生成

## 硬件要求
- **最低**：8GB显存，使用 `--lazy_load true`（按顺序加载/卸载模型）
- **推荐**：16GB+显存，适合舒适的单GPU使用
- **多GPU**：使用 `--mula_device cuda:0 --codec_device cuda:1` 跨GPU拆分
- 3B模型启用lazy_load时峰值显存约6.2GB

## 安装步骤

### 1. 克隆仓库
```bash
cd ~/  # 或所需目录
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
```

### 2. 创建虚拟环境（需要Python 3.10）
```bash
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
```

### 3. 修复依赖兼容性问题

**重要**：截至2026年2月，固定依赖与较新包存在冲突。应用以下修复：

```bash
# 升级datasets（旧版本与当前pyarrow不兼容）
uv pip install --upgrade datasets

# 升级transformers（需要与huggingface-hub 1.x兼容）
uv pip install --upgrade transformers
```

### 4. 修补源代码（transformers 5.x需要）

**补丁1 - RoPE缓存修复** 在 `src/heartlib/heartmula/modeling_heartmula.py` 中：

在 `HeartMuLa` 类的 `setup_caches` 方法中，在 `reset_caches` 的try/except块之后、`with device:` 块之前，添加RoPE重新初始化：

```python
# 重新初始化在元设备加载期间跳过的RoPE缓存
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**原因**：`from_pretrained` 首先在元设备上创建模型；`Llama3ScaledRoPE.rope_init()` 在元张量上跳过缓存构建，之后权重加载到真实设备后从未重建。

**补丁2 - HeartCodec加载修复** 在 `src/heartlib/pipelines/music_generation.py` 中：

在所有 `HeartCodec.from_pretrained()` 调用中添加 `ignore_mismatched_sizes=True`（共有2处：`__init__`中的立即加载和`codec`属性中的延迟加载）。

**原因**：VQ码本 `initted` 缓冲区在检查点中形状为 `[1]`，而在模型中为 `[]`。数据相同，只是标量与0维张量之差。忽略安全。

### 5. 下载模型检查点
```bash
cd heartlib  # 项目根目录
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

三个下载可并行进行。总大小数GB。

## GPU / CUDA

HeartMuLa默认使用CUDA（`--mula_device cuda --codec_device cuda`）。如果用户拥有已安装PyTorch CUDA支持的NVIDIA GPU，则无需额外设置。

- 安装的 `torch==2.4.1` 自带CUDA 12.1支持
- `torchtune` 可能报告版本 `0.4.0+cpu` —— 这只是包元数据，它仍然通过PyTorch使用CUDA
- 要验证是否使用了GPU，请查看输出中的"CUDA memory"行（例如"CUDA memory before unloading: 6.20 GB"）
- **没有GPU？** 可以使用 `--mula_device cpu --codec_device cpu` 在CPU上运行，但生成速度会**极其缓慢**（单个歌曲可能需要30-60分钟以上，而GPU大约4分钟）。CPU模式也需要大量RAM（约12GB+空闲）。如果用户没有NVIDIA GPU，建议使用云GPU服务（Google Colab免费版T4、Lambda Labs等）或在线演示 https://heartmula.github.io/。

## 使用方法

### 基本生成
```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### 输入格式

**标签**（逗号分隔，无空格）：
```
piano,happy,wedding,synthesizer,romantic
```
或
```
rock,energetic,guitar,drums,male-vocal
```

**歌词**（使用方括号结构标签）：
```
[Intro]

[Verse]
您的歌词在此...

[Chorus]
副歌歌词...

[Bridge]
桥段歌词...

[Outro]
```

### 关键参数
| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | 最大时长（毫秒，240秒=4分钟） |
| `--topk` | 50 | Top-k采样 |
| `--temperature` | 1.0 | 采样温度 |
| `--cfg_scale` | 1.5 | 无分类器引导尺度 |
| `--lazy_load` | false | 按需加载/卸载模型（节省显存） |
| `--mula_dtype` | bfloat16 | HeartMuLa的数据类型（推荐bf16） |
| `--codec_dtype` | float32 | HeartCodec的数据类型（推荐fp32以保证质量） |

### 性能
- RTF（实时因子）≈ 1.0 — 生成一首4分钟的歌曲大约需要4分钟
- 输出：MP3，48kHz立体声，128kbps

## 陷阱
1. **不要对HeartCodec使用bf16** — 会降低音频质量。使用fp32（默认）。
2. **标签可能被忽略** — 已知问题（#90）。歌词占主导；可以尝试调整标签顺序。
3. **macOS不支持Triton** — GPU加速仅限Linux/CUDA。
4. **RTX 5080不兼容** — 上游问题中有报告。
5. 依赖锁定冲突需要上述手动升级和补丁。

## 链接
- 仓库：https://github.com/HeartMuLa/heartlib
- 模型：https://huggingface.co/HeartMuLa
- 论文：https://arxiv.org/abs/2601.10547
- 许可：Apache-2.0