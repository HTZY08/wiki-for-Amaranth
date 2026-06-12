# 金纳米综述配图 prompt 示例

本文件是 paper-figure-mapper skill 在金纳米综述上的一次完整应用示例。
输入：`/opt/data/reviews/gold-nanomaterials-review/sections/*.md`（10节，~80k字）
输出：以下 prompt 文件。

## 出图流程

prompt 写好后，用 mcp_meigen_generate_image 或 Codex CLI image2 出图。
模型推荐：GPT Image 2.0 (gpt-image-2) / Nanobanana / Seedream
风格：金琥珀色系（#C5851A）扁平矢量科学风

## 测试图：F01 合成方法时间线

prompt 文件：`/opt/data/reviews/gold-nanomaterials-review/prompts/01-timeline-synthesis-methods.md`
类型：timeline
内容：1857 Faraday → 1908 Mie → 1951 Turkevich → 1973 Frens → 1994 Brust → 1998 种子介导 → 2001 Murphy → 2003 Ag⁺ → 2012 二元表面活性剂