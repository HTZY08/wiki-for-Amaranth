--- frontmatter ---
---
title: "Nemo Curator — 用于LLM训练的GPU加速数据整理"
sidebar_label: "Nemo Curator"
description: "用于LLM训练的GPU加速数据整理"
---

--- body ---
{/* 此页面由网站/scripts/generate-skill-docs.py从技能的SKILL.md自动生成。请编辑源SKILL.md，而不是此页面。 */}

# Nemo Curator

用于LLM训练的GPU加速数据整理。支持文本/图像/视频/音频。具备模糊去重（速度提升16倍）、质量过滤（30多种启发式方法）、语义去重、PII脱敏、NSFW检测等功能。通过RAPIDS在GPU间扩展。适用于准备高质量训练数据集、清洗网络数据或对大型语料库进行去重。

## 技能元数据（Skill Metadata）

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/nemo-curator` 安装 |
| 路径 | `optional-skills/mlops/nemo-curator` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `nemo-curator`, `cudf`, `dask`, `rapids` |
| 平台 | linux, macos |
| 标签 | `数据处理`, `NeMo Curator`, `数据整理`, `GPU加速`, `去重`, `质量过滤`, `NVIDIA`, `RAPIDS`, `PII脱敏`, `多模态`, `LLM训练数据` |

## 参考：完整SKILL.md

:::info
以下是Hermes在该技能触发时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# NeMo Curator - 用于LLM训练的GPU加速数据整理（GPU-Accelerated Data Curation）

NVIDIA的工具包，用于为LLM准备高质量训练数据。

## 何时使用NeMo Curator

**在以下场景使用NeMo Curator：**
- 从网络爬取（如Common Crawl）准备LLM训练数据
- 需要快速去重（比CPU快16倍）
- 整理多模态数据集（文本、图像、视频、音频）
- 过滤低质量或有害内容
- 在GPU集群上扩展数据处理

**性能**：
- **16倍更快的**模糊去重（8TB RedPajama v2）
- **对比CPU方案降低40% TCO**
- **在GPU节点上近线性扩展**

**可考虑使用其他替代方案**：
- **datatrove**：基于CPU的开源数据处理
- **dolma**：Allen AI的数据工具包
- **Ray Data**：通用机器学习数据处理（无整理专注）

## 快速开始

### 安装

```bash
# 文本整理（CUDA 12）
uv pip install "nemo-curator[text_cuda12]"

# 所有模态
uv pip install "nemo-curator[all_cuda12]"

# 仅CPU（较慢）
uv pip install "nemo-curator[cpu]"
```

### 基本文本整理管道

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.datasets import DocumentDataset
import pandas as pd

# 加载数据
df = pd.DataFrame({"text": ["好文档", "差文档", "优秀文本"]})
dataset = DocumentDataset(df)

# 质量过滤
def quality_score(doc):
    return len(doc["text"].split()) > 5  # 过滤短文档

filtered = ScoreFilter(quality_score)(dataset)

# 去重
from nemo_curator.modules import ExactDuplicates
deduped = ExactDuplicates()(filtered)

# 保存
deduped.to_parquet("curated_data/")
```

## 数据整理管道

### 阶段1：质量过滤

```python
from nemo_curator.filters import (
    WordCountFilter,
    RepeatedLinesFilter,
    UrlRatioFilter,
    NonAlphaNumericFilter
)

# 应用30多种启发式过滤器
from nemo_curator import ScoreFilter

# 单词数量过滤器
dataset = dataset.filter(WordCountFilter(min_words=50, max_words=100000))

# 移除重复内容
dataset = dataset.filter(RepeatedLinesFilter(max_repeated_line_fraction=0.3))

# URL比例过滤器
dataset = dataset.filter(UrlRatioFilter(max_url_ratio=0.2))
```

### 阶段2：去重（Deduplication）

**精确去重（Exact deduplication）**：
```python
from nemo_curator.modules import ExactDuplicates

# 移除完全重复的文档
deduped = ExactDuplicates(id_field="id", text_field="text")(dataset)
```

**模糊去重（Fuzzy deduplication）**（在GPU上快16倍）：
```python
from nemo_curator.modules import FuzzyDuplicates

# MinHash + LSH去重
fuzzy_dedup = FuzzyDuplicates(
    id_field="id",
    text_field="text",
    num_hashes=260,      # MinHash参数
    num_buckets=20,
    hash_method="md5"
)

deduped = fuzzy_dedup(dataset)
```

**语义去重（Semantic deduplication）**：
```python
from nemo_curator.modules import SemanticDuplicates

# 基于嵌入的去重
semantic_dedup = SemanticDuplicates(
    id_field="id",
    text_field="text",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    threshold=0.8  # 余弦相似度阈值
)

deduped = semantic_dedup(dataset)
```

### 阶段3：PII脱敏（PII Redaction）

```python
from nemo_curator.modules import Modify
from nemo_curator.modifiers import PIIRedactor

# 脱敏个人身份信息
pii_redactor = PIIRedactor(
    supported_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION"],
    anonymize_action="replace"  # 或 "redact"
)

redacted = Modify(pii_redactor)(dataset)
```

### 阶段4：分类器过滤

```python
from nemo_curator.classifiers import QualityClassifier

# 质量分类
quality_clf = QualityClassifier(
    model_path="nvidia/quality-classifier-deberta",
    batch_size=256,
    device="cuda"
)

# 过滤低质量文档
high_quality = dataset.filter(lambda doc: quality_clf(doc["text"]) > 0.5)
```

## GPU加速

### GPU与CPU性能对比

