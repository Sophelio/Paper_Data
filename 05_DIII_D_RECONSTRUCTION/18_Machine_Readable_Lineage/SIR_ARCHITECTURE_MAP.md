# S7 in the SIR architecture

Every canonical S7 stage, placed in the discovery architecture. Machine-readable:
`CANONICAL_INDEX.json` (`sir_architecture_mapping` per stage) and each stage's
`MANIFEST.json`.

---

## The architecture

**Scientific object**

```
O = (D, Ω_obs, S, E, Π, A)
```

**Discovery contract at operational epoch e**

```
K_q^(e) = ( K_q^claim , K_q^op,(e) )

K_q^claim  = ( q , I_q , U_q , V_q , Ω_q )      fixed in semantic meaning within a branch
K_q^op,(e) = ( P_q , B_q , H_q )                versioned; may advance an epoch
```

**Forward construction**

```
O → O_q → X_q → G_q → 𝔄_q → 𝔄̂_q → (C*,R*) → Q*_q

O_q = I_q(O)              X_q = Obj_q(O_q)
G_q = Γ(X_q, O_q, K_q; Λ, 𝔗)
𝔄_q = {(C,R) : C ∈ ℭ_q, R ∈ ℜ_q(C)}
Σ_q = SearchPolicy(G_q, K_q)          — derived, operationally revisable
𝔄̂_q = Explore(𝔄_q; Σ_q, B_q)
```

**Audit and reconciliation**

```
δ^(e)                                  defect record
ρ_q( K_q^(e), Z_q^(e), δ^(e) ) ↦ ( K_q^(e+1), j_min )
```

`Z_q^(e)` is the instantiated operational construction and `j_min` the earliest
invalidated stage. This map describes **same-branch** reconciliation. Where the
defect touches only the instantiated construction, `K_q^(e+1)` may equal
`K_q^(e)`; the epoch and replay record still preserve provenance. A material
revision of a claim-defining commitment is a *different* disposition of the same
audit: it produces a provenance-linked **descendant claim branch**, not another
same-branch replay.

**Task, branch, epoch**

```
scientific task q
    └── provenance-linked claim branch      fixes (q, I_q, U_q, V_q, Ω_q)
            └── operational epoch(s)        revises (P_q, B_q, H_q)
```

The subscript `q` marks association with a scientific **task**. It does not imply
that exactly one contract or one branch can ever exist under that task. Only a
material change to the task itself requires a new `q`.

Held throughout, and enforced in S7:

```
G_q  ≠  𝔄_q  ≠  𝔄̂_q  ≠  Σ_q
```

- `G_q` — the task-conditioned **grammar** (S7.5, S7.5H). Not a feature library.
- `𝔄_q` — the concrete **admissible universe**: 10,778 atoms (S7.6R).
- `𝔄̂_q` — the **explored frontier**: 162,845 supports in Epoch 1 (S7.7R).
- `Σ_q` — the **search policy** `SIGMA_REC_ONE_SEED_PRIMARY_V2`.

## The `q_rec` lineage

`q_rec` is the scientific **task**:

> contemporaneous reconstruction of an admissible diagnostic quantity from the
> remaining task-admissible observational system, under the declared
> target-selection, information, utility and qualification policies.

It is deliberately more stable than any single target instance. `y* = density` is
the target **instance** selected under the frozen task rules; the earlier `vsurf`
instantiation was corrected under the *same* task and the *same* claim branch.

```
q_rec  (scientific task)
│
├── QREC-B1   sealed-external claim branch
│     │       claim: structural transfer, qualified on a sealed external
│     │              cohort of 42 discharges
│     │
│     ├── operational epoch 1   S7.2 … S7.10
│     │     ├── Case A corrections   vsurf → density (S7.3V2), X_rec (S7.4V2),
│     │     │                        ontology hardening (S7.6R)
│     │     ├── Case B versions      contract V2 (S7.2C), search budget (S7.7R)
│     │     │                        — inside epoch 1, no epoch advance
│     │     └── S7.10  QUALIFICATION FAILED — preserved unmodified
│     │
│     ├── audit                 S7.11, S7.R1  (state hypothesis REFUTED)
│     └── operational epoch 2   S7.K2  Case B: P_rec gains range support,
│                                      AFTER an executed and failed regime
│                                      claim branch UNCHANGED
│
└── QREC-B2   cross-fitted finite-object DESCENDANT claim branch
      │       constituted at S7.E2.0, parent QREC-B1
      │       claim: target-cross-fitted reconstruction over the
      │              predictor-qualified frozen 62-discharge object
      │
      └── operational epoch 1  (S7's historical label: "Epoch 2")
      ├── S7.E2.0    Case C — V_rec materially narrowed after protected
      │              evidence was spent;  Ω_rec unchanged
      ├── S7.E2.0A   Case B version inside the pending epoch — tau_train
      │              retired; I_rec clarified, not redefined
      ├── S7.E2.1    FORMAL PASS
      ├── S7.E2.2    descriptive realization
      └── S7.12      Q_rec*  —  branch CLOSED
```

