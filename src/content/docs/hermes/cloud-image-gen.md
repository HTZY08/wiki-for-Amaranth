---
title: 云端生图配置
description: 无 GPU 也能生成 AI 图片——配置云端 API
---

如果你没有独立显卡（或懒得配 GPU 透传），可以用云端 API 生图。配置好后 Hermes 会通过 API 调用远程模型生成图片，与本地有没有显卡无关。

---

## 原理

```
Hermes → config.yaml 配置的 API → 云端 GPU 生图 → 返回图片 URL
```

不需要本地 GPU、不需要 Docker socket、不需要 ComfyUI。

## 方案一：硅基流动（SiliconFlow）

国内平台，直连无需代理，注册送几十块额度，支持 FLUX.1 等主流模型。

### 注册获取 API Key

1. 打开 [siliconflow.cn](https://siliconflow.cn) 注册（手机号即可）
2. 进入控制台 → API 密钥 → 创建密钥
3. 复制密钥（格式 `sk-xxxxxxxx`）

### 配置环境变量

在 `~/.hermes/.env` 中添加：

```bash
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 配置 config.yaml

在 `~/.hermes/config.yaml` 中添加或修改：

```yaml
model.vision: provider=custom, model=Qwen/Qwen2.5-VL-72B-Instruct, base_url=https://api.siliconflow.cn/v1, api_key=$SILICONFLOW_API_KEY
```

部分 Hermes 版本支持单独的 `image_gen` 配置块：

```yaml
image_gen:
  provider: custom
  model: black-forest-labs/FLUX.1-dev
  base_url: https://api.siliconflow.cn/v1
  api_key: $SILICONFLOW_API_KEY
```

> ⚠️ 不同 Hermes 版本的配置格式可能不同。如果不确定，用 `hermes config set` 命令配：`hermes config set model.vision "provider=custom, model=Qwen/Qwen2.5-VL-72B-Instruct, base_url=https://api.siliconflow.cn/v1"`

### 验证

```bash
# 重启 Hermes 后测试
hermes

# 输入指令：
你：画一只猫
```

应该返回一张生成的图片。

## 方案二：商汤 SenseNova

注册即送 **1500 次生图 + 1500 次视觉识别**（每 5 小时刷新），适合重度使用。

完整注册和配置步骤见 **[商汤 SenseNova 免费 API](/freebies/2026-06-10-sensenova-token-plan/)**。

## 没有图片生成功能的 Hermes 版本

如果你的 Hermes 版本不支持 `image_gen` 配置块，可以：

1. **升级 Hermes** 到最新版本
2. 或者用 `model.vision` 替代——Hermes 会自动调用视觉模型分析/生成图片相关的回复

## 常见问题

### 配置了但生图失败

```bash
# 检查 key 是否正确
grep SILICONFLOW ~/.hermes/.env

# 检查配置
grep -A3 "image_gen\|model.vision" ~/.hermes/config.yaml

# 测试 API 连通性
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" | head -c 200
```

### 返回"请稍后再试"（微信端）

见 [微信接入 → 图片消息发不出去](/hermes/gateway-wechat/#图片消息发不出去请稍后再试)。

### 硅基流动额度不够了

- 硅基流动免费额度一般是邀请制赠送，用完了可以换商汤 SenseNova（1500 次/5h）
- 也可以注册多个平台轮换使用
