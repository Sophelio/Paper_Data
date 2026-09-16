# S7 forensic audit report

Adversarial, reproducibility-grade audit of the complete S7 DIII-D workflow,
conducted read-only before any change was made to the tree.

**Verdict — `S7_AUDIT_PASS_WITH_QUALIFICATIONS`.**

The S7 scientific workflow is sound, internally consistent and independently
reproducible. Every canonical numerical checkpoint was recomputed and matched.
No leakage, no post hoc tuning, no unsupported claim, and no broken hash was
found inside S7.

The qualifications are **not about S7**. They are about the manuscript, which
still presents a `q_rec` result that this repository itself retired, and an
architecture section that predates the vocabulary S7 needs.

Machine-readable: `AUDIT_REPORT.json` (this narrative), plus the re-runnable
checker `audit_s7.py` which writes its own machine-readable report.

---

## 1. Findings

| # | Level | Finding | Where |
|---|---|---|---|
| F-1 | **MAJOR** | The manuscript's `q_rec` result (Results §1.5, Fig. 4b, Supplementary §S7.8) is the branch retired on 2026-09-02 for target-provenance leakage and for having no skill over persistence. | manuscript, **not S7** |
| F-2 | **MAJOR** | Results §1.1 carries the flat 8-tuple contract with no claim-core / operational-epoch split and no defect–reconciliation machinery; the entire S7 `q_rec` arc is inexpressible in it. It also retains the superseded blanket rule that validation data must never influence a revised ontology. | manuscript, **not S7** |
| F-3 | MINOR | `q_desc` canonical artifacts are outside S7, so `q_desc` cannot be audited from this folder alone. | package scope |
| F-4 | MINOR | Three PDF figures declared in the external `Correction_audit` manifest are missing (PNG and SVG present). | external tree |
| F-5 | MINOR | At τ = 0 only, an independent re-implementation of the range-support predicate differs from the frozen sensitivity table by exactly **3 cells of 2,004,708** (1.5 × 10⁻⁶) — a floating-point tie at the strict-interpolation boundary. τ = 0 is not the frozen threshold; the atom count still matches exactly (9), and τ = 1 agrees exactly. | S7.K2 |
| F-6 | MINOR | Four frozen documents state "no support beat persistence by more than 0.0287"; the exact best margin in the Epoch-1 family is **−0.028742**, which exceeds that bound by 4 × 10⁻⁵. **Recorded as an erratum, not applied** — those files are inside stage freeze manifests, and editing them would break byte-for-byte reproduction for a rounding artifact that changes no conclusion. | S7.11-derived prose |
| F-7 | DOCUMENTATION | S7.1's freeze uses named per-artifact hashes, two of which are canonical **DataFrame-content** hashes rather than file-byte hashes. All nine reproduce; the convention is simply heterogeneous. | S7.1 |
| F-8 | DOCUMENTATION | The `prmtan_neped` ablation evidence sits in S7.11 (Epoch 1); a reader of E2.1/E2.2 alone, where the coordinate appears in all six supports, would not find it. | cross-reference |
| F-9 | DOCUMENTATION | A briefing checkpoint expecting "~41 % of samples with \|A\| < 10⁻⁴" is unsupported; the frozen value is **0.24 %**. `0.4125238316` is the cohort-mean-vector RMSE. | briefing, not manuscript |
| F-10 | COSMETIC | `_logs/` is empty. | S7 |

**No `BLOCKER`. No `MAJOR` finding inside S7.** F-3 through F-10 are addressed
by this package; F-1 and F-2 require manuscript edits, which this audit did not
make.

### Errata recorded rather than applied

F-6 is a rounding imprecision in prose that lives inside four **frozen** stage
documents. Correcting the text would change their bytes and break the
reproduction property that every one of the 527 artifact hashes currently
carries. The audit's judgement is that a verifiable freeze is worth more than a
corrected fifth decimal, so the exact value is recorded here and in
`AUDIT_REPORT.json`, and the frozen text is left alone. Any future edition of
those documents should use **−0.028742**, or say "by more than 0.0288".

