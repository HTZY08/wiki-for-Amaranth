---
title: Qwen-Audio-3.0-TTS — 五阶段渐进式 LM+FM 联合优化的生产级语音合成
date: 2026-08-02
source: https://arxiv.org/abs/2607.23938
---

# Qwen-Audio-3.0-TTS — 五阶段渐进式 LM+FM 联合优化的生产级语音合成

**发布日期：** 2026年7月（arXiv 2607.23938）
**来源：** https://arxiv.org/abs/2607.23938
**工程范式：** "先解耦、再耦合、再 RL"的渐进式级联训练——12.5Hz 低帧率 tokenizer 压解码成本，LM 与 Flow Matching 模型从独立预训练到 hidden-state 联合优化，再用两轮 RL（LM 层 GRPO + FM 层 FlowTTS-GRPO）分别修正内容与音质，最终以 16 语言 + 20 方言区 + 3 分钟长文 + 噪声鲁棒性逼近生产级 TTS 全栈

## 设计哲学

核心约束：现代 TTS 有四种互补但互斥的范式——自回归离散 token（VALL-E 系，量化丢细节、解码成本随 token 率增长）、非自回归连续流匹配（Voicebox 系，保真但逐句采样难流式）、混合级联（Seed-TTS/CosyVoice 系，分离语言规划与声学渲染，但离散单 codebook 是信息与优化瓶颈）、连续自回归（DiTAR/Dots.TTS 系，免量化但高维逐块生成稳定性敏感）。生产系统要求同时拿到内容一致性、音色相似、韵律自然、可控性、多语言、低延迟、鲁棒性——单一范式给不了。

Qwen-Audio-3.0-TTS 的选择：**不站队，把四种范式的优点按训练阶段串起来**。骨架继承 CosyVoice 的 LM+FM 级联（自回归语义规划 + 流匹配声学渲染），但做了三个关键修正：

- **tokenizer 帧率减半（25→12.5Hz）**：自回归解码成本直接减半，用更大的量化空间（codebook 6561→59049）和更广的音频分析监督补偿信息损失
- **FM 条件化在 LM 连续 hidden states 而非离散 token 上**（JoyVoice 路线）：打破"token-only 接口"的信息瓶颈——FM 能利用离散 code 里丢失的上下文（韵律、音色、指令跟随）
- **五阶段渐进训练**：LM/FM 独立预训练 → 联合训练 + 高质量数据退火 → LM RL → FM 鲁棒性训练 → FM RL。每个阶段只优化当时最该优化的模块，冻结另一侧

放弃了什么：
- 放弃纯离散 token 接口的可组合性，换取 hidden-state 直通的信息保真
- 放弃 WER/CER 单项极致——论文明确承认"更激进的 CER 优化以牺牲自然度和表现力为代价"，选择平衡点（SEED-TTS-Eval test-zh CER 0.84% 是第二而非第一，但 ERes2Net 音色相似度三项全第一）
- 放弃显式推理期 denoiser，把提示增强（prompt enhancement）内化到 FM 训练——鲁棒性成为模型能力而非后处理

## 关键架构决策

### 12.5Hz 监督式语音 tokenizer

- 继承 CosyVoice3 的 supervised 设计：causal SenseVoice encoder + FSQ（Finite Scalar Quantization）
- 16kHz 输入 → 128 Mel bins @ 100Hz → 12 层 Voice Encoder-1（RoPE）降采样到 25Hz → Quantizer Encoder 降到 **12.5Hz**
- FSQ：10 维 × 3 级 → codebook 3^10 = **59,049** 条目（vs CosyVoice3 的 6,561）
- 多任务监督：ASR、语言识别（LID）、语音情感识别（SER）、音频事件检测（AED）、说话人分析（SA）、通用音频分析（AA）——强制离散 token 保留内容 + 音色 + 情感 + 声学事件
- 训练课程：先连续表示（FSQ bypass，LM 用 LoRA 适配）后量化（FSQ 激活，LM 冻结）
- 消融：帧率 25→12.5Hz 且 codebook 不变时 CER/SIM 退化；codebook 扩到 59,049 后 12.5Hz 反超 25Hz 基线（ASR: CV-zh 10.24 vs 10.63；TTS test-zh CER 1.23 vs 1.45）

### 三组件架构

- **LM**（语义规划）：从文本 + prompt 上下文预测离散语义 token。backbone 细节原文未完整披露（tokenizer 训练用 Qwen2.5-7B-Instruct 初始化）
- **FM**（声学渲染）：chunk-based flow matching，条件输入 = LM 连续 hidden states + prompt mel + speaker embedding，从 token 重建连续声学特征
- **Vocoder**：causal BigVGAN，48kHz 波形合成；配套 SFT 导向超分 vocoder + 多尺度 STFT discriminator 抗条纹伪影 + 训练期噪声注入降 train/inference mismatch

