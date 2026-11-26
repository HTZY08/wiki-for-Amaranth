---
title: MiniMax H3-Image — 砍掉音频分支，把视频模型蒸馏成六步出图
date: 2026-11-11
source: "https://www.minimax.io/blog/minimax-h3-image"
---

# MiniMax H3-Image：16MP 十秒出图，靠的是"减法 + 蒸馏"

**发布日期：** 2026-11-11（官方 blog 日期；多家媒体记为 11 月 10 日发布）
**来源：** https://www.minimax.io/blog/minimax-h3-image（模型卡：https://huggingface.co/MiniMaxAI/MiniMax-H3-Image）
**工程范式：** 不新训一个图像模型，而是把自家视频生成底座 H3 的音频分支摘掉、冻结文本编码器、只重做后训练与采样调度——用 6 步无 CFG 的蒸馏把"16MP 直出"变成可用的产品形态。

## 设计哲学

官方对这次发布的定位是"post-training 全链路改造"，不是新架构："Building on H3's pre-training capabilities, we've made improvements across the entire post-training pipeline, from data and reinforcement learning to sampling-step reduction, PE, and deployment optimization"，并明确"没有任何单项改动决定结果"。

约束是三条互相打架的指标：速度、画质、指令遵循。他们的解法是把矛盾从模型侧挪到采样侧——**蒸馏到 6 步、彻底去掉 classifier-free guidance**，再用原生 16MP 分辨率省掉上采样环节。代价写在 API 契约里：步数只能是 6、guidance 只能是 1、负向提示词直接不支持（其他值一律 HTTP 400 拒绝）。这是把"采样配方"从可调参数变成产品常量——灵活性换确定性。

另一处减法是多模态范围：摘掉音频分支、文本编码器整段沿用 H3（Qwen3-VL）不做重训。工程上这等于承认"图像模型的核心资产是视频底座的时空表示"，而不是单独训一个图像 DiT。

## 关键架构决策

以下参数来自官方 Hugging Face 模型卡（一手），非二手转述：

- **主干**：**33.1B 参数的稠密单流（dense single-stream）Transformer**，50 层，hidden size 5,376，56 个注意力头，FFN 宽度 14,336，3D 多模态 RoPE。结构与 H3-Omni-Transformer 相同，只是去掉音频层。文本与参考图 token 打进**同一条 packed sequence**，由同一个 checkpoint 同时做文生图与多图编辑。
- **文本侧**：完整沿用 MiniMax-H3 的 Qwen3-VL 文本编码器，不改；DiT 读取其**第 50 层**的 hidden states。这是典型的"冻结教师特征"做法——省掉文本侧的全部训练成本。
- **VAE**：CNN 编码器 + 24 层 2D ViT 解码器，16× 空间下采样，24 个 latent 通道；DiT 用 2×2 patchify，因此**每个 transformer token 覆盖 32×32 像素**。这个比例是把 16MP 塞进可承受序列长度的关键。
- **采样**：蒸馏到 6 sampling steps（6 NFEs），**零 CFG**。模型仓库里带 `pdd_fused_heads.safetensors` + `pdd_config.json`——即按步替换输出层的 per-step output heads 与采样时序表（12 MB）。这是"每步一个专用输出头"的蒸馏形态，而不是单纯减少步数。
- **分辨率**：原生约 16MP，全宽高比统一：4096×4096（1:1）、4736×3552（4:3）、5024×3360（3:2）、5472×3072（16:9）、6272×2688（21:9），**不经上采样器**。有效工作区间约 4MP–20MP，官方称 16MP 附近效果最佳。`min_generation_area` 默认 4,194,304 像素（2048×2048）：小于该面积的请求会先在更大画布上按同比例生成再用 LANCZOS 缩回——这是个不显眼但重要的工程折中，因为模型的最佳工作区间不覆盖小图。
- **参考图**：单 checkpoint 支持最多 16 张参考图编辑，指令截断在 4,096 token。
- **推理部署**：官方推荐 SGLang / vLLM-Omni / diffusers / LightX2V / DiffSynth / ComfyUI；vLLM-Omni 覆盖 NVIDIA H200、RTX PRO 6000 Blackwell、AMD Instinct MI350X；低于默认延迟用 Ulysses 序列并行拆到 4 卡（`--num-gpus 4 --usp 4 --text-encoder-tp-size 4`）。
- **体积**：DiT BF16 66.28 GB + 图像 VAE 2.34 GB + 文本编码器 66.7 GB（从 H3 仓库复用，已有时不重复下载），合计约 135 GB；可选提示词扩写模型 PE 为 NVFP4 17.9 GB。
- **Prompt 侧**：模型需要"整幅图的详细英文描述"，官方 API 先用 H3-Image-Context-IR 把任意语言的短 prompt 改写成详细描述并选画幅，再生成；本地可用 PE 模型替代。
- **许可**：MiniMax-H3-Image Community License Agreement，Section IV 的额外书面授权需走申请表（不是 Apache/MIT）。