## 2. What was independently verified

Not re-read from the freezes — **recomputed** and compared.

### Integrity

| check | result |
|---|---|
| every canonical stage freeze | **527 / 527** artifacts reproduce byte-for-byte, across 21 stages |
| S7.1 named hashes | **9 / 9** (7 file-byte, 2 DataFrame-content) |
| fold support hashes | all six `support_id` strings hash to their recorded sha256 |
| qualified basis hash | identical across E2.0A, E2.1 and E2.2 |
| duplicate content | 3 groups, all benign and explanatory — notably `_e2_1_basis.npz` is **byte-identical** to `_e2_2_basis.npz`, so E2.2's independent recomputation of the range-support matrix reproduced E2.1's exactly |

### The contract

The range-support predicate was **re-implemented from the frozen policy equation
alone** and run over all 10,778 atoms × 186 discharge–block cells:

| τ | recomputed survivors | frozen | cell rate |
|---|---|---|---|
| 0.00 | 9 | 9 | ✔ (3 cells of 2,004,708 differ, see F-5) |
| 0.25 | 1,026 | 1,026 | exact |
| 0.50 | 2,099 | 2,099 | exact |
| **1.00** | **3,451** | **3,451** | **exact** |
| 2.00 | 5,957 | 5,957 | exact |
| 5.00 | 8,722 | 8,722 | exact |
| 10.00 | 9,559 | 9,559 | exact |

Constructor counts at τ = 1 exact (C0 51, C1 18, C2 1,488, C3 382, C5 8,
C6 965, C7 539). Degenerate cells **263 of 2,004,708**, exact. `epsilon = null`
and `epsilon_substituted = false` confirmed — the degenerate case is an explicit
status, not a numerical patch. The survivor curve is smooth and monotone, so
τ = 1 does not sit on a cliff.

### Epoch 1

Recomputed from `external_discharge_metrics.csv`: all seven method means and
medians match to 10⁻¹²; `Δ₀ = −0.180095027`, `Δ₁ = +0.532090562`, **V3 FAIL**;
187019 = 11.952633, 187022 = 11.766572; 2 discharges above 1.0.

S7.11 family: 217 supports, 213 full-domain, **70** V3-style passers (0.328638),
`C_dev_star` ranked **184 / 213**, `PROD(gasa,gasa)` in **0 of 70** passers and
**67 of 143** failures. Best margin in the family **−0.028742**.

`C_dev_star` matches the expected 12 coordinates exactly and in order; universe
10,778; explored frontier 162,845.

### Epoch 2

Recomputed from `heldout_discharge_results.csv`: 62 unique out-of-fold
discharges, one per discharge, fold sizes 11/11/10/10/10/10. All seven method
summaries (mean, median, p90, max) and all six paired differences match to
10⁻¹². `Δ₀ = −0.764489`, `Δ₁ = −0.027308`, **V3 PASS**. Era split reproduces
exactly. V-RANGE 2,232 checks / 0 failures, and `12 coords × Σ(held-out cells)`
independently equals 2,232. Zero discharges above NRMSE 1.0.

W/T/L 32/5/25 reproduces under the contract's **own** practical-equivalence floor
0.01 — a principled rule, not an ad hoc tolerance.

Support stability: six supports, all size 12, **none identical**, mean pairwise
Jaccard 0.285244, 35 distinct coordinates, `ID(pcdiamag3)` and
`RATIO(ece21,cerqtit10)` in all six.

Fold assignment **reproduced from the declared rule** for all 62 discharges:
sort by (era, discharge id), `position mod 6`. No seed, one partition generated.

### Epoch 2 descriptive

`C_E2_ALL_DESC` size 12, hash verified; descriptive fit mean 0.177509, max
0.924190 on 187024, 0 above 1.0; identical to **no** fold support, Jaccard
0.143–0.500.

### `q_desc`, by reference