### 五阶段渐进训练范式

**Stage 1 独立预训练**：LM 学 text→token 语义规划，FM 学 token→mel 声学重建。解耦保证两模块各自 scale 空间，保留级联可模块化替换性。

**Stage 2 联合训练 + 高质量数据退火**：FM 条件从离散 token embedding 换成 **LM 连续 hidden states**（JoyVoice 方法），token 预测路径保留、LM token 目标与 FM flow 目标联合优化——FM 重建 loss 通过共享 hidden-state 路径反向塑造 LM 表示。先用广覆盖数据混合建立跨语言/说话人/风格的 LM-FM 对齐，稳定后退火到精选高质量子集（更干净、更有表现力的语音）。**先广度后精度**：覆盖不丢，同时把声学保真/自然度/指令实现推向生产标准。

**Stage 3 LM RL（GRPO + DiffRO）**：冻结 FM 与 vocoder，在线 GRPO 优化 text→token LM。组 reward 四项加权：

$$R_{base,i} = \lambda_{content} R_{content,i} + \lambda_{dur} R_{dur,i} + \lambda_{div} R_{div,i} + \lambda_{prosody} R_{prosody,i}$$

内容项用 token 域 ASR（不跑 FM/vocoder，token-only rollout 高效）；时长项压长度离群；多样性项防机械坍缩；韵律项奖励对齐进展与停顿时机。加可微 DiffRO 分支（Gumbel-Softmax）补 token 级修正梯度，重复/缺 stop token 的极端 rollout 排除，DiffRO 只作用于非负组相对 advantage。两阶段课程：先通用生成优化（排除指令跟随/细粒度控制/方言样本），再加方言分类正确性属性 reward。

**Stage 4 FM 鲁棒性训练（冻结 LM）**：从退化 prompt 恢复干净高质量语音并保留音色。增强池覆盖加性噪声/混响、手机/蓝牙/笔记本麦克风响应、远场、口罩/手遮挡、codec/DAC/功放伪影、丢包、强回声、组合场景（远场嘈杂会议室、噪声+电子失真）。**把 prompt enhancement 内化进克隆路径**，推理时无需显式 denoiser。

**Stage 5 FM RL（FlowTTS-GRPO）**：冻结 LM，针对说话人相似度与感知质量。确定性 ODE 采样转 marginal-preserving SDE（σ_t = a√((1-t)/t)）做 on-policy 探索，reward 三项——speaker-verification 相似度（SS）、ASR 可懂度、DNSMOS 质量——各自按 batch 标准差标准化再加权，探索限制在早期步窗口，训练 rollout 去掉 classifier-free guidance 扩探索。

### 生产级可控性与覆盖

- 自然语言自由指令：角色、情感、语速、音色、口音
- **86 个新增细粒度 inline tags**：短语/词级局部控制，含表现力过渡与笑声/呼吸/咳嗽/叹气等非语言事件
- 16 语言（新增马来语、他加禄语、阿拉伯语、葡萄牙语、印尼语、泰语、越南语 7 种）、20 个中文方言区
- 单次 3 分钟长文合成、硬文本归一化（多音字、生僻字、LaTeX 数学式）
- 两阶段说话人适配协议 + 超分 vocoder 出 48kHz

## 关键结果

**SEED-TTS-Eval 零样本（表 3）：** test-zh CER 0.84%（第二，仅次于 Qwen3-TTS-12Hz 的 0.77）、SIM WavLM 0.792 / **ERes2Net 0.847（全三测试集最高）**；test-en WER 1.54、test-hard CER 7.00，ERes2Net 分别 0.815 / 0.824（均最高）。论文明确说明：CER/WER 压更狠会牺牲自然度，本模型取平衡点。

**CV3-Eval 多语言克隆（表 4，16 语言）：** zh 3.35、en 4.25、ja 4.78（最佳）、ko 4.30（最佳）、ru 4.68（最佳）、ar 3.36（最佳）、ms 2.62（最佳）、th 1.45（最佳）——8 项最佳、其余高度竞争；全面优于 MiniMax-Speech-2.8-HD 与 ElevenLabs-v3（如 ja 4.78 vs 6.29/5.71）。

**hard-zh / hard-en（表 5）：** SIM 78.7 / 76.6 与 DNSMOS 3.93 / 4.04 均最佳，WER 高度竞争——抗噪声提示下音色保真与感知质量同时领先。

