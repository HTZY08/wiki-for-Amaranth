---
title: 自定义技能集
description: 自建的 Hermes Skill 生态——从论文建模到风格复刻，覆盖科研计算、自动化、写作辅助等方向
---

这里收录的是基于日常工作流沉淀的自定义技能，每个都是一个可复用的自动化能力单元。

## 🔬 学术计算

### 论文计算模型提取与实现
从论文/学位论文中提取数学模型，实现第一性原理仿真代码，通过蒙特卡洛和多参数迭代测试做统计验证。

> `paper-computational-modeling`
> **能力**：论文→代码的自动建模管道  
> **适用**：导师扔给你一篇论文说"把这个跑出来"  
> **验证方式**：Monte Carlo + 多参数迭代测试

### 核酸热力学引擎 (NN 模型)
纯 Python 实现 DNA/RNA Nearest-Neighbor 热力学——自由能计算、链置换动力学、盐浓度校正、Tm 预测、序列设计优化、ITC 模拟、荧光探针建模。

> `nucleic-acid-thermodynamics`
> **能力**：无外部依赖的 NUPACK 替代方案  
> **适用**：DNAzyme 动力学、CRISPR 探针设计、微流控核酸检测  
> **数值验证**：NN 参数表与实验数据交叉比对

### DFT/MD 科学计算套件
零预算跑 DFT (CP2K/Quantum ESPRESSO) 和 MD (GROMACS) 的完整方案——本地 GPU 编译、免费云端算力发现、GFW 突破、学术授权绕过策略。

> `dft-md-computing` + `scientific-computing-resources` + `scientific-computing-setup`
> **适用**：材料/化学/物理硕士生，没有学校超算账号  
> **亮点**：从裸机编译到生产跑批的全链路指导

## 🤖 自动化

### Playwright 网页自动化
国内平台浏览器自动化——反检测、验证码绕过、二维码扫码登录流程。弥补 Hermes 浏览器工具无法执行 JS 的短板。

> `playwright-web-automation`
> **适用**：抖音数据采集、政务平台自动填报、需要 JS 执行的网页操作  
> **技术栈**：Playwright + 反检测配置

### 微信接入机器人
微信个人号接入 Hermes 的全流程——iLink Bot API 扫码登录、环境变量配置、Gateway 启动、s6 容器桥接。

> `hermes-wechat-setup`
> **能力**：微信→Hermes→多模型推理的完整链路

## ✍️ 写作与语言

### 中文论文语言编辑器
对工学硕士论文做语言收束与终稿净化——句式润色、AI 词清除、文体一致性、格式净化。不扩写内容，只做减法。

> `chinese-academic-editing`
> **能力**：压低翻译腔、套话、空泛评价和概念标签  
> **适用**：论文终稿提交前的最后一轮语言打磨

### 用户风格语料库
系统收集语言风格数据，用于复刻写作/说话风格的管道。每次对话后主动追加观察，不做被动等待。

> `user-style-corpus` + `user-style-collection`
> **用途**：训练个人风格 LoRA / 风格一致性保持  
> **采集方式**：对话中持续隐式积累，无需用户主动提供样本
