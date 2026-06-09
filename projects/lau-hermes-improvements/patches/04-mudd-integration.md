# MUDDFormer集成补丁说明

## 论文
**MUDDFormer: Breaking Residual Bottlenecks in Transformers via Multiway Dynamic Dense Connections**
- 会议: ICML 2025
- 核心: Q/K/V/R四路独立动态密集连接替代残差
- 代码: https://github.com/Caiyun-AI/MUDDFormer

## Hermes映射
| MUDDFormer | Hermes |
|-----------|--------|
| Q路径 | 查询/搜索任务路径(web, search) |
| K路径 | 知识/记忆任务路径(session_search, memory) |
| V路径 | 执行/操作任务路径(terminal, file) |
| R路径 | 交互/写作任务路径(file, todo) |
| 动态权重 | 根据输入关键词自动路由 |

## 代码
`plugins/mudd_orchestrator.py`
