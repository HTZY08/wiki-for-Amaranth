---
title: "商汤 SenseNova Token Plan · 免费 API 白嫖指南"
description: 商汤日日新平台免费公测（已延长至7月底），零成本获取原生多模态 + GLM 5.2 + DeepSeek V4 API
---

> **更新 2026-07-22：** 免费公测已延长至 **7 月底**，新增支持 GLM 5.2，DeepSeek V4 Flash 配额提升。同时推出 **国际版**（[sensenova.ai](https://www.sensenova.ai/)），新用户首月免费。

商汤（SenseTime）在 2026 年 5 月推出 **SenseNova Token Plan**，公测期完全免费开放。注册即送多个模型的无门槛调用配额，兼容 OpenAI API 格式，可无缝接入 Hermes Agent 等主流框架。

## 免费额度（截至 2026-07）

公测期方案（¥0/月，预计持续至 7 月底）：

| 模型 | 能力 | 配额 |
|------|------|------|
| **SenseNova 6.7 Flash-Lite** | 原生多模态视觉 + 对话，256K 上下文 | 1500 次 / 5 小时 |
| **SenseNova U1 Fast** | 信息图生成（理解 + 生成一体） | 1500 次 / 5 小时 |
| **GLM 5.2** | 智谱 753B MoE 开源前沿模型 | 500 次 / 5 小时 |
| DeepSeek V4 Flash | 转售的 DeepSeek 模型 | 500 次 / 5 小时 |

关键特性：
- 最多创建 **20 个 API Key**
- 兼容 OpenAI SDK 格式
- 原生多模态架构（不需要 OCR → 文本中间层，直接理解图像）
- 支持 Hermes Agent / OpenClaw 快速接入
- 开源 26 个办公 Skills（信息图、PPT、数据分析、深度调研）
- **国际版**（sensenova.ai）已上线，面向香港及全球市场

## 获取步骤

### 1. 注册账号

访问 [sensenova.cn/token-plan](https://www.sensenova.cn/token-plan)，点击「免费开始」：

1. 输入国内手机号注册
2. 设置用户名和密码
3. 登录后进入管理控制台

### 2. 创建 API Key

1. 进入 **管理中心 → API Key 管理**
2. 点击「创建 API Key」
3. **立即复制保存**（密钥只显示一次）

### 3. 配置 Hermes Agent

将 API Key 写入 Hermes 环境变量：

```bash
# 编辑 ~/.hermes/.env（或 /opt/data/.env）
SN_API_KEY=sk-你的Key
```

在 `config.yaml` 中添加自定义 provider：

```yaml
custom_providers:
  sensenova:
    base_url: https://token.sensenova.cn/v1
    api_key_env: SN_API_KEY
    models:
      - sensenova-6.7-flash-lite
      - sensenova-u1-fast
      - deepseek-v4-flash
```

### 4. 安装 Skills

商汤开源了 26 个 Agent Skills，原生兼容 Hermes Agent：

```bash
# 克隆仓库
git clone https://github.com/OpenSenseNova/SenseNova-Skills.git

# 复制到 Hermes skills 目录
cp -r SenseNova-Skills/skills/* ~/.hermes/skills/sensenova/

# 重启 Hermes 加载新 skill
```

Skills 清单：

| Skill | 功能 |
|-------|------|
| `sn-image-base` | 图像生成 / VLM 识别 / LLM 文本优化（底层依赖） |
| `sn-infographic` | 信息图生成（87 布局 × 66 风格，多轮 VLM 质检） |
| `sn-image-imitate` | 模仿参考图生成新图 |
| `sn-image-resume` | 简历图像生成 |
| `sn-ppt-entry` | PPT 统一入口 |
| `sn-ppt-standard` | 标准 PPT 生成（文档→大纲→配图→PPTX） |
| `sn-ppt-creative` | 创意 PPT 模式（整页 PNG） |
| `sn-da-excel-workflow` | Excel 数据分析 |
| `sn-deep-research` | 深度调研（多源检索 + 报告撰写） |
| `sn-search-academic` | 学术搜索 |
| `sn-search-image` | 图片搜索 |
| `sn-search-social-cn` | 中文社交媒体搜索 |

## 使用方式

### 在 Hermes 中使用

```bash
# 切换模型
hermes model  # 选择 custom/sensenova-6.7-flash-lite

# 直接对话使用视觉能力
hermes chat -q "这张图里有什么？"  # Hermes 会自动识别附件的图片
```

### 调用 Skills

```bash
# 在对话中加载 skill 并执行
/skill sn-infographic

# 然后输入你的需求，例如：
# "生成一张关于光合作用的信息图"
```

### 直接 API 调用

```bash
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-你的Key" \
  -d '{
    "model": "sensenova-6.7-flash-lite",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 视觉识别 API

```bash
curl https://token.sensenova.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-你的Key" \
  -d '{
    "model": "sensenova-6.7-flash-lite",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
      ]
    }]
  }'
```

支持图片 URL 和 Base64 格式。

## 架构说明

### 原生多模态

SenseNova 6.7 Flash-Lite 采用 **原生多模态架构**，区别于传统的"视觉转文本"管道：

```
传统多模态: 图片 → OCR/描述 → 文本 → LLM 推理 → 输出
                                     ↑ 信息丢失

SenseNova:  图片 → 原生多模态理解 → 直接输出
            取消视觉转文本中间层
```

优势在于直接理解网页布局、文档结构、图表等结构化信息，减少信息损失，Token 消耗降低约 60%（商汤宣称）。

### Skill 体系分层

```
Tier 1（用户可见）: sn-infographic / sn-ppt-* / sn-da-* / sn-deep-research
                          ↕ 调用
Tier 0（底层工具）: sn-image-base（图像生成 + VLM + LLM）
                          ↕ 配置
环境变量: SN_API_KEY / SN_BASE_URL / SN_VISION_MODEL 等
```

## 注意事项

### 坑点

1. **SKill 强绑定商汤模型** — 尤其是信息图生成（`sn-infographic`）和 PPT 生成，布局模板和提示词策略针对 SenseNova U1 Fast 优化，换其他模型可能效果打折扣
2. **视觉识别可解耦** — 纯看图（VLM）支持 OpenAI 兼容格式，可以切到其他模型
3. **配额限制** — 1500 次 / 5 小时，单个长任务可能消耗多次调用（生成 + VLM 质检 + 重试）
4. **公测期** — 已延长至 7 月底，付费档位（Lite / Pro）即将推出。国际版新用户享首月免费
5. **仅限国内网络** — 服务部署在国内，使用国内 API 需注意代理配置（部分代理可能导致连接失败）

### 推荐的视觉链路

```
主路由: SiliconFlow Qwen3-VL（免费开源模型）
  ├── SenseNova 6.7 Flash-Lite（免费，原生多模态）
  └── 兜底: EasyOCR 本地（零成本离线）
```

## 参考链接

- [Token Plan 注册](https://www.sensenova.cn/token-plan)
- [API 文档](https://github.com/OpenSenseNova/SenseNova6.7/blob/main/API.md)
- [SenseNova-Skills 仓库](https://github.com/OpenSenseNova/SenseNova-Skills)
- [Agent Pack 一键安装](https://github.com/OpenSenseNova/agent_pack)
