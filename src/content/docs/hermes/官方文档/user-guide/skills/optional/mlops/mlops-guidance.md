--- frontmatter ---
---
title: "指导 (Guidance)"
sidebar_label: "指导 (Guidance)"
description: "使用正则表达式和语法控制LLM输出，保证有效的JSON/XML/代码生成，强制执行结构化格式，并使用Guidance（微软研究院的约束生成框架）构建多步骤工作流程。"
---

--- body ---
--- body ---
--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 指导 (Guidance)

使用正则表达式和语法控制LLM输出，保证有效的JSON/XML/代码生成，强制执行结构化格式，并使用Guidance（微软研究院的约束生成框架）构建多步骤工作流程。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/mlops/guidance` 安装 |
| 路径 | `optional-skills/mlops/guidance` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `guidance`, `transformers` |
| 平台 | linux, macos, windows |
| 标签 | `Prompt Engineering`, `Guidance`, `Constrained Generation`, `Structured Output`, `JSON Validation`, `Grammar`, `Microsoft Research`, `Format Enforcement`, `Multi-Step Workflows` |

## 参考：完整SKILL.md

:::info
以下是Hermes在此技能被触发时加载的完整技能定义。这是技能激活时代理看到的指令。
:::

# Guidance：约束生成

## 何时使用此技能

在以下情况下使用Guidance：
- **控制LLM输出语法**（使用正则表达式或语法）
- **保证生成有效的JSON/XML/代码**
- **降低延迟**（相较于传统提示方法）
- **强制执行结构化格式**（日期、电子邮件、ID等）
- **使用Python风格控制流构建多步骤工作流程**
- **通过语法约束防止无效输出**

**GitHub星标**: 18,000+ | **来源**: 微软研究院

## 安装

```bash
# 基础安装
pip install guidance

# 使用特定后端
pip install guidance[transformers]  # Hugging Face模型
pip install guidance[llama_cpp]     # llama.cpp模型
```

## 快速开始

### 基本示例：结构化生成

```python
from guidance import models, gen

# 加载模型（支持OpenAI、Transformers、llama.cpp）
lm = models.OpenAI("gpt-4")

# 使用约束进行生成
result = lm + "法国的首都是" + gen("capital", max_tokens=5)

print(result["capital"])  # "巴黎"
```

### 使用Anthropic Claude

```python
from guidance import models, gen, system, user, assistant

# 配置Claude
lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 使用上下文管理器进行聊天格式
with system():
    lm += "你是一个乐于助人的助手。"

with user():
    lm += "法国的首都是什么？"

with assistant():
    lm += gen(max_tokens=20)
```

## 核心概念

### 1. 上下文管理器（Context Managers）

Guidance使用Python风格的上下文管理器进行聊天式交互。

```python
from guidance import system, user, assistant, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 系统消息
with system():
    lm += "你是JSON生成专家。"

# 用户消息
with user():
    lm += "生成一个包含姓名和年龄的人物对象。"

# 助手回复
with assistant():
    lm += gen("response", max_tokens=100)

print(lm["response"])
```

**优势：**
- 自然的聊天流程
- 清晰的角色分离
- 易于阅读和维护

### 2. 约束生成（Constrained Generation）

Guidance确保输出使用正则表达式或语法匹配指定的模式。

#### 正则表达式约束

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 约束为有效的电子邮件格式
lm += "邮箱: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# 约束为日期格式（YYYY-MM-DD）
lm += "日期: " + gen("date", regex=r"\d{4}-\d{2}-\d{2}")

# 约束为电话号码
lm += "电话: " + gen("phone", regex=r"\d{3}-\d{3}-\d{4}")

print(lm["email"])  # 保证有效的电子邮件
print(lm["date"])   # 保证YYYY-MM-DD格式
```

**工作原理：**
- 正则表达式在令牌级别转换为语法
- 生成过程中过滤掉无效令牌
- 模型只能生成匹配的输出

#### 选择约束

```python
from guidance import models, gen, select

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 约束为特定选项
lm += "情感: " + select(["positive", "negative", "neutral"], name="sentiment")

# 多项选择
lm += "最佳答案: " + select(
    ["A) 巴黎", "B) 伦敦", "C) 柏林", "D) 马德里"],
    name="answer"
)

print(lm["sentiment"])  # 其中之一：positive, negative, neutral
print(lm["answer"])     # 其中之一：A, B, C, D
```

### 3. 令牌修复（Token Healing）

Guidance自动“修复”提示和生成之间的令牌边界。

**问题：** 分词导致不自然的边界。

```python
# 没有令牌修复
prompt = "法国的首都是 "
# 最后一个令牌： "是 "
# 第一个生成的令牌可能是 " 巴"（带前导空格）
# 结果： "法国的首都是  巴黎"（双空格！）
```

