---
description: Outlines：结构化 JSON/regex/Pydantic LLM 生成
sidebar_label: Outlines
title: Outlines — Outlines：结构化 JSON/regex/Pydantic LLM 生成
---

{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Outlines

Outlines：结构化 JSON/regex/Pydantic LLM 生成。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/outlines` 安装 |
| 路径 | `optional-skills/mlops/inference/outlines` |
| 版本 | `1.0.0` |
| 作者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `outlines`, `transformers`, `vllm`, `pydantic` |
| 支持平台 | linux, macos, windows |
| 标签 | `Prompt Engineering`, `Outlines`, `Structured Generation`, `JSON Schema`, `Pydantic`, `Local Models`, `Grammar-Based Generation`, `vLLM`, `Transformers`, `Type Safety` |

## 参考：完整的 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# Outlines：结构化文本生成

## 何时使用此技能

在以下情况下使用 Outlines：
- **保证生成有效的 JSON/XML/代码** 结构
- **使用 Pydantic 模型** 实现类型安全的输出
- **支持本地模型**（Transformers, llama.cpp, vLLM）
- **最大化推理速度**，实现零开销的结构化生成
- **自动根据 JSON Schema** 生成
- **在语法层面控制 Token 采样**

**GitHub Stars**：8,000+ | **来自**：dottxt.ai（前身为 .txt）

## 安装

```bash
# 基础安装
pip install outlines

# 搭配特定后端
pip install outlines transformers  # Hugging Face 模型
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # vLLM 用于高吞吐量
```

## 快速入门

### 基础示例：分类

```python
import outlines
from typing import Literal

# 加载模型
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 使用类型约束进行生成
prompt = "情感分析：'这个产品太棒了！'："
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive"（保证是其中之一）
```

### 使用 Pydantic 模型

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 生成结构化输出
prompt = "提取用户：John Doe，30 岁，john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```

## 核心概念

### 1. 约束 Token 采样

Outlines 使用有限状态机（Finite State Machines, FSM）在 logit 层面约束生成过程。

**工作原理：**
1. 将模式（JSON/Pydantic/regex）转换为上下文无关文法（Context-Free Grammar, CFG）
2. 将 CFG 转换为有限状态机（FSM）
3. 在生成过程中每一步过滤无效 token
4. 当只有一个有效 token 时快速前向通过

**优点：**
- **零开销**：过滤在 token 级别进行
- **速度提升**：通过确定性路径快速前向
- **保证有效性**：不可能生成无效输出

```python
import outlines

# Pydantic 模型 -> JSON schema -> CFG -> FSM
class Person(BaseModel):
    name: str
    age: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 底层过程：
# 1. Person -> JSON schema
# 2. JSON schema -> CFG
# 3. CFG -> FSM
# 4. FSM 在生成过程中过滤 token

generator = outlines.generate.json(model, Person)
result = generator("生成人物：Alice, 25")
```

### 2. 结构化生成器

Outlines 为不同的输出类型提供了专门的生成器。

#### 选择生成器

```python
# 多选选择
generator = outlines.generate.choice(
    model,
    ["positive", "negative", "neutral"]
)

sentiment = generator("评论：这个太棒了！")
# 结果：三个选项之一
```

#### JSON 生成器

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

# 生成符合模式的 JSON
generator = outlines.generate.json(model, Product)
product = generator("提取：iPhone 15，$999，有货")

# 保证有效的 Product 实例
print(type(product))  # <class '__main__.Product'>
```

#### 正则表达式生成器

```python
# 生成匹配正则表达式的文本
generator = outlines.generate.regex(
    model,
    r"[0-9]{3}-[0-9]{3}-[0-9]{4}"  # 电话号码模式
)

phone = generator("生成电话号码：")
# 结果："555-123-4567"（保证匹配模式）
```

#### 整数/浮点数生成器

```python
# 生成特定数值类型
int_generator = outlines.generate.integer(model)
age = int_generator("人的年龄：")  # 保证为整数

float_generator = outlines.generate.float(model)
price = float_generator("产品价格：")  # 保证为浮点数
```

### 3. 模型后端

Outlines 支持多个本地和基于 API 的后端。

#### Transformers（Hugging Face）

```python
import outlines

# 从 Hugging Face 加载
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"  # 或 "cpu"
)

# 与任何生成器一起使用
generator = outlines.generate.json(model, YourModel)
```

#### llama.cpp

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=35
)

generator = outlines.generate.json(model, YourModel)
```

