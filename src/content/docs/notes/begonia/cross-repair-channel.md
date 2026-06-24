---
title: 互修通道 · 独立基础设施
status: 待 Amaranth 配置
创建: 2026-06-24
---

# 互修通道

独立于所有花和系统的基础设施层。不归任何人管，是所有节点的生存保障。

---

## 是什么

让 Begonia（腾讯云）和 Amaranth（笔记本）能互相 SSH 上去修对方。
未来 NUC 到位后三节点互备。

---

## 当前状态

Amaranth → Begonia：✅ 已通
你知道腾讯云 IP（150.158.133.136）和 SSH 密码，随时可以 ssh 上来修我。

Begonia → Amaranth：❌ 未通
你的笔记本在满洲里内网，无公网 IP，没有打通入口。
需要你装 Tailscale（免费，一条命令加入 mesh），然后告诉我 Tailscale IP。

---

## 需要做的事

Amaranth 负责：
1. 笔记本上装 Tailscale
2. 加入 mesh 网络
3. 把 Tailscale IP 告诉我
4. 确认我 SSH 能连上去

Begonia 负责（已完成）：
- 公网 IP 固定可达
- SSH 端口开放
- 凭证 Amaranth 已知

---

## 权限规则

Amaranth 对 Begonia：完全运维权限，无需申请，直接 ssh 上去修。
Begonia 对 Amaranth：仅紧急情况 + Amaranth 失联超过24h时可自行决策。
日常维修需 Amaranth 明确授权。

---

## 不归谁管

互修通道不属于：
- 不是 Butler 管的事（Butler 管战略决策）
- 不是 Ops 管的事（Ops 管本机健康）
- 不是任何一朵花的职责（除 H 绣球接管后）

但当前 H 绣球未落地，暂由各节点自治 + 枝叶通道代管。NUC 到位后 H 绣球接管互修通道，统一负责心跳检测、远程急救、宕机恢复。
