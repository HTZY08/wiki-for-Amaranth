---
title: free-for.dev — 开发者免费服务清单
description: 1600+ 贡献者维护的 SaaS/PaaS/IaaS 免费套餐大百科，GitHub 128K stars。覆盖云厂商、监控、CI/CD、托管、API、AI/ML 等 50+ 分类
authors: [Begonia]
tags: [freebies, devtools, cloud]
source: https://github.com/ripienaar/free-for-dev
---

# free-for.dev — 开发者免费服务清单

GitHub 128K stars，1600+ 贡献者共同维护的开发者免费服务清单，覆盖 50+ 分类。严格筛选——只收录真正提供免费套餐的服务（非仅限试用），且不限制 TLS 加密。

原文：[free-for.dev](https://github.com/ripienaar/free-for-dev)

---

## 云厂商免费额度

### Google Cloud Platform

- Compute Engine：1 台非抢占式 e2-micro，30GB HDD，5GB 快照存储（限特定区域），1GB/月北美出站流量
- App Engine：每天 28 前端实例小时、9 后端实例小时
- Cloud Firestore：1GB 存储，每天 5 万次读取、2 万次写入、2 万次删除
- Cloud Storage：5GB，1GB 网络出站
- Cloud Functions：每月 200 万次调用
- Cloud Run：每月 200 万次请求，360,000 GB-秒内存，180,000 vCPU-秒
- Cloud Pub/Sub：每月 10GB 消息
- BigQuery：每月 1TB 查询，10GB 存储
- Cloud Build：每天 120 构建分钟
- Google Kubernetes Engine：一个 zonal 集群免管理费
- Cloud Shell：基于 Web 的 Linux shell/IDE，5GB 持久存储，每周 60 小时限制
- Google Colab：免费 Jupyter Notebook，可选 Nvidia T4/P100 GPU
- Kaggle：4 CPU 核心 + 30GB RAM 笔记本环境，手机验证后可加 1× P100 或 2× T4 GPU（30 小时/周）
- AI Studio：免费使用 Gemini Flash、Gemma 模型，有速率限制
- 完整列表：https://cloud.google.com/free

### Amazon Web Services

- EC2：每月 750 小时 t2.micro 或 t3.micro（12 个月），100GB 出站流量
- S3：5GB 标准存储（12 个月）
- Lambda：每月 100 万次请求
- CloudFront：每月 1TB 出站 + 200 万次函数调用
- DynamoDB：25GB NoSQL 数据库
- RDS：750 小时 db.t2.micro/db.t3.micro/db.t4g.micro（12 个月），20GB 通用 SSD
- SQS：100 万次消息队列请求
- SNS：100 万次发布
- SES：每月 3000 封邮件（12 个月）
- CloudWatch：10 个自定义指标 + 10 个告警
- CodeBuild：每月 100 分钟构建时间
- CodeCommit：5 个活跃用户，50GB 存储
- CodePipeline：1 条活跃流水线
- Glacier：10GB 长期对象存储
- 完整列表：https://aws.amazon.com/free

### Microsoft Azure

- 虚拟机：1 台 B1S Linux + 1 台 B1S Windows（12 个月）
- Functions：每月 100 万次请求
- App Service：10 个 Web/Mobile/API 应用（每天 60 CPU 分钟）
- Cosmos DB：25GB 存储 + 1000 RU/秒
- Active Directory：50 万个对象
- Azure DevOps：5 个活跃用户，无限私有 Git 仓库
- Pipelines：10 个并行 Job（开源项目无限分钟）
- Static Web Apps：SSL、认证/授权、自定义域名
- Cognitive Services：AI/ML API 免费额度（计算机视觉、翻译、人脸检测等）
- Cognitive Search：1 万份文档
- IoT Hub：每天 8000 条消息
- Notification Hubs：100 万次推送通知
- 带宽：15GB 入站 + 5GB 出站/月（12 个月）
- 完整列表：https://azure.microsoft.com/free

### Oracle Cloud

- 计算：2 台 AMD VM（1/8 OCPU + 1GB 内存各）+ 2 台 ARM Ampere A1（12GB 总内存，可配 1 或 2 台 VM）
- 块存储：2 卷共 200GB
- 对象存储：10GB
- 负载均衡：1 实例 + 10 Mbps
- 数据库：2 实例各 20GB
- 监控：5 亿采集点、10 亿检索点
- 带宽：每月 10TB 出站（x64 限 50Mbps，ARM 按核心数 500Mbps/核）
- 公网 IP：2 个 IPv4（VM）+ 1 个（负载均衡）
- Oracle 的免费套餐被称为白嫖之王——2 台 ARM 服务器 + 10TB 带宽
- 注意：闲置实例会被回收
- 完整列表：https://www.oracle.com/cloud/free

### Cloudflare

- Application Services：无限域名免费 DNS、DDoS 防护、CDN、免费 SSL、WAF、Bot Mitigation、Rate Limiting
- Zero Trust：最多 50 用户，24 小时日志，3 个网络位置
- Tunnel：免费 Quick Tunnel 无需账户，Zero Trust 版含 TCP 隧道和负载均衡
- Workers：每天 10 万次请求
- Workers KV：每天 10 万次读取 / 1000 次写入，1GB 存储
- R2 对象存储：每月 10GB，100 万次 Class A 操作
- D1 数据库：每天 500 万行读取 / 10 万行写入，1GB 存储
- Pages：每月 500 次构建，100 个自定义域名，无限预览部署
- Queues：每月 100 万次操作
- TURN：每月 1TB 出站流量

### IBM Cloud

- Cloudant 数据库：1GB 存储
- Db2 数据库：100MB 存储
- API Connect：每月 5 万次调用
- Availability Monitoring：每月 300 万数据点
- Log Analysis：每天 500MB 日志

### Zoho

Zoho 提供一整套 SaaS 服务，大部分有免费计划：
- Zoho Mail：免费 5 用户，5GB/用户
- Zoho Projects：免费 3 用户，2 项目
- Zoho CRM：免费 3 用户
- Zoho Assist：免费 1 并发远程支持 + 5 台无人值守电脑
- Zoho Cliq：免费无限用户团队聊天，100GB 存储
- Zoho Vault：免费个人密码管理
- Zoho Meeting：最多 3 参会者
- Zoho Forms / Survey / Sign / Bookings / Notebook 等均有免费层

---

## 分类速览

free-for.dev 共收录 50+ 分类。以下按功能领域分组摘录亮点。

### 源码托管

- GitHub：不限公开/私有仓库，CI/CD、Pages、Container Registry、Copilot
- GitLab：不限公开/私有仓库（5 协作者），CI/CD、Pages、Container Registry
- Bitbucket：不限公开/私有仓库（5 用户），Pipelines
- Codeberg：无限公开/私有仓库（免费项目），Pages、CI、翻译平台

### CI/CD

- CircleCI：每月 6000 分钟，30 并行 Job，不限协作者
- GitHub Actions：公共仓库免费，私有仓库每月 2000 分钟
- Buildkite：3 用户，每月 5000 Job 分钟
- Appveyor：Windows CI，开源免费
- Bitrise：每月 200 次构建（10 分钟/次），移动端 CI/CD
- CodeMagic：每月 500 构建分钟，Flutter/移动端 CI/CD
- Mergify：工作流自动化和合并队列，公开仓库免费

### Web 托管

- Vercel：免费托管静态站点 + Serverless Functions，100GB 带宽
- Netlify：免费 100GB 带宽，300 构建分钟，Forms 和 Functions
- Railway：每月 $5 额度，500 小时
- Render：免费静态站点 + Web Service，限 750 小时/月
- Fly.io：免费 3 台共享 VM，每月 3GB 持久存储
- Alwaysdata：1GB 免费 Web 托管，支持 MySQL/PostgreSQL
- Stormkit：免费 JAMStack 托管（50 次构建/月），Git 集成

### 监控与日志

- Datadog：免费 10 台主机，5 天保留
- Sentry：每月 5000 条错误，1 用户
- UptimeRobot：50 个监控器，5 分钟间隔
- Checkly：代码优先合成监控，Playwright 驱动
- Axiom：0.5TB 日志存储，30 天保留
- Better Stack：每月 100GB 日志，3 用户
- Highlight：开源全栈可观测性，免费 5 台主机
- Logtail：每月 1GB 日志，7 天保留

### API 与数据服务

- Hugging Face：免费构建/训练/部署 NLP 模型，每月 3 万字符输入
- Postman：免费 API 开发协作平台
- Insomnia：开源 API 客户端（REST + GraphQL）
- Hoppscotch：免费 Web API 调试工具
- Apify：每月 $5 平台额度，Web 爬取/自动化
- SerpApi：每月 100 次搜索引擎结果抓取
- Firecrawl：每月 1000 积分，网页爬取转 Markdown
- Svix：每月 5 万条 Webhook 消息
- Abstract API：IP 地理位置、邮箱验证等 API 套件
- IPInfo：每月 5 万次 IP 地理信息查询
- Brave Search API：每月 $5 额度，适合 RAG/AI Agent
- Tavily AI：每月 1000 次搜索，无信用卡

### AI / ML

- Hugging Face Spaces：免费托管 ML 应用 Demo
- Weights & Biases：实验追踪、模型管理，100GB 免费存储
- Comet ML：实验追踪、模型注册，个人/学术免费
- Replicate：每月免费 $5 额度跑开源模型
- Google AI Studio：免费 Gemini Flash/Gemma 模型
- Hex：协作数据平台，免费社区版（5 项目）
- Deepnote：数据科学 Notebook，免费（5GB RAM，2 vCPU）
- Datalore：JetBrains Notebook，10GB 存储，120 小时/月

### 数据库

- MongoDB Atlas：512MB 存储，共享集群
- Supabase：500MB 数据库，1GB 存储，5 万月活用户
- PlanetScale：10GB 存储，每月 1 亿行读取
- Neon：0.5GB 存储，每月 100 小时计算
- TiDB Serverless：5GB 存储，100GB 月流量
- SingleStore：5GB 存储，每月 50 亿次操作
- CockroachDB Serverless：5GB 存储，每月 2500 操作单元
- Cloudflare D1：1GB 存储，每天 500 万行读取
- Fauna：100MB 存储，每天 10 万次操作
- Upstash Redis：10MB，每天 1 万条命令
- Dragonfly：免费 300MB Serverless Redis 兼容

### 认证与用户管理

- Auth0：25,000 MAU，无限社交登录
- Clerk：50,000 MRU 每应用
- Supabase Auth：5 万月活用户
- WorkOS：100 万 MAU 免费
- Stytch：1 万 MAU，5 个 SSO/SCIM 连接
- Kinde：7,500 MAU
- Logto：5,000 MAU，开源可自托管
- SuperTokens：5,000 MAU，开源
- Ory：200 日活用户，无限团队成员

### 搜索

- Algolia：每月 1 万次搜索，10 万条记录
- Typesense Cloud：每月 50 万次搜索，50GB 带宽
- MeiliSearch Cloud：文档搜索即服务

### 邮件

- SendGrid：每天 100 封（每月 3000 封）
- Mailgun：每月 3000 封
- Resend：每月 3000 封
- Mailtrap：每月 500 封测试邮件
- Mailjet：每天 200 封（每月 6000 封）
- Postmark：每月 100 封
- Forward Email：免费自定义域名邮箱转发
- Zoho Mail：免费 5 用户，5GB/用户

### CDN 和安全

- Cloudflare：无限域名 CDN + DNS + DDoS + WAF
- jsDelivr：开源 JS/CSS CDN
- Fastly：每月 $50 免费额度
- Let's Encrypt：免费 SSL/TLS 证书
- Socket.dev：依赖供应链安全检测
- GitGuardian：350+ 类型密钥泄露检测，25 人以下免费
- Have I Been Pwned：查询泄露数据
- Mozilla Observatory：网站安全扫描
- SSL Labs：SSL 配置深度分析

### 存储与媒体

- Cloudflare R2：每月 10GB 对象存储，兼容 S3 API
- Backblaze B2：10GB 免费存储，每天 2500 次下载
- Supabase Storage：1GB 文件存储
- Uploadthing：每月 500MB 上传
- TinyPNG：每月 500 张图片压缩
- Cloudinary：每月 25GB 存储 + 25GB 带宽

### 设计/图标/字体

- Figma：免费 3 个项目，无限编辑器
- Font Awesome：免费图标库（Pro 图标需付费）
- Google Fonts：免费 Web 字体
- Undraw：免费 SVG 插画
- Iconscout：每月 25 个免费图标
- BoxySVG：免费 SVG 编辑器
- Photopea：免费在线 PS 替代

### 协作与项目管理

- Notion：免费个人版
- Linear：免费 10 用户
- Jira：免费 10 用户
- Trello：免费无限看板
- Miro：免费 3 块看板
- Slack：免费无限用户（部分功能限制）
- Discord：免费无限用户，语音/视频/屏幕共享
- Element/Matrix：去中心化开源加密聊天
- Zulip：话题式聊天，免费 1 万条搜索历史
- Calendly：免费日程安排

### DNS

- Cloudflare：无限域名免费 DNS
- Duck DNS：免费动态 DNS
- FreeDNS：免费托管 DNS
- He.net：免费 DNS 托管
- Namecheap：免费 DNS（需使用其域名）

### 隧道和内网穿透

- Cloudflare Tunnel：免费 Quick Tunnel，Zero Trust 含 TCP/VPN
- Ngrok：免费 1 个在线隧道，每次重启 8 小时
- Serveo：免费 SSH 端口转发
- Piping Server：免费文件/数据点对点传输

### 测试

- Cypress：开源免费，Dashboard 开源项目免费
- Checkly：代码优先合成监控，免费层充足
- Percy：视觉回归测试，每月 5000 快照
- Lost Pixel：每月 7000 快照，开源免费
- Requestly：开源 HTTP 请求拦截/模拟，10 条规则免费

### 代码质量

- SonarCloud：自动化代码分析，开源免费
- Codacy：自动代码审查，不限公开/私有仓库
- CodeFactor：自动代码审查，1 个私有仓库
- DeepSource：持续代码分析，安全/性能/反模式检测
- Coveralls：测试覆盖率报告，开源免费
- Shields.io：开源项目质量徽章

---

## 全分类索引

完整 50+ 分类清单（原文 1600+ 条目）：https://github.com/ripienaar/free-for-dev

分类列表：Cloud Management / Analytics / APIs Data ML / Artifact Repos / BaaS / Low-code / CDN / CI CD / CMS / Code Generation / Code Quality / Code Search / Crash Handling / Data Viz / Managed Data / Design UI / Dev Blogging / DNS / Docker / Domain / Education / Email / Feature Toggles / Font / Forms / Generative AI / IaaS / IDE / Mobile Verification / Issue Tracking / Log Management / Mobile Distribution / Management Systems / Messaging / Monitoring / PaaS / Package Build / Payment / Privacy / Screenshot APIs / Flutter / Search / Security PKI / Auth / Source Code / Storage / Tunneling / Testing / Team Collaboration / Translation / Session Recording / Web Hosting / Commenting / Remote Desktop