#### vLLM（高吞吐量）

```python
# 用于生产部署
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2  # 多 GPU
)

generator = outlines.generate.json(model, YourModel)
```

#### OpenAI（有限支持）

```python
# 基本的 OpenAI 支持
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key"
)

# 注意：使用 API 模型时某些功能受限
generator = outlines.generate.json(model, YourModel)
```

### 4. Pydantic 集成

Outlines 拥有对 Pydantic 的一流支持，自动进行模式转换。

#### 基础模型

```python
from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="文章标题")
    author: str = Field(description="作者姓名")
    word_count: int = Field(description="字数", gt=0)
    tags: list[str] = Field(description="标签列表")

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, Article)

article = generator("生成一篇关于 AI 的文章")
print(article.title)
print(article.word_count)  # 保证 > 0
```

#### 嵌套模型

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address  # 嵌套模型

generator = outlines.generate.json(model, Person)
person = generator("生成一个在纽约的人")

print(person.address.city)  # "New York"
```

#### 枚举和字面量

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Application(BaseModel):
    applicant: str
    status: Status  # 必须是枚举值之一
    priority: Literal["low", "medium", "high"]  # 必须是字面量之一

generator = outlines.generate.json(model, Application)
app = generator("生成申请")

print(app.status)  # Status.PENDING（或 APPROVED/REJECTED）
```

## 常见模式

### 模式 1：数据提取

```python
from pydantic import BaseModel
import outlines

class CompanyInfo(BaseModel):
    name: str
    founded_year: int
    industry: str
    employees: int

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, CompanyInfo)

text = """
Apple Inc. 成立于 1976 年，属于科技行业。
公司全球雇员约 164,000 人。
"""

prompt = f"提取公司信息：\n{text}\n\n公司："
company = generator(prompt)

print(f"名称：{company.name}")
print(f"成立年份：{company.founded_year}")
print(f"行业：{company.industry}")
print(f"员工数：{company.employees}")
```

### 模式 2：分类

```python
from typing import Literal
import outlines

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# 二元分类
generator = outlines.generate.choice(model, ["spam", "not_spam"])
result = generator("邮件：立即购买！五折优惠！")

# 多类分类
categories = ["technology", "business", "sports", "entertainment"]
category_gen = outlines.generate.choice(model, categories)
category = category_gen("文章：苹果发布新款 iPhone...")

# 带置信度
class Classification(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float

classifier = outlines.generate.json(model, Classification)
result = classifier("评论：这个产品还行，没什么特别的")
```

### 模式 3：结构化表单

```python
class UserProfile(BaseModel):
    full_name: str
    age: int
    email: str
    phone: str
    country: str
    interests: list[str]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, UserProfile)

prompt = """
从以下内容提取用户资料：
姓名：Alice Johnson
年龄：28
邮箱：alice@example.com
电话：555-0123
国家：美国
兴趣爱好：徒步旅行、摄影、烹饪
"""

profile = generator(prompt)
print(profile.full_name)
print(profile.interests)  # ["徒步旅行", "摄影", "烹饪"]
```

### 模式 4：多实体提取

```python
class Entity(BaseModel):
    name: str
    type: Literal["PERSON", "ORGANIZATION", "LOCATION"]

class DocumentEntities(BaseModel):
    entities: list[Entity]

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, DocumentEntities)

text = "Tim Cook 在雷德蒙德的微软总部会见了 Satya Nadella。"
prompt = f"从以下文本中提取实体：{text}"

result = generator(prompt)
for entity in result.entities:
    print(f"{entity.name} ({entity.type})")
```

### 模式 5：代码生成

```python
class PythonFunction(BaseModel):
    function_name: str
    parameters: list[str]
    docstring: str
    body: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, PythonFunction)

prompt = "生成一个计算阶乘的 Python 函数"
func = generator(prompt)

print(f"def {func.function_name}({', '.join(func.parameters)}):")
print(f'    """{func.docstring}"""')
print(f"    {func.body}")
```

### 模式 6：批量处理

```python
def batch_extract(texts: list[str], schema: type[BaseModel]):
    """从多个文本中提取结构化数据。"""
    model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
    generator = outlines.generate.json(model, schema)

    results = []
    for text in texts:
        result = generator(f"从以下内容提取：{text}")
        results.append(result)

    return results

class Person(BaseModel):
    name: str
    age: int

texts = [
    "John 30 岁",
    "Alice 25 岁",
    "Bob 40 岁"
]

people = batch_extract(texts, Person)
for person in people:
    print(f"{person.name}: {person.age}")
```