## 关键结果

**官方 blog 没有给出任何可复核的 benchmark 分数**，只有相对表述：

- 4K（4096×4096）全分辨率生成"in under 10 seconds"，并称"up to 5× the speed of mainstream alternatives"
- Standard 模式比主流方案快 1.5–2×，Highspeed 模式快 3–4×
- 定价为同类主流产品的 50–70%；发布周 4K 及以上请求五折
- 宣称"state-of-the-art prompt adherence among open-weight models"，**未附数字**

第三方（非官方、社区偏好而非基准）记录：DesignArena 图像榜上 H3-Image 于 11 月 11 日前后出现，Elo 约 1,302、位于该榜图像子类第 9；LMArena 于 11 月 10 日让其进入 Battle Mode 盲测投票。两者都是人群偏好信号，不是可复现的实验室指标。

## 范式对比

- **vs 自家 M3 系列（语言）**：MiniMax 的语言线在稀疏注意力（MSA）上做长上下文降本；图像线走的是完全相反的路——**稠密**单流 33B、不稀疏化，用蒸馏步数和 token 压缩（32×32 像素/token）控成本。同一家公司两条完全不同的降本哲学。
- **vs 开源图像侧（Qwen-Image / Seedream 等）**：多数开源图像模型把"可调采样"当卖点（步数、CFG、负向提示词自由调）；H3-Image 反其道把配方写死。这更适合做产品 API，不适合做研究基线。
- **vs 闭源（GPT-Image-2.6 等）**：闭源侧在 Elo 榜首（GPT-Image-2.6 Sunburst 为 11 月图像生成第一），H3-Image 的筹码是"开放权重 + 原生 16MP + 低价"，不是榜首排名。
- **vs 从零训图像 DiT**：这是本次真正的方法论主张——图像能力可以继承自视频底座（时空表示 + 文本对齐），只需重做后训练。若成立，图像模型的门槛会从"重训底座"降到"改造与蒸馏"。

## 社区评价

- 主线批评是**"这是宣称而非测量"**：OrcaRouter 的评测文直接把标题写成 "16 Megapixels in 10 Seconds Is a Claim, Not Yet a Measurement"；Runpod 的实操文同样注明"MiniMax 称约 10 秒，我们没有实测"。截至 11 月 12 日没有独立基准。
- **6 步无 CFG 的可调性**成为讨论焦点：API 对 `num_inference_steps != 6`、`guidance_scale != 1`、负向提示词一律返回 400，等于把参数空间封死。对产品是好事，对想调优的用户是限制。
- **许可与合规**：社区反复提醒权重不是 Apache-2.0，且该 Community License **不覆盖美国、欧盟、英国、韩国**，需 MiniMax 书面授权——这直接决定了它能被谁商用。
- **体积劝退**：135 GB（含 66.7 GB 文本编码器）让"开放权重"与"能在单卡跑"是两件事；实践多走 80 GB 卡 + 序列并行。
- 也有人指出一个文档不一致：某份 serving recipe 记录单请求 9 张参考图，与"最多 16 张"的宣称不一致，可能在所有运行时上并非都能用满 16 张。

## 可复用的工程经验

1. **复用视频底座做图像，是当前性价比最高的捷径**。冻结文本编码器（直接读中间层 hidden states）、摘掉不需要的分支、只重做后训练与采样——比从零训一个图像 DiT 便宜一个数量级。
2. **蒸馏的正确形态是"每步一个输出头"**，不是简单砍步数。per-step fused heads + 采样时序表（本例仅 12 MB）才是 6 步不掉画质的工程抓手。
3. **原生高分辨率的成本在 token 化比例上**。2×2 patchify + 16× VAE 下采样 → 每 token 32×32 像素；这决定了 16MP 是否塞得进上下文。想在 4K 上省钱，先算这个比例。
4. **把采样配方写死是产品决策，要提前想清楚**。固定 6 步 / guidance=1 / 无负向提示词会显著简化服务与成本核算，但会失去调优空间；如果你的用户是开发者而不是终端用户，这可能是错误选择。
5. **小图请求要按大画布生成再缩**。模型的最佳工作区间（本例 16MP 附近）与用户请求的尺寸不一致时，先在最佳区间生成再 LANCZOS 缩回，比直接在目标尺寸上生成更稳。
6. **"开放权重"必须同时说清体积与许可边界**。135 GB 与地区限制（不含美/欧/英/韩）才是落地时的真实门槛，比参数量更能决定它能不能进你的生产环境。
