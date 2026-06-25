---
title: Optional Skills Catalog
---

# 可选技能目录（Optional Skills Catalog）

可选技能随 hermes-agent 一同发布，位于 `optional-skills/` 目录下，但**默认未激活**。需显式安装：

```bash
hermes skills install official/<category>/<skill>
```

例如：

```bash
hermes skills install official/blockchain/solana
hermes skills install official/mlops/flash-attention
```

下面的每个技能都链接到一个专用页面，包含完整的定义、设置和使用方法。

卸载：

```bash
hermes skills uninstall <skill-name>
```

## autonomous-ai-agents（自主AI代理）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | 操作 Antigravity CLI (agy)：插件、认证、沙箱。 |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | 将编码任务委托给 Blackbox AI CLI 代理。多模型代理，内置评估器，通过多个 LLM 运行任务并选择最佳结果。需要 blackbox CLI 和 Blackbox AI API 密钥。 |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | 将编码委托给 xAI Grok Build CLI（功能、PR）。 |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | 使用 Honcho 内存配置 Hermes——跨会话用户建模、多配置文件对等隔离、观察配置、辩证推理、会话摘要和上下文预算强制执行。用于设置 Honcho、故障排除... |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | 将编码委托给 OpenHands CLI（模型无关，LiteLLM）。 |

## blockchain（区块链）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | 只读 EVM 客户端：跨 8 条链的钱包、代币、Gas。 |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | Hyperliquid 市场数据、账户历史、交易回顾。 |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | 查询 Solana 区块链数据并获取美元定价——钱包余额、含价值的代币组合、交易详情、NFT、大户检测和实时网络统计。使用 Solana RPC + CoinGecko。无需 API 密钥。 |

## communication（通信）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**one-three-one-rule**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | 用于技术方案和权衡分析的结构化决策框架。当用户在多个方法之间选择（架构决策、工具选择、重构策略、迁移路径）时，此技能会... |

