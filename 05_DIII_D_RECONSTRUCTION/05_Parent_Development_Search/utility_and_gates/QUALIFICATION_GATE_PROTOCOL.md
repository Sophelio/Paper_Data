# S7.8 — Qualification gate protocol (`V_rec`)

S7.8 freezes **stage ownership** for the ten qualification gates and records
what can and cannot be evaluated before S7.10. It marks **no external gate
PASS**.

Machine-readable form: `V_REC_OPERATIONAL_V1.json`, `gate_stage_ownership.json`.

---

## Allowed states at S7.8

`PROTOCOL_VERIFIED` · `PENDING_S7.9` · `PENDING_S7.10` · `PENDING_S7.11`

`PASS`, `PASS_WITH_QUALIFICATION`, `FAIL` and `NOT_APPLICABLE` are **forbidden
at this stage**. A gate that requires the sealed external cohort cannot be
resolved by an argument; it can only be resolved by evidence that does not yet
exist.

## Stage ownership

| Gate | Requirement | Mandatory | Stage owner | Status at S7.8 |
|---|---|---|---|---|
| **V1** information boundary | no target leakage; no admitted quantity with unresolved target ancestry | yes | S7.3 established it; final table S7.12 | `PROTOCOL_VERIFIED` |
| **V2** development-only discovery | target, ontology, support, estimator, thresholds chosen without external outcomes | yes | S7.9 freeze | `PENDING_S7.9` |
| **V3** nontrivial skill vs B0/B1 | `Δ₀ ≤ −0.01` **and** `Δ₁ ≤ −0.01` | yes | S7.10 | `PENDING_S7.10` |
| **V4** fair raw comparison vs B2/B3 | fair comparison on identical information and geometry | yes | S7.10 | `PENDING_S7.10` |
| **V5** external structural transfer | support frozen and hashed before any external evaluation | yes | S7.10, on the S7.9 freeze | `PENDING_S7.10` |
| **V6** processing-era robustness | reported separately for **24 earlier / 18 later** external discharges | yes | S7.10 | `PENDING_S7.10` |
| **V7** common support | comparisons use identical scored samples | yes | protocol S7.8, empirical S7.10 | `PROTOCOL_VERIFIED` |
| **V8** discharge-level inference | discharge, not time sample, is the independent unit | yes | protocol frozen S7.8 | `PROTOCOL_VERIFIED` |
| **V9** sensitivity | no result depends catastrophically on one discharge, block or realization | **no** | S7.11 | `PENDING_S7.11` |
| **V10** numerical provenance | no claim rests on interpolation-created resolution without qualification | yes | lineage auditable S7.8 | `PROTOCOL_VERIFIED` |

**Mandatory gates:** V1, V2, V3, V4, V5, V6, V7, V8, V10.
**Non-mandatory:** V9.

> **If a mandatory gate fails, `Q_rec` may not be presented as a successful
> structural-transfer result.**

Evaluable before S7.10: V1, V2, V7, V8, V10.
Not evaluable before S7.10: V3, V4, V5, V6. Not before S7.11: V9.

## Why V8 is already `PROTOCOL_VERIFIED`

Every quantity frozen in S7.8 aggregates to the **discharge** before any
standard error is taken. `SE_delta` uses `n = 20` discharges with `ddof = 1`;
the Rank-5 bootstrap resamples **discharges**, never time samples; `SHOT_P90` is
a percentile over 20 discharge-level values. Sample-level inference would
overstate precision by orders of magnitude, and no S7.8 rule permits it.

## Why V7 is `PROTOCOL_VERIFIED` but not resolved

The protocol requirement — identical scored samples across the representation
and all four baselines — is frozen and inherited unchanged. The empirical check
belongs with the comparison itself, at S7.10.

## V3 — the decidable form

The V1 wording "beats B0 and B1 in the predeclared aggregate sense" was **not
decidable**; `aggregate` was never defined. S7.2C clause **C-06** supplied it:

```
NRMSE_method,s = mean over blocks A,B,C of NRMSE_method,s,b
Delta_j        = mean over EXTERNAL discharges of ( NRMSE_REL,s - NRMSE_Bj,s )
PASS  iff  Delta_0 <= -0.01  AND  Delta_1 <= -0.01
```

Confidence intervals are **reported, not used as a significance threshold** for
V3. V3 requires actual skill — it is the gate the retired `q_rec` failed.

## V4 — fairness, not victory

V4 passes if the comparison was conducted properly, **whatever the outcome**.
V4 does **not** require beating B2 or B3. Identical calibration intervals,
identical protected samples and identical estimator discipline are granted to
every comparator; if ridge penalty selection is granted to the relational model
it is granted equally to B2.

## V6 — corrected external counts

| | earlier | later | total |
|---|---|---|---|
| **external cohort — authoritative** | **24** | **18** | **42** |
| parent object — reference only | 35 | 27 | 62 |

The V1 wording "35 earlier / 27 later" is
**`SUPERSEDED_FOR_V6_BY_S7.2C_C07`**. Those are *parent-object* counts; the gate
operates on the *external cohort*. The superseded counts still appear verbatim
in `S7_2_..._V1` documents and in `STATISTICAL_INFERENCE_PLAN.md` item 10; those
occurrences are historical record and must not be repeated as current.

Outcomes: `PASS` · `PASS_WITH_QUALIFICATION` · `FAIL_FOR_FULL_DOMAIN`. A
`FAIL_FOR_FULL_DOMAIN` does not erase the result — it narrows `Omega_rec`
rather than averaging across the processing discontinuity.

## Baselines — defined, not run

`B0` calibration mean · `B1` persistence · `B1A_AR1` diagnostic · `B2` raw ridge
· `B3` `HistGradientBoostingRegressor` · `H0_RAW_HARDENED` diagnostic.

**None has been run.** S7.9 freezes the complete instantiated configurations;
S7.10 evaluates them externally. `S_pers` remains required reporting and does
**not** guide S7.9 selection.

## Discovery is separated from validation

Development selection (S7.9) reduces `Ahat_rec` to one representation using
development discharges only. External validation (S7.10) then tests that frozen
object against a cohort that was sealed before the utility rule existed. The
firewall is what makes V5 meaningful: without a hash that predates the first
external access, per-discharge local calibration would make the transfer claim
vacuous.

External values opened in S7.8: **0**. Baselines run in S7.8: **0**.
