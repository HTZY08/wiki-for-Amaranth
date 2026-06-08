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
      items: [{ autogenerate: { directory: 'hermes' } }],
    }],
  })],
});
