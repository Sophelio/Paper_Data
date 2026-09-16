# S7.E2.2 — full-object descriptive representation: internal audit report

Stage **S7.E2.2** · Freeze `D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1`
Basis `C_E2_FULL_DOMAIN` · Contract `K_REC_V2` · Utility `U_REC_OPERATIONAL_V1`

---

## 1. Verdict

**`FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN`** · 34/34 acceptance checks.

`C_E2_ALL_DESC`, twelve coordinates, `sha256 e7935c35fd30…`, selected by the
unchanged frozen procedure over the whole 62-discharge object. Descriptive only.

## 2. Lineage — eight parents, zero substantive drift

| stage | manifest |
|---|---|
| S7.9 | 45/45 |
| S7.10 | 31/31 |
| S7.11 | 26/26 |
| S7.R1 | 21/21 |
| S7.K2 | 29/29 |
| S7.E2.0 | 22/22 |
| S7.E2.0A | 14/14 |
| **S7.E2.1** | **39/39** |

Every artifact reproduces byte-for-byte. `ZERO_SUBSTANTIVE_DRIFT = true`.

Pinned and verified unchanged: `K_REC_V2` hash · `tau = 1` · `tau_train`
`RETIRED` · E2.0A authoritative and E2.0 preserved · six outer folds over 62
discharges · `U_rec` hash · V3 `Delta_0 <= -0.01 AND Delta_1 <= -0.01` · V6
threshold 0.01 · budget 300 000 · one seed per stratum · shortlist cap 96 ·
support bound [1, 12] · `CLEAN_DEMO` threshold −0.05 ·
`EPOCH2_IS_FINAL_QREC_ATTEMPT = true`.

**E2.1 result re-verified unchanged**: `QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS`,
`FORMAL_PASS`, `CLEAN_DEMO_NOT_MET`, `Delta_0 = -0.764489`,
`Delta_1 = -0.027308`, V3 PASS, V6 `PASS_WITH_QUALIFICATION`, V-RANGE PASS, and
all six fold support hashes present.

## 3. Basis — verified before any target was opened

Recomputed independently from the predictors and `P-RANGE` at `tau = 1`:

**3 451 / 10 778** · C0 51 · C1 18 · C2 1 488 · C3 382 · C5 8 · C6 965 · C7 539.

Hash `1d22aeac2e5f…` matches `E2_0A_CANDIDATE_BASIS.json` **and** the basis E2.1
searched, so E2.2 searched exactly the same coordinate set. `target_reads = 0`
through completion of verification. None of the 7 327 partial-domain atoms was
used; `tau` was not altered; the ontology was not regenerated.

## 4. Search

One fresh full-object search. The search, the utility and the estimator are
**imported from the E2.1 execution modules**, not re-implemented, so the policy
is identical by construction; the only mechanical adaptation is that the
discharge set scored is all 62 rather than a fold's 51–52.

| | |
|---|---|
| proposals | **127 642** of 300 000 |
| distinct supports evaluated | 102 100 |
| strata | 108 |
| shortlist | 461 (cap 96 per constructor) |
| seeds | 108, one per stratum |
| lanes | MAIN + RAW_ONLY |
| second seed | no |
| outcome-triggered extension | no |
| E2.1 supports reused as candidates | no |
| runtime | 120 s |

## 5. Utility

`U_rec` unchanged. Rank 1 admitted 3 212 practically equivalent supports; Rank 2
reduced them to one, leaving Ranks 3–5 non-binding — structurally identical to
all six Epoch-2 folds and to Epoch 1, where Rank 2 was likewise decisive.

FIT 0.177509 (best in frontier 0.170105) · BLOCK_WORST 0.190286 on block A ·
SHOT_P90 0.244117 · size 12, active terms 12 · `COND_MEDIAN` 2.004, P90 2.380,
MAX 2.933 · bootstrap selection frequency **0.009** with **365** distinct
winners · block-omission frequency **0.000**.

The low selection frequency and the zero block-omission frequency are reported
as found. They say the same thing S7.9, S7.11 and E2.1 all said: this object
does not identify a unique support, and the frozen rule picks one member of a
large equivalent family.

Nothing was added to `U_rec` — not fold recurrence, not cross-fitted recurrence,
not E2.1 performance, not manuscript convenience. The size was not forced.

## 6. Target access

`ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION = true`, recorded explicitly
in the access ledger with its justification: the cross-fitted qualification
verdict was already frozen, and no validation claim attaches to E2.2. The
targets are **not** pretended to be held out, and **no new "external"
qualification was computed** — the result record carries no `Delta_0`,
`Delta_1`, V3, V6 or gate table, and the acceptance checks verify their absence.

## 7. Descriptive fit — flagged as in-sample

mean 0.1775 · median 0.1539 · p90 0.2441 · max 0.9242 (187024) · 0 discharges
above 1.0 · earlier 0.1963, later 0.1532.

`IS_NOT_A_VALIDATION_METRIC = true` is carried in the record. The worst
discharge is the same one that is worst in the cross-fitted result (187024,
0.9199), which is a property of that discharge, not of either representation.

## 8. Comparison with the six cross-fitted supports

Performed after the freeze; it could not and did not influence selection.

Shared coordinates 3–8 of 12, Jaccard 0.143–0.500, mean **0.313**, **identical
to none**. Both universal fold coordinates are present; three coordinates
(`PROD(pinj,pinj_30l)`, `RATIO(gasc,cerqtit10)`, `RATIO(gasc,cerqtit11)`) appear
in no fold support.

Constructor composition is consistent with the folds: ratio-dominated (8 of 12
here; 34 of 72 fold slots), no derivative families.

## 9. Qualifications carried

`pcdiamag3` `UNCALIBRATED_SIGNAL` and `prmtan_neped` target-signal-ancestry
independence are carried verbatim from `S7_11_QUALIFICATIONS.json`; `gasc` is
carried as an actuator command voltage from `SIGNAL_UNITS.json`. Each flagged
primitive present in the support has an explicit entry, and an acceptance check
enforces that. No coefficient acquires physical-dimensional meaning here.

## 10. What E2.2 did not do

No gate was evaluated. No threshold was touched. No discharge or block was
dropped. `U_rec` was not modified. The contract, protocol, ontology, information
boundary and folds are untouched. **E2.1's verdict, tiers, gates and metrics are
unchanged**, and the freeze records explicitly that this stage cannot alter
them.

`EPOCH2_IS_FINAL_QREC_ATTEMPT` remains `true`. E2.2 is not a discovery epoch,
not a rescue, not a second validation and not an attempt to improve performance.

## 11. Files

3 Markdown (limit 6) · 4 CSV · 7 JSON · manifests · 3 scripts.

## 12. Recommendation

Use `C_E2_ALL_DESC` for Figure 6 coordinate labels and for a representative
relation display in the supplement, always labelled *representative full-object
descriptive relation*. Report its bootstrap selection frequency (0.009)
alongside it; the honest reading is that it is a legible member of a large
equivalent family, and that is itself one of the example's findings.
