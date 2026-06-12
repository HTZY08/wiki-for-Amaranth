# Journal Targeting Guide for POCT / Microfluidics / Gold Nanomaterial Reviews

> Calibrated 2026-06-09. Impact factors are approximate and subject to change.
> Use this as a decision-support matrix during Phase 0 (thesis decomposition) or Phase 1 (scope definition).
> Always verify current IF, review acceptance policy, and APC before submission.

---

## Domain A: POCT 核酸检测

**Core topics:** Isothermal amplification (RPA, LAMP, RCA), CRISPR/Cas, DNAzyme, spherical nucleic acids, logic-gated signal amplification, nucleic acid LFIA, colorimetric/fluorescent/electrochemical NA sensors.

| Tier | Journal | IF (~2025) | Review Policy | APC | Notes |
|------|---------|------------|---------------|-----|-------|
| ★★★ | **Biosensors and Bioelectronics** (Elsevier) | ~10 | ✅ Invited + unsolicited | ~$4,500 | Covers nucleic acid sensors + POCT broadly. Strong fit for DNAzyme-CRISPR cascaded detection narratives. High selectivity. |
| ★★★ | **TrAC Trends in Analytical Chemistry** (Elsevier) | ~12 | ✅ Review-only journal (invited + unsolicited) | ~$4,000 | Review-only format = no competition with research articles. Needs a strong critical argument (not just summary). Fast review (~4-6 weeks). |
| ★★☆ | **Sensors and Actuators B: Chemical** (Elsevier) | ~8 | ✅ Accepts reviews | ~$3,500 | Sensor-device engineering angle. Higher acceptance rate than B&B. Shorter review cycle (~6 weeks). Good for methods-focused review. |
| ★★☆ | **ACS Sensors** (ACS) | ~8 | ✅ Limited reviews, unsolicited considered | ~$5,000 | ACS brand. Prefers reviews with clear translational angle. High desk-reject rate. |
| ★☆☆ | **Talanta** (Elsevier) | ~6 | ✅ Accepts reviews | ~$3,200 | Analytical chemistry classic. Moderate barrier. Good for a first review. |
| ★☆☆ | **Analytica Chimica Acta** (Elsevier) | ~6 | ✅ Accepts reviews | ~$3,500 | Method-oriented. Fit for logic-gated + isothermal amplification reviews. |
| ★☆☆ | **Microchemical Journal** (Elsevier) | ~5 | ✅ Accepts reviews | ~$2,800 | Lower barrier, fast review. Good backup option. |

### Decision Flow for Domain A

```
Does the review have a strong critical argument (not just "we reviewed X")?
  ├─ Yes → Can the narrative sustain TrAC's standard?
  │   ├─ Yes → Target TrAC Trends Anal Chem (highest prestige)
  │   └─ No  → Target Biosensors Bioelectron (broader scope)
  └─ No  → Does the review emphasize device/engineering over chemistry?
      ├─ Yes → Sens Actuators B (device-oriented readership)
      └─ No  → Talanta or Anal Chim Acta (method/chemistry lens)
```

### Overlap Warning

Reviews combining NA detection + microfluidics (e.g., "microfluidic NA amplification for POCT") compete with both Domain A and Domain B journals. If the microfluidic content is the main contribution, target Domain B instead. If the NA amplification mechanism is the main story, stay in Domain A.

---

## Domain B: 微流控 POCT

**Core topics:** Paper-based microfluidics (µPAD), centrifugal microfluidics (Lab-on-Disc), digital microfluidics (EWOD), Micro-ELISA, passive valves, timing control, integration challenges, bubble management.

