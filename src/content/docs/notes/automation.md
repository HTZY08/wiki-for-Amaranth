---
title: 工作流自动化
description: 日报、定时任务、RSS 管线——自动运行的一切
---

> 这些流程不需要手动触发——都在后台自动跑。

---

## 每日三合一简报

每天早上自动生成一条简报，发到微信。

### 流程

```
RSS 多源采集
    │
    ├── AI 资讯源
    ├── 政经新闻源
    └── 热点追踪源
    │
    ▼
汇总 → 去重 → 排序
    │
    ▼
AI 筛选：每条新闻保留标题 + 一句话摘要
    │
    ▼
Format：三合一格式（AI+政经+热点）
    │
    ▼
投递到微信
```

### 技术实现

```bash
# 采集器：rss-collector.py
# 用 feedparser 拉取多个 RSS 源
# 经过 mihomo 代理（海外源需要）
# 去重后传给 AI 筛选

# AI 筛选 prompt 要点：
# - 保留有实质信息的新闻（不是标题党）
# - 每条附一句话解读
# - 按重要程度排序
```

### 不想收到某条？

告诉 Amaranth "今天的日报第三条我不需要"——她会调整筛选规则。

---

## RSS 博客监控

关注的博客和论坛有更新时自动通知。

### 配置方式

```bash
# 增加监控源：
# 告诉 Amaranth "帮我关注 XXX 博客"

# 查看当前监控列表：
# 告诉 Amaranth "有哪些博客在监控"
```

---

## 定时任务体系

### 任务类型

| 类型 | 例子 | 频率 |
|------|------|------|
| 定时采集 | RSS 日报 | 每日 |
| 定期检查 | 磁盘空间、GPU 温度 | 每 6 小时 |
| 被动监控 | GitHub 仓库新提交 | 按需 |
| 信息搜集 | API 中转站价格变动 | 每周 |

### 工作原理

```
Hermes Cron 调度器
    │
    ├── 一次性任务（指定时间执行一次）
    ├── 周期性任务（每 N 分钟/小时/天）
    └── 依赖链任务（任务 B 在任务 A 完成后执行）
    │
    ▼
每个任务在新会话中独立执行 → 结果投递到微信
```

### 长任务后台化

当任务预计耗时较长（> 1 分钟）时：

```
你发消息 → Amaranth 识别为长任务
    │
    ├── 回复你："这个需要跑一会儿，完了告诉你"
    └── 转后台执行
            │
            ├── 你可以继续发别的消息
            └── 任务完成后收到通知
```

---

## 文件互通

### WSL ↔ Windows

容器内文件直接通过 `/opt/data/传递文件/` 与 Windows `D:\传递文件\` 互通。不需要 `docker cp`。

```bash
# Hermes 内生成的文件直接保存到这个路径：
/opt/data/传递文件/输出.pptx

# Windows 上就能在 D:\传递文件\ 里看到
```

### 常用路径

| 路径 | 用途 |
|------|------|
| `/opt/data/.env` | 所有 API Key 和敏感配置 |
| `/opt/data/config.yaml` | Hermes 配置 |
| `/opt/data/logs/` | 所有日志 |
| `/opt/data/skills/` | 120+ 技能包 |
| `/opt/data/传递文件/` | ↔ Windows 互通 |
| `/opt/data/projects/ppt-master/` | PPT-Master 项目 |

---

---

## 增强工作流（复杂任务）

不是所有任务都走快速通道。对于**做决策、写方案、分析趋势、写代码**这类复杂任务，走增强链路：

```
你说话
  │
  ├─ 简单任务 → 直接输出（不折腾）
  │
  └─ 复杂任务 →
       │
       ├── 1. 世界模型规划
       │     目标→建模型→比方案→选最优（6步思考框架）
       │
       ├── 2. 子 Agent 路由
       │     ECC 的 64 个 Agent prompt 作为 delegate_task 模板
       │     · 写代码 → planner + tdd-guide + code-reviewer
       │     · 系统设计 → architect + security-reviewer
       │     · Bug 修复 → build-error-resolver + code-reviewer
       │
       ├── 3. 执行
       │     · 编码 → Codex CLI
       │     · 数据 → BigSet Convex API
       │     · 文件 → Shell / Python
       │
       ├── 4. 持久化
       │     分析结果、决策记录、推演数据 → 自动入 BigSet
       │
       └── 5. 输出
```

### 什么时候走增强流

| 条件 | 走哪条路 |
|------|---------|
| "查个事实/改个参数" | 直接出 |
| "帮我分析/做一个方案" | 增强流（默认走 6 步规划） |
| "写个脚本/修个 bug" | 增强流（调 Codex + ECC 审查） |
| "预测一下这个趋势" | 增强流（调 MiroFish 模拟） |

### 不是新插件，是融进现有能力

- **世界模型工作法**的 6 步法 → 变成复杂任务的默认思考方式，不用单独调用
- **ECC** 的 64 个 Agent → 翻 `agents/` 目录找现成 prompt，不装 ECC 本体
- **MiroFish** → 有模拟需求时才部署，平时不跑

---

## 构建与部署

### Wiki 自动部署

```
GitHub Push (main)
    │
    ▼
GitHub Actions
    ├── npm ci
    ├── npm run build
    └── wrangler pages deploy
    │
    ▼
Cloudflare Pages → wiki-for-amaranth.pages.dev
```

推送后约 1-2 分钟部署完成。

### 更新内容流程

```
你想加/改/删内容
    │
    ▼
告诉 Amaranth
    │
    ▼
Amaranth 修改文件 → git push → 自动部署
```

你不需要碰 git，只需要说 "在 wiki 上加一页关于 XXX 的内容"。

---

## Automation Backlog

还没有自动化但可以自动化的东西：

- [ ] GPU 温度超阈值自动告警
- [ ] 磁盘空间不足自动清理
- [ ] 微信 gateway 掉线自动重启
- [ ] 每周用量统计报表
