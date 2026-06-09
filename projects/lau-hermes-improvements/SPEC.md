# 集成SPEC：三个论文落地方案的Hermes集成指南

本文档详细说明如何将三个P0级实现集成到Hermes Agent中。
每个方案均支持插件方式（无侵入）或补丁方式（深度集成）。

---

## 1. SepLLM Compressor 集成

### 方式A：直接替换context_engine（推荐，无代码修改）

复制插件到Hermes配置目录：

```bash
cp plugins/sepllm_compressor.py /opt/hermes/plugins/context_engine/sepllm/
```

在 `~/.hermes/config.yaml` 中设置：

```yaml
context:
  engine: sepllm
  sepllm:
    local_window: 20
    min_segment_len: 100
```

### 方式B：在现有ContextCompressor中嵌入（补丁）

修改 `agent/context_compressor.py`，在 `compress()` 方法中LLM摘要之前加入：

```python
# 在 ContextCompressor.compress() 方法中，约第900行
# 在步骤1（prune tool results）之后、步骤4（LLM summarization）之前插入

# --- SepLLM pre-compression ---
_sepllm = getattr(self, '_sepllm_compressor', None)
if _sepllm is None:
    from plugins.sepllm_compressor import SepLLMCompressor
    _sepllm = SepLLMCompressor()
    self._sepllm_compressor = _sepllm
messages = _sepllm.compress_messages(messages)
# --- End SepLLM ---
```

### 验证

```python
# 测试压缩效果
from plugins.sepllm_compressor import SepLLMCompressor
c = SepLLMCompressor()
original = "```python\n" + "print('hello')\n" * 50 + "```"
compressed = c.compress_content(original)
print(f"原始: {len(original)} chars → 压缩后: {len(compressed)} chars")
# 预期: 长代码块被压缩为 文件头+...压缩标记...+文件尾
```

---

## 2. MoR Adaptive Depth 集成

### 方式A：context_engine插件

```bash
cp plugins/mor_context_engine.py /opt/hermes/plugins/context_engine/mor/
```

config.yaml:

```yaml
context:
  engine: mor
  mor:
    local_window: 20
    default_depth: 2
```

### 方式B：run_agent.py补丁（核心修改）

在 `agent/run_agent.py` 的 `run_conversation()` 中：

**修改1：进入工具循环前（约原第150行）**

```python
# 替换:
# max_turns = DEFAULT_MAX_TURNS

# 改为:
if hasattr(ctx_engine, 'estimate_complexity'):
    depth = ctx_engine.estimate_complexity(user_message)
    max_turns = ctx_engine.get_max_turns()
    logger.info("MoR: depth=%d, max_turns=%d", depth, max_turns)
else:
    max_turns = DEFAULT_MAX_TURNS
```

**修改2：每次tool call后（约原第200行）**

```python
# 在每个工具调用迭代结束后加入:
if hasattr(ctx_engine, 'should_early_exit'):
    should_exit, reason = should_early_exit(
        turn_count=turn_count,
        last_assistant_content=last_assistant_message.get('content', ''),
        last_tool_results=[r.get('content', '') for r in recent_results],
    )
    if should_exit:
        logger.info("MoR early exit at turn %d: %s", turn_count, reason)
        break
```

### 验证

```python
from plugins.mor_context_engine import MoRRouter

# 简单问题
d1 = MoRRouter.estimate_complexity("今天天气怎么样")
print(f"简单问题深度: {d1} → max_turns={MoRRouter.max_turns_for_depth(d1)}")
# 预期: 1 → 5

# 复杂问题
d2 = MoRRouter.estimate_complexity("分析React和Vue在性能、安全性和可维护性方面的差异")
print(f"复杂问题深度: {d2} → max_turns={MoRRouter.max_turns_for_depth(d2)}")
# 预期: 3 → 30
```

---

## 3. Multiverse MapReduce 集成

### 方式A：skill（推荐，零修改）

复制skill到Hermes配置目录：

```bash
cp -r skills/multiverse-mapreduce/ ~/.hermes/skills/
```

当用户指令包含"对比"、"多角度"、"同时"等关键词时，skill自动激活。

### 方式B：plugin注册

```bash
cp plugins/multiverse_mapreduce.py /opt/hermes/plugins/multiverse/
```

在config.yaml:

```yaml
tools:
  enabled_plugins: [multiverse]
```

### 方式C：delegate_tool.py增强（深度集成）

在 `tools/delegate_tool.py` 中，新增 MapReduce 执行模式：

```python
# 在 handle_delegate_task() 函数中，处理单个goal时：
# 在执行普通delegate_task前，先用multiverse分析可并行性

def _handle_map_reduce(goal, context, max_parallel=3):
    """MapReduce处理逻辑"""
    from plugins.multiverse_mapreduce import analyze_task, merge_results
    
    sub_tasks = analyze_task(goal, context)
    if not sub_tasks:
        return None  # 无法分解，按常规处理
    
    # 构建并行tasks
    tasks = [{
        "goal": st["goal"],
        "context": st.get("context", context),
    } for st in sub_tasks[:max_parallel]]
    
    return tasks  # 返回给delegate_task的tasks参数
```

### 验证

```python
from plugins.multiverse_mapreduce import analyze_task, merge_results

# 测试分解
tasks = analyze_task("研究React、Vue和Svelte的优缺点")
print(f"分解为{len(tasks)}个子任务:")
for t in tasks:
    print(f"  - {t['goal']}")
# 预期: 3个子任务

# 测试合并
result = merge_results(
    "框架对比",
    [("React分析", "React的优点是..."),
     ("Vue分析", "Vue的优点是...")]
)
print(result[:200])
```

---

## 集成检查清单

### SepLLM
- [ ] 插件复制到指定目录
- [ ] config.yaml设置context.engine: sepllm
- [ ] 测试压缩率（目标15-30%）
- [ ] 验证长对话下的消息完整性

### MoR
- [ ] 插件复制到指定目录  
- [ ] 测试复杂度路由（1/2/3三级是否准确）
- [ ] 测试提前退出（条件触发是否及时）
- [ ] 验证不同深度下的token消耗差异

### Multiverse
- [ ] skill复制到~/.hermes/skills/
- [ ] 测试"对比A和B"类指令是否触发
- [ ] 测试3个子任务并发执行
- [ ] 验证结果合并质量

## 回滚方案

每个方案都支持插件级安装（复制文件即可，不修改核心代码）。
如需回滚：
- SepLLM: 删除插件目录 + 改回context.engine: default
- MoR: 同上
- Multiverse: 删除skill目录 + 移除plugin配置
