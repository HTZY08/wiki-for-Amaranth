---
title: 持久记忆系统
description: Hindsight 记忆、跨会话上下文与 Session 搜索
---

Hermes Agent 拥有多层记忆架构，在对话中表现为"我记得你说过"的能力。

## 记忆层级

```
┌─────────────────────────────┐
│      Memory（持久事实）      │ ← 手动写入，跨会话保持
├─────────────────────────────┤
│      Session DB（会话历史）  │ ← 自动记录，FTS5 检索
├─────────────────────────────┤
│   Hindsight（长期反思记忆）  │ ← 自动构建的行为模式总结
├─────────────────────────────┤
│       当前上下文窗口         │ ← 本次会话
└─────────────────────────────┘
```

## Memory（持久事实）

手动保存的稳定信息，注入每次对话：

```python
# 保存
memory(action='add', target='memory', content='用户使用 uv 而非 pip')
# 替换
memory(action='replace', target='memory', old_text='喜欢简洁回答', content='偏好详细回答')
```

适合存：用户习惯、环境配置、项目约定、常犯的错误。
不适合存：任务进度、会话结果（这些放 Session DB）。

## Session DB（会话历史搜索）

`session_search` 工具可以跨会话检索：

```bash
# 搜索历史
session_search(query="docker GPU 配置", limit=3)

# 浏览最近会话
session_search()

# 滚动查看某个会话详情
session_search(session_id="xxx", around_message_id=123, window=10)
```

基于 SQLite FTS5 全文检索，支持布尔语法和短语匹配。

## Hindsight 记忆系统

Hindsight Lite 是自建的后台记忆服务，定期从对话历史中提取行为模式和偏好，存入 SQLite + 向量数据库，Agent 可以在后续对话中查询并调整行为。

## 记忆污染控制原则

- 不把一次性任务状态写入持久记忆
- 只有确认的偏好/习惯/事实才进 Memory
- Session DB 用于回溯，Memory 用于复用
- 发现记忆过时立即用 `patch` 更新
