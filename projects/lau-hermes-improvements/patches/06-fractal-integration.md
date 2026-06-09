# 分形递归Skill集成补丁说明

## 论文
**Fractal Generative Models**
- 发表: TMLR 2025
- 作者: 何恺明团队
- 核心: 递归原子模块 → 自相似分形架构
- 代码: https://github.com/LTH14/fractalgen

## Hermes映射
| 分形生成 | Hermes |
|---------|--------|
| 原子生成模块 | 标准处理单元 |
| 递归调用 | skill递归调用自身 |
| 4级分形 | Level N → Level N-1 递归 |
| 结果合成 | 子结果合并 |

## 代码
`skills/fractal-recursive/SKILL.md`
