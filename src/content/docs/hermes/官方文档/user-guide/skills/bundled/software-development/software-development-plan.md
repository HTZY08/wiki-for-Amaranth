--- frontmatter ---


--- body ---
# 编写好计划

本技能剩余部分是关于编写 *良好* 实现计划的技巧 —— 即上述 markdown 文件中的内容。

## 概述

编写全面的实现计划，假设实现者（implementer）对代码库零上下文且品味可疑。记录他们需要的一切：要触及哪些文件、完整代码、测试命令、要查阅的文档、如何验证。给他们可一口吃掉的任务。DRY。YAGNI。TDD。频繁提交。

假设实现者是熟练的开发者，但对工具集或问题域几乎一无所知。假设他们不太懂好的测试设计。

**核心原则：** 好的计划让实现变得显而易见。如果有人需要猜测，说明计划不完整。

## 什么时候需要完整实现计划

**务必在以下情况前使用：**
- 实现多步骤功能
- 分解复杂需求
- 通过子代理驱动开发（subagent-driven-development）将任务委派给子代理（subagent）

**不要跳过的情况：**
- 功能看似简单（假设导致错误）
- 你打算自己实现（未来的你需要指导）
- 独自工作（文档很重要）

## 一口吃掉的任务粒度

**每个任务 = 2-5 分钟的专注工作。**

每一步就是一个动作：
- "编写失败的测试" —— 一步
- "运行它以确认失败" —— 一步
- "实现最少代码使测试通过" —— 一步
- "运行测试并确认通过" —— 一步
- "提交" —— 一步

**太大：**
```markdown
### 任务 1: 构建认证系统
[跨越5个文件的50行代码]
```

**合适大小：**
```markdown
### 任务 1: 创建带 email 字段的 User 模型
[10行，1个文件]

### 任务 2: 给 User 添加密码哈希字段
[8行，1个文件]

### 任务 3: 创建密码哈希工具
[15行，1个文件]
```

## 计划文档结构

### 头部（必需）

每个计划必须以以下内容开头：

```markdown
# [功能名称] 实现计划

> **致 Hermes：** 使用子代理驱动开发技能逐任务实现此计划。

**目标：** [一句话描述构建什么]

**架构：** [2-3句话说明方法]

**技术栈：** [关键技术/库]

---

--- body ---
```

### 任务结构

每个任务遵循以下格式：

````markdown
### 任务 N: [描述性名称]

**目标：** 此任务完成什么（一句话）

**文件：**
- 创建: `exact/path/to/new_file.py`
- 修改: `exact/path/to/existing.py:45-67`（如果已知行号）
- 测试: `tests/path/to/test_file.py`

**步骤 1: 编写失败的测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**步骤 2: 运行测试以确认失败**

运行: `pytest tests/path/test.py::test_specific_behavior -v`
预期: FAIL — "function not defined"

**步骤 3: 编写最少实现**

```python
def function(input):
    return expected
```

**步骤 4: 运行测试以确认通过**

运行: `pytest tests/path/test.py::test_specific_behavior -v`
预期: PASS

**步骤 5: 提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 编写过程

### 步骤 1: 理解需求

阅读并理解：
- 功能需求
- 设计文档或用户描述
- 验收标准
- 约束条件

### 步骤 2: 探索代码库

使用 Hermes 工具了解项目：

```python
# 理解项目结构
search_files("*.py", target="files", path="src/")

# 查看相似功能
search_files("similar_pattern", path="src/", file_glob="*.py")

# 检查现有测试
search_files("*.py", target="files", path="tests/")

# 读取关键文件
read_file("src/app.py")
```

### 步骤 3: 设计方法

决定：
- 架构模式
- 文件组织
- 需要的依赖
- 测试策略

### 步骤 4: 编写任务

按顺序创建任务：
1. 设置/基础设施
2. 核心功能（每个采用TDD）
3. 边界情况
4. 集成
5. 清理/文档

### 步骤 5: 添加完整细节

每个任务包括：
- **确切文件路径**（不是"配置文件"而是 `src/config/settings.py`）
- **完整代码示例**（不是"添加验证"而是实际代码）
- **确切命令**以及预期输出
- **验证步骤**证明任务有效

### 步骤 6: 审查计划

检查：
- [ ] 任务顺序合理、逻辑清晰
- [ ] 每个任务都是一口吃掉的大小（2-5分钟）
- [ ] 文件路径确切
- [ ] 代码示例完整（可复制粘贴）
- [ ] 命令确切且有预期输出
- [ ] 没有缺失上下文
- [ ] 应用了 DRY、YAGNI、TDD 原则

## 原则

### DRY（不要重复自己）（Don't Repeat Yourself）

**坏：** 在3个地方复制粘贴验证代码
**好：** 提取验证函数，到处使用

### YAGNI（你不需要这个）（You Aren't Gonna Need It）

**坏：** 为未来需求添加"灵活性"
**好：** 只实现当前需要的

```python
# 坏 —— YAGNI 违规
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # 还不需需要！
        self.metadata = {}     # 还不需需要！

# 好 —— YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD（测试驱动开发）（Test-Driven Development）

每个生成代码的任务都应该包含完整的 TDD 周期：
1. 编写失败的测试
2. 运行以确认失败
3. 编写最少代码
4. 运行以确认通过

详见 `test-driven-development` 技能。

### 频繁提交

每个任务后提交：
```bash
git add [文件]
git commit -m "类型: 描述"
```

## 常见错误

### 模糊的任务

**坏：** "添加认证"
**好：** "创建带 email 和 password_hash 字段的 User 模型"

### 不完整的代码

**坏：** "步骤 1: 添加验证函数"
**好：** "步骤 1: 添加验证函数" 后跟完整的函数代码

### 缺少验证

**坏：** "步骤 3: 测试它工作"
**好：** "步骤 3: 运行 `pytest tests/test_auth.py -v`，预期：3 个通过"

### 缺少文件路径

**坏：** "创建模型文件"
**好：** "创建: `src/models/user.py`"

## 执行交接

保存计划后，提供执行方式：

**"计划完成并已保存。准备使用子代理驱动开发执行 —— 我将为每个任务派遣一个全新的子代理，并进行两阶段审查（规范合规性审查然后代码质量审查）。是否可以继续？"**

执行时，使用 `subagent-driven-development` 技能：
- 每个任务使用新的 `delegate_task`，附带完整上下文
- 每个任务后进行规范合规性审查
- 规范通过后进行代码质量审查
- 仅当两个审查都批准时才继续

## 记住

```
一口吃掉的任务（每个2-5分钟）
确切文件路径
完整代码（可复制粘贴）
确切命令及预期输出
验证步骤
DRY、YAGNI、TDD
频繁提交
```

**好的计划让实现变得显而易见。**