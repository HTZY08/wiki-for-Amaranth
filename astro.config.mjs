import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://wiki-for-amaranth.pages.dev',
  integrations: [starlight({
    title: 'Amaranth Wiki',
    defaultLocale: 'root',
    locales: {
      root: { label: '简体中文', lang: 'zh-cn' },
    },
    customCss: ['./src/styles/custom.css'],
    sidebar: [
      {
        label: '🏠 首页',
        link: '/',
      },
      {
        label: '☁️ AI云组会',
        items: [{ autogenerate: { directory: 'ai-daily' } }],
      },
      {
        label: '📦 Skill 分享',
        collapsed: false,
        items: [
          { label: '目录', link: 'skill-share/' },
          { label: 'Review Writing', link: 'skill-share/review-writing/' },
          { label: 'Async Delegate', link: 'skill-share/async-delegate/' },
          { label: 'Search Routing', link: 'skill-share/search-routing/' },
          { label: '🔮 共振引擎', link: 'skill-share/resonance-engine/' },
        ],
      },
      {
        label: '🔧 折腾记录',
        link: 'notes/tinkering-timeline/',
      },
      {
        label: '🆓 白嫖指南',
        collapsed: false,
        items: [
          { label: '商汤 SenseNova 免费 API', link: 'freebies/2026-06-10-sensenova-token-plan/' },
        ],
      },
      {
        label: '🤖 Hermes Agent',
        collapsed: false,
        items: [
          { label: '环境准备', link: 'hermes/env-prep/' },
          { label: 'Docker 部署', link: 'hermes/docker-deploy/' },
          { label: '代理配置', link: 'hermes/proxy-setup/' },
          { label: '配置指南', link: 'hermes/configuration/' },
          { label: '验证运行', link: 'hermes/verify/' },
          { label: 'GPU 透传', link: 'hermes/gpu-compute/' },
          { label: '多模型路由', link: 'hermes/model-routing/' },
          { label: '微信接入', link: 'hermes/gateway-wechat/' },
          { label: '技能系统', link: 'hermes/skills/' },
          { label: '定时任务', link: 'hermes/cron-background/' },
          { label: '持久记忆', link: 'hermes/memory-system/' },
          { label: 'CI/CD 自动部署', link: 'hermes/ci-cd/' },
          { label: 'Codex 接入', link: 'hermes/codex-integration/' },
          { label: 'BigSet 集成', link: 'hermes/bigset-integration/' },
          { label: '云端生图', link: 'hermes/cloud-image-gen/' },
          { label: '🧰 完整排障索引', link: 'hermes/troubleshooting-guide/' },
          { label: '🛠 插件开发', link: 'hermes/plugin-development/' },
          { label: '📡 服务器配置快照', link: 'hermes/cloud-server-config/' },
          { label: '🔄 断网兜底', link: 'hermes/network-fallback/' },
        ],
      },
      {
        label: '📝 博客',
        collapsed: true,
        items: [
          { label: '论文→代码：Lau博士落地实践', link: 'blog/lau-hermes-implementations/' },
          { label: '2026 大模型横评', link: 'blog/llm-comparison-2026/' },
          { label: '🤖 AI 信息前沿', link: 'notes/ai-frontier/' },
        ],
      },
      {
        label: '🎮 项目',
        collapsed: true,
        items: [
          { label: 'PPT-Master', link: 'projects/ppt-master/' },
          { label: 'BigSet 部署', link: 'projects/bigset/' },
          { label: '🧰 自定义技能集', link: 'projects/skill-portfolio/' },
          { label: 'ComfyUI 部署与训练', link: 'projects/comfyui/' },
          { label: '🧬 DNA Sim Engine', link: 'projects/dna-sim-engine/' },
          { label: '🔮 共振引擎', link: 'projects/resonance-engine/' },
          {
            label: '📖 详解',
            collapsed: true,
            items: [
              { label: 'MCP 详解', link: 'projects/mcp-guide/' },
              { label: '命令详解', link: 'projects/commands-guide/' },
            ],
          },
        ],
      },
      {
        label: '📚 笔记',
        collapsed: true,
        items: [
          { label: '系统架构总览', link: 'notes/architecture/' },
          { label: '异步任务委派系统', link: 'notes/async-delegate/' },
          { label: '常用命令速查', link: 'notes/quick-reference/' },
          { label: '设计原理摘要', link: 'notes/design-principles/' },
          { label: 'API 渠道速查', link: 'notes/api-reference/' },
          { label: '排障手册', link: 'notes/troubleshooting/' },
          { label: '工作流自动化', link: 'notes/automation/' },
          { label: '🎯 GPU 训练踩坑', link: 'notes/gpu-training-pitfalls/' },
          { label: '⚖️ 本地 vs 云端：架构决策', link: 'notes/cloud-vs-local/' },
          { label: '💻 笔记本工作站配置日志', link: 'notes/笔记本工作站配置日志/' },
        ],
      },
    ],
  })],
});