Pooled RMSE recomputed **0.05758467247445299** against the frozen
0.05758467247445343 (float summation order), from 62 discharges × 1,000 samples
with `coefficient_fit_type = per_discharge_calibrated_1_8*`. Cohort-mean
coefficients reproduce the manuscript's Fig. 4a values; mean intercept
−5.8 × 10⁻¹⁹; mean-vector RMSE 0.4125238316.

Correction audit `D3D-SIR-62-COEFFICIENT-CONDITIONING-CORRECTION-V1`: verdict
`D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`; **5** robustly resolved
(κ̇, D_βN W_dia, D_βN κ, β̇_N, D_βN ℓ_i), **2** uncertainty-dominated
(D_κ W_dia, q95/κ); **5** positive eigenvalues → **2** robust directions;
rank-6 removal 0.7993 / 0.03103; `REML_primary_with_ML_sensitivity` with
`random_effects_original_label_accurate = false`. Manifest 74/77 (F-4).

Implicit elimination: `D3D-IMPLICIT-CLOSURE-EXPLICITLY-ILL-CONDITIONED`,
min |A| 2.643 × 10⁻⁷, shift values 14.643–24.243, identity error
7.90 × 10⁻¹⁵, explicit-closure pooled RMSE 187.23.

The retired verdict `D3D-COEFFICIENT-FAMILY-RESOLVED` appears **nowhere** in S7,
and in the external tree only inside the original audit and the correction that
retires it; `STALE_ARTIFACT_RESOLUTION.md` records archival with hashes.

## 3. Leakage audit

Full detail in `INFORMATION_FLOW_AUDIT.md`. **Verdict: no leakage found.**

The decisive test — the same one that retired the previous branch:

| | `q95` vs `I_p` (**retired**) | `prmtan_neped` vs `density` |
|---|---|---|
| median &#124;corr&#124; | 0.945 | 0.892 |
| median R² | 0.79 | 0.796 |
| **residual scatter after removal** | **7.3 %** | **53.5 %** |

`q95` *was* the target algebraically. `prmtan_neped` is not — and the frozen,
predeclared `PRMTAN_NEPED_ONLY` ablation confirms it: that coordinate alone
scores 0.4632 with `Δ₁ = +0.2529` and **fails** V3.

Structurally, S7 excludes all 15 EFIT-derived quantities fail-closed on
unresolved ancestry — exactly the class that contaminated the retired branch —
before any coordinate is constructed.

All nine information-flow checks pass, one with disclosure (check 8:
predictor-side applicability uses the whole finite object, which is the
principal stated limitation of the claim).

## 4. Search reproducibility

| property | status |
|---|---|
| candidate universe | exactly enumerated and hashed |
| duplicate / exact-dependency handling | frozen in `exact_dependency_groups.csv` |
| randomness in search | **none** — one seed per stratum, deterministic lockstep greedy expansion |
| randomness anywhere | only the U_rec Rank-5 discharge bootstrap, seed `2026090501`, 1,000 replicates, and `HistGradientBoostingRegressor(random_state=2026090502)` |
| fold construction | deterministic, reproduced here |
| budget | 765,758 proposals of 1,800,000 in Epoch 2; ≤127,764 per fold against a 300,000 cap |
| tie-breaking | lexicographic on support id, deterministic |

**Deterministic reproducibility**, not merely seed reproducibility, for the
search. The audit did **not** re-run the Epoch-2 searches: the frozen artifacts
are self-consistent, every derived metric recomputes from them, and re-running
discovery during an audit is itself a risk.

The one property that is *not* claimed: **the selected support is not the unique
optimum**. Bootstrap selection frequencies run 0.001–0.121 with 303–443 distinct
winners per fold, and 217 distinct winners in Epoch 1. This is reported as a
finding, not smoothed away.

## 5. Was Epoch 1 → Epoch 2 legitimate?

**Yes**, and for reasons that are checkable rather than rhetorical. Full argument
in `REVISION_LEDGER.md`; the four load-bearing facts:

1. **The alternative explanation was tested and refuted.** S7.R1 rejected the
   operational-state hypothesis using target-blind predictor evidence, which is
   what rules out Case A (incorrect instantiation) and establishes Case B
   (incomplete operational contract).
2. **The K2 operational revision preserved the claim-defining core.**
   At S7.K2, `q`, `I_rec`, `U_rec`, `V_rec` and `Ω_rec` remain unchanged
   as semantic commitments; only `P_rec` gains the range-support clause
   (`revision_class = MINIMAL_P_ONLY`). The later S7.E2.0 transition is
   distinct: `V_rec` is materially narrowed there, constituting descendant
   claim branch QREC-B2.
3. **The rule is generic and was frozen first.** Dimensionless, unit-scale
   invariant, sign-symmetric, constructor-generic, target-blind; no constructor
   family eliminated; τ grid hashed before any survivor count existed.
4. **The evidence budget was reconciled, not reused.** Epoch-1 evaluation
   evidence had informed the revision, so Epoch 2 used a cross-fitted design
   **and** narrowed the claim — two of the three admissible responses, taken
   together — and never describes itself as external validation.

### The `V_q` question, since resolved

This audit recorded the `V_q` question as an unresolved tension and preserved
both defensible readings, because the manuscript architecture had not yet
finalized the task / branch / epoch hierarchy. That was the right disposition at
the time.

A subsequent architecture-semantics hardening pass resolves it. With §1.1
finalized, the cross-fitted narrower qualification is a **Case-C descendant claim
branch under the same task `q_rec`**: `QREC-B1` carries the sealed-external claim
and its preserved failure, and `QREC-B2` — constituted at S7.E2.0, *not* at
S7.K2 — carries the narrowed cross-fitted claim and the final qualified result.
K2 remains a Case-B operational-contract revision inside `QREC-B1`.

Nothing in the scientific verdict, the numbers or the claim boundary changes;
only the vocabulary that describes the transition. See
`ARCHITECTURE_SEMANTICS_AUDIT.md` and the rewritten `REVISION_LEDGER.md`.

## 6. Claim-strength audit

167 markdown files scanned for overstated language. In the result-bearing stages
(S7.9–S7.12, K2, R1, E2.x), **every** match for *virgin/untouched external
validation*, *zero-shot*, *universal*, *canonical equation*, *proves*, *causal*,
*forecast*, *generalizes* occurs inside a disclaimer, an exclusion list, a "✗"
marker, a section heading, or an ordinary word ("evidence mechanism"). **Zero
overstated claims.**

The forbidden causal statement is recorded *as forbidden* alongside the two
permitted formulations, and the permitted ones are used.

## 7. Machine-authorship sanitation

Recursive scan of all 714 files for the full set of vendor, product, model-family and
machine-authorship terms specified in the audit brief — vendor and product names,
model-family terms, and the machine-authorship phrasings the brief lists. The
pattern table is held in `audit_s7.py`, which is tooling rather than a scientific
artifact and is exempt from its own scan, as is the checker's own JSON output.

**0 hits before this audit. 0 hits after.**

Two raw byte matches inside compressed `.npz` archives are coincidental binary
sequences, not text, and are excluded by decoding. Generated `.svg` files carry a
`cc:Agent` element in their Creative Commons RDF metadata naming **Matplotlib
v3.11.1** as the creator — standard scientific-software provenance emitted by the
plotting library, which the audit brief explicitly permits, and not an authorship
attribution. No historical prompt or
transcript artifact exists in S7, so nothing needed relocating and no migration
ledger was required.

## 8. What changed in this directory

Nothing frozen. Every change is category **A** (presentation), **B**
(documentation and provenance clarification) or **C** (reproducibility
hardening). **No category-E scientific correction was required**, and no
canonical result changed.

