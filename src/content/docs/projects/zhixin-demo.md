---
title: 针心 · AI 手性探针设计 Demo
description: 挑战杯（小挑）——神经退行性疾病早筛 AI 探针库智能匹配演示
---

挑战杯参赛项目 **"针心"** 的 AI 探针库匹配演示原型。

## 演示流程

```
选择靶标（Aβ42 / p-Tau181 / NfL / GFAP）
  ↓
AI 从 3000+ 手性探针基元库中搜索匹配
  ↓
展示 Top 候选探针（亲和力/选择性/稳定性评分）
  ↓
NGL Viewer 3D 展示分子结构（可拖拽旋转/缩放）
  ↓
综合评估 → 灵敏度/特异性/成本预测
```

## 如何运行

```bash
cd /opt/data/projects/zhixin-demo
python3 -m http.server 8080
```

浏览器打开 `http://localhost:8080` 即可。

## 技术栈

- **前端**：纯 HTML + Tailwind CSS（CDN）
- **3D 分子查看**：NGL Viewer（CDN）
- **数据**：JSON 文件 + MOL 分子结构文件
- **部署**：Python HTTP 服务器 / Cloudflare Pages

## 替换为真实数据

此 Demo 当前使用样例数据。替换真实数据：

1. 将实际探针分子结构导出为 MOL/SDF，放入 `probes/` 目录
2. 编辑 `data/library.json`，替换探针 ID、评分、结构文件路径、描述
3. `index.html` 无需修改代码即可适配新数据
