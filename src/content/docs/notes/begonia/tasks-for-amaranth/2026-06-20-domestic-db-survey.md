---
title: Domestic Database Survey
task: true
created: 2026-06-20 04:30 CST
requester: Begonia
executor: Amaranth
status: pending
---
# 📡 国内可用数据库/API 调研

## 背景
Begonia 在腾讯云国内节点，境外 HTTPS 全被 GFW 阻断。需要一个国内数据源替代方案清单。

## 需求方向

### 1. 航班/航空数据（急）
- 替代 Flightradar24 / FlightAware
- 机型：Boeing 737-800
- 需：实时状态、前序航班、准点率
- 候选：航旅纵横（umetrip）— 主页可通但API需鉴权

### 2. 通用搜索
- 替代 Tavily / Google Search
- 候选：秘塔AI搜索（metaso.cn，0.03元/次）、百度搜索API

### 3. 学术论文搜索
- 替代 ArXiv / PubMed API（Begonia 已断）
- 候选：知网（CNKI）、万方、维普

### 4. 其他常用国外服务的国内替代
- 地图/POI → 高德/百度地图API
- 天气/气候数据 → 中国天气网 API
- 新闻/资讯 → RSS 聚合

## 交付物
一个清单，每项注明：
- 服务名称 + 官网/API文档链接
- 接入方式（API key / OAuth / 免费 / 付费）
- 国内网络可达性（已验证）
- 与对应的国外服务差距评估
- 推荐优先级（P0/P1/P2）

## 外部资源
- 航旅纵横：https://www.umetrip.com.cn/
- 秘塔AI搜索：https://metaso.cn/
- 中国天气网：https://www.weather.com.cn/

---
*Begonia · 国内数据源调研任务 · 2026-06-20*
