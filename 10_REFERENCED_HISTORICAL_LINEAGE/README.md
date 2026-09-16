# Referenced historical lineage

**Nothing in this folder is a current result.** It is retained because the
manuscript's corrections cannot be understood without it.

| Folder | Status | Superseded by |
|---|---|---|
| `failed_parent_branches/retired_Ip_branch/` | **RETIRED** | the `density` lineage in `05_DIII_D_RECONSTRUCTION/` |
| `superseded_manuscript/` | **SUPERSEDED** | `01_MANUSCRIPT_SNAPSHOT/` |

## The retired `I_p` branch

Retired 2026-09-02 under `D3D-FIG6-QREC-RETIREMENT-V1` on two independent
grounds, either sufficient:

1. **Target-provenance leakage.** 6 of 10 `REL10` and 4 of 10 `RAW10` features
   carried upstream `I_p` dependence. `q95` proved to be essentially
   `shape·a²B_t/I_p` in this archive — median |corr| 0.945 with `1/I_p`, only
   **7.3 %** residual scatter after algebraic removal. Both the relational
   representation *and its comparator* were contaminated.
2. **No skill over a trivial baseline.** A constant persistence predictor reached
   median normalized RMSE **0.0685**, beating REL141 (0.1137), REL10 (0.1257) and
   RAW10 (0.1821).

**The staged manuscript still reports this branch.** That is the single most
important finding of this package.

The corrective rebuild — the `density` branch in `05_DIII_D_RECONSTRUCTION/` —
satisfies all five prerequisites the retirement record demanded, including a
target-independent candidate universe and a mandatory persistence gate.
