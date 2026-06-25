--- frontmatter ---
---
title: "测试驱动开发 — TDD：强制 RED-GREEN-REFACTOR，测试先于代码"
sidebar_label: "测试驱动开发"
description: "TDD：强制 RED-GREEN-REFACTOR，测试先于代码"
---

--- body ---
{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# 测试驱动开发（Test Driven Development）

TDD：强制 RED-GREEN-REFACTOR，测试先于代码。

## 技能元数据（Skill metadata）

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/software-development/test-driven-development` |
| 版本 | `1.1.0` |
| 作者 | Hermes Agent（改编自 obra/superpowers） |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `testing`, `tdd`, `development`, `quality`, `red-green-refactor` |
| 相关技能 | [`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`plan`](/docs/user-guide/skills/bundled/software-development/software-development-plan), [`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是技能激活时代理所看到的指令。
:::

# 测试驱动开发（Test-Driven Development, TDD）

## 概述

先编写测试。看着它失败。编写最少的代码使其通过。

**核心原则：** 如果你没有看着测试失败，你就不知道它是否测试了正确的东西。

**违反规则的文字就是违反规则的精神。**

## 何时使用

**始终：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外情况（先询问用户）：**
- 一次性原型
- 生成的代码
- 配置文件

想着“就这一次跳过 TDD”？打住。那是合理化借口。

## 铁律（The Iron Law）

```
没有失败的测试，就不能有生产代码。
```

先写了代码？删掉它。重新开始。

**没有例外：**
- 不要保留作为“参考”
- 不要在编写测试时“修改”它
- 不要看它
- 删除意味着删除

完全从测试开始实现。句号。

## 红-绿-重构循环（Red-Green-Refactor Cycle）

### 红（RED）——编写失败的测试

编写一个最简测试，展示应该发生什么。

**好的测试：**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'

    result = retry_operation(operation)

    assert result == 'success'
    assert attempts == 3
```
清晰的名称，测试真实行为，只测一件事。

**糟糕的测试：**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # 重试次数呢？时机呢？
```
模糊的名称，测试的是 mock 而非真实代码。

**要求：**
- 每个测试只测一种行为
- 清晰描述性的名称（名称中带有“和”？拆开）
- 使用真实代码，而非 mock（除非实在不可避免）
- 名称描述行为，而非实现

### 验证红（Verify RED）——看着它失败

**必须执行。绝不可跳过。**

```bash
# 使用终端工具运行特定测试
pytest tests/test_feature.py::test_specific_behavior -v
```

确认：
- 测试失败（不是因拼写错误导致的报错）
- 失败信息符合预期
- 失败是因为功能缺失

**测试立即通过了？** 你在测试已有的行为。修正测试。

**测试报错？** 修正报错，重新运行直到正确失败。

### 绿（GREEN）——最简代码

编写能让测试通过的最简单代码。不要多写。

**好的：**
```python
def add(a, b):
    return a + b  # 什么都不多写
```

**糟糕的：**
```python
def add(a, b):
    result = a + b
    logging.info(f"Adding {a} + {b} = {result}")  # 多余的！
    return result
```

不要添加功能、重构其他代码或“改进”超出测试范围。

**在绿阶段作弊是可以的：**
- 硬编码返回值
- 复制粘贴
- 重复代码
- 跳过边界情况

我们会在重构阶段修正。

### 验证绿（Verify GREEN）——看着它通过

**必须执行。**

```bash
# 运行特定测试
pytest tests/test_feature.py::test_specific_behavior -v

# 然后运行所有测试检查回归
pytest tests/ -q
```

确认：
- 测试通过
- 其他测试仍然通过
- 输出干净（无错误、无警告）

**测试失败？** 修正代码，而非测试。

**其他测试失败？** 立即修复回归。

### 重构（REFACTOR）——清理

仅在变绿后：
- 消除重复
- 改善命名
- 提取辅助函数
- 简化表达式

保持测试在整个重构过程中为绿。不要添加行为。

**如果重构时测试失败：** 立即撤销。采取更小的步骤。

### 重复

下一个失败测试对应下一个行为。一次一个循环。

## 为什么顺序很重要

**“我之后会写测试来验证它是否工作”**

测试在代码之后编写会立即通过。立即通过证明不了什么：
- 可能测试了错误的东西
- 可能测试了实现，而非行为
- 可能遗漏了你忘记的边界情况
- 你从未看到它捕获过 Bug

测试优先迫使你看到测试失败，证明它确实在测试某些东西。

**“我已经手动测试了所有边界情况”**

手动测试是临时的。你以为你测试了所有东西，但实际上：
- 没有记录你测试了什么
- 代码变更时无法重新运行
- 压力下容易忘记测试用例
- “我试过是工作的” ≠ 全面

自动化测试是系统的。它们每次都以相同方式运行。

**“删除 X 小时的工作是浪费”**

沉没成本谬误。时间已经过去了。你现在可以选择：
- 删除并用 TDD 重写（高信心）
- 保留并在之后添加测试（低信心，很可能有 Bug）

“浪费”的是保留你不信任的代码。

**“TDD 是教条式的，务实意味着调整”**

TDD 本身就是务实的：
- 在提交前发现 Bug（比之后调试更快）
- 防止回归（测试立即捕获破坏）
- 记录行为（测试展示如何使用代码）
- 支持重构（自由修改，测试捕获破坏）

“务实”的捷径 = 在生产中调试 = 更慢。

**“事后测试也能达到相同目标——这是精神而非仪式”**

不。事后测试回答“这段代码做了什么？”测试优先回答“这段代码应该做什么？”

事后测试受你的实现影响。你测试的是你构建的东西，而并非需要的东西。测试优先强制你在实现之前发现边界情况。

## 常见合理化借口

| 借口 | 现实 |
|--------|---------|
| “太简单了，不用测试” | 简单的代码也会出问题。测试只需 30 秒。 |
| “我之后会测试” | 测试立即通过证明不了什么。 |
| “事后测试也能达到相同目标” | 事后测试 = “这段代码做了什么？” 测试优先 = “这段代码应该做什么？” |
| “已经手动测试过了” | 临时 ≠ 系统。没有记录，无法重新运行。 |
| “删除 X 小时是浪费” | 沉没成本谬误。保留未经验证的代码是技术债务。 |
| “保留作为参考，先写测试” | 你会修改它。那就成了事后测试。删除意味着删除。 |
| “需要先探索一下” | 可以。扔掉探索代码，用 TDD 重新开始。 |
| “测试难写 = 设计不清晰” | 倾听测试。难以测试 = 难以使用。 |
| “TDD 会拖慢我” | TDD 比调试更快。务实 = 测试优先。 |
| “手动测试更快” | 手动测试无法证明边界情况。每次变更你都得重新测试。 |
| “已有代码没有测试” | 你正在改进它。为你碰到的代码添加测试。 |

## 红旗（Red Flags）——停下并重新开始

如果你发现自己做了下面任何一件事，删除代码并用 TDD 重新开始：

- 先写代码，后写测试
- 实现之后才测试
- 测试在首次运行时就通过了
- 无法解释测试为何失败
- “稍后”添加测试
- 找借口“就这一次”
- “我已经手动测试过了”
- “事后测试也能达到相同目的”
- “保留作为参考”或“修改现有代码”
- “已经花了 X 小时，删除是浪费”
- “TDD 是教条式的，我是务实的”
- “这次不同因为……”

**所有这些都意味着：删除代码。用 TDD 重新开始。**

## 验证清单（Verification Checklist）

在标记工作完成前：

- [ ] 每个新的函数/方法都有对应的测试
- [ ] 在实现前看着每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，而非笔误）
- [ ] 编写了最少的代码来通过每个测试
- [ ] 所有测试通过
- [ ] 输出干净（无错误、无警告）
- [ ] 测试使用真实代码（mock 仅当不可避免时）
- [ ] 覆盖了边界情况和错误

不能全部勾选？你跳过了 TDD。重新开始。

## 卡住时（When Stuck）

| 问题 | 解决方案 |
|---------|----------|
| 不知道如何测试 | 编写期望的 API。先写断言。询问用户。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须 mock 一切 | 代码耦合太紧。使用依赖注入。 |
| 测试设置太庞大 | 提取辅助函数。仍然复杂？简化设计。 |

## Hermes 代理集成（Hermes Agent Integration）

### 运行测试

使用 `terminal` 工具在每个步骤运行测试：

```python
# 红 —— 验证失败
terminal("pytest tests/test_feature.py::test_name -v")

# 绿 —— 验证通过
terminal("pytest tests/test_feature.py::test_name -v")

# 全量套件 —— 验证无回归
terminal("pytest tests/ -q")
```

### 与 delegate_task 配合

在分派子代理进行实现时，在目标中强制 TDD：

```python
delegate_task(
    goal="使用严格的 TDD 实现 [功能]",
    context="""
    遵循测试驱动开发技能：
    1. 首先编写失败的测试
    2. 运行测试以确认它失败
    3. 编写最少的代码使其通过
    4. 运行测试以确认它通过
    5. 如果需要，进行重构
    6. 提交

    项目测试命令：pytest tests/ -q
    项目结构：[描述相关文件]
    """,
    toolsets=['terminal', 'file']
)
```

### 与 systematic-debugging 配合

发现 Bug？编写一个重现它的失败测试。遵循 TDD 循环。测试既证明修复也防止回归。

永远不要在没有测试的情况下修复 Bug。

## 测试反模式（Testing Anti-Patterns）

- **测试 mock 行为而非真实行为** —— mock 应验证交互，而非替代被测系统
- **测试实现细节** —— 测试行为/结果，而非内部方法调用
- **只测快乐路径** —— 始终测试边界情况、错误和临界值
- **脆弱测试** —— 测试应验证行为，而非结构；重构不应破坏它们

## 最终规则（Final Rule）

```
生产代码 → 测试存在且先失败过
否则 → 不是 TDD
```

未经用户明确许可，没有例外。