**Epoch bookkeeping.** An operational-contract *version* change is not
automatically an operational-*epoch* advance. A Case-B revision advances the
epoch only when the superseded contract had already governed an **executed**
operational realization. `S7.2C`, `S7.7R` and `S7.E2.0A` are therefore versioned
corrections inside their pending epochs; **`S7.K2` is the one epoch advance**,
because it follows a regime that had executed and failed qualification. Counted
branch-locally, `QREC-B2` has a single operational epoch — its first — retaining
S7's historical label "Epoch 2".

**Closure.** The final canonical `q_rec` descendant branch is closed, and the
`q_rec` scientific lineage has no authorized further discovery epoch on any
branch. The frozen fields `Q_REC_BRANCH_CLOSED = true` and
`NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED = true` in `S7_12_FREEZE.json` carry that
meaning and are not modified here.

## Stage map

| Stage | Instantiates / audits / revises | What it produced |
|---|---|---|
| **S7.1** | `O` | 62 discharges, 95 quantities, provenance, units, temporal support |
| **S7.2** | `K^claim`, `K^op` | target-blind contract skeleton; 20/42 partition; block geometry |
| **S7.2C** | `K^claim`, `K^op`, `δ`, `ρ` | nine superseded clauses corrected; V1 preserved |
| **S7.3** → **S7.3V2** | `K^claim`, `O_q`, `δ`, `ρ` | target **instance** `y* = density` selected under the frozen task rules; 78 of 95 predictors admitted, 17 excluded |
| **S7.4V2** | `X_q` | discharge-wise trajectory ensemble on source-supported grids |
| **S7.5** → **S7.5H** | `G_q` | 70 primitives, constructor families C0–C8, 23,861 symbolic coordinates |
| **S7.6R** | `𝔄_q` | `A_REC_DENSITY_HARDENED_V2` — **10,778** admissible atoms |
| **S7.7R** | `Σ_q`, `𝔄̂_q` | `AHAT_REC_DENSITY_ONE_SEED_V2` — **162,845** supports explored |
| **S7.8** | `K^claim` (`U_q`, `V_q` made executable) | five lexicographic ranks; equivalence floor 0.01; gates operationalized |
| **S7.9** | `(C*,R*)` | `C_dev_star`, 12 coordinates; frozen before any external access |
| **S7.10** | `Q*_q`, **`δ`** | **external qualification FAILED** — QREC-B1's negative qualification outcome: V3 FAIL, V6 FAIL, `Ω*_rec` EMPTY |
| **S7.11** | `δ` | the failure is a property of the family, not only of the representative |
| **S7.R1** | `δ`, `ρ`, **`j_min`** | state hypothesis **refuted**; `j_min = NONE_OF_THE_INSTANTIATED_OBJECTS` |
| **S7.K2** | **`K^op`**, `ρ` | `P_rec` revised: observational range support, τ = 1 → **3,451** atoms |
| **S7.E2.0** | `K^claim`, `K^op` | six deterministic folds; budget; stop rule. **Constitutes descendant claim branch QREC-B2** |
| **S7.E2.0A** | `K^op`, `δ`, `ρ` | transition-specific information boundary; `tau_train` retired |
| **S7.E2.1** | `Σ_q`, `𝔄̂_q`, `(C*,R*)`, `Q*_q` | six fresh searches, six supports, **FORMAL_PASS** |
| **S7.E2.2** | `(C*,R*)` | `C_E2_ALL_DESC` — descriptive realization, not validation evidence |
| **S7.12** | `Q*_q` | `Q_rec*` assembled; branch closed |

![The q_rec iterative arc](figures/fig_s7_iterative_arc.png)

## The two dispositions that matter

S7 contains the clearest concrete instance of the audit machinery in the paper,
because the same failure produced **two different dispositions in sequence**.

### S7.R1 rules out Case A

The external failure had an obvious candidate explanation: the development cohort
pooled distinct operational states, so the instantiated object `X_rec` was wrong.
That would be **Case A** — repair the object, same contract, same branch.

S7.R1 **tested** that explanation with target-blind predictor evidence and
**rejected** it. Development already covered the external gas-actuation range,
and one development discharge exceeded both catastrophic discharges. No clean
actuator state separated the failures.