| Tier | Journal | IF (~2025) | Review Policy | APC | Notes |
|------|---------|------------|---------------|-----|-------|
| ★★★ | **Lab on a Chip** (RSC) | ~6.5 | ✅ Reviews published (invited + unsolicited) | ~$2,750 (OA opt) | Microfluidics flagship. Very selective (~80% rejection). Review needs to demonstrate both device physics novelty AND application significance. |
| ★★★ | **Microsystems & Nanoengineering** (Nature-Springer) | ~7.5 | ✅ OA, accepts reviews | $2,990 | Nature partner journal. OA. Strong fit for centrifugal/digital microfluidics POCT reviews. Growing IF. |
| ★★☆ | **Sensors and Actuators B: Chemical** (Elsevier) | ~8 | ✅ Accepts reviews | ~$3,500 | Broad sensor coverage includes microfluidic devices. Good for reviews emphasizing the sensing outcome over the fluidic mechanism. |
| ★★☆ | **Analytical Chemistry** (ACS) | ~7 | ⚠️ Limited reviews (mostly invited) | ~$5,000 | High prestige but review slots are scarce. Only suitable if the microfluidic review has a truly novel perspective. |
| ★☆☆ | **Micromachines** (MDPI) | ~3.5 | ✅ OA, actively seeks reviews | $2,600 | Low barrier, fast turnaround. Good for a first review or a comprehensive survey. OA = high visibility but lower prestige. |
| ★☆☆ | **Microfluidics and Nanofluidics** (Springer) | ~2.5 | ✅ Accepts reviews | ~$2,200 | Dedicated microfluidics journal. Lower IF but well-respected within the community. |
| ★☆☆ | **Biomedical Microdevices** (Springer) | ~2.5 | ✅ Accepts reviews | ~$2,200 | BioMEMS focus. Good for POCT + implantable/wearable microfluidics. |
| ★☆☆ | **SLAS Technology** (Elsevier) | ~3 | ✅ Accepts reviews | $2,700 | Lab automation angle. Good fit for "full workflow integration" narratives. |

### Decision Flow for Domain B

```
Is the review about a single microfluidic modality (e.g., centrifugal only)
or a comprehensive comparison across modalities?
  ├─ Single modality:
  │   Does it include full engineering design + application data?
  │   ├─ Yes → Lab on a Chip or Microsystems Nanoeng
  │   └─ No  → Microfluidics Nanofluidics or Micromachines
  └─ Cross-modality comparison:
      Does it have a strong integrative argument (e.g., "which platform
      for which application")?
      ├─ Yes → Anal Chem or Sens Actuators B
      └─ No  → Micromachines (comprehensive survey fits here)
```

### Critical Constraint for Domain B

Many microfluidics reviews are written by engineers for engineers. But POCT reviews need a clinical/application grounding. If the review lacks real-sample validation data or clinical context, Lab on a Chip and Anal Chem will desk-reject it. Add a "real-world performance" section even if it only discusses the gap.

---

## Domain C: 金纳米材料 — Fundamental

**Core topics:** Synthesis (Turkevich-Frens, Brust-Schiffrin, seed-mediated), growth mechanisms (nucleation, capping agent function, twin vs single-crystal), LSPR optical properties, surface chemistry, scalability.

**Scope boundary:** This domain covers fundamental physical chemistry — NOT biosensing/drug delivery/imaging applications. Reviews with application content belong under Domain A or a materials-for-biomedicine journal instead.

| Tier | Journal | IF (~2025) | Review Policy | APC | Notes |
|------|---------|------------|---------------|-----|-------|
| ★★★ | **Chemical Reviews** (ACS) | ~50+ | ❌ Invited only | N/A | Not accessible for unsolicited submission. Don't target. |
| ★★★ | **Chemical Society Reviews** (RSC) | ~40+ | ❌ Invited only | N/A | Same — invited-only. |
| ★★★ | **ACS Nano** (ACS) | ~17 | ⚠️ Mostly invited, accepts some unsolicited | ~$5,000 | Very competitive. Requires breakthrough perspective. Only if the "synthesis has outpaced mechanism" thesis is truly novel. |
| ★★★ | **Nano Today** (Elsevier) | ~17 | ⚠️ Mostly invited | ~$4,500 | High bar. Only if the review proposes a new framework, not just surveys. |
| ★★☆ | **Nanoscale** (RSC) | ~7.5 | ✅ Accepts unsolicited reviews | ~$2,750 (OA opt) | Best fit for most AuNP fundamental reviews. Published numerous reviews on synthesis, LSPR, growth mechanism. Good balance of prestige and accessibility. |
| ★★☆ | **Nanoscale Horizons** (RSC) | ~9 | ✅ Accepts reviews (higher bar than Nanoscale) | ~$2,750 (OA opt) | Requires "a new concept or new understanding" — not just a comprehensive survey. Use only if the central argument is genuinely novel. |
| ★★☆ | **Chemistry of Materials** (ACS) | ~8.5 | ✅ Accepts reviews | ~$5,000 | Materials chemistry focus. Good fit for reviews emphasizing synthetic chemistry and structure-property relationships. |
| ★☆☆ | **Langmuir** (ACS) | ~4.5 | ✅ Accepts reviews | ~$5,000 | Surface/colloid chemistry focus. Perfect for capping agent, surface ligand, and interfacial topics within AuNP. Lower IF but high relevance. |
| ★☆☆ | **Journal of Physical Chemistry C** (ACS) | ~3.5 | ✅ Accepts reviews | ~$5,000 | Good for LSPR theory-heavy reviews (Mie, DDA, FDTD). Physical chemistry audience. |
| ★☆☆ | **Nanomaterials** (MDPI) | ~5 | ✅ OA, actively seeks reviews | $2,900 | OA. Fast review. Good backup. Broad readership but lower selectivity. |
| ★☆☆ | **Journal of Materials Chemistry C** (RSC) | ~6.5 | ✅ Accepts reviews | ~$2,750 (OA opt) | Good for reviews emphasizing optical/electronic properties. |

