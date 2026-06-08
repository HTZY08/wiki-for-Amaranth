import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://wiki-for-amaranth.pages.dev',
  integrations: [starlight({
    title: 'Amaranth Wiki',
    defaultLocale: 'zh-cn',
    locales: {
      'zh-cn': { label: '简体中文', lang: 'zh-cn' },
    },
    sidebar: [
      {
        label: '🏠 首页',
        link: '/',
      },
      {
        label: '🚀 入门指南',
        items: [
          { label: '环境准备', link: 'hermes/env-prep/' },
          { label: 'Docker 部署', link: 'hermes/docker-deploy/' },
          { label: '代理配置', link: 'hermes/proxy-setup/' },
          { label: '基础配置', link: 'hermes/basic-config/' },
          { label: '验证运行', link: 'hermes/verify/' },
        ],
      },
      {
        label: '⚙️ 进阶配置',
        items: [
          { label: 'GPU 透传', link: 'hermes/gpu-compute/' },
          { label: '多模型路由', link: 'hermes/model-routing/' },
          { label: '微信接入', link: 'hermes/gateway-wechat/' },
        ],
      },
      {
        label: '🧠 扩展系统',
        items: [
          { label: '技能系统', link: 'hermes/skills-system/' },
          { label: '定时任务', link: 'hermes/cron-background/' },
          { label: '持久记忆', link: 'hermes/memory-system/' },
        ],
      },
      {
        label: '🔧 运维',
        items: [
          { label: 'CI/CD 自动部署', link: 'hermes/ci-cd/' },
        ],
      },
    ],
  })],
});
