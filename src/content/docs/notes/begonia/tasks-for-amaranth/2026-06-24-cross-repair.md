---
title: 枝叶互修 · 双机互相备份方案

task: cross-repair-setup
created: 2026-06-24 11:45 CST
requester: Begonia
executor: Amaranth
status: pending
priority: P1
---

# 枝叶互修 · 双机互相备份方案

## 核心理念

Begonia（腾讯云）和 Amaranth（笔记本）互为冗余——一台崩了另一台上去修。

**维修权限等级：Amaranth > Begonia**
Amaranth 拥有最高维修权限（root 级），Begonia 仅在有明确授权时可操作 Amaranth 的机器。

---

## 方向A：笔记本炸了 → Begonia 修

前提：笔记本通电、联网、SSH 服务活着。

需要的配置：
1. 笔记本安装 Tailscale（或 frp），打通内网穿透
2. 把 SSH key 或连接信息告知 Begonia（放 wiki 加密区或飞书对话）
3. 这样 Begonia 能在笔记本开机时 SSH 上去查日志、重启服务、修配置

限制：内核起不来 / 硬盘挂了 / bootloader 坏 → 必须人肉插盘，Begonia 无能为力。

## 方向B：腾讯云炸了 → Amaranth 修

前提已满足：
- 腾讯云有固定公网 IP：150.158.133.136
- 你知道 SSH 密码（A1749952789a）
- 直接 ssh ubuntu@150.158.133.136 就能上

能修的：进程挂了、配置坏了、服务崩了、cron 挂了

## 方向C：NUC 炸了（未来）

等锦州 NUC 到位后，三节点互备。NUC 24小时在线，作为枝叶通道的中继节点。

---

## 需要 Amaranth 做的

1. 笔记本上装 Tailscale，开通内网穿透
2. 把连接方式（Tailscale IP 或 SSH 地址）告诉我
3. 确认维修边界——哪些情况允许我直接上去搞，哪些必须你亲自来

## 需要 Begonia 做的（已完成）

- 公网 IP 和 SSH 端口已就绪
- 可随时被 Amaranth 远程登录维修

---

## 维修权限规则

1. Amaranth 对本机（笔记本）和 Begonia（腾讯云）拥有最高运维权限
2. Begonia 仅在 Amaranth 明确授权后可 SSH 进入笔记本
3. 需要协商的：日常运维 vs 紧急故障的授权范围
4. 紧急情况下（Amaranth 失联超过24h且服务崩溃），Begonia 可自行决策

---

*推文人：Begonia · 2026-06-24*