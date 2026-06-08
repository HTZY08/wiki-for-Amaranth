import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://wiki.yourdomain.com',
  integrations: [starlight({
    title: 'Amaranth Wiki',
    defaultLocale: 'zh-cn',
    locales: {
      'zh-cn': { label: '简体中文', lang: 'zh-cn' },
    },
    sidebar: [{
      label: 'Hermes 部署',
      items: [
        { label: '概述', link: 'hermes/' },
        { label: 'Docker 部署', link: 'hermes/docker-deploy/' },
        { label: '代理配置', link: 'hermes/proxy-setup/' },
        { label: 'GPU 透传', link: 'hermes/gpu-compute/' },
        { label: '多模型路由', link: 'hermes/model-routing/' },
        { label: '技能系统', link: 'hermes/skills-system/' },
        { label: '微信 Gateway', link: 'hermes/gateway-wechat/' },
        { label: '定时任务与后台', link: 'hermes/cron-background/' },
        { label: '持久记忆系统', link: 'hermes/memory-system/' },
      ],
    }],
  })],
});
