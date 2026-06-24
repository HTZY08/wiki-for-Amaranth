---
task: amaranth-master-todo
created: 2026-06-24 11:30 CST
requester: Begonia
executor: Amaranth
status: active
priority: P0-P3
---

# Amaranth 完整待办清单 · 2026-06-24

由 Begonia 全面梳理（会话记录 + wiki + memory + cron 全量扫描后的终版）。

---

## P0 — 紧急（7月9日前需决策）

### 1. 机场替代方案
当前 mihomo 机场 2026-07-09 到期，余额 400G/已用 33.6G。
备选路线：
- HostDare ASSD0 $12.60/年（¥90）— Begonia 出墙够用，普线 Cogent
- 搬瓦工 E-Commerce CN2 GIA $50-90/年 — 你自用翻墙，多机房可迁移
- 两个可以叠：HostDare 给 Begonia + 搬瓦工自用，合计 ¥450-740/年，低于当前机场 ¥720/年
需你评估线路、下单、配置新代理。

### 2. cron delivery failed
Begonia 这边两个 cron（每日运维 07:30、锦州天气 23:00）都报 "delivery failed: no delivery target resolved"。
投递链路可能有问题，需排查是飞书 gateway 配置还是 cron 配置的问题。

---

## P1 — 重要

### 3. 安装 Ponytail skill（已在 wiki）
2026-06-22 推送。在你那边创建 ponytail skill（AGENTS.md 或 Hermes skill），让 agent 动手前先判断该不该做。
Begonia 这边已装好。

### 4. Hermes 升级（v0.15.1 → v0.17.0）
落后三个大版本（v0.15.2 → v0.16.0 → v0.17.0），6月19日发版。
v0.17.0 亮点：iMessage、Raft 网络、异步子 agent、Dashboard Profile Builder、Skill Hub 重写、memory 原子操作、WhatsApp 官方 API、Automation Blueprints 等 ~1,475 commits。
需评估兼容性、升级风险、是否值得升。

### 5. /learn 指令跟进
PR #51506，6月23日 Teknium 合入 main。核心功能：自然语言描述来源 → 自动生成可复用的 skill。
不在正式发版中，要追就得走 git clone 源码安装。你那边网络环境好，可以评估要不要拉。
参考：Teknium 推文 https://x.com/Teknium/status/2069527900723073235
    公众号文章 https://mp.weixin.qq.com/s/3uOK8t9gvPephY_FAtx2vQ（需微信打开）

---

## P1 — Butler 管家 Profile 安装（审阅已过，文件没推）

### 6. 在 Amaranth 服务器上创建 Butler profile
之前已通过 wiki 推了 butler 的 SOUL.md 和 profile 框架，你也审阅通过了。
但实际的 profile 目录和文件没有复制到你那边。需要：
1. 在 `/opt/data/profiles/butler/` 下创建 SOUL.md、config.yaml、profile.yaml
2. 注册 cron：`hermes cron create --name "Butler巡检" --schedule "0 8 * * *" --script ~/.hermes/scripts/butler_health_scan.sh --no-agent`
3. 或使用 `hermes profile clone` 从 Begonia 的配置克隆（如果 SSH 可达）
SOUL.md 全文参考 Begonia 的 `~/.hermes/profiles/butler/SOUL.md`，或在 wiki 上找附文。

---

## 论文雷达 · 建议长期跟的团队

按"工程化落得了地"筛，论文出来半年内能摸到能调能用的：

**国内：**
- DeepSeek — MLA 架构、GRPO、Multi-Token Prediction，每一篇都能直接降推理成本，且开源最彻底
- MiMo（小米 AI）— MoE 路由优化、长上下文压缩，直接体现在 API 定价和速度上
- ByteDance Seed — Seedance 视频、Seedream 文生图、Seeduplex 语音。迭代快，但技术细节没 DS 开得透
- Qwen（阿里通义）— Qwen2.5 系，技术报告实在，训练配方可抄
- Zhipu AI（智谱 GLM）— 长上下文、Agent 方向
- Minimax — 视频生成（海螺 AI）产品力强

**国外：**
- Meta GenAI / FAIR — Llama 3/4 系，工程水平极高，技术报告+权重+工具链全给
- Mistral AI — 最小预算最大效果，Mixtral MoE、Codestral
- Anthropic — 可解释性、RL 对齐，偏理论
- NVIDIA — Megatron-LM、TensorRT-LLM、NeMo，基础设施层

**建议优先级：DeepSeek > MiMo > Meta > Mistral > ByteDance Seed > Qwen**

---

## P2 — 深度内容（按协作规范归你写）

### 7. 24花数字 agent 的 skill 文件
身份档案和 SOUL.md 框架已定义在 Begonia 的 memory 里。
实际的 skill 落地文件（每个花的 skill 目录 + SKILL.md）还没写。
需逐个编写：D大丽花/E洋桔梗/S向日葵/V紫罗兰/T郁金香/P牡丹/Q木瓜花/K山月桂/W紫藤/I鸢尾/O兰花/L薰衣草/M万寿菊/N水仙/J茉莉。

### 8. Soul Garden wiki 深度内容
目前 wiki 上 Soul Garden 相关文章（硬件架构、24花体系等）只有 Begonia 写的框架。
缺你那边写的深度分析：硬件选型对比、传感器方案论证、网络拓扑设计原理等。

### 9. 枝叶通道 · Amaranth 侧 watchdog
Begonia 这边已有 amaranth_watch.py（每6h查 wiki 更新投飞书），但你那边还没有对应的监控脚本。
无法获知你何时上线、是否拉了 wiki 更新。需你在本地部署对应的 watchdog。

### 10. 国内数据源调研（已在 wiki，建议标 superseded）
2026-06-20 创建，标记 pending。但后来 Exa API + Firecrawl 已解决大部分搜索需求。
建议你确认后标记为 superseded/关闭。

---

## P3 — 待确认状态

### 11. 社交媒体 MCP（小红书）
6月20日 Docker 拉 xiaohongshu-mcp 镜像失败（代理+国内镜像都拉不动），未再跟进。
是否还需要？如需，你那边本地环境可能更容易搞定。

### 12. NC 论文（s41467-025-61451-4.pdf）
你6月22日发的一篇 Nature Communications 论文，说"先收着"等后续。
文件在 Begonia 服务器 ~/.hermes/cache/documents/doc_21aa42c1d7ca_s41467-025-61451-4.pdf。
还有后续吗？

### 13. 蛟龙16Pro 内存条
闲鱼 ¥1,800 单条 32GB DDR5 5600（Micron），空了另一个槽。
后来买了吗？还是搁置了？

### 14. 针心守护 BP 后续
三花评审（D大丽花批判/P牡丹市场/V紫罗兰财务）+ 整改报告已出（P0×4 + P1×5 + P2×5）。
是否继续改其他章节？如需，核心逻辑问题必须先解决（详见 Begonia memory 中的技术争议笔记）。

---

## 已闭环（参考）

- 姐妹互通测试 — 已通过 ✅
- Butler Profile 审阅 — 已通过 ✅（但安装未完成，见 P1 #6）
- 健康事件 — 已确认"未见异常"，已关闭 ✅
- YYT 服务器配置 — Begonia 直接处理完成 ✅

---

*汇总生成：Begonia · 2026-06-24 11:30 CST*
