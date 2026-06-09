# LoRI集成补丁说明

## 论文
**LoRI: Reducing Cross-Task Interference in Multi-Task Low-Rank Adaptation**
- 会议: COLM 2025
- 核心: 冻结A矩阵 + 稀疏B掩码(90%稀疏) + 正交性
- 代码: https://github.com/juzhengz/LoRI/

## Hermes映射
| LoRI | Hermes |
|-----|--------|
| 冻结A矩阵(工具全集) | 工具注册表永远完整 |
| 稀疏B矩阵(5%参数) | 每类任务仅激活6-8个工具 |
| 正交性无干扰 | 不同任务类型不重叠 |

## 代码
`plugins/lori_selector.py`
