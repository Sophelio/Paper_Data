# Manuscript alignment

**No manuscript source was edited.** This document records where the current
manuscript and the frozen S7 evidence agree, where they disagree, and what the
exact proposed correction is.

| | |
|---|---|
| Manuscript artifact audited | `draft/SIR_paper.pdf`, 64 pp, modified 2026-09-02 10:45 |
| sha256 | `94ccf533b841fe39a0468735eb2dbc31a80cceba70b094bcaa480a4029ea7b70` |
| Re-checked at the semantics pass | **unchanged** — same bytes, same date |
| LaTeX source in this repository | **none found** — the PDF is the only manuscript artifact |
| Sections read | Results §1.1, §1.5; Methods; Supplementary S1–S3, **S7**, S8; Fig. 4 caption |
| Machine-readable | `MANUSCRIPT_ALIGNMENT.json` |

### Two things called "the manuscript"

| | |
|---|---|
| **manuscript artifact audited** | the shipped PDF above. Still carries the flat 8-tuple §1.1 and the retired `q_rec` result. |
| **current manuscript architecture** | the finalized §1.1 semantics — claim-defining core, operational contract, operational epoch, descendant claim branch, defect record and reconciliation. |

The S7 documentation layer now expresses the **current architecture**. The
shipped PDF has not yet been regenerated to match it, so findings §1 and §2 below
stand against the artifact, not against the architecture.

---

## 1. The headline finding

> **The manuscript's `q_rec` result — Fig. 4b, Results §1.5 and Supplementary
> §S7.8 — is the reconstruction branch that this repository's own audit retired
> on 2026-09-02, for target-provenance leakage and for having no skill over a
> trivial baseline.**

The retirement is recorded in the repository, not inferred here:

- `DIIID_example/fig6data/RETIREMENT_RECORD.json` —
  `D3D-FIG6-QREC-RETIREMENT-V1`, status `RETIRED_FOR_PROVENANCE_LEAKAGE`
- `DIIID_example/Figure6_qualification_audit/FIGURE6_QUALIFICATION_AUDIT_REPORT.md`
- `S7/_legacy_reference/LEGACY_QREC_STATUS.md` — S7's own firewall against it

The two grounds, quoted from the retirement record:

1. **Target-provenance leakage.** 6 of 10 `REL10` and 4 of 10 `RAW10` features
   carry upstream `I_p` dependence. `q95` is essentially `shape·a²B_t/I_p` in
   this archive — median |corr| with `1/I_p` of **0.945**, only **7.3 %**
   relative scatter remaining after removing `I_p` algebraically, and `I_p`
   recoverable from `a²B_t/q95` at median **R² = 0.79**. `betan = β_t·a·B_t/I_p`
   contains `I_p` explicitly. Both the relational representation *and its
   comparator* are contaminated, so "REL10 beats RAW10 on 46 of 55" compares two
   leaking representations.
2. **No demonstrated skill.** A constant persistence predictor reaches median
   normalized RMSE **0.0685** on the protected final 20 %, beating REL141
   (0.1137), REL10 (0.1257) and RAW10 (0.1821). The protected window carries a
   median of **0.32 %** of the calibration-segment variance.

The S7 directory is the corrective rebuild that the retirement record demanded,
and it satisfies every one of its five stated requirements (see §4).

**Consequence.** Every `q_rec` number and claim in Results §1.5, Fig. 4b and
Supplementary §S7.8 must be replaced. This is not a wording fix.

## 2. The architecture in §1.1 predates the S7 vocabulary

The shipped §1.1 defines a single flat contract

```
K_q = (q, I_q, P_q, B_q, H_q, U_q, V_q, Ω_q)
```

with **no** claim-defining core, **no** operational contract, **no** operational
epoch, and **no** defect/reconciliation machinery. A recursive search of the
extracted manuscript text finds **zero** occurrences of: *claim-defining*,
*operational contract*, *operational epoch*, *defect record*, *reconciliation*,
*earliest invalidated*, *j_min*, *range support*, *cross-fitted*, *Epoch*.

§1.1 also still carries the superseded blanket rule:

> "data reserved for final validation must not influence the revised ontology or
> search policy"

Under the current architecture this is too broad. A change to operational
machinery after protected evaluation may define a **new operational epoch within
the same claim branch**, provided the claim-defining core is unchanged; and where the
evidentiary commitment itself must narrow, the result is a provenance-linked
**descendant claim branch under the same task**, not a forbidden move and not a
new `q`. The S7 `q_rec` lineage contains both dispositions in sequence — S7.K2 is
the epoch advance, S7.E2.0 the descendant branch — and under the shipped §1.1
neither could be described at all.