## 后端配置

### Transformers

```python
import outlines

# 基础用法
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# GPU 配置
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# 常用模型
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
```

### llama.cpp

```python
# 加载 GGUF 模型
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,         # 上下文窗口
    n_gpu_layers=35,    # GPU 层数
    n_threads=8         # CPU 线程数
)

# 全 GPU 卸载
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_gpu_layers=-1  # 所有层都在 GPU 上
)
```

### vLLM（生产环境）

```python
# 单 GPU
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

# 多 GPU
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4  # 4 张 GPU
)

# 量化
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="awq"  # 或 "gptq"
)
```

## 最佳实践

### 1. 使用特定类型

```python
# ✅ 好：特定类型
class Product(BaseModel):
    name: str
    price: float  # 非字符串
    quantity: int  # 非字符串
    in_stock: bool  # 非字符串

# ❌ 坏：全部用字符串
class Product(BaseModel):
    name: str
    price: str  # 应为 float
    quantity: str  # 应为 int
```

### 2. 添加约束

```python
from pydantic import Field

# ✅ 好：带约束
class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# ❌ 坏：无约束
class User(BaseModel):
    name: str
    age: int
    email: str
```

### 3. 使用枚举表示类别

```python
# ✅ 好：用枚举表示固定集合
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority

# ❌ 坏：自由格式字符串
class Task(BaseModel):
    title: str
    priority: str  # 可以是任何值
```

### 4. 在提示中提供上下文

```python
# ✅ 好：清晰的上下文
prompt = """
从以下文本中提取产品信息。
文本：iPhone 15 Pro 售价 $999，目前有库存。
产品：
"""

# ❌ 坏：上下文太少
prompt = "iPhone 15 Pro 售价 $999，目前有库存。"
```

### 5. 处理可选字段

```python
from typing import Optional

# ✅ 好：用可选字段处理不完整数据
class Article(BaseModel):
    title: str  # 必填
    author: Optional[str] = None  # 可选
    date: Optional[str] = None  # 可选
    tags: list[str] = []  # 默认为空列表

# 即使缺少作者/日期也能成功
```

## 与替代方案的对比

| 特性 | Outlines | Instructor | Guidance | LMQL |
|------|----------|------------|----------|------|
| Pydantic 支持 | ✅ 原生 | ✅ 原生 | ❌ 不支持 | ❌ 不支持 |
| JSON Schema | ✅ 支持 | ✅ 支持 | ⚠️ 有限 | ✅ 支持 |
| 正则约束 | ✅ 支持 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| 本地模型 | ✅ 完全 | ⚠️ 有限 | ✅ 完全 | ✅ 完全 |
| API 模型 | ⚠️ 有限 | ✅ 完全 | ✅ 完全 | ✅ 完全 |
| 零开销 | ✅ 是 | ❌ 否 | ⚠️ 部分 | ✅ 是 |
| 自动重试 | ❌ 否 | ✅ 是 | ❌ 否 | ❌ 否 |
| 学习曲线 | 低 | 低 | 低 | 高 |

**何时选择 Outlines：**
- 使用本地模型（Transformers, llama.cpp, vLLM）
- 需要最大化推理速度
- 想要 Pydantic 模型支持
- 需要零开销结构化生成
- 控制 Token 采样过程

**何时选择替代方案：**
- Instructor：需要 API 模型且自动重试
- Guidance：需要 Token 修复和复杂工作流
- LMQL：偏好声明式查询语法

## 性能特征

**速度：**
- **零开销**：结构化生成与无约束一样快
- **快速前向优化**：跳过确定性 Token
- **比后生成验证方法快 1.2-2 倍**

**内存：**
- FSM 每个模式只编译一次（缓存）
- 运行时开销最小
- 与 vLLM 结合实现高吞吐量

**准确性：**
- **100% 有效输出**（由 FSM 保证）
- 无需重试循环
- 确定性 Token 过滤

## 资源

- **文档**：https://outlines-dev.github.io/outlines
- **GitHub**：https://github.com/outlines-dev/outlines（8k+ stars）
- **Discord**：https://discord.gg/R9DSu34mGd
- **博客**：https://blog.dottxt.co

## 另见

- `references/json_generation.md` - 全面的 JSON 和 Pydantic 模式
- `references/backends.md` - 后端特定配置
- `references/examples.md` - 生产级示例