| 操作 | CPU (16核) | GPU (A100) | 加速比 |
|-----------|----------------|------------|---------|
| 模糊去重 (8TB) | 120小时 | 7.5小时 | 16倍 |
| 精确去重 (1TB) | 8小时 | 0.5小时 | 16倍 |
| 质量过滤 | 2小时 | 0.2小时 | 10倍 |

### 多GPU扩展

```python
from nemo_curator import get_client
import dask_cuda

# 初始化GPU集群
client = get_client(cluster_type="gpu", n_workers=8)

# 使用8个GPU处理
deduped = FuzzyDuplicates(...)(dataset)
```

## 多模态整理（Multi-modal curation）

### 图像整理

```python
from nemo_curator.image import (
    AestheticFilter,
    NSFWFilter,
    CLIPEmbedder
)

# 美学评分
aesthetic_filter = AestheticFilter(threshold=5.0)
filtered_images = aesthetic_filter(image_dataset)

# NSFW检测
nsfw_filter = NSFWFilter(threshold=0.9)
safe_images = nsfw_filter(filtered_images)

# 生成CLIP嵌入
clip_embedder = CLIPEmbedder(model="openai/clip-vit-base-patch32")
image_embeddings = clip_embedder(safe_images)
```

### 视频整理

```python
from nemo_curator.video import (
    SceneDetector,
    ClipExtractor,
    InternVideo2Embedder
)

# 检测场景
scene_detector = SceneDetector(threshold=27.0)
scenes = scene_detector(video_dataset)

# 提取片段
clip_extractor = ClipExtractor(min_duration=2.0, max_duration=10.0)
clips = clip_extractor(scenes)

# 生成嵌入
video_embedder = InternVideo2Embedder()
video_embeddings = video_embedder(clips)
```

### 音频整理

```python
from nemo_curator.audio import (
    ASRInference,
    WERFilter,
    DurationFilter
)

# ASR转录
asr = ASRInference(model="nvidia/stt_en_fastconformer_hybrid_large_pc")
transcribed = asr(audio_dataset)

# 按WER（词错误率）过滤
wer_filter = WERFilter(max_wer=0.3)
high_quality_audio = wer_filter(transcribed)

# 时长过滤
duration_filter = DurationFilter(min_duration=1.0, max_duration=30.0)
filtered_audio = duration_filter(high_quality_audio)
```

## 常见模式

### 网络爬取数据整理（Common Crawl）

```python
from nemo_curator import ScoreFilter, Modify
from nemo_curator.filters import *
from nemo_curator.modules import *
from nemo_curator.datasets import DocumentDataset

# 加载Common Crawl数据
dataset = DocumentDataset.read_parquet("common_crawl/*.parquet")

# 管道
pipeline = [
    # 1. 质量过滤
    WordCountFilter(min_words=100, max_words=50000),
    RepeatedLinesFilter(max_repeated_line_fraction=0.2),
    SymbolToWordRatioFilter(max_symbol_to_word_ratio=0.3),
    UrlRatioFilter(max_url_ratio=0.3),

    # 2. 语言过滤
    LanguageIdentificationFilter(target_languages=["en"]),

    # 3. 去重
    ExactDuplicates(id_field="id", text_field="text"),
    FuzzyDuplicates(id_field="id", text_field="text", num_hashes=260),

    # 4. PII脱敏
    PIIRedactor(),

    # 5. NSFW过滤
    NSFWClassifier(threshold=0.8)
]

# 执行
for stage in pipeline:
    dataset = stage(dataset)

# 保存
dataset.to_parquet("curated_common_crawl/")
```

### 分布式处理

```python
from nemo_curator import get_client
from dask_cuda import LocalCUDACluster

# 多GPU集群
cluster = LocalCUDACluster(n_workers=8)
client = get_client(cluster=cluster)

# 处理大型数据集
dataset = DocumentDataset.read_parquet("s3://large_dataset/*.parquet")
deduped = FuzzyDuplicates(...)(dataset)

# 清理
client.close()
cluster.close()
```

## 性能基准测试

### 模糊去重（8TB RedPajama v2）

- **CPU（256核）**：120小时
- **GPU（8× A100）**：7.5小时
- **加速比**：16倍

### 精确去重（1TB）

- **CPU（64核）**：8小时
- **GPU（4× A100）**：0.5小时
- **加速比**：16倍

### 质量过滤（100GB）

- **CPU（32核）**：2小时
- **GPU（2× A100）**：0.2小时
- **加速比**：10倍

## 成本对比

**基于CPU的整理**（AWS c5.18xlarge × 10）：
- 成本：$3.60/小时 × 10 = $36/小时
- 处理8TB时间：120小时
- **总计**：$4,320

**基于GPU的整理**（AWS p4d.24xlarge × 2）：
- 成本：$32.77/小时 × 2 = $65.54/小时
- 处理8TB时间：7.5小时
- **总计**：$491.55

**节省**：减少89%（节省$3,828）

## 支持的数据格式

- **输入**：Parquet, JSONL, CSV
- **输出**：Parquet（推荐），JSONL
- **WebDataset**：用于多模态的TAR存档

## 用例

**生产部署**：
- NVIDIA使用NeMo Curator准备Nemotron-4训练数据
- 已整理的开源数据集：RedPajama v2, The Pile

## 参考资料

- **[过滤指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/filtering.md)** - 30多种质量过滤器、启发式方法
- **[去重指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/nemo-curator/references/deduplication.md)** - 精确、模糊、语义方法

## 资源

- **GitHub**：https://github.com/NVIDIA/NeMo-Curator ⭐ 500+
- **文档**：https://docs.nvidia.com/nemo-framework/user-guide/latest/datacuration/
- **版本**：0.4.0+
- **许可证**：Apache 2.0