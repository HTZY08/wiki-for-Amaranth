---
title: CI/CD 自动部署
description: 推送代码到 GitHub 后自动构建并部署到 Cloudflare Pages
---

本 Wiki 使用 GitHub + Cloudflare Pages 实现自动部署。你只需要把更新推送到 GitHub，系统会自动构建并发布。

---

## 部署流程

```
你本地修改 → git push → GitHub 收到更新
                         ↓
                   GitHub Actions 自动触发
                         ↓
                   安装依赖、构建静态页面
                         ↓
                   Cloudflare Pages 部署
                         ↓
                   网站更新完成 🎉
```

## 技术栈

| 组件 | 用途 |
|------|------|
| **Astro + Starlight** | 静态网站框架 |
| **GitHub** | 代码托管 |
| **GitHub Actions** | CI/CD 流水线 |
| **Cloudflare Pages** | 静态网站托管 |

## 日常操作

### 修改内容

所有文档都是 Markdown 文件，存放在 `src/content/docs/` 目录下：

```bash
src/content/docs/
├── index.md                    # 首页
└── hermes/
    ├── env-prep.md             # 环境准备
    ├── docker-deploy.md        # Docker 部署
    ├── proxy-setup.md          # 代理配置
    ├── basic-config.md         # 基础配置
    ├── verify.md               # 验证运行
    ├── gpu-compute.md          # GPU 透传
    ├── model-routing.md        # 多模型路由
    ├── gateway-wechat.md       # 微信接入
    ├── skills-system.md        # 技能系统
    ├── cron-background.md      # 定时任务
    ├── memory-system.md        # 持久记忆
    └── ci-cd.md                # 本页
```

### 添加新页面

1. 在目录下新建 `.md` 文件，开头加上 YAML 元数据：

```markdown
---
title: 页面标题
description: 简短描述
---

正文内容...
```

2. 在 `astro.config.mjs` 的 `sidebar` 中添加导航链接

### 预览本地更改

```bash
npm run dev
```

在浏览器中打开 `http://localhost:4321` 即可预览。

### 发布

```bash
git add .
git commit -m "更新说明"
git push
```

推送后约 1-2 分钟，网站自动更新。

## 工作流文件

CI/CD 配置在 `.github/workflows/deploy.yml`，内容如下：

```yaml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: \${{ secrets.CLOUDFARE }}
          command: pages deploy dist --project-name wiki-for-amaranth --branch main
```

### 依赖的 Secrets

需要在 GitHub 仓库的 Settings → Secrets and Variables → Actions 中配置：

| Secret 名称 | 说明 |
|------------|------|
| `CLOUDFARE` | Cloudflare API Token，用于部署到 Pages |

## 域名

- **Pages 默认域名**: `https://wiki-for-amaranth.pages.dev`
- 如需绑定自定义域名，在 Cloudflare Pages 的域名设置中添加