## 3. Statement-by-statement

Legend — `SUPPORTED_CURRENT` · `WORDING` (supported, wording needs update) ·
`STALE_SUPERSEDED` · `NUM_INCONSISTENT` · `SEM_INCONSISTENT` · `UNVERIFIED` ·
`MISSING`

### Results §1.1 — architecture

The four entries below are stated against the **shipped PDF**. S7's own
documentation already uses the current architecture; see
`SIR_ARCHITECTURE_MAP.md` and `ARCHITECTURE_SEMANTICS_AUDIT.md`.

| # | Manuscript statement | Class | Proposed correction |
|---|---|---|---|
| 1.1-a | `K_q = (q, I_q, P_q, B_q, H_q, U_q, V_q, Ω_q)` as one flat tuple | `SEM_INCONSISTENT` | Split into `K_q^(e) = (K_q^claim, K_q^op,(e))` with `K^claim = (q, I_q, U_q, V_q, Ω_q)` and `K^op,(e) = (P_q, B_q, H_q)`. |
| 1.1-b | "data reserved for final validation must not influence the revised ontology or search policy" | `SEM_INCONSISTENT` | Replace with the protected-evidence rule: inspected evaluation evidence becomes development evidence for the revised epoch, and a later qualification must use new protected evidence, a valid cross-fitted design, or an explicitly narrowed claim. |
| 1.1-c | `Σ_q = SearchPolicy(G_q, K_q)`, ontology ≠ universe ≠ frontier ≠ policy | `SUPPORTED_CURRENT` | None. S7 instantiates the distinction exactly: `G_q` (S7.5H) ≠ `A_q` 10,778 (S7.6R) ≠ `Â_q` 162,845 (S7.7R) ≠ `Σ_q`. |
| 1.1-d | "A construction absent from `Â_q` has not thereby been shown inadmissible, inferior or nonexistent" | `SUPPORTED_CURRENT` | None. S7.9 records `global_optimality_claim = false` and `unsearched_status = ADMISSIBLE_UNSEARCHED`. |
| 1.1-e | no audit/reconciliation machinery (`δ`, `ρ`, `j_min`) | `MISSING` | Add. S7.R1 is the concrete instance: `earliest_invalidated_stage = NONE_OF_THE_INSTANTIATED_OBJECTS`, `K_REC_REVISION_REQUIRED = true`, minimal component `P_rec`. |
| 1.1-f | no task / claim-branch / operational-epoch hierarchy | `MISSING` | Add. Without it the `q_rec` lineage cannot be stated: S7 has one task and two claim branches (`QREC-B1` with two operational epochs, `QREC-B2` with one). Note that a contract *version* change is not automatically an *epoch* advance. |
| 1.1-g | no descendant-claim-branch disposition | `MISSING` | Add. It is what the Epoch-1 → Epoch-2 transition actually is: a material narrowing of `V_q` after protected evidence was spent, producing a descendant branch under an unchanged `q`. |
| 1.1-h | `I_q` and `V_q` not clearly separated, and evidence roles are treated as global per datum | `SEM_INCONSISTENT` | Separate them: `I_q` = what information is epistemically admissible; `V_q` = what evidentiary role it may play. Roles are variable- and transition-specific — S7's predictor-side applicability versus target-side discovery is the worked example. |

### Results §1.5 and Fig. 4 — `q_desc`

