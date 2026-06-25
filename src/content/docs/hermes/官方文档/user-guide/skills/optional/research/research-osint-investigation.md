--- frontmatter ---
---
title: "开源情报调查"
sidebar_label: "开源情报调查"
description: "公共记录开源情报调查框架 —— SEC EDGAR 备案、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄漏、纽约市房产记录..."
---

--- body ---
{/* 此页面由 website/scripts/generate-skill-docs.py 从技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 开源情报调查

公共记录开源情报调查框架 —— SEC EDGAR 备案、USAspending 合同、参议院游说、OFAC 制裁、ICIJ 离岸泄漏、纽约市房产记录 (ACRIS)、OpenCorporates 注册信息、CourtListener 法庭记录、Wayback Machine 存档、Wikipedia + Wikidata、GDELT 新闻监控。跨源实体解析、交叉链接分析、时间相关性分析、证据链构建。仅依赖 Python 标准库。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/research/osint-investigation` 安装 |
| 路径 | `optional-skills/research/osint-investigation` |
| 版本 | `0.1.0` |
| 作者 | Hermes 代理（改编自 ShinMegamiBoson/OpenPlanter，MIT 许可） |
| 平台 | linux, macos, windows |
| 标签 | `osint`, `investigation`, `public-records`, `sec`, `sanctions`, `corporate-registry`, `property`, `courts`, `due-diligence`, `journalism` |
| 相关技能 | [`domain-intel`](/docs/user-guide/skills/optional/research/research-domain-intel), [`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整 SKILL.md

:::info
以下为 Hermes 在此技能被触发时加载的完整技能定义。这是代理在技能激活时看到的指令。
:::

# 开源情报调查 —— 公共记录交叉引用

用于公共记录开源情报的调查框架：政府合同、公司备案、游说、制裁、离岸泄漏、房产记录、法庭记录、网页存档、知识库和全球新闻。跨异构来源解析实体，基于明确置信度构建交叉链接，运行统计时间相关性测试，并生成结构化的证据链。

**仅依赖 Python 标准库。** 零安装。支持 Linux、macOS、Windows。大多数来源无需 API 密钥即可使用（OpenCorporates 提供可选免费令牌，可提高速率限制）。

改编自 MIT 许可的 ShinMegamiBoson/OpenPlanter 项目；扩展了原始项目未涵盖的身份/房产/诉讼/存档/新闻来源。

## 何时使用此技能

当用户提出以下要求时使用：

- “追踪资金流向”—— 政府合同、游说 → 立法、制裁
- 企业尽职调查 —— 谁控制公司 X，他们在哪里注册，谁担任董事会成员，他们提交过哪些备案
- 制裁筛查 —— 实体 X 是否在 OFAC SDN 名单、ICIJ 离岸泄漏数据库中
- 付费游说调查 —— 有离岸关联的承包商、赢得奖项的游说客户
- 房产所有权 —— 按姓名或地址查找记录的契约/抵押（纽约市；对于其他县，请指引用户到相关记录机构）
- 诉讼历史 —— 查找联邦和州法院判决及 PACER 案卷
- 多源实体解析（名称变体如 LLC 后缀、缩写）
- 具有明确置信度级别的证据链构建
- “关于 X 有哪些报道”—— 国际新闻（GDELT）+ Wikipedia 叙述 + Wayback Machine 恢复失效 URL

**请勿**在以下情况下使用此技能：

- 通用网页研究 → `web_search` / `web_extract`
- 域名/基础设施开源情报 → `domain-intel` 技能
- 学术文献 → `arxiv` 技能
- 社交媒体个人资料发现 → `sherlock` 技能（可选）
- 美国**联邦**竞选财务 —— 有意不在此处包含 FEC（其在免费 DEMO_KEY 层级上对临时捐款人姓名查询的 API 不可靠）。对于联邦捐款，请指引用户直接访问 https://www.fec.gov/data/。

## 工作流程

代理通过 `terminal` 工具运行脚本。`SKILL_DIR` 是包含此 SKILL.md 的目录。

### 1. 确定哪些来源适用

阅读数据源维基条目以规划调查：

```
ls SKILL_DIR/references/sources/

# 联邦财务 / 监管
cat SKILL_DIR/references/sources/sec-edgar.md       # 公司备案
cat SKILL_DIR/references/sources/usaspending.md     # 联邦合同
cat SKILL_DIR/references/sources/senate-ld.md       # 游说
cat SKILL_DIR/references/sources/ofac-sdn.md        # 制裁
cat SKILL_DIR/references/sources/icij-offshore.md   # 离岸泄漏

# 身份 / 房产 / 诉讼 / 存档 / 新闻
cat SKILL_DIR/references/sources/nyc-acris.md       # 纽约市房产记录
cat SKILL_DIR/references/sources/opencorporates.md  # 全球公司注册信息
cat SKILL_DIR/references/sources/courtlistener.md   # 法庭记录（联邦 + 州）
cat SKILL_DIR/references/sources/wayback.md         # Wayback Machine 存档
cat SKILL_DIR/references/sources/wikipedia.md       # Wikipedia + Wikidata
cat SKILL_DIR/references/sources/gdelt.md           # 全球新闻监控
```

每个条目遵循 9 节模板：摘要、访问、架构、覆盖范围、交叉引用键、数据质量、获取、法律、参考文献。

**交叉引用潜力**部分映射了来源之间的连接键 —— 优先阅读这些内容以选择合适的配对。

### 2. 获取数据

每个来源在 `SKILL_DIR/scripts/` 中都有仅依赖标准库的获取脚本：

**联邦财务 / 监管**

```bash
# SEC EDGAR 备案（公司披露）
python3 SKILL_DIR/scripts/fetch_sec_edgar.py --cik 0000320193 \
    --types 10-K,10-Q --out data/edgar_filings.csv

# USAspending 联邦合同
python3 SKILL_DIR/scripts/fetch_usaspending.py --recipient "EXAMPLE CORP" \
    --fy 2024 --out data/contracts.csv

# 参议院 LD-1 / LD-2 游说披露
python3 SKILL_DIR/scripts/fetch_senate_ld.py --client "EXAMPLE CORP" \
    --year 2024 --out data/lobbying.csv

# OFAC SDN 制裁名单（完整快照）
python3 SKILL_DIR/scripts/fetch_ofac_sdn.py --out data/ofac_sdn.csv

# ICIJ 离岸泄漏 —— 首次使用时下载约 70 MB 批量 CSV，
# 然后在本地搜索。在 $HERMES_OSINT_CACHE/icij/ 下缓存 30 天
# （默认：~/.cache/hermes-osint/icij/）。
python3 SKILL_DIR/scripts/fetch_icij_offshore.py --entity "EXAMPLE CORP" \
    --out data/icij.csv
```

**身份 / 房产 / 诉讼 / 存档 / 新闻**

```bash
# 纽约市房产记录（契约、抵押、留置权）—— 通过 Socrata 的 ACRIS
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --name "SMITH, JOHN" \
    --out data/acris.csv
python3 SKILL_DIR/scripts/fetch_nyc_acris.py --address "571 HUDSON" \
    --out data/acris_addr.csv

# OpenCorporates —— 130 多个司法管辖区的公司注册信息
# （需要免费令牌；设置 OPENCORPORATES_API_TOKEN 或使用 --token 传入）
python3 SKILL_DIR/scripts/fetch_opencorporates.py --query "Example Corp" \
    --jurisdiction us_ny --out data/opencorporates.csv

# CourtListener —— 联邦 + 州法院判决、PACER 案卷
python3 SKILL_DIR/scripts/fetch_courtlistener.py --query "Smith v. Example Corp" \
    --type opinions --out data/courts.csv

# Wayback Machine —— 历史网页捕获
python3 SKILL_DIR/scripts/fetch_wayback.py --url "example.com" \
    --match host --collapse digest --out data/wayback.csv

# Wikipedia + Wikidata —— 叙事简介 + 结构化事实
# 设置 HERMES_OSINT_UA=your-app/1.0 (your@email) 以表明身份
python3 SKILL_DIR/scripts/fetch_wikipedia.py --query "Bill Gates" \
    --out data/wp.csv

# GDELT —— 100 多种语言的全球新闻，约 2015 年至今
python3 SKILL_DIR/scripts/fetch_gdelt.py --query '"Example Corp"' \
    --timespan 1y --out data/gdelt.csv
```

所有输出均为带表头的规范化 CSV。重新运行脚本是幂等的。

当某个私人个体不会出现在某个来源中时（例如，SEC EDGAR 中不涉及非上市公司人员，USAspending 中不涉及非联邦承包商人员，参议院 LDA 中不涉及非游说客户人员），脚本会返回 0 行并附带明确警告，而非静默写入空 CSV。EDGAR 会特别标记公司名称解析器匹配到的是个人 Form 3/4/5 备案者而非公司注册者。

每个来源维基条目中均有速率限制说明。默认获取器在分页请求之间礼貌等待。**API 密钥可提高速率限制**，支持密钥的来源包括：`SEC_USER_AGENT`、`SENATE_LDA_TOKEN`、`OPENCORPORATES_API_TOKEN`、`COURTLISTENER_TOKEN`。所有脚本都会立即显示 429 响应并附带上游的配额消息，以便用户知道应该降低速度或提供密钥。

### 3. 跨源解析实体

规范化名称，并在两个 CSV 文件之间查找匹配：

```bash
# 匹配游说客户（参议院 LDA）与合同接受方（USAspending）
python3 SKILL_DIR/scripts/entity_resolution.py \
    --left  data/lobbying.csv   --left-name-col  client_name \
    --right data/contracts.csv  --right-name-col recipient_name \
    --out data/cross_links.csv
```

三种匹配层级，带明确置信度：

| 层级 | 方法 | 置信度 |
|------|------|--------|
| `exact` | 去除后缀/标点后规范化字符串相等 | 高 |
| `fuzzy` | 排序后令牌相等（词袋匹配） | 中 |
| `token_overlap` | 令牌重叠度 ≥60%，至少 2 个共享令牌，令牌长度 ≥4 字符 | 低 |

输出 `cross_links.csv` 列：`match_type, confidence, left_name, right_name, left_normalized, right_normalized, left_row, right_row`。

### 4. 统计时间相关性分析（可选）

使用置换检验测试两个时间序列是否可疑地接近 —— 例如，游说备案接近合同授予：

```bash
python3 SKILL_DIR/scripts/timing_analysis.py \
    --donations data/lobbying.csv --donation-date-col filing_date \
        --donation-amount-col income --donation-donor-col client_name \
        --donation-recipient-col registrant_name \
    --contracts data/contracts.csv --contract-date-col award_date \
        --contract-vendor-col recipient_name \
    --cross-links data/cross_links.csv \
    --permutations 1000 \
    --out data/timing.json
```

脚本的列标志故意保持通用 —— 原工具是为捐款与奖项设计的，但适用于通过交叉链接连接的任何（事件，收款方）时间序列。零假设：事件时间与奖项日期独立。单尾 p 值 = 平均最近奖项距离 ≤ 观测值的置换比例。每个（付款方，供应商）对至少需要 3 个事件才能运行检验。

### 5. 构建发现 JSON（证据链）

```bash
python3 SKILL_DIR/scripts/build_findings.py \
    --cross-links data/cross_links.csv \
    --timing data/timing.json \
    --out data/findings.json
```

每个发现包含 `id, title, severity, confidence, summary, evidence[], sources[]`。每个证据项都指向源 CSV 中的特定行。用户（或后续代理）可以针对来源验证每个声明。

## 置信度与证据纪律

这是技能的核心规则。请告知用户：

- 每个声明必须追溯到一条记录。不得进行无依据的断言。
- 置信度层级随声明传递。`match_type=fuzzy` 表示“可能”，而非“确认”。
- 实体解析产生的是候选对象，而非结论。`fuzzy` 匹配（如 “ACME LLC” 与 “Acme Holdings Group”）是一条线索，而非事实。
- 统计显著性 ≠ 不当行为。p < 0.05 仅意味着时间模式在零假设下不太可能出现。它并不确立腐败行为。
- 此处所有数据源均为公共记录。它们仍可能包含不准确、过时信息或编辑内容（GDPR、密封记录）。

## 添加新的数据源

使用模板：

```bash
cp SKILL_DIR/templates/source-template.md \
    SKILL_DIR/references/sources/<your-source>.md
```

填写所有 9 个部分。在 `scripts/` 中编写一个仅使用标准库并输出规范化 CSV 的 `fetch_<source>.py` 脚本。更新上方“何时使用”部分中的来源列表。

## 工具及其局限性

- `entity_resolution.py` **不**使用外部模糊匹配库（没有 rapidfuzz，没有 jellyfish）。词袋匹配是上限。如果您需要 Levenshtein 距离、音译或语音匹配，请单独通过 pip 安装。
- `timing_analysis.py` 使用 Python 的 `random` 进行置换。为获得可重复性，请传入 `--seed N`。
- `fetch_*.py` 脚本使用 `urllib.request` 并遵循 `Retry-After`。大量批量使用仍可能违反服务条款 —— 请先阅读每个来源的法律部分。

## 法律说明

所有第一阶段来源均为公共记录。根据其各自的访问条款（FOIA、公共记录法、ICIJ 明确发布、OFAC 公共数据），允许批量获取。但是：

- 某些来源的速率限制较为严格。请尊重其头部信息。
- 某些来源会编辑注册人信息（GDPR 在 WHOIS 上的应用、密封备案）。
- 交叉引用公共记录以识别私人个体可能涉及伦理问题。此技能生成的是证据链，而非指控。