**跨语言克隆（表 6，12 个方向）：** 8 个方向最佳、4 个第二；平均错误率从 CosyVoice3-1.5B 的 10.09% 降至 **4.05%（相对降 ~60%）**。

**Qwen-Audio-TTS-Eval（新增部署向诊断基准）：** 文本归一化总体准确率中文 68.7% / 英文 65.7% 双最佳（覆盖数字/金融/缩写/代码/公式五类）；长文 1.5–3 分钟单次合成；894 条噪声/混响/模糊 prompt 鲁棒性集。

**第三方榜单：** Artificial Analysis TTS Arena（2026-07-16 快照）Qwen-Audio-3.0-TTS-Plus Elo 1,237（1,427 样本），按点估计排名第一，与 Simba 3.2 置信区间重叠（统计领先组内）。

## 范式对比

| 维度 | Qwen-Audio-3.0-TTS | CosyVoice3（前代） | Dots.TTS / VoxCPM2（连续 AR） | Seed-TTS（混合级联） |
|------|-------------------|-------------------|------------------------------|---------------------|
| 表示 | 12.5Hz 离散 + LM hidden-state 直通 | 25Hz 单 codebook | 连续 latent 逐块 | 离散 + 连续声学 |
| 训练 | 五阶段（解耦→联合→双 RL） | 多任务 + 后训练 | 端到端自回归 | 级联 + 强化 |
| 跨语言 | 16 语言 / 20 方言区 | 9 语言 | 较少 | 中英为主 |
| 鲁棒性 | 训练内化 prompt 增强 | 有限 | 敏感 | 部分 |

关键差异：与前代 CosyVoice3 相比，帧率减半 + codebook ×9 + hidden-state 联合训练 + 双层 RL 是四个独立贡献点，任一单独都不够（消融表验证帧率与 codebook 需配对）。与连续 AR 系（Dots.TTS）相比，保留离散语义规划的稳定性，同时用 hidden-state 直通拿走离散瓶颈——等于"AR 的稳定 + NAR 的信息密度"。

## 社区评价

（HN/Reddit 讨论未在此次扫描中独立核实，暂不引用外部评价。可观察信号：TTS Arena 第一名的第三方确认 + 与 MiniMax-Speech-2.8-HD / ElevenLabs-v3 两大商业 API 的全面对比胜出，是生产部署选型层面的强信号。）

## 可复用的工程经验

1. **"帧率减半 + 量化空间扩大"是成对设计**：降低 token 率省解码成本时，必须同步扩大 codebook 容量并加宽监督任务，否则信息损失吃掉全部收益（消融：6561 codebook @12.5Hz 全面退化，59049 @12.5Hz 反超 25Hz 基线）。
2. **级联系统不要一步到位耦合**：先独立预训练 LM/FM（各自 scale 空间、可替换），再联合训练——"先解耦再耦合"比从头端到端稳定得多，且保住了模块化。
3. **hidden-state 直通是离散 token 瓶颈的低成本解**：FM 条件改用 LM 连续 hidden states 而非 token embedding，无需改动推理链路就能让下游模块吃到 code 序列丢掉的上下文。
4. **数据退火要"先广度后精度"**：广覆盖混合建立对齐 → 高质量子集精修声学细节。直接上高质量数据会丢多语言/多说话人覆盖。
5. **两轮 RL 分工明确**：LM 层 RL 管内容/时长/多样性/韵律（token-only rollout 便宜），FM 层 RL 管音色/感知质量（SDE 探索 + 分项标准化 reward）。reward 先各自标准化再加权，λ 才表达真实意图而非被 reward 方差绑架。
6. **鲁棒性是训练属性而非后处理**：把 prompt enhancement 作为 FM 训练目标（噪声/混响/带宽/遮挡/编解码伪影增强池），推理期零额外 denoiser——生产系统的失败模式（脏参考音）在训练期就消掉。
7. **评测别只看 WER**：论文明示 WER/CER 与自然度/表现力存在 trade-off，且 WavLM 与 ERes2Net 对同一批系统给出不同排序——多指标交叉看，选型时按部署权重取平衡。

> 交叉引用：与 Qwen-Audio-3.0-Gen-Preview（非自回归音频场景生成，见 07-31-qwen-audio-3-gen-preview.md）同属 Qwen-Audio-3.0 家族但方向不同——Gen 走共享连续潜空间 DiT 做场景生成，TTS 走 LM+FM 级联做语音合成；后者保留自回归语义规划的稳定性。