| # | Manuscript statement | Class | Note |
|---|---|---|---|
| desc-1 | 62 discharges, eight quantities `{W_dia, P_NBI, n_e, I_p, β_N, q95, ℓ_i, κ}` | `SUPPORTED_CURRENT` | Verified. |
| desc-2 | seven-coordinate support `{D_κW_dia, D_βN W_dia, D_βN κ, D_βN ℓ_i, q95/κ, β̇_N, κ̇}` | `SUPPORTED_CURRENT` | Verified against `d3d_discharge_coefficients.csv`. |
| desc-3 | pooled RMSE `5.76 × 10⁻²` with discharge-specific coefficients | `SUPPORTED_CURRENT` | Recomputed **0.05758467247445299** from the 62 per-discharge MSEs against the frozen 0.05758467247445343 (float summation order). 1,000 samples per discharge, 62,000 total. |
| desc-4 | cohort-mean coefficients `(0.248, 1.075, −1.070, −0.0150, −0.0106, 0.0509, 0.893)` summarize, not define | `SUPPORTED_CURRENT` | Recomputed `(0.2480, 1.0755, −1.0705, −0.0150, −0.0106, 0.0509, 0.8928)`; mean intercept −5.8 × 10⁻¹⁹. Applying the mean vector gives 0.4125238316. |
| desc-5 | target-containing implicit closure, not an independent predictor | `SUPPORTED_CURRENT` | Verdict `D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED`; explicit-closure pooled RMSE 187.23, median amplification 33.7. |
| desc-6 | S7.7 mixed identifiability: 5 resolved, 2 uncertainty-dominated, 2 robust directions of 5 positive | `SUPPORTED_CURRENT` | Verdict `D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`; rank-6 removal gives 0.7993 median relative coefficient change and 0.03103 median absolute RMSE change. REML primary with ML sensitivity; the original label was inaccurate and is corrected. |
| desc-7 | aligned / spline / RTS variants "should remain provisional until tied to the frozen manifest" | `UNVERIFIED` | Still correct as written. The spline and RTS variants are **not** tied to a frozen run manifest in either tree. Keep the provisional wording or drop the variants. |
| desc-8 | "The canonical analysis does not use a fixed 20 ms grid" | `SUPPORTED_CURRENT` | Confirmed; 1,000 aligned samples per discharge. |

### Results §1.5, Fig. 4b and Supplementary §S7.8 — `q_rec`

| # | Manuscript statement | Class | Proposed correction |
|---|---|---|---|
| rec-1 | "the designated target was `I_p`" | `STALE_SUPERSEDED` | The canonical `q_rec` target is **`density`** (line-averaged electron density). |
| rec-2 | "the resulting explored frontier contained 141 relational coordinates" | `STALE_SUPERSEDED` | Canonical: admissible universe **10,778** atoms; Epoch-1 explored frontier **162,845** supports; Epoch-2 qualified basis **3,451** atoms. |
| rec-3 | "seven development discharges … then frozen before evaluation on 55 external discharges" | `STALE_SUPERSEDED` | Epoch 1 used **20 development / 42 external**. Epoch 2 uses **six discharge-grouped folds over all 62**. |
| rec-4 | "pooled RMSE 0.126 REL10, 0.114 REL141, 0.182 RAW10" | `STALE_SUPERSEDED` | Retired: leaking, and beaten by persistence (0.0685). Replace with the Epoch-2 table in §5. |
| rec-5 | "lower error on 46 of 55 external discharges" | `STALE_SUPERSEDED` | Retired. Replace with **32 wins / 5 ties / 25 losses against persistence** across 62 out-of-fold discharges. |
| rec-6 | "effective degrees of freedom decreased from ≈99 to 10.6" | `UNVERIFIED` | Never reproduced from primary artifacts, and belongs to the retired branch. Remove. |
| rec-7 | "Compact Representation With External Structural Transfer" (Fig. 4b title) | `STALE_SUPERSEDED` | The frozen S7.10 verdict for the corrected branch is `NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`. The Epoch-2 claim is **target-cross-fitted reconstruction over a predictor-qualified finite object**, explicitly *not* external validation. |
| rec-8 | "the utility of that coordinate system survives structural transfer to discharges excluded from support selection" | `STALE_SUPERSEDED` | Replace with the Epoch-2 statement in §5, with both qualifications attached. |
| rec-9 | "93 % Nominal Reduction · Support Selected on 7 Development Discharges" (Fig. 4b) | `STALE_SUPERSEDED` | Remove. |
| rec-10 | §S7.8 `I_p ∉ C_rec, Desc(I_p) ∩ C_rec = ∅` "applied before structural search" | `SEM_INCONSISTENT` | The principle is right and is retained; in the archive it was **not achieved** for `I_p`, which is why the branch was retired. For `density` it *is* achieved: 17 of 95 quantities excluded, including all 15 EFIT quantities under a fail-closed unresolved-ancestry rule. |
| rec-11 | the whole Epoch-1 → Epoch-2 arc | `MISSING` | Add. It is the strongest methodological content the DIII-D example produces. |

### Methods, S1, S3

| # | Statement | Class | Proposed correction |
|---|---|---|---|
| m-1 | Methods DIII-D paragraphs referring to `I_p` reconstruction and structural-transfer diagnostics | `STALE_SUPERSEDED` | Retarget to `density` and to the cross-fitted design. |
| m-2 | Any statement that all post-evaluation operational change constitutes a new scientific branch | `SEM_INCONSISTENT` | Replace with the operational-epoch rule. Searched: the blanket form appears in §1.1 (1.1-b); S1/S3 carry no stronger form. |
| m-3 | S8 provenance-preserving ontology refinement | `WORDING` | Compatible, but frame refinement as advancing an **operational epoch**, and cite S7.K2 as the worked example. |

