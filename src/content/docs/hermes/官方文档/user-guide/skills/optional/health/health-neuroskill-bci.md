---
title: "Neuroskill Bci"
---

## 示例交互（Example Interactions）

**"我现在状态如何？"**
```bash
npx neuroskill status --json
```
→ 自然解读分数，提及专注度、放松度、情绪以及任何值得注意的比率（如FAA、TBR）。仅在指标显示需要时才建议采取行动。

**"我无法集中注意力"**
```bash
npx neuroskill status --json
```
→ 检查指标是否证实（高θ波、低β波、TBR上升、高困倦度）。
→ 如果得到证实，从 `references/protocols.md` 中建议一个合适的方案。
→ 如果指标看起来正常，问题可能源于动机而非神经状态。

**"比较我今天和昨天的专注度"**
```bash
npx neuroskill compare --json
```
→ 解读趋势，而非单纯数字。提及哪些方面改善了、哪些下降了，以及可能的原因。

**"我上次进入心流状态是什么时候？"**
```bash
npx neuroskill search-labels "flow" --json
npx neuroskill search --json
```
→ 报告时间戳、相关指标以及用户当时正在做什么（通过标签信息）。

**"我睡得怎么样？"**
```bash
npx neuroskill sleep --json
```
→ 报告睡眠结构（N3百分比、REM百分比、效率），对比健康目标，并指出任何问题（如高唤醒次数、低REM）。

**"标记此刻——我刚有了一个突破"**
```bash
npx neuroskill label "breakthrough"
```
→ 确认标签已保存。可选项：记录当前指标以记住该状态。

---

## 参考文献（References）

- [NeuroSkill 论文 — arXiv:2603.03212](https://arxiv.org/abs/2603.03212) (Kosmyna & Hauptmann, MIT Media Lab)
- [NeuroSkill 桌面应用](https://github.com/NeuroSkill-com/skill) (GPLv3)
- [NeuroLoop CLI 伴侣](https://github.com/NeuroSkill-com/neuroloop) (GPLv3)
- [MIT 媒体实验室项目](https://www.media.mit.edu/projects/neuroskill/overview/)