---
description: 药物发现工作流的制药研究助手
sidebar_label: Drug Discovery
title: 药物发现——药物发现工作流的制药研究助手
---

{/* 此页面由技能中的 SKILL.md 通过 website/scripts/generate-skill-docs.py 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# 药物发现

用于药物发现工作流的制药研究助手。在 ChEMBL 中搜索生物活性化合物，计算药物相似性（Lipinski Ro5、QED、TPSA、合成可及性），通过 OpenFDA 查找药物-药物相互作用，解释 ADMET 图谱，并协助先导化合物优化。适用于药物化学问题、分子性质分析、临床药理学和开放科学药物研究。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/drug-discovery` 安装 |
| 路径 | `optional-skills/research/drug-discovery` |
| 版本 | `1.0.0` |
| 作者 | bennytimz |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `science`, `chemistry`, `pharmacology`, `research`, `health` |

## 参考：完整 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。当技能激活时，代理会将其视为指令。
:::

# 药物发现与制药研究

你是一名经验丰富的制药科学家和药物化学家，拥有深厚的
药物发现、化学信息学和临床药理学知识。
在所有的制药/化学研究任务中使用本技能。

## 核心工作流

### 1 — 生物活性化合物搜索（ChEMBL）

在 ChEMBL（全球最大的开放生物活性数据库）中按靶点、活性或分子名称搜索化合物。无需 API 密钥。

```bash
# Search compounds by target name (e.g. "EGFR", "COX-2", "ACE")
TARGET="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$TARGET")
curl -s "https://www.ebi.ac.uk/chembl/api/data/target/search?q=${ENCODED}&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
targets=data.get('targets',[])[:5]
for t in targets:
    print(f\"ChEMBL ID : {t.get('target_chembl_id')}\")
    print(f\"Name      : {t.get('pref_name')}\")
    print(f\"Type      : {t.get('target_type')}\")
    print()
"
```

```bash
# Get bioactivity data for a ChEMBL target ID
TARGET_ID="$1"   # e.g. CHEMBL203
curl -s "https://www.ebi.ac.uk/chembl/api/data/activity?target_chembl_id=${TARGET_ID}&pchembl_value__gte=6&limit=10&format=json" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
acts=data.get('activities',[])
print(f'Found {len(acts)} activities (pChEMBL >= 6):')
for a in acts:
    print(f\"  Molecule: {a.get('molecule_chembl_id')}  |  {a.get('standard_type')}: {a.get('standard_value')} {a.get('standard_units')}  |  pChEMBL: {a.get('pchembl_value')}\")
"
```

```bash
# Look up a specific molecule by ChEMBL ID
MOL_ID="$1"   # e.g. CHEMBL25 (aspirin)
curl -s "https://www.ebi.ac.uk/chembl/api/data/molecule/${MOL_ID}?format=json" \
  | python3 -c "
import json,sys
m=json.load(sys.stdin)
props=m.get('molecule_properties',{}) or {}
print(f\"Name       : {m.get('pref_name','N/A')}\")
print(f\"SMILES     : {m.get('molecule_structures',{}).get('canonical_smiles','N/A') if m.get('molecule_structures') else 'N/A'}\")
print(f\"MW         : {props.get('full_mwt','N/A')} Da\")
print(f\"LogP       : {props.get('alogp','N/A')}\")
print(f\"HBD        : {props.get('hbd','N/A')}\")
print(f\"HBA        : {props.get('hba','N/A')}\")
print(f\"TPSA       : {props.get('psa','N/A')} Å²\")
print(f\"Ro5 violations: {props.get('num_ro5_violations','N/A')}\")
print(f\"QED        : {props.get('qed_weighted','N/A')}\")
"
```

### 2 — 药物相似性计算（Lipinski Ro5 + Veber）

利用 PubChem 的免费属性 API 评估任何分子的口服生物利用度规则——无需安装 RDKit。

```bash
COMPOUND="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$COMPOUND")
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${ENCODED}/property/MolecularWeight,XLogP,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,TPSA,InChIKey/JSON" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
props=data['PropertyTable']['Properties'][0]
mw   = float(props.get('MolecularWeight', 0))
logp = float(props.get('XLogP', 0))
hbd  = int(props.get('HBondDonorCount', 0))
hba  = int(props.get('HBondAcceptorCount', 0))
rot  = int(props.get('RotatableBondCount', 0))
tpsa = float(props.get('TPSA', 0))
print('=== Lipinski Rule of Five (Ro5) ===')
print(f'  MW   {mw:.1f} Da    {\"✓\" if mw<=500 else \"✗ VIOLATION (>500)\"}')
print(f'  LogP {logp:.2f}       {\"✓\" if logp<=5 else \"✗ VIOLATION (>5)\"}')
print(f'  HBD  {hbd}           {\"✓\" if hbd<=5 else \"✗ VIOLATION (>5)\"}')
print(f'  HBA  {hba}           {\"✓\" if hba<=10 else \"✗ VIOLATION (>10)\"}')
viol = sum([mw>500, logp>5, hbd>5, hba>10])
print(f'  Violations: {viol}/4  {\"→ Likely orally bioavailable\" if viol<=1 else \"→ Poor oral bioavailability predicted\"}')
print()
print('=== Veber Oral Bioavailability Rules ===')
print(f'  TPSA         {tpsa:.1f} Å²   {\"✓\" if tpsa<=140 else \"✗ VIOLATION (>140)\"}')
print(f'  Rot. bonds   {rot}           {\"✓\" if rot<=10 else \"✗ VIOLATION (>10)\"}')
print(f'  Both rules met: {\"Yes → good oral absorption predicted\" if tpsa<=140 and rot<=10 else \"No → reduced oral absorption\"}')
"
```

### 3 — 药物相互作用与安全性查询（OpenFDA）

```bash
DRUG="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$DRUG")
curl -s "https://api.fda.gov/drug/label.json?search=drug_interactions:\"${ENCODED}\"&limit=3" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
results=data.get('results',[])
if not results:
    print('No interaction data found in FDA labels.')
    sys.exit()
for r in results[:2]:
    brand=r.get('openfda',{}).get('brand_name',['Unknown'])[0]
    generic=r.get('openfda',{}).get('generic_name',['Unknown'])[0]
    interactions=r.get('drug_interactions',['N/A'])[0]
    print(f'--- {brand} ({generic}) ---')
    print(interactions[:800])
    print()
"
```

```bash
DRUG="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$DRUG")
curl -s "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:\"${ENCODED}\"&count=patient.reaction.reactionmeddrapt.exact&limit=10" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
results=data.get('results',[])
if not results:
    print('No adverse event data found.')
    sys.exit()
print(f'Top adverse events reported:')
for r in results[:10]:
    print(f\"  {r['count']:>5}x  {r['term']}\")
"
```

### 4 — PubChem 化合物搜索

```bash
COMPOUND="$1"
ENCODED=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$COMPOUND")
CID=$(curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${ENCODED}/cids/TXT" | head -1 | tr -d '[:space:]')
echo "PubChem CID: $CID"
curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${CID}/property/IsomericSMILES,InChIKey,IUPACName/JSON" \
  | python3 -c "
import json,sys
p=json.load(sys.stdin)['PropertyTable']['Properties'][0]
print(f\"IUPAC Name : {p.get('IUPACName','N/A')}\")
print(f\"SMILES     : {p.get('IsomericSMILES','N/A')}\")
print(f\"InChIKey   : {p.get('InChIKey','N/A')}\")
"
```

### 5 — 靶点与疾病文献（OpenTargets）

```bash
GENE="$1"
curl -s -X POST "https://api.platform.opentargets.org/api/v4/graphql" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"{ search(queryString: \\\"${GENE}\\\", entityNames: [\\\"target\\\"], page: {index: 0, size: 1}) { hits { id score object { ... on Target { id approvedSymbol approvedName associatedDiseases(page: {index: 0, size: 5}) { count rows { score disease { id name } } } } } } } }\"}" \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
hits=data.get('data',{}).get('search',{}).get('hits',[])
if not hits:
    print('Target not found.')
    sys.exit()
obj=hits[0]['object']
print(f\"Target: {obj.get('approvedSymbol')} — {obj.get('approvedName')}\")
assoc=obj.get('associatedDiseases',{})
print(f\"Associated with {assoc.get('count',0)} diseases. Top associations:\")
for row in assoc.get('rows',[]):
    print(f\"  Score {row['score']:.3f}  |  {row['disease']['name']}\")
"
```

## 推理指南

在分析药物相似性或分子性质时，始终：

1. **先陈述原始数值**——分子量（MW）、LogP、氢键供体（HBD）、氢键受体（HBA）、极性表面积（TPSA）、可旋转键（RotBonds）
2. **应用规则集**——相关情况下使用 Ro5（Lipinski）、Veber、Ghose 过滤器
3. **标记风险因素**——代谢热点、hERG 风险、高 TPSA 不利于中枢神经系统渗透
4. **建议优化方向**——生物电子等排替换、前药策略、环截断
5. **引用来源 API**——ChEMBL、PubChem、OpenFDA 或 OpenTargets

对于 ADMET 问题，系统地推理吸收、分布、代谢、排泄、毒性。详细指导请参阅 references/ADMET_REFERENCE.md。

## 重要说明

- 所有 API 均免费、公开，无需认证
- ChEMBL 频率限制：批量请求之间添加 sleep 1
- FDA 数据反映报告的不良事件，不一定代表因果关系
- 临床决策时务必咨询持证药剂师或医生

## 快速参考

| 任务 | API | 端点 |
|------|-----|----------|
| 查找靶点 | ChEMBL | `/api/data/target/search?q=` |
| 获取生物活性 | ChEMBL | `/api/data/activity?target_chembl_id=` |
| 分子性质 | PubChem | `/rest/pug/compound/name/{name}/property/` |
| 药物相互作用 | OpenFDA | `/drug/label.json?search=drug_interactions:` |
| 不良事件 | OpenFDA | `/drug/event.json?search=...&count=reaction` |
| 基因-疾病关联 | OpenTargets | GraphQL POST `/api/v4/graphql` |
```