**解决方案：** Guidance后退一个令牌并重新生成。

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# 默认启用令牌修复
lm += "法国的首都是" + gen("capital", max_tokens=5)
# 结果： "法国的首都是巴黎"（正确空格）
```

**优势：**
- 自然的文本边界
- 没有尴尬的空格问题
- 更好的模型性能（看到自然的令牌序列）

### 4. 基于语法的生成（Grammar-Based Generation）

使用上下文无关语法定义复杂结构。

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# JSON语法（简化）
json_grammar = """
{
    "name": <gen name regex="[A-Za-z ]+" max_tokens=20>,
    "age": <gen age regex="[0-9]+" max_tokens=3>,
    "email": <gen email regex="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}" max_tokens=50>
}
"""

# 生成有效的JSON
lm += gen("person", grammar=json_grammar)

print(lm["person"])  # 保证有效的JSON结构
```

**使用场景：**
- 复杂的结构化输出
- 嵌套数据结构
- 编程语言语法
- 领域特定语言（DSL）

### 5. Guidance函数（Guidance Functions）

使用 `@guidance` 装饰器创建可重用的生成模式。

```python
from guidance import guidance, gen, models

@guidance
def generate_person(lm):
    """生成一个包含姓名和年龄的人物。"""
    lm += "姓名: " + gen("name", max_tokens=20, stop="\n")
    lm += "\n年龄: " + gen("age", regex=r"[0-9]+", max_tokens=3)
    return lm

# 使用该函数
lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = generate_person(lm)

print(lm["name"])
print(lm["age"])
```

**有状态函数：**

```python
@guidance(stateless=False)
def react_agent(lm, question, tools, max_rounds=5):
    """具有工具使用能力的ReAct代理。"""
    lm += f"问题: {question}\n\n"

    for i in range(max_rounds):
        # 思考
        lm += f"思考 {i+1}: " + gen("thought", stop="\n")

        # 行动
        lm += "\n行动: " + select(list(tools.keys()), name="action")

        # 执行工具
        tool_result = tools[lm["action"]]()
        lm += f"\n观察: {tool_result}\n\n"

        # 检查是否完成
        lm += "完成？ " + select(["是", "否"], name="done")
        if lm["done"] == "是":
            break

    # 最终答案
    lm += "\n最终答案: " + gen("answer", max_tokens=100)
    return lm
```

## 后端配置

### Anthropic Claude

```python
from guidance import models

lm = models.Anthropic(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key"  # 或设置ANTHROPIC_API_KEY环境变量
)
```

### OpenAI

```python
lm = models.OpenAI(
    model="gpt-4o-mini",
    api_key="your-api-key"  # 或设置OPENAI_API_KEY环境变量
)
```

### 本地模型（Transformers）

```python
from guidance.models import Transformers

lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda"  # 或 "cpu"
)
```

### 本地模型（llama.cpp）

```python
from guidance.models import LlamaCpp

lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35
)
```

## 常见模式

### 模式1：JSON生成

```python
from guidance import models, gen, system, user, assistant

lm = models.Anthropic("claude-sonnet-4-5-20250929")

with system():
    lm += "你生成有效的JSON。"

with user():
    lm += "生成一个用户档案，包含姓名、年龄和邮箱。"

with assistant():
    lm += """{
    "name": """ + gen("name", regex=r'"[A-Za-z ]+"', max_tokens=30) + """,
    "age": """ + gen("age", regex=r"[0-9]+", max_tokens=3) + """,
    "email": """ + gen("email", regex=r'"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"', max_tokens=50) + """
}"""

print(lm)  # 保证有效JSON
```

### 模式2：分类

```python
from guidance import models, gen, select

lm = models.Anthropic("claude-sonnet-4-5-20250929")

text = "这款产品太棒了！我喜欢它。"

lm += f"文本: {text}\n"
lm += "情感: " + select(["positive", "negative", "neutral"], name="sentiment")
lm += "\n置信度: " + gen("confidence", regex=r"[0-9]+", max_tokens=3) + "%"

print(f"情感: {lm['sentiment']}")
print(f"置信度: {lm['confidence']}%")
```

### 模式3：多步骤推理

```python
from guidance import models, gen, guidance

@guidance
def chain_of_thought(lm, question):
    """通过逐步推理生成答案。"""
    lm += f"问题: {question}\n\n"

    # 生成多个推理步骤
    for i in range(3):
        lm += f"步骤 {i+1}: " + gen(f"step_{i+1}", stop="\n", max_tokens=100) + "\n"

    # 最终答案
    lm += "\n因此，答案是: " + gen("answer", max_tokens=50)

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = chain_of_thought(lm, "200的15%是多少？")

print(lm["answer"])
```

### 模式4：ReAct代理

```python
from guidance import models, gen, select, guidance

@guidance(stateless=False)
def react_agent(lm, question):
    """具有工具使用能力的ReAct代理。"""
    tools = {
        "calculator": lambda expr: eval(expr),
        "search": lambda query: f"关于'{query}'的搜索结果",
    }

    lm += f"问题: {question}\n\n"

    for round in range(5):
        # 思考
        lm += f"思考: " + gen("thought", stop="\n") + "\n"

        # 行动选择
        lm += "行动: " + select(["calculator", "search", "answer"], name="action")

        if lm["action"] == "answer":
            lm += "\n最终答案: " + gen("answer", max_tokens=100)
            break

        # 行动输入
        lm += "\n行动输入: " + gen("action_input", stop="\n") + "\n"

        # 执行工具
        if lm["action"] in tools:
            result = tools[lm["action"]](lm["action_input"])
            lm += f"观察: {result}\n\n"

    return lm

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = react_agent(lm, "25 * 4 + 10 等于多少？")
print(lm["answer"])
```

