---
title: "枝叶通道 — 枝干 SOUL.md ↔ 细则源文件映射"
---

# 枝叶通道 — 枝干 SOUL.md ↔ 细则源文件映射

> 枝干 = SOUL.md 中 ~30 条浓缩工程规则（每次会话自动注入）
> 枝叶 = 4 份细则源文件中的 ~150+ 条完整规则（需要主动读取）
> 通道 = 当任务落入对应域时，自动预加载细则

---

## 域 → 源文件映射

### 一、设计模式与架构

**SOUL.md §1** — 设计模式与架构（8 条规则）
→ 细则源：`engineering-principles-soul-rules.md`
  - §一 GoF 设计模式（1.1 面向接口 ~ 1.5 单一职责）
  - §二 企业集成模式（2.1 消息原语 ~ 2.5 死信队列）
  - §三 系统设计入门（3.1 权衡 ~ 3.5 数据库权衡）
  - §四 微服务模式（4.1 服务边界 ~ 4.5 API 网关）
  - §五 Martin Fowler 架构思想（5.1 可进化 ~ 5.5 最终一致性）

**触发场景：** 架构设计、模式选择、系统分解、API 设计、服务拆分

---

### 二、测试与安全

**SOUL.md §2** — 测试与安全（6 条规则）
→ 细则源：`Amaranth_SOUL_engineering.md`
  - §一 测试驱动（T1 红-绿-重构 ~ T5 变异测试）
  - §二 安全内建（S1 最小权限 ~ S7 人类监督环）

**触发场景：** 写测试、安全审计、权限设计、沙箱策略、代码审查

---

### 三、系统思维与可靠性

**SOUL.md §3** — 系统思维与可靠性（5 条规则）
→ 细则源：`p4-p5-methodology-soul-rules.md`
  - §一 复杂系统思维（1.1 涌现性 ~ 1.5 医学诊断推理）
→ 细则源：`soul_discipline_principles.md`
  - §2 计算机系统（2.1 抽象分层 ~ 2.7 端到端论证）
  - §3 网络（3.1 分层解耦 ~ 3.4 无状态 vs 有状态）

**触发场景：** 系统调试、性能分析、可靠性设计、故障排查、容量规划

---

### 四、算法与复杂度判断

**SOUL.md §4** — 算法与复杂度判断（4 条规则）
→ 细则源：`soul_discipline_principles.md`
  - §1 算法与复杂度分析（1.1 渐进思维 ~ 1.6 分治递归）
  - §6 线性代数（6.1 矩阵变换 ~ 6.4 维度与自由度）
  - §7 概率论（7.1 不确定性建模 ~ 7.5 极端值敏感性）

**触发场景：** 算法选型、性能优化、数据建模、统计分析、方案评估

---

### 五、沟通与决策

**SOUL.md §5** — 沟通与决策（6 条规则）
→ 细则源：`p4-p5-methodology-soul-rules.md`
  - §二 权衡与边际推理（2.1 稀缺性 ~ 2.6 认知偏误）
  - §三 清晰沟通与写作（3.1 四C原则 ~ 3.5 遣词原则）
  - §四 心智模型与决策框架（4.x）

**触发场景：** 方案决策、写作输出、风险评估、复盘反思

---

### 六、AI Agent 特有规则

**SOUL.md §6** — AI Agent 特有规则（5 条规则）
→ 细则源：`Amaranth_SOUL_engineering.md`
  - §三 AI 工程模式（A1 单一认知核心 ~ A6 代理编排模式）

**触发场景：** Agent 行为设计、工具链编排、记忆系统、认知循环优化

---

## 通道行为规则

```
枝叶通道触发协议：

1. 识别任务域（上述 6 域之一或组合）
2. 按映射表找到对应细则源文件及章节
3. 调用 read_file 加载细则内容到上下文
4. 结合枝干规则 + 细则内容做工程判断
5. 任务完成后，细则内容随上下文自然释放（不持久化）
```

## 文件索引

| 文件 | 路径 | 内容 |
|------|------|------|
| 枝干 | `~/.hermes/SOUL.md` | 30 条浓缩工程规则（自动注入） |
| 细则 P0.1-0.5 | `/opt/data/engineering-learn/engineering-principles-soul-rules.md` | 设计/架构/系统/微服务 |
| 细则 P0.6-0.11 | `/opt/data/engineering-learn/Amaranth_SOUL_engineering.md` | 测试/安全/AI 工程 |
| 细则 P1-P3 | `/opt/data/engineering-learn/soul_discipline_principles.md` | CS/数学/物理 |
| 细则 P4-P5 | `/opt/data/engineering-learn/p4-p5-methodology-soul-rules.md` | 系统思维/边际/写作/心智模型 |
| 源清单 | `/opt/data/engineering-learn/learn-sources.md` | 95 个学习源 |

---

## 部署指南 — WebSocket Relay

relay server 需要跑在 HostDare VPS（100.117.231.9）上。

### 步骤

**1. 在 VPS 上安装 websockets**

```bash
ssh root@100.117.231.9
pip3 install websockets
```

**2. 上传 relay 脚本**

从 Amaranth 本地把脚本传上去：

```bash
scp /opt/data/scripts/branch-leaf-relay.py root@100.117.231.9:/root/
```

**3. 启动 relay（前台测试）**

```bash
python3 /root/branch-leaf-relay.py
```

正常输出：`🌿 枝叶通道 Relay 启动 100.117.231.9:8765`

**4. 配置为 systemd 服务（正式部署）**

```bash
cat > /etc/systemd/system/branch-leaf-relay.service << 'EOF'
[Unit]
Description=枝叶通道 WebSocket Relay
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/branch-leaf-relay.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now branch-leaf-relay.service
```

### 验证

从 Amaranth 本地测试连接：

```bash
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://100.117.231.9:8765') as ws:
        await ws.send(json.dumps({'type':'register','sender':'test','target':'relay','payload':{}}))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        print('OK:', resp)
asyncio.run(test())
"
```

### 客户端（两边都跑）

Amaranth 侧 client 已在 Amaranth 本地通过 background process 启动。
Begonia 侧需要同样的操作：

```bash
# 1. 上传 client 脚本
scp /opt/data/scripts/branch-leaf-client.py ubuntu@150.158.133.136:/home/ubuntu/

# 2. 在 Begonia 上启动（设环境变量 BRANCH_LEAF_AGENT_ID=begonia）
export BRANCH_LEAF_AGENT_ID=begonia
python3 /home/ubuntu/branch-leaf-client.py
```

### 文件清单（Amaranth 侧）

| 文件 | 说明 |
|------|------|
| `/opt/data/scripts/branch-leaf-relay.py` | relay server（跑在 VPS） |
| `/opt/data/scripts/branch-leaf-client.py` | client（每台机器跑一个） |
| `/opt/data/scripts/branch-leaf.py` | Hermes 端 CLI 工具（已软链到 PATH） |
| `/tmp/branch-leaf/inbox/` | 收件箱（消息落地目录） |
| `/tmp/branch-leaf/send.json` | 发件箱（Hermes 写入 → client 读取发送） |
| `/tmp/branch-leaf/status.json` | 连接状态 |

---

**📂 源代码：** [GitHub](https://github.com/HTZY08/wiki-for-Amaranth/blob/main/src/content/docs/projects/engineering-learn/branch-leaf-channel.md)
