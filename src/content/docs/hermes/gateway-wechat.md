---
title: 微信 Gateway
description: Hermes 微信消息网关配置
---

Hermes Gateway 是消息平台接入层，支持微信（WeChat）等渠道。通过微信收发消息，实现移动端与 Hermes Agent 的交互。

## 架构

```
手机微信 → 微信公众平台 → Cloudflare Worker → Hermes Gateway → Agent
```

通信路径：微信消息经公众平台推送到 Cloudflare Worker，Worker 透传到本地 Hermes Gateway 服务，由 Agent 处理后经同样路径返回。

## 配置要点

Gateway 配置在 `config.yaml` 中：

```yaml
gateway:
  platforms:
    wechat:
      enabled: true
      token: ${WECHAT_TOKEN}
      port: 8080
```

微信公众平台侧需配置：
- 服务器地址：指向 Cloudflare Worker 的 URL
- Token：与 config.yaml 中一致
- 消息加解密方式：根据安全需求选择

## 恢复流程

容器重启后，Gateway 配置可能丢失，使用 `hermes-env-recovery` Skill 一键恢复：

```bash
# 在 Hermes 对话中执行
> 恢复微信网关
```

该 Skill 会重新打 TTS 流式补丁、配置 Gateway 参数、重启相关服务。

## 功能

- 文本消息收发
- 支持 `/background` 长任务后台化（微信端可随时插话）
- 图片自动走 SiliconFlow Qwen3-VL 视觉理解
- 语音消息转文字（基于 faster-whisper GPU 加速）
