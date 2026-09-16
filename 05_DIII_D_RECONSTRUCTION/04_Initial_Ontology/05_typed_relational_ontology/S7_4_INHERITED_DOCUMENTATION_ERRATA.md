# Inherited documentation errata — S7.4 V2 prose

Machine-readable: `manifests/PREFLIGHT_SEMANTIC_CHECKS.json`

Two wording defects were found in S7.4 V2 **prose**. In both cases the
machine-readable artifacts and the frozen computation are **correct**. No S7.4
file was modified, and neither finding reopens S7.4 or S7.3R.

---

## E-1 · "four" heterogeneous type blocks → **three**

**Prose said:** *"Four of the eight type blocks are dimensionally
heterogeneous"* — while naming only three (`X_NBI`, `X_mag`,
`X_density_aux`).

**Machine-readable artifacts say three.** `X_REC.json` flags exactly
`X_NBI`, `X_mag`, `X_density_aux` as `dimensionally_homogeneous: false`.

**Independently recounted at component level** from `typed_signal_blocks.csv`,
counting distinct canonical units plus an uncalibrated marker per block:

| Block | distinct component types | heterogeneous |
|---|---|---|
| `X_ECE` | 1 (eV) | no |
| `X_CER_v` | 1 (m/s) | no |
| `X_CER_Ti` | 1 (eV) | no |
| **`X_NBI`** | **2** (W, N·m) | **yes** |
| **`X_mag`** | **3** (T, A, uncalibrated) | **yes** |
| `X_fs` | 1 | no |
| `X_gas` | 1 (V) | no |
| **`X_density_aux`** | **2** (m⁻³, eV) | **yes** |

The recount **agrees** with the machine-readable flags.

**Correction:** *four* → **three**. Substance unaffected — the three blocks
requiring component-level dimensional checks were correctly named throughout;
only the count word was wrong.

**Verdict:** `DOCUMENTARY_ERRATUM_ONLY`. S7.4 is not reopened.

Affected prose: `S7_4_MATHEMATICAL_INTERPRETATION_AUDIT_REPORT.md` §1 and §7,
`X_REC_DEFINITION.md`, `README.md` (all under
`04_mathematical_interpretation/retry_source_resolution_v2/`), and the S7.4
block of `S7/STATUS.md`. The frozen files are left as written; `STATUS.md` is a
living document and has been corrected in place.

---

## E-2 · cadence-estimate denominator wording

**Prose said:** *"the archived temporal support divided by the number of
samples the archival pipeline received."*

**The frozen definition and implementation both use `n − 1`:**

```
Δt_src_hat(i,s) = archived_support(i,s) / (original_length(i,s) − 1)
```

- `temporal_semantics.json` records exactly that expression.
- `s7_3r_reconcile.py` implements
  `j.support_ms / (j.original_length - 1)` — verified by source inspection.

**Correction:** the precise wording is *"the archived temporal support divided
by **one fewer than** the number of source samples over the recorded support"*.

This is the correct denominator: `n` samples span `n − 1` intervals, so dividing
by `n` would understate the spacing and thereby **overstate** the resolution —
the opposite of the conservative direction the policy requires. The frozen
computation already does the right thing; only the sentence was loose.

**Verdict:** `DOCUMENTARY_ERRATUM_ONLY`. Frozen computation unchanged.

---

## Handling

Both errata are recorded here and inherited downstream. S7.5 uses the **correct
values** — three heterogeneous blocks, `n − 1` denominator — throughout
`G_REC.json` and its type rules.

Per the stage instruction, no frozen S7.4 artifact was edited. Anyone reading
the S7.4 prose should read it alongside this file.
