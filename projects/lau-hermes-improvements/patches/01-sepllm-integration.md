# SepLLM集成补丁说明

## 论文
**SepLLM: Accelerate Large Language Models by Compressing One Segment into One Separator**
- 会议: ICML 2025
- 核心洞察: 自然语言中的分隔符(句号、换行、分段符)在注意力分数中占比异常高，
  本质上在充当段落的"摘要节点"。
- 源码: https://github.com/HKUDS/SepLLM

## 映射关系

| SepLLM概念 | Hermes映射 |
|-----------|-----------|
| 稀疏注意力掩码(Initial+Separator+Neighbor) | 三段式消息拆分(系统提示+分隔符+最新N条) |
| 段落→分隔符压缩 | 长段→"[工具: xxx, 主题: xxx]"摘要标记 |
| 流式缓存管理(四块缓存) | Initial / Separator / Past / Local 缓存 |
| Training-Free模式 | 纯规则驱动，无需修改模型 |

## 代码

`plugins/sepllm_compressor.py` — 独立的context_engine插件

## 预期效果

- 长对话中token减少 15-30%
- 零LLM调用（规则驱动，免费）
- 保留关键上下文结构（不损坏分隔符信息）

## 风险

- 规则覆盖不全：某些对话结构可能没有被分隔符模式匹配到
- 过度压缩：过短的段也会被命中，需要min_segment_len参数控制
