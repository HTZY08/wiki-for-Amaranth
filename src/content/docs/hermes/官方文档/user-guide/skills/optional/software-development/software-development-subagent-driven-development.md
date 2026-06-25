# 子代理驱动开发（Subagent Driven Development）

通过 `delegate_task` 子代理执行计划（两阶段审查）。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/software-development/subagent-driven-development` 安装 |
| 路径 | `optional-skills/software-development/subagent-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `delegation`，`subagent`，`implementation`，`workflow`，`parallel` |
| 相关技能 | [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan)，[`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review)，[`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# 子代理驱动开发（Subagent-Driven Development）

## 概述

通过为每个任务分派全新的子代理，并辅以系统的两阶段审查，来执行实现计划。

**核心原则：** 每个任务使用全新子代理 + 两阶段审查（规范审查 + 质量审查）= 高质量、快速迭代。

## 何时使用

在以下情况下使用此技能：
- 你有一个实现计划（来自 `plan` 技能或用户需求）
- 任务基本相互独立
- 质量和规范符合性很重要
- 你希望在任务之间进行自动审查

**与手动执行的对比：**
- 每个任务拥有全新上下文（不会因累积状态而混乱）
- 自动审查过程能及早发现问题
- 对所有任务进行一致的质量检查
- 子代理在开始工作前可以提问

## 流程

### 1. 读取并解析计划

读取计划文件。提前提取所有任务的完整文本和上下文。创建待办列表：

```python
# 读取计划
read_file("docs/plans/feature-plan.md")

# 创建包含所有任务的待办列表
todo([
    {"id": "task-1", "content": "创建带 email 字段的用户模型", "status": "pending"},
    {"id": "task-2", "content": "添加密码哈希工具", "status": "pending"},
    {"id": "task-3", "content": "创建登录端点", "status": "pending"},
])
```

**关键点：** 只读取一次计划。提取所有内容。不要让子代理读取计划文件——而是在上下文中直接提供完整的任务文本。

### 2. 每个任务的工作流程

对于计划中的每个任务：

#### 第 1 步：分派实现者子代理

使用 `delegate_task` 并携带完整上下文：

```python
delegate_task(
    goal="实现任务 1：创建包含 email 和 password_hash 字段的用户模型",
    context="""
    来自计划的任务：
    - 创建文件：src/models/user.py
    - 添加 User 类，包含 email (str) 和 password_hash (str) 字段
    - 使用 bcrypt 进行密码哈希
    - 包含 __repr__ 方便调试

    遵循 TDD：
    1. 在 tests/models/test_user.py 中编写失败的测试
    2. 运行：pytest tests/models/test_user.py -v（验证失败）
    3. 编写最小实现
    4. 运行：pytest tests/models/test_user.py -v（验证通过）
    5. 运行：pytest tests/ -q（验证无回归）
    6. 提交：git add -A && git commit -m "feat: add User model with password hashing"

    项目上下文：
    - Python 3.11，Flask 应用位于 src/app.py
    - 现有模型位于 src/models/
    - 测试使用 pytest，从项目根目录运行
    - bcrypt 已在 requirements.txt 中
    """,
    toolsets=['terminal', 'file']
)
```

#### 第 2 步：分派规范合规性审查员

实现者完成后，对照原始规范进行验证：

```python
delegate_task(
    goal="检查实现是否与计划中的规范相符",
    context="""
    原始任务规范：
    - 创建 src/models/user.py，包含 User 类
    - 字段：email (str)，password_hash (str)
    - 使用 bcrypt 进行密码哈希
    - 包含 __repr__

    检查：
    - [ ] 规范中的所有需求都已实现？
    - [ ] 文件路径与规范一致？
    - [ ] 函数签名与规范一致？
    - [ ] 行为符合预期？
    - [ ] 没有添加多余内容（无范围蔓延）？

    输出：PASS 或需要修复的规范缺陷列表。
    """,
    toolsets=['file']
)
```

**如果发现规范问题：** 修复缺陷，然后重新运行规范审查。只有在符合规范后才继续。

#### 第 3 步：分派代码质量审查员

在规范合规性通过后：

```python
delegate_task(
    goal="审查任务 1 实现的代码质量",
    context="""
    需审查的文件：
    - src/models/user.py
    - tests/models/test_user.py

    检查：
    - [ ] 遵循项目约定和风格？
    - [ ] 适当的错误处理？
    - [ ] 变量/函数名称清晰？
    - [ ] 充分的测试覆盖？
    - [ ] 没有明显的 bug 或遗漏的边界情况？
    - [ ] 没有安全问题？

    输出格式：
    - 关键问题：[必须修复后才能继续]
    - 重要问题：[应该修复]
    - 次要问题：[可选]
    - 结论：APPROVED 或 REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**如果发现质量问题：** 修复问题，重新审查。仅在批准后继续。

#### 第 4 步：标记完成

```python
todo([{"id": "task-1", "content": "创建带 email 字段的用户模型", "status": "completed"}], merge=True)
```

### 3. 最终审查

在所有任务完成后，分派一个最终的集成审查员：

```python
delegate_task(
    goal="审查整个实现的一致性和集成问题",
    context="""
    计划中的所有任务已完成。审查完整实现：
    - 所有组件是否协同工作？
    - 任务之间是否存在不一致？
    - 所有测试是否通过？
    - 准备好合并了吗？
    """,
    toolsets=['terminal', 'file']
)
```

### 4. 验证并提交

```bash
# 运行完整测试套件
pytest tests/ -q

# 审查所有更改
git diff --stat

# 如果需要，最终提交
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## 任务粒度

**每个任务 = 2-5 分钟的专注工作。**

**太大：**
- "实现用户认证系统"

**合适的大小：**
- "创建包含 email 和 password 字段的用户模型"
- "添加密码哈希函数"
- "创建登录端点"
- "添加 JWT 令牌生成"
- "创建注册端点"

## 红旗——切勿执行

- 在没有计划的情况下开始实现
- 跳过审查（规范合规性或代码质量）
- 在未修复关键/重要问题的情况下继续
- 为操作相同文件的多个任务分派多个实现子代理
- 让子代理读取计划文件（改为在上下文中提供全文）
- 跳过场景设置上下文（子代理需要理解任务在整体中的位置）
- 忽略子代理的问题（在让他们继续之前回答）
- 在规范合规性上接受“差不多”
- 跳过审查循环（审查者发现问题 → 实现者修复 → 再次审查）
- 让实现者自我审查代替实际审查（两者都需要）
- **在规范合规性通过之前开始代码质量审查**（顺序错误）
- 在任一审查存在未解决问题时，进行下一个任务

## 问题处理

### 如果子代理提问

- 清晰完整地回答
- 必要时提供额外上下文
- 不要催促他们实施

### 如果审查者发现问题

- 让实现者子代理（或新的子代理）修复
- 审查者再次审查
- 重复直到批准
- 不要跳过重新审查

### 如果子代理任务失败

- 分派一个新的修复子代理，并附带关于出错原因的具体说明
- 不要在控制器会话中手动修复（会导致上下文污染）

## 效率说明

**为什么每个任务使用全新子代理：**
- 防止累积状态导致的上下文污染
- 每个子代理获得干净、专注的上下文
- 不会因先前任务的代码或推理而产生混淆

**为什么采用两阶段审查：**
- 规范审查及早发现构建不足或过度构建
- 质量审查确保实现质量良好
- 在问题跨任务复合之前捕获它们

**成本权衡：**
- 更多的子代理调用（每个任务有一个实现者 + 两个审查员）
- 但能及早发现问题（比后期调试复合问题更便宜）

## 与其他技能的集成

### 与 plan 技能

此技能执行由 `plan` 技能创建的计划：
1. 用户需求 → 计划 → 实现计划
2. 实现计划 → subagent-driven-development → 可用代码

### 与 test-driven-development 技能

实现者子代理应遵循 TDD：
1. 先编写失败的测试
2. 实现最小代码
3. 验证测试通过
4. 提交

在每个实现者上下文中包含 TDD 指令。

### 与 requesting-code-review 技能

两阶段审查过程本身就是代码审查。对于最终集成审查，使用 requesting-code-review 技能的审查维度。

### 与 systematic-debugging 技能

如果子代理在实现过程中遇到 bug：
1. 遵循 systematic-debugging 流程
2. 在修复前找到根本原因
3. 编写回归测试
4. 继续实现

## 示例工作流

```
[读取计划：docs/plans/auth-feature.md]
[创建包含 5 个任务的待办列表]

--- 任务 1：创建用户模型 ---
[分派实现者子代理]
  实现者："email 应该是唯一的吗？"
  你："是的，email 必须唯一"
  实现者：已实现，3/3 测试通过，已提交。

[分派规范审查员]
  规范审查员：✅ PASS —— 所有需求已满足

[分派质量审查员]
  质量审查员：✅ APPROVED —— 代码整洁，测试良好

[标记任务 1 完成]

--- 任务 2：密码哈希 ---
[分派实现者子代理]
  实现者：无问题，已实现，5/5 测试通过。

[分派规范审查员]
  规范审查员：❌ 缺失：密码强度验证（规范要求"最少 8 个字符"）

[实现者修复]
  实现者：已添加验证，7/7 测试通过。

[再次分派规范审查员]
  规范审查员：✅ PASS

[分派质量审查员]
  质量审查员：重要：魔法数字 8，应提取为常量
  实现者：提取了 MIN_PASSWORD_LENGTH 常量
  质量审查员：✅ APPROVED

[标记任务 2 完成]

...（对所有任务继续）

[所有任务完成后：分派最终集成审查员]
[运行完整测试套件：全部通过]
[完成！]
```

## 记住

```
每个任务使用全新子代理
每次都进行两阶段审查
优先规范合规性
其次代码质量
永不跳过审查
及早发现问题
```

**质量不是偶然。它是系统化流程的结果。**

## 延伸阅读（相关时加载）

当编排涉及大量上下文使用、长时间的审查循环或复杂的验证检查点时，加载这些参考资料以获取具体指导：

- **`references/context-budget-discipline.md`** — 四级上下文退化模型（PEAK / GOOD / DEGRADING / POOR），随上下文窗口大小伸缩的读取深度规则，以及静默退化的早期预警信号。当运行将明显消耗大量上下文时（多阶段计划、多个子代理、大型工件）加载。
- **`references/gates-taxonomy.md`** — 四种规范关卡类型（Pre-flight、Revision、Escalation、Abort），包括行为、恢复和示例。当设计或审查任何具有验证检查点的工作流时加载——明确使用该词汇，使每个关卡都有定义的输入、失败行为和恢复规则。

两个参考资料改编自 gsd-build/get-shit-done（MIT © 2025 Lex Christopherson）。