## 4. What S7 did that the retirement record required

The retirement record listed five prerequisites for any future `q_rec` claim.
All five are met, and each is independently verified:

| Required | Where met | Verified |
|---|---|---|
| rebuild the candidate universe from target-independent primitives only | S7.3V2 — 78 of 95 admitted; 15 EFIT quantities excluded fail-closed on unresolved ancestry | ✅ `audit_s7.py numbers/boundary` |
| rerun development-cohort support selection and freeze it | S7.9 — frozen before any external access, firewall intact | ✅ `freeze/S7.9` 45/45 |
| rerun all external discharges | S7.10 — 42 external discharges, all evaluated | ✅ recomputed |
| report skill against a persistence baseline, not normalized RMSE alone | B1 persistence is a **mandatory gate** (V3 requires `Δ₁ ≤ −0.01`) | ✅ V3 is the binding gate in both epochs |
| confirm the evaluation-window variance issue with the exact frozen protocol | block-local geometry with calibration-only scale; `INVALID_FOR_NORMALIZED_SCORING` on zero scale, no epsilon | ✅ `numbers/K2_policy` |

And the corrected branch produced an honest negative first (S7.10 `V3 FAIL`),
which is itself evidence the rebuild was not steered.

## 5. Replacement text for the `q_rec` result

Drop-in replacements are held in
`S7_12_qualified_result/S7_12_MANUSCRIPT_SUMMARY.md` — a ≈150-word main-text
paragraph and a ≈400-word supplement handoff. The numbers they must carry:

| quantity | value |
|---|---|
| target | `density` (line-averaged electron density) |
| object | 62 discharges, 78 admissible predictors |
| admissible universe / qualified basis | 10,778 atoms / **3,451** at τ = 1 |
| design | six discharge-grouped folds, target cross-fitted |
| `Δ₀` vs calibration mean | **−0.764489** |
| `Δ₁` vs persistence | **−0.027308** |
| REL mean / median / p90 / max | 0.1891 / 0.1515 / 0.2959 / **0.9199** |
| vs raw ridge (78) / raw HistGB (78) / hardened ridge (70) | −0.0960 / −0.1573 / −0.0951 |
| record vs persistence | 32 W / 5 T / 25 L |
| era | earlier n=35 **+0.0076** practical tie; later n=27 **−0.0726** material |
| V3 / V6 / V-RANGE | PASS / PASS_WITH_QUALIFICATION / PASS (2,232 checks, 0 failures) |
| tiers | `FORMAL_PASS` **and** `CLEAN_DEMO_NOT_MET` |
| supports | six, all size 12, none identical, mean Jaccard 0.285 |

Figure 4b should be rebuilt from `figures/fig_s7_epoch_tail.png`,
`fig_s7_baselines.png` and `fig_s7_iterative_arc.png`; see
`S7_12_qualified_result/FIGURE_6_HANDOFF.json`.

## 6. One briefing-note discrepancy

An audit-briefing checkpoint expected "about 41 % of samples with |A| < 10⁻⁴" in
the implicit-elimination analysis. The frozen artifact
(`Implicit_elimination_and_denominator_conditioning/outputs/eliminated_A_summary.json`)
gives `frac_abs_lt["0.0001"] = 0.002355`, i.e. **0.24 %**. The only 0.41 in that
package is `0.4125238316`, the cohort-mean-vector pooled RMSE. The frozen values
that *are* confirmed: min |A| = **2.643 × 10⁻⁷**, shift values
**14.643 – 24.243**, elimination identity max error **7.90 × 10⁻¹⁵**. The
manuscript does not state a 41 % figure, so no manuscript text is affected.

## 7. Terminology to normalize

Use: scientific object · task-admissible record · task-conditioned mathematical
interpretation · relational ontology · admissible coordinate–relation universe ·
search policy · explored frontier · qualified representation · claim-defining
core · operational contract · operational epoch · defect record ·
reconciliation · earliest invalidated stage · observational range support ·
target cross-fitting · representative full-object descriptive realization ·
qualified ambiguity.

Avoid: "ontology" for a feature library · "validation" for development evidence ·
"prediction" for `q_rec` · "zero-shot" for finite-object cross-fitting ·
"physical constants" for `q_desc` coefficients · "canonical" for the E2.2
support · "not found" as "does not exist".
