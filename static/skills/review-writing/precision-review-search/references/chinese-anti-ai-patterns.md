# Chinese Anti-AI Patterns for Scientific Reviews

Collated from a 2026-06-04 session where the user rejected "language too AI" in a
Chinese gold nanomaterial review. These patterns are specific to Chinese academic
writing — they supplement the general humanizer skill's 29 English patterns.

## Judgment Markers (Hard Remove)

These insert the author between the data and the reader. Remove them and let the
data stand on its own.

| Pattern | Fix |
|---------|-----|
| 这表明/这说明/这显示 | Delete. Start next clause directly. |
| 这意味着 | Delete. The implication should be obvious from the data. |
| 这反映了/这体现了 | Delete. Replace with the actual observation. |
| 由此可见/由此可知 | Delete. If it's visible it's visible. |

Before: "原始方案产率50-70%。这表明孪晶不是唯一决定因素。"
After:  "原始方案产率50-70%。孪晶不是唯一决定因素。"

## Redundant Qualifiers (Trim)

These add length without information. Delete them.

| Pattern | Fix |
|---------|-----|
| 关键性的/关键 | Keep one mention max per section. Usually deletable. |
| 根本性的 | → "结构性的" or delete. |
| 显著的 | Delete unless quantified. |
| 极其/极度/非常/相当 | Delete 90% of cases. |
| 重要的/核心的 | Delete. Importance emerges from content. |

## Meta-Commentary (Redirect)

Don't tell the reader what you're about to say. Just say it.

| Pattern | Fix |
|---------|-----|
| 值得注意的是/值得关注的是 | Delete the phrase, keep the fact. |
| 需要指出的是 | Delete. |
| 从这个角度来看/从这个意义上说 | Delete. |
| 我们可以看到/我们注意到 | Delete. Remove "我们". |
| 众所周知/每个实践者都学过 | Replace with the fact itself. |

Before: "每个实践者都学过 Turkevich 法：将氯金酸溶液加热至沸..."
After:  "Turkevich 法的实际操作很简单：将氯金酸溶液加热至沸..."

## Formulaic Transitions (Naturalize)

C-E-L-T Transition sentences that read like signposts.

| Original | Better |
|----------|--------|
| 这个缺口的解决方案不是来自机理洞察，而是一种新的配方。 | 这个缺口用一种新配方解决了。 |
| 产率问题在很大程度上通过银离子的精确浓度控制得到了解决。 | 产率问题通过银离子的精确浓度控制得到了解决。 |
| 两种方法在根本不同的生长模式下运作。 | (Natural opening — keep context-appropriate) |

## "仍然" Overuse

"仍然" is the Chinese equivalent of "still" in English — AI defaults to it.

| Before | After |
|--------|-------|
| 仍然是未知的 | 不知道 |
| 仍然是一个挑战 | 不好制备/需要解决的问题 |
| 仍然无法弥合 | 无法弥合 |
| 仍然是一个显著的技术挑战 | 是一个技术挑战 |

## Passive Voice in Chinese

Chinese AI writing overuses "通过X可实现的Y" and "X被Y所Z" constructions.

Before: "通过改进合成可实现的线宽缩小远大于基本极限"
After:  "改进合成能实现的线宽缩小远大于基本极限"

Before: "这些产物的身份随反应时间和温度而变化"
After:  "这些产物的身份随反应时间和温度变化"

## "这" as Vague Subject

Cut "这" when it refers vaguely to the previous sentence's whole idea.
Rewrite with the actual noun.

Before: "这表明孪晶的存在与否不是唯一的决定因素"
After:  "孪晶的存在与否不是唯一的决定因素"

## General Principle

After writing with C-E-L-T framework, audit every sentence for:
1. Is there a judgment word (表明/意味着/反映)? Delete it.
2. Is there a redundant qualifier (关键/根本/显著)? Delete it.
3. Does the sentence start with "这"? Rewrite with the real subject.
4. Is there a "仍然"? Replace with direct statement.
5. Does the sentence sound like it was assembled from a template? It was — rewrite it.
