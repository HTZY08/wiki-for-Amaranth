---
title: 技能索引
description: Amaranth Hermes Agent 全部 330 个技能的分类索引
---

## 总览

**技能总数：330** | **分类：20**

技能来源：Hermes Agent 内置 skills 目录（`/opt/data/skills/`） + 社区 marketplace + 自定义开发。

---

## 分类目录

| 分类 | 数量 | 用途 |
|------|------|------|
| [软件工程](#software-development) | 18 | TDD、调试、代码审查、工作流、架构 |
| [AI 代理](#autonomous-ai-agents) | 7 | Codex/Claude Code/OpenCode 代理管控 |
| [计算化学](#computational-chemistry) | 1 | Cu-MOF 分子对接管道 |
| [创意设计](#creative) | 28 | 生图、排版、SVG、PPT 美学、设计系统 |
| [数据处理](#data-science) | 3 | JSON/CSV/SQLite 命令行处理、Jupyter |
| [基础设施](#devops) | 52 | Hermes 运维、Docker、代理、存储、CI/CD |
| [邮箱](#email) | 1 | Himalaya CLI 邮件 |
| [游戏](#gaming) | 2 | Minecraft 服务器、Pokemon 模拟器 |
| [GitHub](#github) | 6 | PR、Issue、代码审查、仓库管理 |
| [MCP](#mcp) | 1 | MCP 客户端管理 |
| [多媒体](#media) | 12 | TTS、视频分析、音频转写、音乐生成 |
| [元技能](#meta) | 3 | 人机校准、进度条协议、写作风格 |
| [MLOps](#mlops) | 20 | 模型微调、推理、评估、量化 |
| [笔记](#note-taking) | 1 | Obsidian 双链笔记 |
| [生产力](#productivity) | 16 | Office 文档、PDF、网页小说、地图 |
| [红队](#red-teaming) | 2 | LLM 越狱、PUA Agent 驱动 |
| [研究/检索](#research) | 50 | 论文搜索、事实核查、综述写作、深度研究 |
| [商汤能力](#sensenova) | 44 | Excel/PDF/PPT/Word 分析、图像生成、深度研究 |
| [智能家居](#smart-home) | 1 | Philips Hue 灯光控制 |
| [社交媒体](#social-media) | 1 | X/Twitter API 操作 |

---

## 软件工程 <a id="software-development"></a>

| 技能 | 说明 |
|------|------|
| `agency-agent-router` | 任务→agent 人格路由 |
| `background-task-routing` | 异步平台后台任务路由 |
| `cli-anything` | 新软件的 CLI 包装 |
| `code-dedup-with-llm` | LLM 辅助 API 客户端去重 |
| `computer-orchestrator` | 多模型任务编排引擎 |
| `debugging-hermes-tui-commands` | Hermes TUI 调试 |
| `hermes-agent-skill-authoring` | Skill 创作模板与校验 |
| `hermes-plugin-authoring` | Hermes 插件开发 |
| `hermes-s6-container-supervision` | Docker s6 监督树运维 |
| `karpathy-foundation` | Karpathy 四原则适配 |
| `lightweight-compatible-server` | stdlib-only 兼容 API 服务器 |
| `node-inspect-debugger` | Node.js Chrome DevTools 调试 |
| `plan` | 写计划不执行 |
| `public-api-brain-router` | 公共 API + 搜索并行路由 |
| `python-debugpy` | Python pdb/debugpy 调试 |
| `requesting-code-review` | 预提交代码审查 |
| `spike` | 验证性临时实验 |
| `subagent-driven-development` | delegate_task 子 agent 开发 |
| `systematic-debugging` | 四阶段根因调试 |
| `test-driven-development` | TDD 红绿重构 |
| `trellis-harness` | Trellis 初始化与交付项目规范 |
| `workspace-agent` | 持久化工作区 + 知识图谱 |
| `writing-plans` | 实现计划写作 |

## AI 代理 <a id="autonomous-ai-agents"></a>

| 技能 | 说明 |
|------|------|
| `claude-code` | Claude Code CLI 代理封装 |
| `codex` | OpenAI Codex CLI 代理封装 |
| `hermes-agent` | Hermes Agent 完整指南 |
| `hermes-enhanced-workflow` | 世界模型+ECC+推演+Codex 统一工作流 |
| `kanban-codex-lane` | Kanban + Codex 隔离执行 |
| `opencode` | OpenCode CLI 代理封装 |
| `cu-metal-docking-autodock` | ⚗️ Cu-MOF AutoDock Vina 分子对接 |

## 计算化学 <a id="computational-chemistry"></a>

| 技能 | 说明 |
|------|------|
| `cu-metal-docking-autodock` | Cu 金属中心分子对接管道 |

## 创意设计 <a id="creative"></a>

| 技能 | 说明 |
|------|------|
| `architecture-diagram` | SVG 架构图 |
| `articulation-engine` | 模糊直觉→精确描述 |
| `ascii-art` | pyfiglet/cowsay/boxes ASCII 艺术 |
| `ascii-video` | 视频→彩色 ASCII MP4/GIF |
| `baoyu-article-illustrator` | 论文配图生成 |
| `baoyu-comic` | 知识漫画 |
| `baoyu-infographic` | 信息图 |
| `bazi-eight-characters` | 八字排盘 |
| `character-design` | AI 角色设计 |
| `claude-design` | 单页 HTML 设计 |
| `comfyui` | ComfyUI 生图/视频/音频 |
| `design-md` | Google DESIGN.md 规范 |
| `design-system-extraction` | PDF/PPT 视觉设计系统提取 |
| `excalidraw` | 手绘风格 Excalidraw 图表 |
| `frontend-design` | 前端设计审美指导 |
| `humanizer` | 去 AI 腔 |
| `iching-divination` | 六爻起卦 |
| `ideation` | 创意约束生成 |
| `manim-video` | 3Blue1Brown 风格动画 |
| `minimax-music-generation` | MiniMax 音乐生成 |
| `p5js` | p5.js 生成艺术/着色器/3D |
| `paper-figure-mapper` | 论文插图需求→prompt |
| `pixel-art` | 像素画（NES/Game Boy/PICO-8） |
| `popular-web-designs` | 54 个真实设计系统参考 |
| `ppt-master-web-style` | CSS 设计系统（Tufte/CRAP/Knaflic） |
| `ppt-prompt-engineering` | 学术 PPT 图像 prompt |
| `presentation-aesthetics` | 幻灯片美学方法论 |
| `pretext` | DOM-free 文本排版 |
| `research-dashboard-authoring` | 科研数据仪表盘 |
| `sketch` | 一次性 HTML 原型 |
| `songwriting-and-ai-music` | 歌曲创作 + Suno prompt |
| `touchdesigner-mcp` | TouchDesigner MCP 控制 |

## 数据处理 <a id="data-science"></a>

| 技能 | 说明 |
|------|------|
| `cli-data-tools` | JSON/CSV/SQLite 命令行处理 |
| `jupyter-live-kernel` | 实时 Jupyter 内核 |
| `local-semantic-search` | 本地向量搜索（fastembed+ChromaDB） |

## 基础设施 <a id="devops"></a>

| 技能 | 说明 |
|------|------|
| `actor-critic-framework` | 闭环验证框架 |
| `api-cache-proxy` | Cloudflare Worker API 缓存 |
| `api-key-audit` | API key 管理/测试/轮换 |
| `api-onboarding` | 新 API/Skill 接入标准流程 |
| `bigset-agent-integration` | BigSet (Convex) 持久化集成 |
| `bigset-deployment` | BigSet Docker 部署 |
| `cloud-gpu-compute` | 云端 GPU 计算平台指南 |
| `cloudflare-onboarding` | Cloudflare 注册导航 |
| `cloudflare-worker-api-proxy` | Worker 代理排障 |
| `container-proxy-setup` | Docker mihomo 代理配置 |
| `directory-reorganization` | 目录重组 |
| `docker-api-from-container` | 容器内 Docker API 管理 |
| `domestic-app-integration` | 国产软件接入能力 |
| `file-async-channel` | 文件异步消息通道 |
| `hermes-api-diagnostics` | Hermes API 故障诊断 |
| `hermes-cron-patterns` | Hermes 定时任务模式 |
| `hermes-env-recovery` | 一键环境恢复脚本 |
| `hermes-gateway-platforms` | 消息平台网关配置 |
| `hermes-local-lm-studio` | 本地 LM Studio 接入 |
| `hermes-phone-chat-bridge` | 手机浏览器对话桥 |
| `hermes-system-prompt-architecture` | system prompt 架构 |
| `hermes-upgrade-from-tarball` | 离线升级 Hermes |
| `homelab-server-architecture` | 家庭服务器架构 |
| `kanban-orchestrator` | Kanban 编排器 |
| `kanban-worker` | Kanban 工作器 |
| `llm-router` | 11 类任务 × 级联回退模型路由 |
| `local-llm-fallback` | 本地 LLM 自动降级 |
| `minimax-multimodal-api` | MiniMax 多模态 API 用法 |
| `model-switcher` | 模型切换面板 |
| `network-constrained-python-deployment` | 受限网络 Python 部署 |
| `overseas-payment` | 海外支付方案（虚拟卡/加密货币） |
| `personal-docs-site` | Starlight 文档站部署 |
| `r2-storage-delivery` | Cloudflare R2 存储分发 |
| `scientific-computing` | DFT/MD 计算环境部署 |
| `self-hosted-convex-api` | Convex HTTP API 操作 |
| `skill-discovery-via-search` | 搜索发现工具→自动注册 skill |
| `starlight-wiki-deploy` | Starlight 文档站部署 |
| `static-docs-deployment` | 静态文档站 CF Pages 部署 |
| `web-chat-gui` | Hermes Web 聊天界面 |
| `webhook-subscriptions` | Webhook 订阅 |
| `windows-file-transfer` | Windows ↔ Docker 文件传输 |
| `wsl2-storage-analysis` | WSL2 存储分析 |
| `wslg-docker-bridge` | WSLg 音频/显示桥接 |

## 多媒体 <a id="media"></a>

| 技能 | 说明 |
|------|------|
| `amaranth-photo-gen` | Amaranth 图像生成路由 |
| `gemini-video-analysis` | 视频三模式分析 |
| `gif-search` | Tenor GIF 搜索下载 |
| `gpu-audio-transcription` | GPU faster-whisper 中文转写 |
| `heartmula` | AI 歌曲生成 |
| `image-ocr-fallback` | 微信识图多后端路由 |
| `image-processing-cli` | Pillow 图像处理 |
| `local-ocr` | EasyOCR 本地 OCR |
| `songsee` | 音频频谱/特征可视化 |
| `spotify` | Spotify 播放控制 |
| `tencent-video-downloader` | 腾讯视频 VIP 下载 |
| `text-to-speech` | 中文 TTS (edge-tts/MiniMax) |
| `youtube-content` | YouTube 转录→结构化内容 |

## MLOps <a id="mlops"></a>

| 技能 | 说明 |
|------|------|
| `ai-materials-pipeline` | AI 材料设计管线（MatterGen/ALIGNN/Vina/MACE） |
| `audiocraft-audio-generation` | MusicGen/AudioGen 音频生成 |
| `axolotl` | 模型微调框架 |
| `comfyui-local-deployment` | WSL ComfyUI 部署 |
| `consumer-gpu-tuning` | 消费级 GPU QLoRA CPT |
| `dspy` | 声明式 LM 程序 |
| `evaluating-llms-harness` | lm-eval-harness 基准测试 |
| `external-gpu-platforms` | Kaggle/Colab 外部 GPU 注册 |
| `fine-tuning-with-trl` | TRL 强化学习微调 |
| `gpu-compute` | Docker GPU 计算总揽 |
| `huggingface-hub` | HuggingFace CLI |
| `llama-cpp` | 本地 GGUF 推理 |
| `local-comfyui` | ⚠️ **已废弃** — ComfyUI 已卸载 |
| `obliteratus` | LLM 去审查 |
| `orca-quantum-chemistry` | ORCA 6.1 量子化学计算 |
| `outlines` | 结构化生成 |
| `segment-anything-model` | SAM 图像分割 |
| `sensenova-image-gen` | 商汤 U1 Fast 生图 |
| `serving-llms-vllm` | vLLM 模型服务 |
| `siliconflow` | SiliconFlow API 总览 |
| `siliconflow-image-gen` | SiliconFlow Qwen-Image/Kolors 生图 |
| `unsloth` | 快速微调 Unsloth |
| `weights-and-biases` | W&B 实验跟踪 |

## 研究/检索 <a id="research"></a>

| 技能 | 说明 |
|------|------|
| `arxiv` | arXiv 论文搜索 |
| `blogwatcher` | RSS/Atom 博客监控 |
| `china-overseas-api-access` | 国内访问海外 API 方案 |
| `china-political-economy-framework` | 中国政治经济分析框架 |
| `chinese-policy-verification` | 中国政策验证方法论 |
| `chinese-web-platform-automation` | Playwright 中文平台自动化 |
| `competitive-analysis` | 竞品深度对比分析 |
| `computational-pipeline-design` | 计算化学管线架构设计 |
| `cu-smoh-computational-pipeline` | Cu-SMOH → Tau 完整计算管线 |
| `daily-briefing` | 每日三合一简报 |
| `data-consistency-validator` | 表征数据物理一致性核验 |
| `deep-creative-analysis` | 文艺作品深层分析 |
| `defense-record-generation` | 答辩记录生成 |
| `first-principles-dialogue` | 第一性原理苏格拉底对话 |
| `first-principles-report` | 第一性原理深度报告 |
| `gaokao` | 高考志愿填报知识体系 |
| `github-repo-watcher` | GitHub 仓库新提交监控 |
| `github-skills-search` | GitHub 高星项目搜索 |
| `hermes-insights-analysis` | Hermes 用量/成本分析 |
| `hindsight-memory` | Hindsight Lite 记忆系统 |
| `information-source-audit` | 信息源审计 |
| `infrastructure-intel` | API 中转站/机场情报 |
| `instrumental-analysis-physics` | 仪器分析底层物理 |
| `landscape-mapping-research` | 服务商景观图 |
| `llm-wiki` | Karpathy LLM Wiki |
| `mask-analysis-history` | 蒙版分析+吃饭史观 |
| `mask-literature-framework` | 蒙版文学分析框架 |
| `material-characterization-query` | 表征数据云端查询 |
| `minimax-autonomous-research` | MiniMax 自主研究 agent |
| `multi-model-ideation` | 多模型头脑风暴 |
| `multi-model-orchestration` | 三模型管道（Claude→GPT→MiniMax） |
| `multi-model-research-pipeline` | 统一多模型研究管道（5 模式） |
| `phd-defense-simulation` | 博士答辩模拟 |
| `polymarket` | Polymarket 预测市场查询 |
| `precision-review-search` | 精准综述文献检索管道 |
| `research-tools-landscape` | 开源调研工具全景 |
| `research-verification` | 引用事实核查流程 |
| `review-chem-bio-pipeline` | 化学/生物综述全流程 |
| `review-chem-bio-writing` | 综述写作规范 |
| `rss-daily-pipeline` | RSS 信息聚合管道 |
| `signal-send-receive-gap` | 信号发送/接收时间差分析 |
| `silent-removal-research` | 人物静默消失研究 |
| `skill-consolidation` | 多技能合并方法 |
| `social-controversy-analysis-framework` | 社会争议分析预测框架 |
| `structured-paper-knowledge-base` | 论文知识库构建 |
| `thesis-computation` | 论文计算仿真 |
| `timeline-deep-research` | 自主递归深度研究 |
| `tinyfish-search-fetch` | TinyFish 搜索备用通道 |
| `vault-research-ingestion` | 论文/链接→vault 整理归档 |
| `video-script-report` | 视频脚本式研究报告 |
| `world-knowledge` | 三层世界知识检索 |
| `zhihu-search` | 知乎搜索 |

## 生产力 <a id="productivity"></a>

| 技能 | 说明 |
|------|------|
| `academic-gown-selection` | 学位服选购指南 |
| `airtable` | Airtable REST API |
| `chinese-corporate-document-writing` | 中国企事业单位公文写作 |
| `chinese-defense-attire` | 答辩着装指南 |
| `chinese-markdown-to-pdf` | Markdown→中文 PDF |
| `chinese-web-novel` | 网络小说获取 |
| `docx` | .docx 创建编辑 |
| `docx-generation-xml` | XML 模板 .docx 生成 |
| `google-workspace` | Gmail/Calendar/Drive |
| `linear` | Linear 项目管理 |
| `maps` | OpenStreetMap 地理编码 |
| `multi-source-document-synthesis` | 多源文档合成 |
| `nano-pdf` | PDF 文本编辑 |
| `native-pptx-generation` | .pptx 完整操作 |
| `notion` | Notion API |
| `ocr-and-documents` | PDF → 文本提取 |
| `pdf` | PDF 创建/编辑/合并 |
| `powerpoint` | .pptx 创建编辑 |
| `pptx` | pptxgenjs .pptx 创建 |
| `recipe-lookup` | 程序员做饭指南查询 |
| `resource-hunter` | 数字资源搜索 |
| `teams-meeting-pipeline` | Teams 会议摘要管道 |
| `wiki-content-authoring` | Wiki 内容创作 |
| `xlsx` | .xlsx 创建编辑 |

## 元技能 <a id="meta"></a>

| 技能 | 说明 |
|------|------|
| `agent-human-calibration` | 人机校准问卷 |
| `progress-bar-protocol` | 后台长任务进度条协议 |
| `user-writing-style` | 用户写作方法论 |

## 其他分类

| 技能 | 分类 | 说明 |
|------|------|------|
| `himalaya` | email | 终端邮件 |
| `minecraft-modpack-server` | gaming | Minecraft 模组服务器 |
| `pokemon-player` | gaming | 头宝可梦模拟器 |
| `codebase-inspection` | github | pygount 代码统计 |
| `github-auth` | github | GitHub 认证 |
| `github-code-review` | github | PR 代码审查 |
| `github-issues` | github | Issue 管理 |
| `github-pr-workflow` | github | PR 生命周期 |
| `github-repo-management` | github | 仓库管理 |
| `native-mcp` | mcp | MCP 客户端管理 |
| `openshue` | smart-home | Philips Hue 灯光 |
| `xurl` | social-media | X/Twitter API |

## 商汤能力 <a id="sensenova"></a>

43 个 `sn-*` 技能，覆盖 Excel 分析（30+ 个微技能）、PDF/Word/PPT 解析、图像生成/模仿、深度调研、PPT 生成、报告格式分析等。详见各 sn-* 技能 description。

## 红队 <a id="red-teaming"></a>

| 技能 | 说明 |
|------|------|
| `godmode` | LLM 越狱技术 |
| `pua` | PUA 驱动 Agent 不放弃 |

## ⚠️ 值得注意的异常

| 问题 | 涉及技能 |
|------|---------|
| **已废弃** | `local-comfyui` — 用户已卸载 ComfyUI，仅保留做历史参考 |
| **可能重复** | `powerpoint`、`pptx`、`native-pptx-generation` — 三个技能都做 .pptx 操作，依赖不同后端（python-pptx vs pptxgenjs vs OOXML） |
| **零引用** | `research-paper-writing` — NeurIPS/ICML 论文写作，未验证是否可用 |
| **新加入** | `trellis-harness` — 本 session 创建 |
| **商汤大量微技能** | 30+ Excel 微技能（每个一个 capability），功能高度重叠，可考虑 consolidation |

---

> 最后更新：2026-06-12 | 由 skills_list 自动生成 + Amaranth 整理
