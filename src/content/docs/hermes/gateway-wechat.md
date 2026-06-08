---
title: 微信接入
description: 通过微信与 Hermes 对话——配置消息网关
---

配置微信网关后，你可以用微信给 Hermes 发消息，就像跟朋友聊天一样。

---

## 原理

```
你（手机微信） → 微信公众平台 → Cloudflare Worker → 你的 Hermes
```

消息从微信发出，经过三层转发到达你的 Hermes，处理结果原路返回。

## 前提条件

- ✅ Hermes 已正常运行
- ✅ 有一个**微信公众平台**订阅号（个人可注册，免费）
- ✅ 有一个 **Cloudflare** 账号（免费版即可）
- ✅ 你的 Hermes 机器有公网 IP，或用内网穿透

## 第一步：注册微信公众平台订阅号

1. 访问 [mp.weixin.qq.com](https://mp.weixin.qq.com)
2. 点击"立即注册" → 选择"订阅号"
3. 用未注册过公众号的邮箱注册
4. 填写信息，选择"个人"类型
5. 注册成功后进入后台

## 第二步：部署 Cloudflare Worker

Cloudflare Worker 作为中间转发层，把微信的消息转给你的 Hermes。

创建 Worker，填入以下代码：

```javascript
// Cloudflare Worker — 微信消息转发
export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // 微信验证 Token
    if (request.method === 'GET') {
      const params = url.searchParams;
      const signature = params.get('signature');
      const timestamp = params.get('timestamp');
      const nonce = params.get('nonce');
      const echostr = params.get('echostr');
      
      // 验证通过后返回 echostr
      return new Response(echostr);
    }
    
    // 处理微信消息
    if (request.method === 'POST') {
      // 转发消息到你的 Hermes 服务器
      const response = await fetch('http://你的服务器IP:端口', {
        method: 'POST',
        headers: request.headers,
        body: await request.text()
      });
      
      return response;
    }
  }
}
```

> 注意：需要把 `你的服务器IP:端口` 替换为你的实际地址。

## 第三步：配置 Hermes Gateway

在 `~/.hermes/config.yaml` 中启用微信网关：

```yaml
gateway:
  platforms:
    wechat:
      enabled: true
      token: "你自己设定的 Token 字符串"
      port: 8080
```

> Token 是任意字符串，与微信公众平台中设置的一致即可。

## 第四步：配置微信公众平台

1. 登录公众号后台
2. 左侧菜单 → 设置与开发 → 基本配置
3. 点击"服务器配置" → 修改配置
4. 填写：
   - **服务器地址**：你的 Cloudflare Worker URL
   - **Token**：与 Hermes config 中一致
   - **消息加解密方式**：选"明文模式"（调试阶段）
5. 提交，微信会发送验证请求，Worker 自动响应

## 第五步：测试

给公众号发一条消息，应该能收到 Hermes 的回复。

## 功能说明

### 支持的消息类型

- **文本消息** — 直接对话
- **图片消息** — 自动识别图片内容
- **语音消息** — 转文字后处理

### 长任务处理

耗时任务（如"帮我查一下过去一周的新闻"）会自动转后台执行，你可以在微信上发别的消息，任务完成后收到通知。

## 故障排查

### 公众号提示 "Token 验证失败"

```bash
# 检查 Hermes Gateway 是否在运行
docker compose logs hermes | grep gateway

# 确认 Token 拼写一致
```

### 消息发出去没回复

```bash
# 检查 Workerr 日志
# 进入 Cloudflare Dashboard → Workers → 你的 Worker → 日志

# 检查 Hermes 日志
docker compose logs -f hermes
```

### 图片识别不工作

需要配置图片识别服务，参见相关配置文档。
