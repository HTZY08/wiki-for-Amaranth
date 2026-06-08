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
    sidebar: [
      {
        label: '🏠 首页',
        link: '/',
      },
      {
        label: '🤖 Hermes Agent',
        collapsed: false,
        items: [
          { label: '环境准备', link: 'hermes/env-prep/' },
          { label: 'Docker 部署', link: 'hermes/docker-deploy/' },
          { label: '代理配置', link: 'hermes/proxy-setup/' },
          { label: '基础配置', link: 'hermes/basic-config/' },
          { label: '验证运行', link: 'hermes/verify/' },
          { label: 'GPU 透传', link: 'hermes/gpu-compute/' },
          { label: '多模型路由', link: 'hermes/model-routing/' },
          { label: '微信接入', link: 'hermes/gateway-wechat/' },
          { label: '技能系统', link: 'hermes/skills-system/' },
          { label: '定时任务', link: 'hermes/cron-background/' },
          { label: '持久记忆', link: 'hermes/memory-system/' },
          { label: 'CI/CD 自动部署', link: 'hermes/ci-cd/' },
          { label: 'BigSet 集成', link: 'hermes/bigset-integration/' },
        ],
      },
      {
        label: '📝 博客',
        collapsed: true,
        items: [
          { label: '暂无内容', link: '#' },
        ],
      },
      {
        label: '🎮 项目',
        collapsed: true,
        items: [
          { label: 'PPT-Master', link: 'projects/ppt-master/' },
          { label: 'BigSet 部署', link: 'projects/bigset/' },
          { label: '🧰 自定义技能集', link: 'projects/skill-portfolio/' },
          {
            label: '📖 详解',
            collapsed: true,
            items: [
              { label: 'Skill 详解', link: 'projects/skills-guide/' },
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
          { label: '技能索引', link: 'notes/skills-index/' },
          { label: '设计原理摘要', link: 'notes/design-principles/' },
          { label: '配置模板参考', link: 'notes/config-templates/' },
          { label: 'API 渠道速查', link: 'notes/api-reference/' },
          { label: '故障排除手册', link: 'notes/troubleshooting/' },
          { label: '工作流自动化', link: 'notes/automation/' },
        ],
      },
    ],
  })],
});