### S7.K2 is Case B — operational contract, same branch

What remained was that every instantiated object satisfied the contract *as it
was written*, and the contract itself was incomplete. `P_rec` guarded
denominators against division pathology but permitted unbounded extrapolation of
any coordinate. So:

```
δ^(e)  = "a fitted relation was applied far outside its calibration range,
          and no clause forbade it"

ρ_q    ↦ K_rec^op,(e+1) with a new P_rec clause (observational range support)

j_min  = the admissible universe: the candidate set changes, so search must
         be replayed from A_q onward
```

`q`, `I_rec`, `U_rec`, `V_rec` and `Ω_rec` are unchanged **as semantic
commitments**, and the frozen record states `revision_class = MINIMAL_P_ONLY`.

**On `V-RANGE`.** `P-RANGE-SUPPORT` is the K2 revision; it lives in `P_rec` and
is an operational admissibility rule. `V-RANGE` is the *operational qualification
check* that tests satisfaction of that revised admissibility condition. It is
**not** evidence that the claim-defining `V_rec` changed at K2, and this document
does not say that it is.

So K2 advances the **operational epoch inside QREC-B1**. It did not create a new
branch.

### S7.E2.0 is Case C — descendant claim branch

The branch changes one stage later, and for a different reason. Because the
Epoch-1 evaluation evidence had been inspected and then used to diagnose the
defect, it became development evidence for the revised procedure and could no
longer qualify anything downstream. The sealed-external claim of QREC-B1 was
therefore no longer evidenceable.

Epoch 2 responded with a cross-fitted qualification design **and** an explicitly
narrower claim. That is a material revision of `V_rec` — a **Case-C
disposition**, which under an unchanged task produces a provenance-linked
**descendant claim branch**, `QREC-B2`.

`Ω_rec`, the **intended** claim domain and a member of `K_q^claim`, is unchanged:
the same frozen 62-discharge object in both branches. The domain actually
**supported** by qualification, `Ω*_rec`, narrows as a consequence — but `Ω*_rec`
is part of `Q*_q`, not of `K_q^claim`, so it is an outcome of the revision, not a
second claim-defining revision.

It is **not a new `q`**: the scientific task never changed. And it is **not
external validation**: nothing in `QREC-B2` may be described that way.

## Why Epoch 2 is not post hoc tuning

Four independent properties, each checkable from the frozen record:

1. **The revision was diagnosed, not fitted.** The candidate explanation was
   stated, tested against target-blind evidence, and refuted. The surviving
   diagnosis is a structural gap in an admissibility clause.
2. **The rule is generic.** `P-RANGE-SUPPORT` is dimensionless, unit-scale
   invariant, sign-symmetric, constructor-generic and target-blind. It is not
   special-cased to gas actuators, to self-products, to the two failing
   discharges or to the two failing blocks. Every constructor family survives at
   τ = 1 (77 %, 31 %, 72 %, 16 %, 21 %, 26 %, 23 %).
3. **The threshold was fixed before any count existed.** The τ grid was frozen
   with a recorded hash before survivor counts were produced; the survivor curve
   is smooth and monotone (9 → 1,026 → 2,099 → **3,451** → 5,957 → 8,722 →
   9,559), so τ = 1 sits in a broad region rather than on a cliff chosen to
   isolate anything.
4. **The evidence design was reconciled, not reused.** Because the Epoch-1
   evaluation evidence had informed the revision, it could no longer serve as
   untouched validation evidence. Epoch 2 therefore used a cross-fitted design
   *and* narrowed the claim, and states both explicitly.

![Range support](figures/fig_s7_range_support.png)

## What the protected-evidence rule cost

The cost is the descendant branch itself, and the narrower claim it carries.

Under the protected-evidence rule the honest consequence is recorded rather than
avoided: Epoch 2 tests whether the **target relationship** transfers to
discharges whose targets were withheld. It does **not** test whether the
predictor geometry would survive discharges never observed. That sentence
travels with the result everywhere it appears.

The reporting tier was also fixed in advance and **missed**: `Δ₁ = −0.027308`
against a declared `CLEAN_DEMO` threshold of −0.05. The threshold was not moved,
and `FORMAL_PASS` and `CLEAN_DEMO_NOT_MET` are carried as separate fields.

## The `q_desc` branch

`q_desc` is a **different scientific task**, and therefore a different lineage
entirely — not a branch of `q_rec` and not an operational epoch of it. The task,
the information policy (target-containing coordinates are admissible), the
utility and the validation structure all differ materially. Its canonical artifacts are not in this
directory — see `WORKFLOW.md` §7 and `MANUSCRIPT_ALIGNMENT.md` §3.
