# POCT Nucleic Acid Detection: Quantitative Data Anchors

Verified quantitative benchmarks for POCT reviews. Each anchor includes the specific number, the source paper, and how to use it.

## PCR Inhibitors

| Inhibitor | Target | IC50/Threshold | Effect | Source |
|-----------|--------|---------------|--------|--------|
| Hemoglobin (in blood) | Taq polymerase | 39-470 μM | dPCR positive reactions from 410→58 at 470 μM | Sidstedt 2018, DOI:10.1007/s00216-018-0931-z |
| Hemoglobin | EvaGreen fluorescence | ~1.6 μM | Complete fluorescence quenching (but gel shows product) | Sidstedt 2018 |
| Hemoglobin (complete) | dPCR | 620 μM | Complete inhibition | Sidstedt 2018 |
| IgG | ssDNA template | 190 μM | Cq from 26.6→32.6; binds ssDNA not dsDNA | Sidstedt 2018 |
| IgG | dsDNA template | 190 μM | Less affected: 269±8 vs 333±8 positive reactions | Sidstedt 2018 |
| Whole blood | qPCR | 0.5% v/v | Flat amplification curves despite gel product | Sidstedt 2018 |
| Whole blood | dPCR | 15% v/v | Complete inhibition (417→5 positive reactions) | Sidstedt 2018 |
| EDTA | PCR | ≥0.5 mM | Complete (chelates Mg²⁺) | Al-Soud 2001 |
| Heparin | Taq polymerase | ≥1 μg/mL | Begins inhibition | Al-Soud 2001 |
| Humic acid | PCR | ~1 ng/μL | Inhibits polymerase directly; phenolic structures responsible | Sidstedt 2020 |

**Key use in reviews:** "0.5% v/v whole blood flatlined qPCR; 15% v/v completely inhibited dPCR. 1 μL whole blood in 50 μL PCR ≈ 46 μM hemoglobin — in the IC50 zone."

## Sample Preparation Correction Factors

| Preparation method | Recovery | Concentration | Inhibitor removal | Total correction vs buffer | Source |
|-------------------|----------|---------------|-------------------|--------------------------|--------|
| Buffer (academic baseline) | 100% | 1× | 100% | 1× | — |
| Direct lysis - saliva | ~70% | ~0.5× | ~50% | ~6× degradation | Various |
| Direct lysis - NP swab | ~70% | ~0.5× | ~20% | ~14× degradation | Various |
| Magnetic bead extraction (chip) | ~60% | ~1.7× | ~90% | ~1.3× degradation | Cepheid design |
| Filter paper (DBS) | ~20% | ~0.3× | ~80% | ~60× degradation | Hagström 2022 |
| Direct lysis - whole blood | — | — | — | Not feasible | Sidstedt 2018 |

**Key use in reviews:** "Academic LOD of 1 fM (~600 copies/reaction) with direct lysis NP swab correction → ~8,400 copies/reaction effective LOD — lands inside FDA product LOD range."

## Commercial Product LOD Comparison

| Product | Amplification | Sample prep | Label LOD | Verified LOD | TAT | Device cost |
|---------|--------------|-------------|-----------|--------------|-----|-------------|
| Cepheid Xpert Xpress | RT-PCR | US + magnetic bead | 250 cp/mL | 100-400 cp/mL | 45 min | ~$50K |
| Roche cobas Liat | RT-PCR | Direct lysis | 180 cp/mL | 200-500 cp/mL | 20 min | ~$25K |
| Abbott ID NOW | Nicking isothermal | Heat lysis + filter | 125 GE/mL | 500-20K cp/mL | 13 min | ~$3K |
| Lucira Check-It | RT-LAMP | Direct lysis | 900 cp/mL | — | 30 min | Disposable (~$50) |
| Visby Medical | RT-PCR | Filter capture | — | ~2,000 cp/mL | 30 min | Disposable (~$45) |
| Mesa Accula | RT-PCR | Direct lysis | — | ~10,000 cp/mL | 30 min | ~$300 |

