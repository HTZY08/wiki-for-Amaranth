# 大综述 (Comprehensive Review) 框架模板

## 什么是大综述

大综述不捍卫一个单一论点，而是提供一个分析框架——读者可以用它来理解整个领域、比较不同方法、在特定场景中做出选择。典型的例子是"简化-代价交换"（simplify-and-pay trade-off）框架。

## 框架模板：简化-代价交换

### 核心问题
每一次技术简化都放弃了什么、换来了什么？在什么场景下这个代价可以接受？

### Section结构示例（POCT核酸检测）

```
1.  Introduction — Open with a specific tension point, not WHO ASSURED
2.  Analytical framework — The organizing principle (six-dimension comparison)
3.  Sample preparation — The first bottleneck with quantitative inhibitor data
4.  Technology tree — Organized by "what was sacrificed", not by chronology
5.  Paradigm-shifting method — e.g. CRISPR-Dx as a separate paradigm
6.  Signal readout — The cost of each simplification in the optical chain
7.  Integration — Fluid control logic categories
8.  Commercialization gap — Academic LOD vs real product LOD
9.  Outlook — AI, synthetic biology, wearables
10. Conclusion — Scenario-method decision tree
```

### 六维比较框架

| 维度 | 符号 | 度量 | 交换关系 |
|------|------|------|---------|
| 灵敏度 | S | LOD (copies/reaction or copies/mL) | S-Sp: 提高严谨度损失速度 |
| 特异性 | Sp | NTC假阳性率 (%) | Sp-V: 更快的扩增损失特异性 |
| 速度 | V | TAT (min) | V-R: 越快越不鲁棒 |
| 便携性 | P | 设备重量/体积/电源需求 | P-S: 越便携灵敏度越低 |
| 成本 | C | 试剂+耗材+设备摊销 (元) | C-R: 越便宜越不鲁棒 |
| 鲁棒性 | R | 基质退化因子 (倍数) | R-P: 越鲁棒越不便携 |

### 场景-方法决策树模板

```
场景类型识别
├─ 急诊/ICU（极高S+Sp, C不敏感）
│  └─ 全集成RT-PCR + 荧光读出
│     (代价: 设备体积大, 单次成本高)
├─ 基层诊所（中等S, 成本敏感）
│  ├─ 如果靶标是DNA: RPA + CRISPR侧流
│  └─ 如果靶标是RNA: RT-LAMP + 手机荧光
├─ 居家自检（极高P+R, 极低误判容忍度）
│  └─ 分子POCT卡盒 (代价: 成本/灵敏度退化)
└─ 野外/资源零限（最低设备需求）
   └─ 纸基LAMP + 比色 (代价: 灵敏度受限)
```

### 学术LOD到产品LOD的校正因子模板

| 前处理方案 | 回收率因子 | 浓缩因子 | 抑制剂损失 | 基质CV | 总校正因子 |
|-----------|-----------|---------|-----------|-------|-----------|
| 缓冲液(学术基准) | 1.0 | 1.0 | 1.0 | 1.0 | 1x |
| 直接裂解-鼻咽 | 0.7 | 0.5 | 0.2 | 2.5 | ~14x退化 |
| 芯片磁珠提取 | 0.6 | 1.7 | 0.9 | 1.3 | ~1.3x退化 |
| 滤纸(DBS) | 0.2 | 0.3 | 0.8 | 3.0 | ~60x退化 |

### 为什么框架优先于论点

大综述读者（Chem Rev / Chem Soc Rev的受众）不是来被说服的——他们来找的是理解领域的方法。一个统一的比较框架比一个特定的论证更有价值。

### 适用场景
- 领域已经成熟到有多种技术路径竞争（如POCT核酸：PCR vs LAMP vs RPA vs CRISPR）
- 不存在"最优"方法，只有"场景最适配"方法
- 学术LOD与产品表现之间存在系统性断层需要解释
