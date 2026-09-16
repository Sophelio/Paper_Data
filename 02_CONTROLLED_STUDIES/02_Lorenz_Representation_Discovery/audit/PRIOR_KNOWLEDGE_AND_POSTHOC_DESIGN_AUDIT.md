# Prior knowledge and post-hoc design audit

**Date:** 2026-08-27

## Statement of exposure

**This second benchmark is confirmatory with respect to a NEW holdout, but its
design was informed by the exposed first benchmark.** That is a real limitation
on the strength of the evidence and is stated here rather than buried.

## What was already seen (PRIOR EXPOSED FINDINGS — not new results)

From `D:/SIR_paper/Lorenz/benchmark/`, all of the following were inspected
*before* this study was designed:

1. Conventional PySINDy and a restricted local SIR contract agreed on canonical
   Lorenz recovery (max |Δc| between methods 3.9×10⁻¹⁴).
2. The hidden-z task used 48 trajectories with 32/8/8 splits.
3. The candidate grammar contained 38 target-free coordinates.
4. The selected representation was `C* = C0 + {Q[ẏ|x], Q[y|x]}`.
5. It recovered the analytic identity `z = ρ − (ẏ + y)/x`, including ρ = 28.
6. The full expanded basis slightly beat the selected basis in noiseless RMSE
   (1.30×10⁻⁵ vs 3.32×10⁻⁵).
7. The selected basis was much smaller (12 vs 38) and better conditioned
   (2.6×10¹² vs 7.5×10¹⁶).
8. An unchanged MLP benefited strongly on clean data (0.248 → 0.029).
9. That MLP advantage vanished under 1% observational noise (C0 0.757 became
   the best input).

## How this knowledge shaped the present design

Honestly enumerated, because a reviewer will ask:

| Design choice | Motivated by prior finding |
|---|---|
| Introducing a **robust** contract with an explicit noise envelope | 9 — the clean-data advantage was already known to be fragile |
| Introducing a **compact** contract separate from accuracy | 6 + 7 — accuracy and parsimony were already known to disagree |
| Including strong **poly2/poly3 raw baselines** | anticipated reviewer objection that the prior linear raw baseline was weak |
| Including the **RS/SC regularised families** as named candidates | 4 — the prior search chose the *unregularised* quotient, so the regularised variants needed a fair chance under noise |
| Fixing a **finite candidate list** rather than greedy search | the prior greedy path made "which contract selects what" hard to compare |

**The most serious exposure risk** is that `Q[ẏ|x]` and `Q[y|x]` are already
known to be the analytically correct coordinates. Any contract that selects them
is not discovering them for the first time. This is why:

- the confirmation ensemble is entirely new (24 trajectories, new seed, new seed
  trajectory, different initial condition, audited for non-duplication);
- the candidate list includes many alternatives that could win instead;
- the scientific claim under test is **not** "SIR finds the quotient" (already
  seen) but "**different contracts select different representations from the
  same object**", which the first benchmark did not test at all.

## What is genuinely new here

1. The SIR MCP executes the contracts (the first benchmark could not reach it).
2. Three *distinct* task contracts over one scientific object.
3. A protected confirmation ensemble never used for any selection.
4. A strong conventional polynomial PySINDy baseline.
5. An external-contract PySINDy wrapper as a nesting control.

## What may NOT be claimed

- The old 8 test trajectories are **not** protected any more and are used only as
  development data.
- No result from the first benchmark is reused as confirmatory evidence.
- The recovery of the analytic identity is **prior knowledge**, not a new finding
  of this study, and must be presented as such.
