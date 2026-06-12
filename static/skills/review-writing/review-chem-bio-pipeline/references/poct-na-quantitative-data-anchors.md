# POCT Nucleic Acid Detection: Quantitative Data Anchors

Verified quantitative benchmarks for POCT reviews. Each anchor includes the specific number, the source paper, and how to use it.

## PCR Inhibitors

| Inhibitor | Target | IC50/Threshold | Effect | Source |
|-----------|--------|---------------|--------|--------|
| Hemoglobin (blood) | Taq polymerase | 39-470 μM | dPCR positive reactions from 410 → 58 at 470 μM | Sidstedt 2018, DOI:10.1007/s00216-018-0931-z |
| Hemoglobin | EvaGreen fluor. | ~1.6 μM | Complete fluorescence quenching (but gel shows product) | Sidstedt 2018 |
| Hemoglobin (complete) | dPCR | 620 μM | Complete inhibition | Sidstedt 2018 |
| IgG | ssDNA template | 190 μM | Cq from 26.6 → 32.6; binds ssDNA not dsDNA | Sidstedt 2018 |
| IgG | dsDNA template | 190 μM | Less affected: 269±8 vs 333±8 positive reactions | Sidstedt 2018 |
| Whole blood | qPCR | 0.5% v/v | Flat amplification despite gel product | Sidstedt 2018 |
| Whole blood | dPCR | 15% v/v | Complete inhibition (417 → 5 positive) | Sidstedt 2018 |
| EDTA | PCR | ≥0.5 mM | Chelates Mg²⁺ | Al-Soud 2001 |
| Heparin | Taq polymerase | ≥1 μg/mL | Begins inhibition | Al-Soud 2001 |
| Humic acid | PCR | ~1 ng/μL | Phenolic structures responsible | Sidstedt 2020 |

## Sample Prep Correction Factors

| Method | Recovery | Concentration | Inhibitor removal | Total correction vs buffer | Source |
|--------|----------|--------------|-------------------|--------------------------|--------|
| Buffer (baseline) | 100% | 1× | 100% | 1× | — |
| Direct lysis - saliva | ~70% | ~0.5× | ~50% | ~6× | Various |
| Direct lysis - NP swab | ~70% | ~0.5× | ~20% | ~14× | Various |
| Magnetic bead (chip) | ~60% | ~1.7× | ~90% | ~1.3× | Cepheid design |
| Filter paper (DBS) | ~20% | ~0.3× | ~80% | ~60× | Hagström 2022 |
| Direct lysis - whole blood | — | — | — | Not feasible | Sidstedt 2018 |

## Commercial Product LOD

| Product | Amplification | Sample prep | Label LOD | Verified LOD | TAT | Device cost |
|---------|--------------|-------------|-----------|--------------|-----|-------------|
| Cepheid Xpert Xpress | RT-PCR | US + magnetic bead | 250 cp/mL | 100-400 cp/mL | 45 min | ~$50K |
| Roche cobas Liat | RT-PCR | Direct lysis | 180 cp/mL | 200-500 cp/mL | 20 min | ~$25K |
| Abbott ID NOW | Nicking isothermal | Heat lysis + filter | 125 GE/mL | 500-20K cp/mL | 13 min | ~$3K |
| Lucira Check-It | RT-LAMP | Direct lysis | 900 cp/mL | — | 30 min | ~$50 disposable |
| Visby Medical | RT-PCR | Filter capture | — | ~2,000 cp/mL | 30 min | ~$45 disposable |
| Mesa Accula | RT-PCR | Direct lysis | — | ~10,000 cp/mL | 30 min | ~$300 |

Source: Smithgall 2020 J Clin Microbiol, Basu 2020, Zhen 2020 J Clin Virol

## Academic-to-Product LOD Gap Factors

| Factor | Range | Source |
|--------|-------|--------|
| Sample preparation | 1.3-50× | Section 2 analysis |
| Batch consistency margin | 2-5× | Bisseling 2024 |
| Fixed threshold vs ROC-optimal | 2-3× | Standard practice |
| Storage stability | 1.5-3× | Manufacturer data |
| Operator variability | 1.5-2× | Training studies |
| **Total: direct lysis** | **~224×** | Product of factors |
| **Total: extraction** | **~12×** | Product of factors |

## LAMP Performance

| Metric | Value | Source |
|--------|-------|--------|
| Best LOD (triple-target RT-LAMP) | 22-25 copies/reaction | Li 2024 |
| Typical LOD range | 10²-10³ copies/reaction | Meta-analysis |
| NTC false positive rate | 5-30% | Kim 2023, DOI:10.1016/j.aca.2023.341693 |
| Reaction temperature | 60-65°C | Notomi 2000 |
| Time to plateau | ~30 min | Field standard |
| Reagent cost/run | ~$1-3 | Vendor-estimated |

## RPA Performance

| Metric | Value | Source |
|--------|-------|--------|
| Best LOD (fluorescence) | ~25 copies/reaction | Tan 2024 |
| Best LOD (nested RPA) | ~2 copies/reaction | 2024 report |
| Typical LOD range | 1-50 copies/reaction | Meta-analysis |
| LFA readout LOD | ~50 copies/reaction | Tan 2024 |
| NTC false positive rate | >40% (single), worse in multiplex | Ullah 2024, Johnson 2024 |
| Reaction temperature | 37-42°C | Piepenburg 2006 |
| Time to plateau | 10-20 min | Field standard |

## CRISPR-Dx Performance

| Metric | Value | Source |
|--------|-------|--------|
| Cas12a collateral kcat | ~1,250 s⁻¹ | Chen 2018 Science |
| Cas13a collateral | ~10⁴ probes/min/recognition | Gootenberg 2017 Science |
| Dynamic range | 2-3 orders of magnitude | Gootenberg 2017, Chen 2018 |
| LOD (no preamp) | 10⁶-10⁹ cp/mL | Kaminski 2021 |
| LOD (with RPA preamp) | 1-25 copies/reaction | Tan 2024, Zhou 2025 |
| One-pot compromise | 50-60% of optimal Cas12a activity | Tan 2024 |

## Key Ratios for Reviews

- Academic papers : FDA-approved microfluidic POCT products ≈ 2,500:1
- Thermoplastic mold investment: $10K-$500K
- PDMS-to-thermoplastic transfer: 6-18 months
- TPE injection cycle: 30-60 sec vs PDMS curing: 1-4 hours
