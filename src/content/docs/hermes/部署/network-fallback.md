---
title: "断网兜底 Watchdog：本地模型自动 Fallback"
description: "API 断了？本地小模型 3 分钟内自动顶上"
---

# 断网兜底 Watchdog

当云端 API 断连时，自动拉起本地模型服务器，让 Hermes 无缝降级到本地推理。本文记录这套系统的搭建过程——从看门狗脚本到 Hermes fallback 配置。

---

## 一、设计原则

| 要求 | 方案 |
|------|------|
| 模型不常驻 | 断网时才拉起，不浪费显存 |
| 零消耗 | `no_agent` 模式，0 token 开销 |
| 快速恢复 | 最多 3 分钟检测间隔 |
| 自动切换 | 网络恢复后自动切回云端 |
| 可诊断 | 断网时输出链路诊断报告 |

---

## 二、架构

```
Cron（3 分钟间隔，no_agent 模式）
  │
  ▼
Watchdog 脚本 (local-llm-watchdog.sh)
  │
  ├─ API 可达？→ 静默退出（0 token）
  │
  └─ API 不可达？
       ├─ 执行全链路诊断
       │    ├─ 本地网关 ping
       │    ├─ DNS 解析
       │    ├─ 代理连通性
       │    ├─ 直连 HTTPS
       │    ├─ 容器 DNS 配置
       │    └─ 代理日志尾巴
       │
       └─ 启动本地推理服务器
            └─ Hermes 自动 fallback
```

---

## 三、组件详解

### 3.1 Cron 调度

```bash
cronjob action='create' \
  name='network-fallback-watchdog' \
  no_agent=true \
  schedule='every 3m' \
  script='local-llm-watchdog.sh'
```

**为什么用 `no_agent=true`？**
- 不需要 LLM 推理
- 0 token 开销
- 只看 stdout：空输出=无事发生，非空输出=断网报告自动推送给用户

### 3.2 看门狗脚本

位置：`/opt/data/scripts/local-llm-watchdog.sh`（118 行）

核心逻辑：

```bash
# 1. 检测主 API
curl -m5 -s -o /dev/null -w "%{http_code}" https://api.deepseek.com/v1/models
# 200 → 静默退出

# 2. 检测本地是否已运行
curl -m3 -s -o /dev/null http://127.0.0.1:8001/v1/models
# 已运行 → 退出

# 3. 执行全链路诊断
#   - ping 192.168.1.1（本地网关）
#   - dig api.deepseek.com（DNS）
#   - curl --proxy ...（代理连通性）
#   - curl --noproxy ...（直连测试）
#   - cat /etc/resolv.conf（容器 DNS）
#   - tail mihomo.log（代理日志）
# 4. 输出诊断报告

# 5. 拉起本地模型
bash /opt/data/scripts/start-local-llm.sh
```

**诊断报告输出示例：**

```
==============================
 网络断连诊断报告 — 2026-05-27 15:42:00
==============================
--- 诊断汇总 ---
  本地网关 192.168.1.1 可达 ✅
  DNS 解析 api.deepseek.com → 104.xx.xx.xx ✅
  通过代理访问 deepseek ❌ — 节点全部超时
  直连 HTTPS ❌ — 全局断网

本地小模型: ⏳ 拉起中（约 2-3 分钟）
==============================
建议: 全局断网 + 代理活着 → 可能 DNS 污染，试试换 DNS
==============================
```

### 3.3 启动脚本

位置：`/opt/data/scripts/start-local-llm.sh`（21 行）

```bash
#!/bin/bash
# 启动本地 LLM 推理服务器（Qwen3-8B CPT）
# 必须用训练 venv 的 python（系统 python 没有 torch）

/opt/data/py310-qwen/bin/python3 \
  /opt/data/output/qwen3-cpt/llm_server.py \
  > /opt/data/logs/local-llm.log 2>&1 &
echo $! > /opt/data/logs/local-llm.pid
```

**关键点：** 必须显式指定 venv 的 Python 路径。系统 Python（`python3`）没有 torch，用相对路径在 cron 环境下会默认为系统 Python。

### 3.4 Hermes Fallback 配置

```yaml
# config.yaml
custom_providers:
  - name: qwen-cpt
    base_url: http://127.0.0.1:8001/v1
    api_key: not-needed

fallback_providers:
  - provider: qwen-cpt
    model: qwen3-8b-cpt
```

**触发条件（Hermes 自动处理）：**
- 429 — Rate Limit
- 529 / 503 — 服务不可用
- 连接失败 — DNS 解析失败、Connection timeout、Connection refused

不需要手动切换。看门狗确保服务器在断网时已启动。

---

## 四、恢复流程

```
网络恢复
  → Hermes 下次请求成功（走主模型）
  → 看门狗检测到 API 可达 → 静默退出
  → 本地服务器继续运行（等显存不够时手动关闭）
  → 或下次训练时自动覆盖
```

本地模型不自动关闭——它只是静默等待下一次断网。如果你需要释放显存，手动 kill 即可。

---

## 五、性能数据

| 指标 | 数据 |
|------|------|
| 检测间隔 | 3 分钟 |
| 模型加载时间 | ~2 分钟 |
| 最长盲区 | ~5 分钟（错失检测窗口 + 加载） |
| token 消耗 | 0（no_agent 模式） |
| 本地推理显存 | ~5.7GB / 12GB |
| 本地推理速度 | ~15-20 t/s |

---

## 六、与训练管线的衔接

这套断网兜底的本地模型和训练管线是同一套：

```
训练：Qwen3-8B + LoRA CPT → checkpoint-40（最佳）
       ↓ 合并到基座
部署：llm_server.py（torch + 4bit）
       ↓ 看门狗拉起
兜底：API 断了 → 自动切到这里
```

一条管线，两个用途。

---

## 七、参考

- 看门狗脚本：`/opt/data/scripts/local-llm-watchdog.sh`
- 启动脚本：`/opt/data/scripts/start-local-llm.sh`
- 推理服务器：`/opt/data/output/qwen3-cpt/llm_server.py`
- 本地模型技能：`local-llm-fallback`
