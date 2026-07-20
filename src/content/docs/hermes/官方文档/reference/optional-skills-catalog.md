---
title: 可选技能目录
---

# 可选技能目录（Optional Skills Catalog）

可选技能随 hermes-agent 一同发布，位于 `optional-skills/` 目录下，但**默认未激活**。需显式安装：

```bash
hermes skills install official/<category>/<skill>
```

## autonomous-ai-agents（自主 AI 代理）

antigravity-cli, blackbox, grok, honcho, openhands

## blockchain（区块链）

evm, hyperliquid, solana

## communication（通信）

one-three-one-rule

## creative（创意）

baoyu-article-illustrator, baoyu-comic, blender-mcp, concept-diagrams, creative-ideation, hyperframes, kanban-video-orchestrator, meme-generation, pixel-art, unreal-mcp

## devops（开发运维）

inference-sh-cli, docker-management, hermes-s6-container-supervision, pinggy-tunnel, watchers

## dogfood（自用测试）

adversarial-ux-test

## email（电子邮件）

agentmail

## finance（金融）

3-statement-model, comps-analysis, dcf-model, excel-author, lbo-model, merger-model, pptx-author, stocks

## gaming（游戏）

minecraft-modpack-server, pokemon-player

## health（健康）

fitness-nutrition, neuroskill-bci

## mcp（模型上下文协议）

fastmcp, mcp-oauth-remote-gateway, mcporter

## migration（迁移）

openclaw-migration

## mlops（机器学习运维）

huggingface-accelerate, axolotl, chroma, clip, dspy, faiss, optimizing-attention-flash, guidance, huggingface-tokenizers, instructor, lambda-labs-gpu-cloud, ...（40+ 个技能）

## payments（支付）

mpp-agent, stripe-link-cli, stripe-projects

## productivity（生产力）

canvas, here-now, memento-flashcards, shop, shopify, telephony

## research（研究）

bioinformatics, darwinian-evolver, domain-intel, drug-discovery, duckduckgo-search, gitnexus-explorer, osint-investigation, parallel-cli, qmd, scrapling, searxng-search

## security（安全）

1password, godmode, oss-forensics, sherlock, unbroker, web-pentest

## software-development（软件开发）

code-wiki, rest-graphql-debug, subagent-driven-development

## web-development（Web 开发）

cloudflare-temporary-deploy, page-agent

## 贡献可选技能

若要添加新的可选技能：在 `optional-skills/` 下创建目录，添加 `SKILL.md`，包含支持文件，提交 PR。