### Decision Flow for Domain C

```
Is the review's central argument genuinely novel (not "we summarized X")?
  ├─ Yes, it proposes a new framework:
  │   → Nanoscale Horizons or Chem Mater
  └─ No, it's a comprehensive critical survey:
      → Nanoscale (default best fit)
      │
      Does the review emphasize surface/colloid chemistry?
      ├─ Yes → Langmuir
      └─ No  → Does it emphasize optical theory over synthesis?
          ├─ Yes → JPCC
          └─ No  → Nanomaterials (backup)
```

### Critical Constraint for Domain C

**Do NOT include application content** (biosensing, drug delivery, imaging) when targeting fundamental AuNP journals like Nanoscale or Langmuir. Application content dilutes the focus and confuses the journal fit. If the user wants to include applications, redirect to Domain A journals or to a different review entirely (which is why thesis Chapter 1 decomposition often yields a separate application-focused review alongside the fundamental one).

---

## Cross-Domain Comparison Table

| Dimension | A: POCT核酸检测 | B: 微流控POCT | C: 金纳米材料 |
|-----------|----------------|---------------|---------------|
| Reader community | Biochemists, sensor engineers | Microfluidics engineers, device physicists | Materials chemists, physical chemists |
| Preferred journal family | Elsevier (B&B, TrAC, SAB) | RSC (LoC), Nature partner (Microsys Nanoeng) | RSC (Nanoscale), ACS (Chem Mater, Langmuir) |
| Typical review length | 8,000-15,000 words | 10,000-20,000 words | 10,000-20,000 words |
| Figure density | High (schematic + data plots) | Very high (schematics + CAD + fluid simulation) | High (TEM/SEM + spectra + crystallography) |
| Typical reference count | 100-200 | 100-250 | 150-300 |
| OA preference | Optional (Elsevier hybrid) | RSC OA optional | Varies (RSC hybrid, ACS hybrid) |
| First-author friendly | Yes (Talanta, ACA) | Yes (Micromachines) | Yes (Nanomaterials, Langmuir) |
| Desk-reject risk (top tier) | Moderate | High (LoC) | Moderate |

---

## General Submission Strategy

### Tier Strategy for First-Time Review Authors

| Phase | Action |
|-------|--------|
| First submission | Target one tier down from the ideal. Get the experience of peer review. |
| If accepted | Publish, build CV, then next review goes one tier up. |
| If rejected | Use reviewer comments to improve, then submit to the ideal tier. The improvement often lands it. |
| Rinse | Repeat. |

### Timing

| Factor | Typical |
|--------|---------|
| Desk decision | 1-2 weeks |
| First round review | 4-10 weeks |
| Revision | 2-8 weeks |
| Acceptance to publication | 2-6 weeks (varies by journal, OA faster) |
| **Total realistic timeline** | **3-8 months** |

### What Reviewers and Editors Care About

1. **Novelty of argument** — Not "what has been done" but "what does it mean and where should we go?"
2. **Coverage** — Missing a key paper = immediate rejection signal
3. **Fair criticism** — A review that only praises its own sub-field is not credible
4. **Clarity of figures** — Bad figures kill reviews faster than bad text
5. **Organization** — The reader should know after reading each section's first paragraph what that section argues

---

## AI Search Integration for Journal Selection

When the user asks "what journal should I submit to" and the topic doesn't match the three domains above, use this search pattern:

```
web_search("review article [TOPIC] journal recommendations impact factor submission guidelines 2025 2026")
web_search("[TOPIC] published in [JOURNAL] 2024 2025")  # Check what's actually been published recently
```

Then verify:
- Does this journal accept unsolicited reviews? → Check journal's "Review Article" or "Author Guidelines" page
- Has this journal published a similar review in the last 2 years? → If yes, your review needs a clearly different angle
- What is the typical review length? → Some journals cap reviews at 10,000 words; others allow up to 25,000

Record the findings as session notes, not in this reference file — the three domains above are the calibrated set; new domains need fresh verification.
