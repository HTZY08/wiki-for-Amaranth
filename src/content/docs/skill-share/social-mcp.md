---
title: 社媒 MCP 接入指南
description: 小红书、抖音等国内社交媒体通过 MCP 接入 Hermes Agent 的方法
---

# 社媒 MCP 接入指南

通过 Docker MCP 容器，将国内社交媒体的数据能力接入 AI Agent。

---

## 📕 小红书 (xiaohongshu-mcp)

已接入，正常运行中。

### 架构

```
Hermes Agent → Python MCP 调用 → xiaohongshu-mcp (Go, Docker)
                                    ↓
                              headless Chromium
                                    ↓
                              小红书 Web
```

- MCP 端点：`http://172.17.0.1:18060/mcp`
- 传输协议：StreamableHTTP（需 `Accept: application/json, text/event-stream`）
- 端口：18060
- 技术栈：Go + Chromium + Docker

### 部署

```bash
docker run -d \
  --name xiaohongshu-mcp \
  --network host \
  -v xhs-cookies:/app/cookies \
  xpzouying/xiaohongshu-mcp
```

首次启动后需扫码登录（二维码通过 `get_login_qrcode` 工具获取）。

### 持久化

Cookies 存储在 Docker volume `xhs-cookies` 中，容器重启后登录状态保持。

### 可用工具（13个）

| 工具 | 功能 |
|:----|:-----|
| `check_login_status` | 检查登录状态 |
| `get_login_qrcode` | 获取登录二维码 |
| `search_feeds` | 搜索笔记（支持综合/最新/最多点赞等排序） |
| `list_feeds` | 获取首页推荐流 |
| `get_feed_detail` | 获取笔记详情（含评论） |
| `publish_content` | 发布图文笔记 |
| `publish_with_video` | 发布视频笔记 |
| `like_feed` | 点赞/取消点赞 |
| `favorite_feed` | 收藏/取消收藏 |
| `post_comment_to_feed` | 发表评论 |
| `reply_comment_in_feed` | 回复评论 |
| `user_profile` | 获取用户信息 |
| `delete_cookies` | 清除 Cookies |

### 二次开发

Hermes Skill 文件：`/opt/data/skills/research/xiaohongshu-research/SKILL.md`

```python
from xiaohongshu_research import xhs_search, xhs_get_note

# 搜索
feeds = xhs_search("攻略关键词", sort_by="最多点赞")

# 看详情
detail = xhs_get_note(feed_id, xsec_token)
```

---

## 🎵 抖音 (douyin-mcp)

待接入，可复用同样架构。

### 可选方案

| 方案 | 侧重 | 端口 | 技术栈 |
|:----|:-----|:----|:------|
| [flyerhzm/douyin-mcp](https://github.com/flyerhzm/douyin-mcp) | 视频发布 | 18062 | Node.js + Playwright |
| [yc-w-cn/douyin-mcp-server](https://github.com/yc-w-cn/douyin-mcp-server) | 视频解析下载 | — | Node.js |
| [ashinh/dy-xhs-mcp-server](https://github.com/ashinh/dy-xhs-mcp-server) | 抖音+小红书合并 | — | — |

### 部署方式（待执行）

```bash
docker run -d \
  --name douyin-mcp \
  -p 18062:18062 \
  flyerhzm/douyin-mcp
```

---

## 📺 B 站 (bilibili)

无需 Docker MCP，已有更轻量的 CLI 工具：

- `bili-cli` — 搜索、热门、排行榜、视频信息
- `yt-dlp` — 视频/字幕下载（兼容 B 站）

Agent-Reach 已配置 B 站渠道。

---

## 🐦 Twitter / X

通过 `xurl CLI` 接入，已配置。

- 读推文、搜关键词、看个人主页
- 需 Cookie 认证（已配）

---

## 📖 Reddit

通过 `rdt-cli` 接入。

- 搜帖子、看热门、读评论区
- 需 Cookie 登录

---

## 📧 RSS

所有支持 RSS/Atom 的源均可通过 `feedparser` 接入。

已配置的 RSS 源见 rss-daily-pipeline。

---

## 统一入口

所有社媒数据最终通过以下两种方式接入 Hermes：

1. **MCP 协议** — 小红书、抖音（待接入）
2. **CLI 工具** — Twitter、Reddit、B站、GitHub

对应 Skill：
- `xiaohongshu-research` — 小红书
- `resource-hunter` — 资源搜索（跨平台）
- `blogwatcher` — RSS 监控
