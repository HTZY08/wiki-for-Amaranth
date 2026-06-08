---
title: 技能索引
description: 最常用的技能和工作流速查
---

当前系统有 120+ 个技能包（skills）。以下是实际使用中最常用的——按场景分类，需要的直接翻。

---

## 🛠 运维排障

### 微信网关诊断

微信连不上时，按这个顺序查：

```bash
# 1. 查 gateway 进程是否活着
ps aux | grep "hermes gateway run"

# 2. 查连接状态
cat /opt/data/gateway_state.json | python3 -m json.tool

# 3. 查日志——三个日志文件都要看
tail -20 /opt/data/logs/agent.log       # 实时微信错误
tail -20 /opt/data/logs/errors.log      # 完整错误堆栈
tail -20 /opt/data/logs/gateway.log     # s6 管道日志

# 4. 查代理环境变量——微信必须直连
env | grep -i proxy
```

**最常见的挂掉原因：#1 代理冲突**（gateway 继承了代理环境变量，连不上 `ilinkai.weixin.qq.com`），#2 限流（`rate limited`），#3 s6 环境变量丢失。

👉 详细操作手册：[微信接入](/hermes/gateway-wechat/)

### 环境恢复

容器出问题后一键恢复配置：

```bash
# 执行 hermes-env-recovery skill 中的恢复流程
# 包括：TTS 流式补丁、微信 Gateway、视觉模型、GPU 服务
```

---

## 🖼 图像生成

### 生图管线

实际有三条管线，按优先级选：

| 管线 | 成本 | 质量 | 适用场景 |
|------|------|------|----------|
| **API Yi → chatgpt-image-latest** | ~$1/张 | ⭐⭐⭐⭐⭐ | 角色图、高质量出图 |
| **SiliconFlow → Qwen-Image** | ~$0.03/张 | ⭐⭐⭐ | 日常插图、快速出图 |
| **SiliconFlow → Z-Image-Turbo** | ~$0.005/张 | ⭐⭐⭐⭐ | 写实人像（男性） |

关键规则：
- **国内 API（SiliconFlow）**：不能走代理，调用前 `unset http_proxy https_proxy`
- **海外 API（API Yi）**：走代理
- **角色图（Amaranth/莲）**：用 API Yi，贵但脸不崩
- **微信发图**：超过 1MB 的图需要压缩（缩到 1200px + quality=85）

---

## 📰 自动化日报

每天自动生成的"三合一简报"：

```
RSS/API 多源采集 → 汇总 → 筛选（AI+政经+热点）→ 投递到微信
```

定时任务在 Hermes cron 中配置，结果自动发到微信。

---

## 🎤 语音合成

```bash
# TTS 输出到音频文件
# 内置引擎：edge-tts（免费首选）
# 备用引擎：MiniMax TTS（Token Plan）
```

语音消息通过微信发送时，可以用 `[[audio_as_voice]]` 指令让音频以原生语音气泡形式发送。

---

## 💾 记忆系统

```bash
# 持久记忆——记住用户偏好、环境事实、工作流
# 存在 SQLite（Hindsight Lite），跨会话持久

# 会话搜索——查过去聊过什么
# 不用猜，直接搜
```

使用原则：
- **存**：用户偏好、纠正、环境事实、学到的工作流
- **不存**：任务进度、会话日志、临时状态（用 session_search 查）
- **写**：声明式事实（"用户偏好简洁回复"），不是指令式（"必须简洁回复"）

---

## ⏰ 定时任务

| 场景 | 方案 |
|------|------|
| 每日定时任务 | Hermes 内置 cron |
| 长耗时的批量任务 | 自动转后台执行 |
| 脚本直出（不经过 LLM） | `no_agent: true` 模式 |
| 任务链 | 用 `context_from` 串起来 |

所有定时任务结果投递到微信，不用守在电脑前看。

---

## 🧠 模型路由速查

| 你要做什么 | 用什么模型 | 怎么调 |
|-----------|-----------|--------|
| 日常对话 | DeepSeek V4 Flash | 默认就是 |
| 写代码 | Codex → GPT-5.5 | 切 Codex CLI |
| 复杂推理 | Claude Opus | 手动切换 |
| 图片识别 | Qwen-VL / Gemini | Hermes 自动调 |
| 本地推理 | LM Studio | 本地 GPU 跑 |

---

## 技能怎么来的

这些技能不是一次性写好的。大部分是在实际使用中碰到问题→修好→写成 skill 存下来。以后再遇到同样的问题不用重新想。

所以如果有一天某个流程变了，记得顺手更新对应的 skill——下次需要它的人（可能是你自己）会感谢你。