| added | category | what |
|---|---|---|
| `<stage>/MANIFEST.json` × 21 | B | uniform stage record that **indexes** the existing freeze rather than replacing it |
| `<stage>/index.html` × 21 | A | self-contained stage page with the SIR position strip |
| `index.html`, `README.md` | A | dashboard and entry point |
| `WORKFLOW.md`, `SIR_ARCHITECTURE_MAP.md`, `REVISION_LEDGER.md` | B | dependency graph, architecture mapping, revision classification |
| `INFORMATION_FLOW_AUDIT.md/.json` | B | leakage audit |
| `CLAIM_EVIDENCE_MATRIX.json` | B | 11 claims, each with a reproducible evidence path |
| `MANUSCRIPT_ALIGNMENT.md/.json` | B | 27 classified statements |
| `AUDIT_REPORT.md/.json` | B | this report |
| `REPRODUCIBILITY.md` | C | independent verification instructions |
| `audit_s7.py` | C | re-runnable checker |
| `CANONICAL_INDEX.json` | B | canonical stage map |
| `figures/` (5 figures + provenance + script) | A/C | deterministic figures from frozen artifacts |
| `_audit/` | C | registry, build scripts, independent recomputations, Phase-A inventory |

**Nothing was moved, renamed or deleted**, so no migration ledger exists. The
existing structure was already coherent, every stage already froze its own
artifacts, and §28 of the audit brief prefers minimal restructuring; a
normalization layer was added on top instead.

## 9. Independent-reviewer test

| question | answer |
|---|---|
| Can I determine the scientific object? | Yes — S7.1, 62 discharges, 95 quantities |
| Can I identify `q_desc` and `q_rec` without ambiguity? | Yes; `q_desc` artifacts are **external** and that is stated |
| Can I recover each claim-defining core? | Yes — `SIR_ARCHITECTURE_MAP.md`, `Q_REC_STAR.json` |
| Can I recover each operational contract version? | Yes — `K_REC_PRE`, `K_REC_V2`, changeset, E2.0 → E2.0A |
| Can I identify every contract revision and why? | Yes — `REVISION_LEDGER.md`, 14 rows |
| Can I tell whether protected evidence was reused? | Yes — explicitly, and how it was handled |
| Can I reproduce the important numbers? | Yes — `python audit_s7.py` |
| Can I trace every figure to a script and artifact? | Yes — `figures/FIGURE_PROVENANCE.json` |
| Can I identify superseded results? | Yes — six historical entries in `CANONICAL_INDEX.json` |
| Can I tell which representations are unique? | Yes — none are, prominently |
| Can I distinguish validation from descriptive fit? | Yes — E2.2 carries four explicit negative flags |
| Can I tell what the claim does and does not establish? | Yes — `S7_12_CLAIM_BOUNDARY.md` |
| Can I map every stage to the SIR graph? | Yes — every `MANIFEST.json` |
| Is there an unexplained gap between stages? | No |
| Does any canonical artifact attribute authorship to a machine? | No — 0 hits |
| Does any active document contradict another? | No contradiction found inside S7 |
| Could a skeptic see why Epoch 2 is not post hoc tuning? | Yes — §5, four checkable properties |

The one honest "no": a reviewer **cannot** audit `q_desc` from this folder alone
(F-3).

## 10. Recommendation

**S7 is publication-ready. The manuscript is not, on the `q_rec` result.**

Priority order:

1. **Replace the `q_rec` result** — Results §1.5, Fig. 4b, Supplementary §S7.8.
   It currently reports a retired, leaking branch. Replacement text and numbers
   are ready in `S7_12_qualified_result/S7_12_MANUSCRIPT_SUMMARY.md` and
   `MANUSCRIPT_ALIGNMENT.md` §5.
2. **Update §1.1** to the claim-core / operational-epoch architecture, and
   replace the blanket validation-data rule with the protected-evidence rule.
   Without this, S7's central methodological contribution cannot be stated.
3. **Add the iterative arc** to the Supplement. It is the strongest thing the
   DIII-D example produces — stronger than either accuracy number.
4. Keep the `q_desc` result as written; it verified cleanly.
5. Consider relocating or mirroring the `q_desc` canonical package so both
   branches are auditable from one place (F-3).
