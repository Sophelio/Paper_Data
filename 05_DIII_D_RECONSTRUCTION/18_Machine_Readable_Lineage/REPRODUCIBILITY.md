# Reproducing and checking S7

Everything below runs offline, from this directory, against the frozen
artifacts. No network, no credentials, no external service.

---

## 1. The one command

```bash
cd D:\SIR_paper\DIIID_example\S7
python audit_s7.py
```

Exit code `0` if no `BLOCKER` or `MAJOR` check fails, `1` otherwise. Writes
`AUDIT_CHECKS.json`. Takes about a minute, most of it hashing.

It verifies: the package structure; **every** artifact hash in **every**
canonical stage freeze; the S7.1 named hashes under both hashing conventions;
the object, boundary, universe and frontier counts; the range-support policy
invariants; the qualified basis and its hash across three stages; the fold
assignment, recomputed from the declared rule; the Epoch-2 primary metrics, era
split, V-RANGE counts and support statistics, recomputed from the per-discharge
table; the fold support hashes; the `q_desc` pooled RMSE by reference; branch
closure; the stage dependency graph; machine-authorship language; retired-claim
language; every link in every generated page; and figure provenance.

## 2. Environment

The frozen artifacts were produced under, and the checks reproduce under:

| | |
|---|---|
| Python | 3.13.5 |
| numpy | 2.5.2 |
| pandas | 3.0.5 |
| scikit-learn | 1.9.0 |
| matplotlib | 3.11.1 (figures only) |
| platform | Windows-11-10.0.26200-SP0 |

On this machine that is the virtual environment at
`D:\SIR_paper\.venv_lorenz_benchmark` (base interpreter
`C:\Users\micho\anaconda3\python.exe`). The base interpreter's own
`site-packages` carry **numpy 2.1.3 / pandas 2.2.3 / sklearn 1.6.1**, which do
**not** match the freeze records — check with:

```bash
python -c "import numpy,pandas,sklearn;print(numpy.__version__,pandas.__version__,sklearn.__version__)"
# expect: 2.5.2 3.0.5 1.9.0
```

Every stage freeze records the environment it ran under, under `environment`.

## 3. Input data

The 62-discharge archive is at `DIIID_example/data/resampled_data_v6/`, read
through `DIIID_example/diiid_sir_data_provider.py`. It is outside S7 and is not
duplicated here. `S7.1` records its inventory and hashes;
`_audit/PHASE_A_INVENTORY.json` records every external path S7 references.

## 4. Independent recomputations

These do not read S7's own analysis code — they re-derive results from the
frozen policy statements and raw data, then compare.

```bash
# Re-implement the observational range-support predicate from the frozen
# policy equation and reproduce the whole tau grid.  (~2 min)
python _audit/verify_range_support.py out.json

# Adversarial target-ancestry test on all 78 admitted predictors, using the
# same instrument that retired the previous I_p branch.  (~3 min)
python _audit/verify_target_ancestry.py table.csv summary.json
```

Expected, and archived in `_audit/`:

| | |
|---|---|
| survivors at τ = 0, .25, .5, **1**, 2, 5, 10 | 9, 1026, 2099, **3451**, 5957, 8722, 9559 |
| constructor counts at τ = 1 | C0 51 · C1 18 · C2 1488 · C3 382 · C5 8 · C6 965 · C7 539 |
| degenerate cells | 263 of 2,004,708 |
| `prmtan_neped` residual scatter | 0.535 (retired `q95`/`I_p` was 0.073) |
| predictors with median R² ≥ 0.75 | 2 of 78 |

τ = 0 differs from the frozen table by exactly 3 cells of 2,004,708 — a
floating-point tie at the strict-interpolation boundary, at a threshold that is
not the frozen one. See `AUDIT_REPORT.md` F-5.

## 5. Regenerating the package

Presentation and indexing only. None of these touch a frozen artifact.

```bash
python _audit/build_s7_package.py     # 21 stage MANIFEST.json + index.html, CANONICAL_INDEX.json
python _audit/build_matrices.py       # INFORMATION_FLOW_AUDIT.json, CLAIM_EVIDENCE_MATRIX.json
python _audit/build_alignment_json.py # MANUSCRIPT_ALIGNMENT.json
python _audit/build_findings.py       # AUDIT_REPORT.json
python figures/make_s7_figures.py     # 5 figures, PNG + SVG, + FIGURE_PROVENANCE.json
python audit_s7.py                    # verify the result
```

Figures are deterministic: no sampling, no seeds, no fitting.

## 6. Re-running the science

**Not required for verification, and not recommended casually.** Every derived
number recomputes from the frozen artifacts, which is what `audit_s7.py` does.
Re-running discovery during an audit is itself a risk.

If you must, each stage carries its own scripts and reproduces in order:

```bash
python E2_1_crossfitted_discovery_and_qualification/scripts/e2_1_a_verify.py
python E2_1_crossfitted_discovery_and_qualification/scripts/e2_1_b_run.py
python E2_1_crossfitted_discovery_and_qualification/scripts/e2_1_c_aggregate.py

python E2_2_full_object_descriptive_representation/scripts/e2_2_a_verify.py
python E2_2_full_object_descriptive_representation/scripts/e2_2_b_search.py
python E2_2_full_object_descriptive_representation/scripts/e2_2_c_freeze.py

python S7_12_qualified_result/scripts/s7_12_assemble.py
```

Epoch-2 discovery takes roughly 12 minutes for the six folds and 2 minutes for
the descriptive search.

**These scripts rewrite their stage's freeze with a new timestamp.** That is
expected and does not indicate a defect, but it changes the freeze file's own
hash. If you re-run, re-run the stage's freeze step afterwards and note it.

### Determinism

| element | status |
|---|---|
| coordinate universe, strata, shortlist | deterministic |
| search (one seed per stratum, lockstep greedy) | **deterministic**, not merely seeded |
| fold assignment | deterministic; no seed at all |
| `U_rec` Rank-5 discharge bootstrap | seeded — `2026090501`, 1,000 replicates |
| baseline B3 | seeded — `HistGradientBoostingRegressor(random_state=2026090502)` |
| tie-breaking | lexicographic on support id |

Bit-identical reproduction requires the environment in §2. Different BLAS or
numpy versions can move the last digits of an SVD or a least-squares solve, and
because `U_rec` Rank 1 uses exact-equality comparisons on the fit score, a
sufficiently large numerical difference could in principle change a selected
support. That is a property of the procedure and is stated rather than hidden.

## 7. Checking a specific claim

`CLAIM_EVIDENCE_MATRIX.json` maps each of 11 claims to its stage, script, data
artifact, result artifact, value, validation status and limitations. Start
there, then open the stage's `index.html` or `MANIFEST.json`.

## 8. What verification cannot tell you

- Whether the **q_desc** branch reproduces — its artifacts are outside this
  directory (`AUDIT_REPORT.md` F-3). `audit_s7.py` checks its headline pooled
  RMSE by reference and reports `DOCUMENTATION` if the tree is unreachable.
- Whether the manuscript matches — see `MANUSCRIPT_ALIGNMENT.md`. It does not,
  on the `q_rec` result.
- Whether a better representation exists outside the explored frontier. It may.
  `global_optimality_claim = false`, and the unsearched region is recorded as
  `ADMISSIBLE_UNSEARCHED`.