## creative（创意）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | 文章插图：类型 × 风格 × 调色板一致性。 |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | 知识漫画（knowledge comics）：教育、传记、教程。 |
| [**blender-mcp**](/docs/user-guide/skills/optional/creative/creative-blender-mcp) | 通过 socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，并运行任意 Blender Python (bpy) 代码。当用户想要在 Blender 中创建或修改任何内容时使用。 |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | 生成扁平、极简、浅色/深色适应的 SVG 图表作为独立 HTML 文件，使用统一的教育视觉语言，包含 9 种语义色阶、句首大写排版和自动深色模式。最适合教育和通知... |
| [**creative-ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | 通过创意实践中的命名方法产生想法。 |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | 使用 HyperFrames 创建基于 HTML 的视频合成、动画标题卡、社交叠加层、带字幕的讲话头视频、音频响应式视觉效果和着色器过渡。HTML 是视频的真相来源。当用户想要... |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | 规划、设置并监控基于 Hermes Kanban 的多代理视频生产管道。当用户想要制作任何视频时使用——叙事电影、产品/营销、音乐视频、解释片、ASCII/终端艺术、抽象/生成外观... |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | 通过选择模板并使用 Pillow 叠加文字，生成真实的 meme 图像。生成实际的 .png meme 文件。 |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | 使用时代调色板（NES、Game Boy、PICO-8）的像素艺术。 |

## devops（开发运维）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-cli) | 通过 inference.sh CLI (infsh) 运行 150+ AI 应用——图像生成、视频创建、LLM、搜索、3D、社交自动化。使用终端工具。触发器：inference.sh、infsh、ai apps、flux、veo、image generation、video generation、seedrea... |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | 管理 Docker 容器、镜像、卷、网络和 Compose 栈——生命周期操作、调试、清理和 Dockerfile 优化。 |
| [**hermes-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-hermes-s6-container-supervision) | 修改、调试或扩展 Hermes Agent Docker 镜像内部的 s6-overlay 监督树——添加新服务、调试配置文件网关、理解架构 B 主程序模式。 |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | 通过 SSH 和 Pinggy 进行零安装的 localhost 隧道。 |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | 使用水印去重轮询 RSS、JSON API 和 GitHub。 |

## dogfood（自用测试）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | 扮演最困难、最抗拒技术的用户来测试你的产品。以该角色浏览应用，找出所有 UX 痛点，然后通过实用层过滤投诉，将真正的问题与噪音分开。创建可操作的工单... |

## email（电子邮件）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | 通过 AgentMail 为代理提供专属的电子邮件收件箱。使用代理拥有的电子邮件地址（例如 hermes-agent@agentmail.to）自主发送、接收和管理电子邮件。 |

## finance（金融）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**3-statement-model**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | 在 Excel 中构建完全集成的三表模型（利润表、资产负债表、现金流量表），包含营运资金表、折旧摊销滚动表、债务表以及使现金和留存收益平衡的插入项。与 excel-author 搭配使用。 |
| [**comps-analysis**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | 在 Excel 中构建可比公司分析——运营指标、估值倍数、与同行组的统计基准比较。与 excel-author 搭配使用。适用于上市公司估值、IPO 定价、行业基准测试或异常值检测。 |
| [**dcf-model**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | 在 Excel 中构建机构质量的 DCF 估值模型——收入预测、自由现金流构建、WACC、终值、悲观/基准/乐观情景、5x5 敏感性表格。与 excel-author 搭配使用。适用于内在价值股权分析。 |
| [**excel-author**](/docs/user-guide/skills/optional/finance/finance-excel-author) | 使用 openpyxl 以无头方式构建可审计的 Excel 工作簿——蓝色/黑色/绿色单元格约定、公式而非硬编码、命名区域、平衡检查、敏感性表格。适用于财务模型、审计输出、对账。 |
| [**lbo-model**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | 在 Excel 中构建杠杆收购模型——资金来源与使用、债务表、现金扫除、退出倍数、IRR/MOIC 敏感性。与 excel-author 搭配使用。适用于 PE 筛选、赞助商案例估值或推介中的说明性 LBO。 |
| [**merger-model**](/docs/user-guide/skills/optional/finance/finance-merger-model) | 在 Excel 中构建增值/稀释（并购）模型——备考利润表、协同效应、融资组合、每股收益影响。与 excel-author 搭配使用。适用于并购推介、董事会材料或交易评估。 |
| [**pptx-author**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | 使用 python-pptx 以无头方式构建 PowerPoint 演示文稿。与 excel-author 搭配使用，构建模型支持的演示文稿，其中每个数字都能追溯到工作簿单元格。适用于推介 Deck、IC 备忘录、收益说明。 |
| [**stocks**](/docs/user-guide/skills/optional/finance/finance-stocks) | 通过 Yahoo 获取股票报价、历史数据、搜索、比较、加密货币。 |

## gaming（游戏）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | 托管模组版 Minecraft 服务器（CurseForge、Modrinth）。 |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | 通过无头模拟器 + RAM 读取玩 Pokemon。 |

## health（健康）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | 健身房锻炼计划器和营养追踪器。通过 wger 按肌肉、设备或类别搜索 690+ 项锻炼。通过 USDA FoodData Central 查询 380,000+ 种食物的宏量和热量。计算 BMI、TDEE、最大单次重复重量、宏量营养素分配和身体... |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | 连接到正在运行的 NeuroSkill 实例，将用户的实时认知和情绪状态（注意力、放松程度、情绪、认知负荷、困倦、心率、心率变异性、睡眠分期以及 40+ 导出的 EXG 分数）融入响应中... |

## mcp（模型上下文协议）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | 使用 Python 中的 FastMCP 构建、测试、检查、安装和部署 MCP 服务器。用于创建新的 MCP 服务器、将 API 或数据库封装为 MCP 工具、暴露资源或提示，或为 Claude Code、Cur... 准备 FastMCP 服务器。 |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | 使用 mcporter CLI 列出、配置、认证和直接调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑和 CLI/类型生成。 |

## migration（迁移）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | 将用户的 OpenClaw 自定义配置迁移到 Hermes Agent。导入与 Hermes 兼容的记忆、SOUL.md、命令允许列表、用户技能以及来自 ~/.openclaw 的选定工作区资产，然后报告哪些内容无法迁移... |

## mlops（机器学习运维）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**huggingface-accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | 最简单的分布式训练 API。4 行代码即可为任何 PyTorch 脚本添加分布式支持。统一的 DeepSpeed/FSDP/Megatron/DDP API。自动设备放置、混合精度（FP16/BF16/FP8）。交互式配置、单一启动命令... |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl：基于 YAML 的 LLM 微调（LoRA、DPO、GRPO）。 |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | 用于 AI 应用的开源嵌入数据库。存储嵌入和元数据，执行向量和全文搜索，按元数据过滤。简单的 4 函数 API。从笔记本扩展到生产集群。用于语义搜索、RAG... |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | OpenAI 的连接视觉与语言的模型。支持零样本图像分类、图像-文本匹配和跨模态检索。在 4 亿图像-文本对上训练。用于图像搜索、内容审核或视觉语言任务... |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy：声明式 LM 程序，自动优化提示，RAG。 |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Facebook 的高效稠密向量相似性搜索和聚类库。支持数十亿向量、GPU 加速和各种索引类型（Flat、IVF、HNSW）。用于快速 k-NN 搜索、大规模向量检索或... |
| [**optimizing-attention-flash**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | 使用 Flash Attention 优化 Transformer 注意力机制，实现 2-4 倍加速和 10-20 倍内存减少。用于训练/运行长序列（>512 tokens）的 Transformer、遇到注意力机制的 GPU 内存问题或需要更快推理... |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | 使用正则表达式和语法控制 LLM 输出，保证生成有效的 JSON/XML/代码，强制执行结构化格式，并使用 Guidance（微软研究院的约束生成框架）构建多步骤工作流。 |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | 针对研究和生产优化的快速分词器。基于 Rust 的实现可在 <20 秒内分词 1GB。支持 BPE、WordPiece 和 Unigram 算法。训练自定义词汇表、跟踪对齐、处理填充/截断。集成... |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | 从 LLM 响应中提取结构化数据，使用 Pydantic 验证，自动重试失败的提取，解析复杂 JSON 并保证类型安全，使用 Instructor（经过实战检验的结构化输出库）流式输出部分结果。 |
| [**lambda-labs-gpu-cloud**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | 用于 ML 训练和推理的预留和按需 GPU 云实例。当你需要专用 GPU 实例、简单的 SSH 访问、持久文件系统或高性能多节点集群进行大规模训练时使用。 |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | 大型语言与视觉助手。支持视觉指令微调和基于图像的对话。结合 CLIP 视觉编码器与 Vicuna/LLaMA 语言模型。支持多轮图像聊天、视觉问答和指令... |
| [**modal-serverless-gpu**](/docs/user-guide/skills/optional/mlops/mlops-modal) | 用于运行 ML 工作负载的无服务器 GPU 云平台。当你需要按需 GPU 访问而无需管理基础设施、将 ML 模型部署为 API 或运行具有自动扩展功能的批处理作业时使用。 |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | 用于 LLM 训练的 GPU 加速数据管理工具。支持文本/图像/视频/音频。功能包括模糊去重（16 倍更快）、质量过滤（30+ 启发式）、语义去重、PII 编辑、NSFW 检测。跨 GPU 扩展... |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS：消除 LLM 拒绝（差异均值法）。 |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines：结构化 JSON/正则/Pydantic LLM 生成。 |
| [**peft-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-peft) | 使用 LoRA、QLoRA 和 25+ 方法进行参数高效的 LLM 微调。用于在有限 GPU 内存下微调大型模型（7B-70B），训练 <1% 的参数且准确率损失最小，或多适配器服务... |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | 用于生产 AI 应用的托管向量数据库。完全托管、自动扩展，支持混合搜索（稠密 + 稀疏）、元数据过滤和命名空间。低延迟（p95 <100ms）。用于生产 RAG、推荐系统或... |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | 使用 PyTorch FSDP 进行全分片数据并行训练的专家指导——参数分片、混合精度、CPU 卸载、FSDP2。 |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | 高级 PyTorch 框架，包含 Trainer 类、自动分布式训练（DDP/FSDP/DeepSpeed）、回调系统以及最小样板代码。使用相同代码从笔记本扩展到超级计算机。当你希望拥有简洁的训练循环时使用... |
| [**qdrant-vector-search**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | 用于 RAG 和语义搜索的高性能向量相似性搜索引擎。用于构建需要快速最近邻搜索、带过滤的混合搜索或使用 Rust 驱动的高性能可扩展向量存储的生产 RAG 系统... |
| [**sparse-autoencoder-training**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | 提供使用 SAELens 训练和分析稀疏自编码器（SAE）的指导，以将神经网络激活分解为可解释的特征。用于发现可解释特征、分析叠加或研究... |
| [**simpo-training**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | 用于 LLM 对齐的简单偏好优化（Simple Preference Optimization）。DPO 的免参考替代方案，性能更优（在 AlpacaEval 2.0 上 +6.4 分）。无需参考模型，比 DPO 更高效。用于偏好对齐，当你想要简单... |
| [**slime-rl-training**](/docs/user-guide/skills/optional/mlops/mlops-slime) | 提供使用 slime（Megatron+SGLang 框架）对 LLM 进行基于强化学习的后训练的指导。用于训练 GLM 模型、实现自定义数据生成工作流或需要紧密集成 Megatron-LM 进行 RL 扩展时使用。 |
| [**stable-diffusion-image-generation**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | 使用 HuggingFace Diffusers 和 Stable Diffusion 模型进行最先进的文本到图像生成。用于从文本提示生成图像、执行图像到图像转换、图像修复或构建自定义扩散管道。 |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | 使用 NVIDIA TensorRT 优化 LLM 推理，以实现最大吞吐量和最低延迟。用于在 NVIDIA GPU（A100/H100）上进行生产部署，当你需要比 PyTorch 快 10-100 倍的推理速度，或使用量化... 提供模型服务时使用。 |
| [**distributed-llm-pretraining-torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | 使用 torchtitan 提供 PyTorch 原生的分布式 LLM 预训练，支持 4D 并行（FSDP2、TP、PP、CP）。用于预训练 Llama 3.1、DeepSeek V3 或自定义模型，规模从 8 到 512+ GPU，使用 Float8、torch.compile 和分布式... |
| [**fine-tuning-with-trl**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL：用于 LLM RLHF 的 SFT、DPO、PPO、GRPO、奖励建模。 |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth：2-5 倍更快的 LoRA/QLoRA 微调，更少的显存占用。 |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | OpenAI 的通用语音识别模型。支持 99 种语言、转录、翻译为英语和语言识别。六种模型大小，从 tiny（3900 万参数）到 large（15.5 亿参数）。用于语音转文本、播客... |

## payments（支付）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**mpp-agent**](/docs/user-guide/skills/optional/payments/payments-mpp-agent) | 通过机器支付协议（MPP）支付 HTTP 402 API。 |
| [**stripe-link-cli**](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli) | 通过 Stripe Link 进行代理支付——卡片、SPT、审批。 |
| [**stripe-projects**](/docs/user-guide/skills/optional/payments/payments-stripe-projects) | 通过 Stripe Projects 提供 SaaS 服务并同步凭据。 |

## productivity（生产力）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | Canvas LMS 集成——使用 API 令牌认证获取已注册课程和作业。 |
| [**here.now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | 将静态网站发布到 &#123;slug&#125;.here.now，并在云驱动器中存储私有文件，用于代理到代理的交接。 |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | 间隔重复闪卡系统。从事实或文本创建卡片，使用由代理评分的自由文本答案与闪卡聊天，从 YouTube 转录生成测验，使用自适应调度复习到期卡片，并导出/导入... |
| [**shop**](/docs/user-guide/skills/optional/productivity/productivity-shop) | 商店目录搜索、结账、订单跟踪、退货。 |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | 通过 curl 使用 Shopify Admin & Storefront GraphQL API。产品、订单、客户、库存、元字段。 |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | 思源笔记 API，用于通过 curl 搜索、读取、创建和管理自托管知识库中的块和文档。 |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | 在不修改核心工具的情况下赋予 Hermes 电话能力。配置并持久化一个 Twilio 号码，发送和接收 SMS/MMS，拨打直接电话，并通过 Bland.ai 或 Vapi 进行 AI 驱动的外呼电话。 |

## research（研究）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**bioinformatics**](/docs/user-guide/skills/optional/research/research-bioinformatics) | 来自 bioSkills 和 ClawBio 的 400+ 生物信息学技能入口。涵盖基因组学、转录组学、单细胞、变异检测、药物基因组学、宏基因组学、结构生物学等。获取领域特定参考资料... |
| [**darwinian-evolver**](/docs/user-guide/skills/optional/research/research-darwinian-evolver) | 使用 Imbue 的进化循环进化提示词/正则表达式/SQL/代码。 |
| [**domain-intel**](/docs/user-guide/skills/optional/research/research-domain-intel) | 使用 Python 标准库进行被动域名侦察。子域名发现、SSL 证书检查、WHOIS 查询、DNS 记录、域名可用性检查和批量多域名分析。无需 API 密钥。 |
| [**drug-discovery**](/docs/user-guide/skills/optional/research/research-drug-discovery) | 用于药物发现工作流的药物研究助手。在 ChEMBL 上搜索生物活性化合物，计算类药性（Lipinski Ro5、QED、TPSA、合成可及性），通过 OpenFDA 查询药物-药物相互作用，解释 ADMET... |
| [**duckduckgo-search**](/docs/user-guide/skills/optional/research/research-duckduckgo-search) | 通过 DuckDuckGo 进行免费网络搜索——文本、新闻、图片、视频。无需 API 密钥。优先使用已安装的 `ddgs` CLI；仅当验证当前运行时环境中有 `ddgs` 时才使用 Python DDGS 库。 |
| [**gitnexus-explorer**](/docs/user-guide/skills/optional/research/research-gitnexus-explorer) | 使用 GitNexus 索引代码库，并通过 Web UI + Cloudflare 隧道提供交互式知识图谱服务。 |
| [**osint-investigation**](/docs/user-guide/skills/optional/research/research-osint-investigation) | 公共记录 OSINT 调查框架——SEC EDGAR 文件、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄露、纽约物业记录（ACRIS）、OpenCorporates 注册、CourtListener 法庭记录、Wayback... |
| [**parallel-cli**](/docs/user-guide/skills/optional/research/research-parallel-cli) | Parallel CLI 的可选供应商技能——代理原生网络搜索、提取、深度研究、富化、FindAll 和监控。优先使用 JSON 输出和非交互式流程。 |
| [**qmd**](/docs/user-guide/skills/optional/research/research-qmd) | 使用 qmd 在本地搜索个人知识库、笔记、文档和会议记录——混合检索引擎，结合 BM25、向量搜索和 LLM 重排序。支持 CLI 和 MCP 集成。 |
| [**scrapling**](/docs/user-guide/skills/optional/research/research-scrapling) | 使用 Scrapling 进行网络抓取——通过 CLI 和 Python 进行 HTTP 抓取、隐身浏览器自动化、Cloudflare 绕过和爬虫爬取。 |
| [**searxng-search**](/docs/user-guide/skills/optional/research/research-searxng-search) | 通过 SearXNG 进行免费元搜索——聚合来自 70+ 搜索引擎的结果。自托管或使用公共实例。无需 API 密钥。当网络搜索工具集不可用时自动回退。 |

## security（安全）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**1password**](/docs/user-guide/skills/optional/security/security-1password) | 设置并使用 1Password CLI (op)。用于安装 CLI、启用桌面应用集成、登录以及为命令读取/注入密钥。 |
| [**godmode**](/docs/user-guide/skills/optional/security/security-godmode) | 越狱 LLM：Parseltongue、GODMODE、ULTRAPLINIAN。 |
| [**oss-forensics**](/docs/user-guide/skills/optional/security/security-oss-forensics) | 针对 GitHub 仓库的供应链调查、证据恢复和取证分析。涵盖删除提交恢复、强制推送检测、IOC 提取、多源证据收集、假设形成/验证和 st... |
| [**sherlock**](/docs/user-guide/skills/optional/security/security-sherlock) | 跨 400+ 社交网络的 OSINT 用户名搜索。通过用户名追踪社交媒体账户。 |
| [**web-pentest**](/docs/user-guide/skills/optional/security/security-web-pentest) | 授权的 Web 应用渗透测试——侦察、漏洞分析、基于利用的漏洞验证和专业报告。采用 Shannon 的“无漏洞即无报告”方法论，并带有严格的范围、授权... |

## software-development（软件开发）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**code-wiki**](/docs/user-guide/skills/optional/software-development/software-development-code-wiki) | 为任何代码库生成维基文档 + Mermaid 图表。 |
| [**rest-graphql-debug**](/docs/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) | 调试 REST/GraphQL API：状态码、认证、模式、复现。 |
| [**subagent-driven-development**](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) | 通过 delegate_task 子代理执行计划（两阶段审查）。 |

## web-development（Web 开发）

| 技能（Skill） | 描述（Description） |
|-------|-------------|
| [**page-agent**](/docs/user-guide/skills/optional/web-development/web-development-page-agent) | 将 alibaba/page-agent 嵌入到你自己的 Web 应用中——一个纯 JavaScript 的页面内 GUI 代理，作为单个 &lt;script> 标签或 npm 包分发，让你的网站最终用户能够使用自然语言驱动 UI（“点击登录，填写用户名...”）。

---

--- body ---
## 贡献可选技能（Contributing Optional Skills）

要向仓库添加新的可选技能：

1. 在 `optional-skills/<category>/<skill-name>/` 下创建目录。
2. 添加包含标准 frontmatter（名称、描述、版本、作者）的 `SKILL.md` 文件。
3. 将任何支持文件放入 `references/`、`templates/` 或 `scripts/` 子目录。
4. 提交拉取请求——技能将出现在此目录中，并在合并后获得自己的文档页面。