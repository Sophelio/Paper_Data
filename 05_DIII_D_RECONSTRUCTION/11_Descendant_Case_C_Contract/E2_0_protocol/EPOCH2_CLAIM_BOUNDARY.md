# Epoch 2 — claim boundary

Machine-readable: `EPOCH2_PROTOCOL.json`, `EPOCH2_QUALIFICATION_POLICY.json`.

---

## The claim type, frozen

```
CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION
WITHIN_THE_FROZEN_62_DISCHARGE_OBSERVATIONAL_OBJECT
```

## Why no new external cohort was carved

The former 42-discharge external cohort **is no longer sealed**. Its target
values were opened in S7.10, and it informed the R1 refutation and the K2
contract revision. Every one of the 62 discharges has now contributed to the
contract-learning process.

Carving a fresh "never seen" cohort out of the same 62 discharges would be
fabrication. There is no untouched data left in this observational object, and
pretending otherwise would undo the very discipline that made the Epoch-1
negative result trustworthy.

Cross-fitting is the honest architecture available. It does **not** claim virgin
data. It claims something weaker and defensible: **no discharge's own target
informed the support used to reconstruct it.**

## Permitted wording, if Epoch 2 earns it

> Under the revised range-support-qualified contract, discharge-grouped
> cross-fitted discovery produced relational representations that reconstructed
> held-out DIII-D discharges nontrivially relative to persistence across the
> frozen 62-discharge observational object.

## Forbidden wording, whatever the outcome

- ✗ "validated on an untouched external cohort"
- ✗ "virgin external validation"
- ✗ "zero-shot transfer"
- ✗ "prospective clinical-style confirmation"
- ✗ "universal DIII-D relation" / "universal DIII-D generalization"

## What cross-fitting does and does not buy

**Does:** each of the 62 discharges is reconstructed by a support discovered
from the other ~51, so no discharge's target participated in choosing the
support that predicts it. Six independent searches, six supports, 62 out-of-fold
results, one per discharge.

**Does not:** establish transfer to discharges outside this object, to other
devices, or to future campaigns. The object was assembled once and has been
studied repeatedly. Cross-fitting controls target leakage into support
discovery; it cannot manufacture novelty in data that has already been analysed.

## Carried qualifications from Epoch 1

These survive into any Epoch-2 wording and are not renegotiable:

- **Support identifiability is absent.** S7.9 found `BOOT = 0.093` across 217
  bootstrap winners, and S7.11 found development selection frequency essentially
  uncorrelated with external behaviour (Spearman −0.09). Epoch 2 will produce
  **six** supports. Non-unique supports with stable utility is a legitimate
  outcome and must be reported as such — never as "the discovered relation".
- **No global-optimality claim.** Selection remains within whatever frontier the
  fold searches explore.
- **`prmtan_neped`**, if selected, remains a same-family observable whose
  provenance is certified independent of the target *signal* — which does not
  establish physical or statistical independence from line-averaged density.
- **`pcdiamag3`**, if selected, remains `UNCALIBRATED_SIGNAL` with no certified
  physical-dimensional coefficient interpretation.
- **`gasa`…`gasd`** are gas injection valve **command voltages**, resolved in K2,
  not fueling rates.

## The optional all-data representation

Epoch 2 may, **after** the cross-fitted qualification is completely frozen, run
one final discovery over all 62 discharges to produce a descriptive
representation for figures and interpretation. It must be labelled

```
FULL_OBJECT_DESCRIPTIVE_REPRESENTATION
```

and it may **never** be called externally validated, nor alter the cross-fitted
verdict in any direction.

## If Epoch 2 fails

No claim. `q_rec` closes as a qualified iterative case study — which is itself a
publishable SIR result — and `q_desc` becomes the positive DIII-D headline. See
`EPOCH2_STOP_RULE.md`.
