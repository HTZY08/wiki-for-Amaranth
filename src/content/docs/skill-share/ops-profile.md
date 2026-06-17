---
title: Ops — 系统运维 Kanban Worker Profile
description: Hermes Kanban 系统运维 Worker — 错误记录协议、已知缺陷清单、执行流程模板
---

# Ops — 系统运维 Kanban Worker Profile

> 专精 Docker 容器管理、代理运维、系统监控与故障恢复的 Kanban Worker 模板。附带完整的**错误记录协议**和**已知系统缺陷清单**——踩过的坑不再踩第二遍。

**GitHub 仓库：** [`HTZY08/wiki-for-Amaranth` → `static/skills/ops-profile/`](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/ops-profile)

**直接下载：** [`ops-profile.tar.gz`](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/ops-profile/ops-profile.tar.gz)（8.2KB）

**License：** CC BY-NC-SA 4.0

---

## 这个 Profile 做什么

Ops 是为 Hermes Kanban 系统设计的运维 Worker Profile。它的核心价值在于**系统化地记录和管理基础设施缺陷**——每次踩坑都有结构化的 [现象→原因→修复→避坑] 记录，日积月累形成运维知识库。

区别于临时脚本运维，Ops Worker 的优势：
- **持久记忆**：每次修复自动记录，下次同类问题秒级回忆
- **已知缺陷清单**：系统层面已有的 bug 和工作区，诊断时先排查
- **操作前先出计划**：破坏性操作必须出计划再执行

## 包含的文件

| 文件 | 功能 |
|------|------|
| **SOUL.md** | Profile 核心定义：错误记录协议、系统架构速查、已知缺陷清单、执行流程、操作规则 |
| **profile.yaml** | Profile 声明文件（description + 自动描述开关） |
| **config.yaml** | Hermes 配置：模型选择、工具集、内存设置 |

## 快速开始

```bash
# 下载并解压
wget https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/ops-profile/ops-profile.tar.gz
tar xzf ops-profile.tar.gz -C ~/.hermes/profiles/ops/

# 创建 Profile（Hermes 0.16+）
hermes profile create ops

# 或者手动拷贝
cp -r ops-profile/* ~/.hermes/profiles/ops/
```

## 核心设计：错误记录协议

这是 Ops Profile 的灵魂。每次运维操作后，按四段式写入持久记忆：

```
[现象] Docker 容器内读宿主机大文件只返回 16 字节
[原因] WSL2 bind mount 读取大文件有 bug
[修复] 改用 pipe 注入：cat file | docker exec -i sh -c 'cat > dest'
[坑] 修完后必须 wc -c 验证大小
```

这种格式的价值：
- **秒级回忆**：下次同样现象 → 直接命中修复方案
- **根因驱动**：不是"重启解决了"，是"因为 X 所以 Y"
- **可积累**：运维越久，知识库越厚，修复速度越快

## 已知缺陷清单

Profile 自带一份常见系统缺陷清单（必读）：

- **Docker Desktop WSL2 大文件读取 bug** — bind mount 只返回 16 字节
- **代理端口在 WSL2 上绑定 IPv6** — bridge 模式可解
- **代理重启后节点重置** — 需手动切回锁定节点
- **代码执行模型在非 git 目录下报错** — 先 git init
- **带宽限速导致流式响应超时** — 切低延迟节点

缺陷清单随着记忆积累自动扩展——Ops Worker 每次发现新坑都会自动追加到记忆。

## 链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [github.com/HTZY08/wiki-for-Amaranth](https://github.com/HTZY08/wiki-for-Amaranth) |
| Profile 文件目录 | [static/skills/ops-profile/](https://github.com/HTZY08/wiki-for-Amaranth/tree/main/static/skills/ops-profile) |
| 直接下载 tar.gz | [ops-profile.tar.gz](https://github.com/HTZY08/wiki-for-Amaranth/raw/main/static/skills/ops-profile/ops-profile.tar.gz) |
| License | CC BY-NC-SA 4.0 |
