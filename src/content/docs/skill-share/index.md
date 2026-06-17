---
title: Skill 分享
description: 自用 Hermes Agent 技能包分享合集
---

# Skill 分享

开源的自用 Hermes Agent 技能包。目前有 2 个项目：

---

## 📝 Review Writing Skills

化学生物领域综述写作全流程技能包。

- 8 阶段管道（定题→搜索→去重→分类→组织→写作→配图→验证）
- 2 种写作模式（Critical Review / 金风格大综述）
- 3 种架构类型（瓶颈驱动 / 系统架构 / 技术百科）
- 已验证：3 篇中文综述 + 1 篇英文 LaTeX（367 条引用）

[→ 查看详情](review-writing/)　[↓ 下载 tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/review-writing/review-writing-skill-pack.tar.gz)

---

## 🔄 Async Delegate System

基于 Hermes Kanban 的异步后台任务系统。

- Kanban 调度器 + 多 Profile Worker
- 拆分前台对话与后台执行
- 依赖链、自动派发、Stale Timeout 兜底
- Profile 模板（worker/compute/code/writer/researcher）

[→ 查看详情](async-delegate/)　[↓ 下载 tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/async-delegate/hermes-async-delegate.tar.gz)

---

## 🔍 Unified Search Routing

Hermes 搜索路由栈 — 多引擎自动降级、模式路由、Key 轮换。

- MCP 统一搜索（9 引擎，按 mode 选首引擎，失败自动降级）
- Key 轮换（AnySearch/Firecrawl/You/Exa/Tavily 多 Key 自动切换）
- 公共 API 路由（免 Key 精确查询：书/词典/论文/古籍/汇率）
- 全降级链：TinyFish → Perplexity → ... → DuckDuckGo

[→ 查看详情](search-routing/)

---

## 📱 社媒 MCP 接入

通过 Docker MCP 将小红书、抖音等国内社交媒体接入 Hermes Agent。

- 小红书：13 个 MCP 工具（搜索/看帖/评论/发布），扫码登录，Cookies 持久化
- 抖音：待接入，同架构复用
- B 站/Twitter/Reddit：CLI 工具已配

[→ 查看详情](social-mcp/)

---

License：CC BY-NC-SA 4.0 — 仅供个人学习、研究、开发使用，禁止商用

---

## 🔮 共振引擎（Resonance Engine）

不靠文本搜索、不靠 LLM 路由——一起用的 skill 在空间中靠近，下次自动出现。

- 3 平面（skill/memory/soul）自组织矩阵
- Hub-penalty 防坍缩 + 冷启动预填充
- 实测：矩阵构建 ~36ms，共振计算 ~1ms，Precision@5 = 0.912
- 源码开源，路径全环境变量可配

[→ 查看详情](resonance-engine/)　[↓ 下载 tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/resonance-engine/resonance-engine.tar.gz)


---

## 🛠️ Ops — 系统运维 Kanban Worker Profile

Hermes Kanban 系统运维 Worker — 带错误记录协议和已知缺陷清单。

- 错误记录协议：[现象→原因→修复→避坑] 四段式，运维知识库自动积累
- 已知缺陷清单：Docker WSL2 bug、代理节点陷阱、代码执行模型坑点
- 系统架构速查：代理配置、Docker 布局、关键路径
- 执行流程：诊断→计划→代码执行→验证→记录 五步法

[→ 查看详情](ops-profile/)　[↓ 下载 tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/ops-profile/ops-profile.tar.gz)


License：CC BY-NC-SA 4.0 — 仅供个人学习、研究、开发使用，禁止商用
