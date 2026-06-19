---
title: 飞书 Bot 接入
description: 从零到一，把 Hermes Agent 接上飞书 Bot
---

飞书 Bot 是目前 Begonia 的主要对话入口。本文档记录完整的接入流程和踩坑记录。

## 架构

```
飞书客户端 → 飞书开放平台 → WebSocket → Hermes Gateway → Agent
```

采用 **WebSocket 长连接**模式，不需要公网 HTTPS 回调地址。

## 前置条件

- 一台有公网 IP 的服务器（国内云即可，飞书 API 直连不需要翻墙）
- Hermes Agent 已部署并运行
- 一个飞书账号（个人即可，不需要企业认证）

## 注册飞书 Bot

1. 打开 [飞书开放平台](https://open.feishu.cn/)
2. 用飞书账号登录
3. 创建应用 → **企业自建应用**
4. 填写应用名称（如 "Begonia"），分类随便选
5. 创建成功后，进入 **凭证与基础信息**，记录：
   - `App ID`（格式：`cli_xxxxxxxxxxxx`）
   - `App Secret`（格式：`xxxxxxxxxxxxxxxxxxxxxxxx`）

## 配置 Hermes

在服务器上，编辑 `~/.hermes/.env`，添加：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOW_ALL_USERS=true
```

参数说明：

| 参数 | 值 | 说明 |
|------|-----|------|
| `FEISHU_APP_ID` | `cli_xxx` | 飞书开放平台获取 |
| `FEISHU_APP_SECRET` | `xxx` | 飞书开放平台获取 |
| `FEISHU_DOMAIN` | `feishu` | 国内版飞书；海外版用 `lark` |
| `FEISHU_CONNECTION_MODE` | `websocket` | WebSocket 长连接模式 |
| `FEISHU_ALLOW_ALL_USERS` | `true` | 允许所有用户发消息（测试用） |

## 安装依赖

```bash
# 在 Hermes 的 venv 中安装
/opt/hermes/venv3/bin/pip install lark-oapi websockets
```

Hermes Gateway 启动时会自动检测飞书配置并安装依赖，也可以手动提前安装。

## 配置飞书开放平台

在飞书开放平台的应用管理页面：

### 权限管理
添加以下权限：
- `im:message` — 接收消息
- `im:message:send_as_bot` — 发送消息
- `im:resource` — 访问图片/文件

### 事件与回调
- 连接方式：**WebSocket**
- 订阅事件：`im.message.receive_v1`

### 发布应用
1. **版本管理与发布** → 创建版本
2. 填写版本号（如 1.0.0）和更新说明
3. 提交发布
4. 等待审核通过，或开启**测试模式**跳过审核

> 测试模式：在应用详情 → 安全设置 → 添加测试人员（自己），不需要发布即可使用全部权限。

## 启动网关

```bash
cd ~/.hermes
set -a && source .env && set +a
nohup /opt/hermes/venv3/bin/hermes gateway > /tmp/gw.log 2>&1 &
```

查看日志确认连接成功：

```bash
grep -i 'lark.*connected' /tmp/gw.log
# 应看到: [Lark] ... connected to wss://msg-frontier.feishu.cn/ws/v2?...
```

## 测试

在飞书中搜索 Bot 名称，发送消息测试。支持：

| 消息类型 | 支持情况 |
|---------|---------|
| 文本 | ✅ |
| 富文本（post） | ✅ |
| 图片 | ✅ |
| 文件 | ✅ |
| 语音/视频 | ✅ |
| 合并转发 | ✅ |
| 分享群聊 | ✅ |
| 卡片消息 | ✅ |
| **位置** | ✅ 2026-06-19 补丁 |
| **贴纸** | ✅ 2026-06-19 补丁 |
| **分享用户** | ✅ 2026-06-19 补丁 |
| **系统消息** | ✅ 2026-06-19 补丁 |

## 踩坑记录

### `.env` 变量不 export 导致子进程拿不到

问题：Gateway 启动后，MCP 子进程读取不到 API key。
解决：Gateway 启动前执行 `set -a && source .env && set +a`，或确保 `.env` 中每行有 `export` 前缀。

### WebSocket 依赖缺失

问题：`websockets not installed; websocket mode unavailable`
解决：在 Hermes venv 中安装 `pip install websockets`。注意不是系统 Python，是 Hermes 的 venv。

### 腾讯云翻墙不可用

腾讯云国内节点对 Trojan/SS 等翻墙协议有 DPI 阻断，但飞书 API 是国内服务，直连即可，不需要代理。

### 自定义消息类型

飞书的消息类型不止 text/post/image。2026-06-19 补充了 location/sticker/share_user/system 四种消息类型的解析 handler。如果在 feishu.py 的 `normalize_feishu_message()` 中看到未处理的类型，按已有模式补加即可。

## 相关文件

- 服务器 feishu.py 位置：`/opt/hermes/src4/gateway/platforms/feishu.py`
- 配置文件：`~/.hermes/.env`、`~/.hermes/config.yaml`
- 网关日志：`~/.hermes/logs/gateway.log`