### 模式5：数据提取

```python
from guidance import models, gen, guidance

@guidance
def extract_entities(lm, text):
    """从文本中提取结构化实体。"""
    lm += f"文本: {text}\n\n"

    # 提取人物
    lm += "人物: " + gen("person", stop="\n", max_tokens=30) + "\n"

    # 提取组织
    lm += "组织: " + gen("organization", stop="\n", max_tokens=30) + "\n"

    # 提取日期
    lm += "日期: " + gen("date", regex=r"\d{4}-\d{2}-\d{2}", max_tokens=10) + "\n"

    # 提取地点
    lm += "地点: " + gen("location", stop="\n", max_tokens=30) + "\n"

    return lm

text = "Tim Cook 于2024-09-15在库比蒂诺的Apple Park宣布。"

lm = models.Anthropic("claude-sonnet-4-5-20250929")
lm = extract_entities(lm, text)

print(f"人物: {lm['person']}")
print(f"组织: {lm['organization']}")
print(f"日期: {lm['date']}")
print(f"地点: {lm['location']}")
```

## 最佳实践

### 1. 使用正则表达式进行格式验证

```python
# ✅ 好：正则表达式确保有效格式
lm += "邮箱: " + gen("email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# ❌ 坏：自由生成可能产生无效邮箱
lm += "邮箱: " + gen("email", max_tokens=50)
```

### 2. 对固定类别使用select()

```python
# ✅ 好：保证有效类别
lm += "状态: " + select(["pending", "approved", "rejected"], name="status")

# ❌ 坏：可能生成拼写错误或无效值
lm += "状态: " + gen("status", max_tokens=20)
```

### 3. 利用令牌修复

```python
# 默认启用令牌修复
# 不需要特殊操作——只需自然拼接
lm += "首都是" + gen("capital")  # 自动修复
```

### 4. 使用停止序列

```python
# ✅ 好：单行输出在换行处停止
lm += "姓名: " + gen("name", stop="\n")

# ❌ 坏：可能生成多行
lm += "姓名: " + gen("name", max_tokens=50)
```

### 5. 创建可重用函数

```python
# ✅ 好：可重用模式
@guidance
def generate_person(lm):
    lm += "姓名: " + gen("name", stop="\n")
    lm += "\n年龄: " + gen("age", regex=r"[0-9]+")
    return lm

# 多次使用
lm = generate_person(lm)
lm += "\n\n"
lm = generate_person(lm)
```

### 6. 平衡约束

```python
# ✅ 好：合理的约束
lm += gen("name", regex=r"[A-Za-z ]+", max_tokens=30)

# ❌ 过于严格：可能失败或非常慢
lm += gen("name", regex=r"^(John|Jane)$", max_tokens=10)
```

## 与替代方案的比较

| 特性 | Guidance | Instructor | Outlines | LMQL |
|---------|----------|------------|----------|------|
| 正则表达式约束 | ✅ 是 | ❌ 否 | ✅ 是 | ✅ 是 |
| 语法支持 | ✅ CFG | ❌ 否 | ✅ CFG | ✅ CFG |
| Pydantic 验证 | ❌ 否 | ✅ 是 | ✅ 是 | ❌ 否 |
| 令牌修复 | ✅ 是 | ❌ 否 | ✅ 是 | ❌ 否 |
| 本地模型 | ✅ 是 | ⚠️ 有限 | ✅ 是 | ✅ 是 |
| API模型 | ✅ 是 | ✅ 是 | ⚠️ 有限 | ✅ 是 |
| Python风格语法 | ✅ 是 | ✅ 是 | ✅ 是 | ❌ SQL风格 |
| 学习曲线 | 低 | 低 | 中等 | 高 |

**何时选择Guidance：**
- 需要正则表达式/语法约束
- 想要令牌修复
- 构建带有控制流的复杂工作流程
- 使用本地模型（Transformers, llama.cpp）
- 偏好Python风格语法

**何时选择替代方案：**
- Instructor：需要带自动重试的Pydantic验证
- Outlines：需要JSON schema验证
- LMQL：偏好声明式查询语法

## 性能特征

**延迟降低：**
- 比传统提示方法快30-50%（对于约束输出）
- 令牌修复减少不必要的重新生成
- 语法约束阻止无效令牌生成

**内存使用：**
- 与无约束生成相比，开销极小
- 首次使用后语法编译缓存
- 推理时高效的令牌过滤

**令牌效率：**
- 防止无效输出浪费令牌
- 无需重试循环
- 直接通向有效输出的路径

## 资源

- **文档**: https://guidance.readthedocs.io
- **GitHub**: https://github.com/guidance-ai/guidance（18k+星标）
- **笔记本**: https://github.com/guidance-ai/guidance/tree/main/notebooks
- **Discord**: 社区支持

## 另请参阅

- `references/constraints.md` - 全面的正则表达式和语法模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产就绪示例