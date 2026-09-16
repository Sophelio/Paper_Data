# Inherited documentation errata — S7.5 prose

Machine-readable: `manifests/PREFLIGHT_CHECKS.json`

Two wording defects in S7.5 **prose**. In both cases the machine-readable
artifacts are correct, no executable admissibility depends on the wording, and
S7.5 was **not** reopened.

---

## E-1 · B2 nesting semantics

**Prose said (S7.5 `ontology_constraints.json` annotation and README):**
*"the raw-coordinate baseline B2 is nested inside the SIR ontology rather than
being an external alternative."*

That conflates two different statements.

| | |
|---|---|
| **TRUE** | the **raw coordinate representation family** is nested in `G_rec`, because C0 primitive coordinates are admissible |
| **NOT GENERALLY TRUE** | the **specific frozen B2 model** is itself a member of `A_rec` |

B2 is frozen as Ridge on the *same target-admissible primitive predictors, with
no constructed coordinates* — potentially all **78** primitives. Members of
`A_rec` obey `m ≤ 12`. A 78-primitive model is therefore **not** an `m ≤ 12`
member of `A_rec`.

**Corrected wording, carried downstream:**

> Primitive-only representations are nested within the SIR ontology. B2 is the
> frozen full-information raw linear comparator using the same
> target-admissible primitive information.

The fairness claim is **SAME INFORMATION BOUNDARY**, not an identical
support-size constraint.

**B2 was not modified and was not restricted to 12 coordinates** to preserve a
nesting claim. Weakening the comparator to make a slogan true would be exactly
the wrong repair — B2 exists to be hard to beat on the same information.

**Verdict:** the claim appears only as a documentary annotation; no executable
admissibility or baseline configuration depends on it. Verified by searching
`constructor_catalog.json`, `constructor_type_rules.json`,
`relation_templates.json` and `G_REC.json` for any B2 reference — none found.
→ `DOCUMENTARY_ERRATUM_ONLY`.

---

## E-2 · "eight primitives cannot enter derived coordinates"

**Prose said:** *"Eight of 78 primitives cannot enter derived coordinates."*

Inaccurate. The authoritative constructor rules are:

| Primitives | C0 | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|
| `pcbcoil`, `pcdiamag3` (2, uncalibrated) | ✓ | ✗ | ✗ | ✗ | ✗ |
| 6 `UPSTREAM_UPSAMPLED` | ✓ | sensitivity-only | **✓** | **✓** | sensitivity-only |

The six upstream-upsampled primitives **do** enter products and ratios. Only the
two uncalibrated primitives are barred from every derived family.

**Corrected wording:**

> Two uncalibrated primitives cannot enter any primary derived coordinate. Six
> upstream-upsampled primitives remain eligible for products and ratios but not
> for primary derivative-based coordinates.

**The machine-readable `G_rec` was already correct** — `constructor_catalog.json`
records `n_eligible_operands` of `C0: 78`, `C1: 70`, `C2: 76`, `C3: 76`,
`C4: 70`, which is exactly the corrected statement. Verified in stage A.

This matters arithmetically: had the prose been executable, C2 and C3 would each
have lost 6 operands, changing the symbolic counts from 2 926 and 5 700 to
2 485 and 4 830. The instantiated registry reproduces **2 926** and **5 700**,
confirming the correct rule was applied.

→ `DOCUMENTARY_ERRATUM_ONLY`. S7.5 not reopened.

---

## Handling

Both errata are recorded here and inherited downstream. S7.6 used the **correct
rules** throughout: 76 product/ratio operands, 70 derivative/phase operands, and
no claim that B2 is an `A_rec` member.

No frozen S7.5 artifact was edited.