Source: Smithgall 2020 J Clin Microbiol, Basu 2020 J Clin Microbiol, Zhen 2020 J Clin Virol

**Key observation:** PCR-based products have tight LOD spread (100-500 cp/mL, ~2×); isothermal products have wide spread (500-20K cp/mL, ~40×). This reflects the robustness gap.

## Academic-to-Product LOD Gap: Five Factors

| Factor | Range | Source |
|--------|-------|--------|
| Sample preparation | 1.3-50× | Section 2 analysis |
| Batch consistency margin | 2-5× | Bisseling 2024 |
| Fixed threshold vs ROC-optimal | 2-3× | Standard practice |
| Storage stability | 1.5-3× | Manufacturer data |
| Operator variability | 1.5-2× | Training studies |
| **Total: direct lysis route** | **~224×** | Product of factors |
| **Total: extraction route** | **~12×** | Product of factors |

## LAMP Performance Data

| Metric | Value | Source |
|--------|-------|--------|
| Best LOD (triple-target RT-LAMP) | 22-25 copies/reaction | Li 2024 |
| Typical LOD range | 10²-10³ copies/reaction | Meta-analysis |
| NTC false positive rate | 5-30% | Kim 2023, DOI:10.1016/j.aca.2023.341693 |
| Reaction temperature | 60-65°C | Notomi 2000 |
| Time to plateau | ~30 min | Field standard |
| Reagent cost/run | ~$1-3 | Vendor-estimated |

## RPA Performance Data

| Metric | Value | Source |
|--------|-------|--------|
| Best LOD (fluorescence) | ~25 copies/reaction | Tan 2024 |
| Best LOD (nested RPA) | ~2 copies/reaction | 2024 report |
| Typical LOD range | 1-50 copies/reaction | Meta-analysis |
| LFA readout LOD | ~50 copies/reaction | Tan 2024 |
| NTC false positive rate | >40% (single), worse in multiplex | Ullah 2024, Johnson 2024 |
| Reaction temperature | 37-42°C | Piepenburg 2006 |
| Time to plateau | 10-20 min | Field standard |

## RCA Performance Data

| Metric | Value | Source |
|--------|-------|--------|
| LOD (RCA alone) | ~100-1000 copies/reaction | Han 2025 |
| LOD (CRISPR-RCA cascade) | ~1.41 aM | Ma 2026 |
| Optimal temperature | 30°C (Phi29) | Dean 2001 |
| Time to plateau | 30-60 min | Field standard |
| Ligation step sensitivity | Degrades >90% in >10% serum | Field reports |

## CRISPR-Dx Performance Data

| Metric | Value | Source |
|--------|-------|--------|
| Cas12a collateral cleavage kcat | ~1,250 s⁻¹ | Chen 2018 Science |
| Cas13a collateral cleavage | ~10⁴ probes/min per recognition | Gootenberg 2017 Science |
| Dynamic range | 2-3 orders of magnitude | Gootenberg 2017, Chen 2018 |
| LOD (no preamp) | 10⁶-10⁹ cp/mL | Kaminski 2021 |
| LOD (with RPA preamp) | 1-25 copies/reaction | Tan 2024, Zhou 2025 |
| One-pot compromise | Cas12a activity at 50-60% of optimal | Tan 2024 |
| Photocleavage efficiency | ~50-70% | Zhou 2025 |

## Key Ratios for Reviews

- Academic papers : FDA-approved microfluidic POCT products ≈ 2,500:1 (from microfluidic review)
- Thermoplastic mold investment: $10K-$500K (from microfluidic review)
- PDMS-to-thermoplastic transfer time: 6-18 months (from microfluidic review)
- TPE injection cycle: 30-60 sec vs PDMS curing: 1-4 hours (from microfluidic review)
