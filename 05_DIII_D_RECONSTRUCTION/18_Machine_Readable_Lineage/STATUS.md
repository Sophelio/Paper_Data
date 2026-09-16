S7 PACKAGE AUDITED, STABILIZED, AND ARCHITECTURE-SEMANTICS RECONCILED
  Forensic audit verdict: S7_AUDIT_PASS_WITH_QUALIFICATIONS
  Semantics verdict:      S7_ARCHITECTURE_SEMANTICS_RECONCILED
  Automated checker:      python audit_s7.py
  Frozen artifacts:       527/527 reproduce byte-for-byte across 21 stages

  q_rec LINEAGE (current §1.1 semantics; documentation layer only):
    scientific task  q_rec       one task throughout
      QREC-B1  sealed-external claim branch
               operational epoch 1  S7.2..S7.10  -> NEGATIVE QUALIFICATION OUTCOME
                                    versioned Case-B corrections: S7.2C, S7.7R
               audit                S7.11, S7.R1
               operational epoch 2  S7.K2  Case B, branch unchanged
      QREC-B2  cross-fitted finite-object DESCENDANT branch (parent QREC-B1)
               operational epoch 1  S7.E2.0..S7.12   (S7 label: "Epoch 2")
                 S7.E2.0   Case C - V_rec narrowed; constitutes the branch
                 S7.E2.0A  Case B version inside the pending epoch
                 S7.E2.1 .. S7.12  -> Q_rec*, CLOSED
    vsurf -> density corrected a target INSTANCE, not the task or the branch.
    Omega_rec (intended claim domain) is UNCHANGED throughout; only V_rec was
    materially revised. A contract VERSION change is not automatically an
    operational-EPOCH advance: S7.K2 is the one epoch advance.
    Epoch 2 is NOT external validation. Both branches are closed.
  Both MAJOR findings concern the MANUSCRIPT, not S7:
    F-1  Results 1.5 / Fig. 4b / Suppl. S7.8 still present the RETIRED I_p branch
    F-2  Results 1.1 predates the claim-core / operational-epoch architecture
  Entry points: index.html | README.md | AUDIT_REPORT.md | MANUSCRIPT_ALIGNMENT.md
  This audit modified NO frozen artifact, moved nothing, deleted nothing.

--------------------------------------------------------------------------
CURRENT_STAGE: S7.12 (q_rec branch CLOSED)
STATUS: Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT

FREEZE_ID: D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1
ACCEPTANCE: 36/36 | 15 artifacts | 6 markdown
RECORD: S7_12_qualified_result/S7_12_FREEZE.json

  Q_REC_STATUS        = QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
  CLEAN_DEMO_STATUS   = CLEAN_DEMO_NOT_MET
  NON_UNIQUE_RELATIONAL_SUPPORTS
  Q_REC_BRANCH_CLOSED = true

>> THE q_rec BRANCH IS CLOSED. No Epoch 3. No S7.13. No further search.
>> NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED = true. q_desc UNTOUCHED.

THE QUALIFIED CLAIM:
  Within the predictor-qualified frozen 62-discharge observational object,
  relational supports discovered WITHOUT a discharge's own target values
  reconstruct that discharge nontrivially relative to the frozen baselines.
  PREDICTOR_QUALIFIED | TARGET_CROSS_FITTED | RECONSTRUCTION.

NOT SUPPORTED: virgin/untouched external validation; unknown-predictor-
distribution transfer; fully inductive generalization; future-discharge
applicability; zero-shot; universal DIII-D relation; cross-device; unique
physical equation; universal coefficient vector.

THE RESULT (carried unchanged from E2.1, 62 out-of-fold discharges):
  Delta_0 = -0.764489   Delta_1 = -0.027308   V3 = PASS
  V6 = PASS_WITH_QUALIFICATION | V-RANGE = PASS (2232 checks, 0 failures)
  REL mean 0.1891 median 0.1515 p90 0.2959 max 0.9199 | 0 shots > 1.0
  vs B2 -0.0960 | vs B3 -0.1573 | vs H0 -0.0951 | vs B1 32/5/25
  earlier (35) +0.0076 PRACTICAL_TIE | later (27) -0.0726 MATERIAL_IMPROVEMENT
  The pooled pass is CARRIED BY THE LATER ERA. Persistence margin is MODEST.

Q_rec* IS A FAMILY, NOT AN EQUATION:
  {(C_k*, R_k*)}_{k=1..6} - six supports, all size 12, NONE identical,
  mean Jaccard 0.285, 35 distinct coordinates. E2.2 produced a SEVENTH
  distinct support. Stable utility, non-unique relational supports.
  No canonical-equation claim. No universal coefficients.

--------------------------------------------------------------------------
S7.E2.2 - Full-object descriptive representation
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1
STATUS: FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN
ACCEPTANCE: 34/34 | 21 artifacts | 3 markdown
RECORD: E2_2_full_object_descriptive_representation/E2_2_FREEZE.json

  C_E2_ALL_DESC  size 12  sha256 e7935c35fd30...
  ID(pcdiamag3) | PROD(ece37,ece39) | PROD(pinj,pinj_30l) |
  RATIO(ece21,cerqtit10) | RATIO(fs03da,cerqtit3) | RATIO(gasc,cerqtit10) |
  RATIO(gasc,cerqtit11) | RATIO(ip,ece39) | RATIO(pinj_33r,cerqtit10) |
  RATIO(prmtan_neped,ece38) | RATIO(tinj,ece20) | RECIP(cerqtit10)

  C3 ratios 8 | C2 2 | C0 1 | C5 1 | no derivative family
  One fresh search, 127,642 proposals of 300,000, same 3,451-atom basis,
  U_rec unchanged (Rank 1 left 3,212; Rank 2 left one). FIT 0.1775,
  COND_MEDIAN 2.004, bootstrap selection frequency 0.009 / 365 winners.
  Descriptive fit mean 0.1775 max 0.9242, 0 shots > 1.0 - IN-SAMPLE,
  NOT A VALIDATION METRIC.
  Overlap with the six folds: 3-8 of 12, Jaccard 0.143-0.500, mean 0.313,
  IDENTICAL TO NONE. Shares both universal fold coordinates; contributes
  three that no fold selected (incl. two gasc ratios).

>> DESCRIPTIVE ONLY. Not externally validated, not held out, not the support
>> that produced the cross-fitted metric, NOT CANONICAL. Cannot alter
>> FORMAL_PASS, CLEAN_DEMO_NOT_MET, V3, V6, V-RANGE or any cross-fitted metric.

--------------------------------------------------------------------------
S7.E2.1 - Cross-fitted discovery and qualification  (parent, unchanged)
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1
STATUS: QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
ACCEPTANCE: 38/38 | 39 artifacts | 6 markdown
RECORD: E2_1_crossfitted_discovery_and_qualification/E2_1_FREEZE.json
>> re-verified in E2.2 and S7.12: all 39 artifacts reproduce BYTE-FOR-BYTE.

>> THE CONTRACT HARDENING WORKED:
>>   Epoch 1 mean 0.7424 max 11.95, 2 shots > 1.0
>>   Epoch 2 mean 0.1891 max  0.92, 0 shots > 1.0
>>   187019: 11.95 -> 0.297   187022: 11.77 -> 0.436
>> The catastrophic extrapolation tail is GONE. Consistent with the R1 -> K2
>> reconciliation having localized the right defect. NO STRONGER CAUSAL CLAIM:
>> contract, basis, validation geometry and supports all differ between epochs.

THE ITERATIVE ARC (the primary methodological story):
  Epoch 1 discovery -> external qualification FAILED (mean 0.74, max 11.95)
  -> provenance: extrapolation of PROD(gasa,gasa)
  -> operational-state explanation PROPOSED
  -> R1 tested it TARGET-BLINDLY and REFUTED it
  -> defect localized to P_rec, NOT X_rec
  -> K2 added a generic range-support predicate, tau = 1, frozen FIRST
  -> E2.0A clarified the transition-specific information boundary
  -> Epoch 2 searched afresh, cross-fitted -> FORMAL PASS, tail gone.

CARRIED QUALIFICATIONS: coefficients locally calibrated, no universal
coefficient vector; pcdiamag3 remains UNCALIBRATED_SIGNAL; prmtan_neped is
target-SIGNAL-ancestry independent only; gasa..gasd are command voltages.

PAPER_UTILITY = MEDIUM_HIGH (high for the method demonstration, moderate for
the reconstruction claim itself). RECOMMENDATION: use the positive q_rec
result, with editorial caution on the accuracy claim.

LINEAGE AT S7.12: 13 parents verified, ALL reproduce byte-for-byte.
  S7.2 35/35 | S7.3 33/33 | S7.6 27/27 | S7.7 19/19 | S7.9 45/45
  S7.10 31/31 | S7.11 26/26 | S7.R1 21/21 | S7.K2 29/29 | S7.E2.0 22/22
  S7.E2.0A 14/14 | S7.E2.1 39/39 | S7.E2.2 20/20
  (self-referential manifest entries excluded by construction)

NEXT_STAGE: NONE. Q_REC_BRANCH_CLOSED = true.

UTILITY RULES (S7.8, parent, unchanged):
FREEZE_ID: D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1
FREEZE_STATUS: FROZEN_READY_FOR_S7.9
ACCEPTANCE: 48/48 PASS
RECORD: 08_utility_and_qualification_rules/S7_8_FREEZE.json
>> re-verified in S7.9: all 26 artifacts reproduce BYTE-FOR-BYTE.

PRIMARY SEARCH (S7.7R, parent, unchanged):
FREEZE_ID: D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2
FREEZE_STATUS: FROZEN_WITH_QUALIFICATIONS
ACCEPTANCE: 43/43 PASS
  Sigma_rec  SIGMA_REC_ONE_SEED_PRIMARY_V2  FROZEN_AND_EXECUTED  sha 2049cf99
  Ahat_rec   AHAT_REC_DENSITY_ONE_SEED_V2   162,845 supports, sizes 1-12
RECORD: 07_search_policy_and_frontier/one_seed_primary_v2/S7_7R_FREEZE.json
>> re-verified in S7.8: all 41 artifacts reproduce BYTE-FOR-BYTE.

>> S7.7 V1 (BLOCKED_SEARCH_BUDGET) is PRESERVED_AS_AUDIT_HISTORY,
>> re-verified BYTE-FOR-BYTE UNCHANGED after the re-run.
>> RECORD: 07_search_policy_and_frontier/S7_7_FREEZE.json

UNIVERSE (S7.6R, authoritative, unchanged):
FREEZE_ID: D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2
FREEZE_STATUS: FROZEN_WITH_QUALIFICATIONS
ACCEPTANCE: 49/49 PASS
UNIVERSE: A_REC_DENSITY_HARDENED_V2
  10,778 atoms from 23,861 symbolic | 9 families C0-C8 | represented FACTORIALLY
RECORD: 06_admissible_universe/hardened_v2/S7_6R_FREEZE.json

PRIMARY ONTOLOGY: G_REC_DENSITY_HARDENED_V2 v2.0.0 (S7.5H, 48/48)
  70 primitives | 9 families C0-C8 | 23,861 symbolic coordinates
RECORD: 05H_primitive_space_and_ontology_hardening/S7_5H_FREEZE.json

>> S7.6 V1 (D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1, 6034 atoms, C0-C4 on the
>> 78-primitive ontology) is HISTORICAL_SUPERSEDED /
>> NOT_A_PRIMARY_PARENT_FOR_ADMISSIBILITY_RESULTS, re-verified
>> BYTE-FOR-BYTE UNCHANGED after the rebuild.
>> RECORD: 06_admissible_universe/S7_6_FREEZE.json

ONTOLOGY: D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1 (50/50)
  RECORD: 05_typed_relational_ontology/S7_5_FREEZE.json

X_rec: D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2 (44/44)
  RECORD: 04_mathematical_interpretation/retry_source_resolution_v2/
          S7_4_FREEZE_V2.json

BOUNDARY: D3D-SIR-S7.3-...-SOURCE-RESOLUTION-V2 (31/31)
  RECORD: 03_target_feasibility_and_boundary/reconciliation_source_resolution/
          S7_3_FREEZE_V2.json

SELECTED TARGET: y* = density (line-averaged electron density)
  archived cm^-3 -> canonical m^-3 | class DIAGNOSTIC_RECONSTRUCTION
  78 admissible primitives / 7 families
  corrected cadence 5.853 - 14.187 ms, DISCHARGE-SPECIFIC, source-supported
  target NEVER upsampled in any discharge

SUPERSEDES: S7.3 V1 (target vsurf) - preserved unmodified
UNBLOCKS:   S7.4 V1 (TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED)

CONTRACT: D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2 (24/24)
  RECORD: 02_reconstruction_contract/correction_v1/S7_2_FREEZE_V2.json
  SUPERSEDES: D3D-SIR-S7.2-...-V1 (31/31, preserved unmodified)
  V1 verification: 35/35 substantive artifacts intact, 0 drift
  (2 self-referential manifest entries excluded by construction)

PARENT: D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1 (FROZEN, 32/32)
PARENT_VERIFICATION: 9/9 hashes verified
  02_reconstruction_contract/manifests/S7_1_INPUT_VERIFICATION.json

--------------------------------------------------------------------------
S7.1 - Observational object O          FROZEN_WITH_QUALIFICATIONS
--------------------------------------------------------------------------
- O_DIIID_FINAL_V1 = (D, Omega_obs, S, E, Pi, A)
- 62 DIII-D discharges (155537-195659), 95 scientific quantities
- 5890/5890 signal x discharge pairs, finite fraction 1.0
- D / Omega_obs / S INSTANTIATED | E NOT_INSTANTIATED
- Pi / A PARTIALLY_INSTANTIATED
- A means ancillary observational information, NOT admissibility

--------------------------------------------------------------------------
S7.2 - Reconstruction contract K_rec^pre    FROZEN_READY_FOR_S7.3
--------------------------------------------------------------------------
NO TARGET HAS BEEN SELECTED. This stage freezes the target-blind contract
skeleton only.

K_rec = (q, I, P, B, H, U, V, Omega)
- q       FROZEN     continuous reconstruction; structural transfer with
                     local calibration (NOT zero-shot)
- I       PARTIAL    exclusion rules + fail-closed + sibling rule FROZEN;
                     instantiated set DEFERRED_TO_S7.3
- P       PARTIAL    8 invariant classes + unit canonicalisation +
                     numerical-resolution rule FROZEN
- B       PARTIAL    depth 1, first derivative, pairwise only,
                     support size 1-12 FROZEN
- H       FROZEN     knowledge uses + seeding firewall
- U       FROZEN     lexicographic utility + practical-equivalence rule
- V       PARTIAL    geometry + 4 baselines + 10 gates FROZEN;
                     gate evaluation DEFERRED_TO_S7.10
- Omega   PARTIAL    62-discharge candidate domain + cohort partition FROZEN

Cohort partition (deterministic, target-blind, no seed)
- development  20 shots (32.3%)  era 11 earlier / 9 later   periods 2-7
- external     42 shots (67.7%)  era 24 earlier / 18 later  periods 1-7
- external cohort SEALED until S7.10

Validation geometry (frozen without any target value; fractions UNCHANGED by
S7.2C, only the protection semantics were clarified - see C-04)
- 3 rolling-origin blocks per discharge, BLOCK-LOCAL PROTECTION
  A calibration [0.00,0.40) evaluation [0.40,0.50)
  B calibration [0.00,0.60) evaluation [0.60,0.70)
  C calibration [0.00,0.80) evaluation [0.80,0.90)
- feasible at ALL 7 native cadences: 186/186
- worst case (20 ms grid): >=18 evaluation, >=75 calibration samples

Baselines frozen before target selection
- B0 calibration mean | B1 persistence
- B2 raw ridge linear | B3 HistGradientBoostingRegressor

Key hashes
- K_REC_PRE            7bcc35aff40c8e9ec18301b2adb1071aeffffeecc950f97f3ed9e496d32ace28
- cohort partition     9ccc5dc96e76fe34e4689f2adcead62b0ba9ad5d7b215e39697c92e90c191b81
- validation protocol  c7bedec96e961b3fab24e6a413cbd5129a27dd864b7abc4a36666ff58ef0cb3c
- information boundary e8242957e5bdacb0b8c7f506e1b4b366c0540184677eacd715c8e75db879ec64
- decision ledger      5dacf55ba93abbfafab987284d8573ea105528ec86d65a6fcd4dcf93c6718d04

Gate assertions for S7.2
- target selected ................... NO
- candidate targets ranked .......... NO
- coordinates generated ............. NO
- G_rec / A_rec / Ahat_rec .......... NO
- SIR run ........................... NO
- regression run .................... NO
- performance inspected ............. NO
- external signal values inspected .. NO
- S7.3 started ...................... NO
- frozen S7.1 artifacts modified .... NO

S7.2C corrections applied (9 superseded clauses; V2 inherits V1 otherwise)
- C-01 practical equivalence: delta_equiv = max(SE_delta, 0.01), NOT AND.
       V1 conjunction made the 0.01 floor inoperative exactly when SE was tiny.
       SE_delta = SE of the paired discharge-level difference over the 20
       development discharges.
- C-02 ordinary CV retired. Replaced by robust relative variation:
       RRV_s = 1.4826*MAD(y_s)/RMS(y_s), 0 if RMS=0
       RRV_dev = median_s(RRV_s); min_median_robust_relative_variation = 0.05
- C-03 primary metric defined exactly:
       scale_{s,b} = std(y_calibration_{s,b}, ddof=0)
       NRMSE_{s,b} = RMSE(protected)/scale_{s,b}
       scale==0 -> INVALID_FOR_NORMALIZED_SCORING; no epsilon
- C-04 BLOCK-LOCAL PROTECTION (sequential/prequential). Time fractions
       UNCHANGED. Score a block, freeze the score, only then may those target
       values act as ordinary calibration history for later blocks.
       External cohort remains GLOBALLY SEALED before S7.10.
- C-05 deterministic 5-level lexicographic target-selection rule frozen;
       top-ranked eligible candidate IS the primary target.
- C-06 gate V3 defined exactly:
       Delta_j = mean_s(NRMSE_REL,s - NRMSE_Bj,s) over external discharges
       PASS iff Delta_0 <= -0.01 AND Delta_1 <= -0.01
- C-07 gate V6 uses EXTERNAL counts 24 earlier / 18 later (NOT 35/27, which
       are parent-object counts). PASS / PASS_WITH_QUALIFICATION /
       FAIL_FOR_FULL_DOMAIN.
- C-08 all six previously open human decisions frozen (below).
- C-09 hash manifest excludes self-referential files by construction.

Human decisions FROZEN by S7.2C (no longer open)
- H-A no EFIT-lineage recovery campaign for the primary study
- H-B no PROVENANCE_RELAXED variant (V1 escape 2 from fail-closed is CLOSED)
- H-C no target-class override (pcdiamag3 stays excluded: uncalibrated)
- H-D no second-order derivatives
- H-E no support beyond 12
- H-F do not rewrite the S7.1 mixed-hash historical freeze

S7.2C key hashes
- K_REC_PRE_V2       100b2a1cfc19bb97d7b7dbb8c874052ea1567d281205c86a82521733a9356a17
- correction report  30bca5850bbda93c811ca9b8b90997349f9496ad6d664ef8cc08bc07c15ed13d
- contract V2        c7a5be8a44750730503928816875be8e9ee1e22299eeef78d9b3652cd87970f8
- decision ledger    97b91014e3b66f5ade6373e49482cfe5f36077ca6f224d5841c3e140f6c30351
- selection rule     2b988067b3f87f32ec075ce16c855e243282eb7f769f4577afd62d083387d1de
- selection schema   09341740a1db8104b449578d7d154fa7b100a3b0aa981eef3c0d540eb56ee3d2
- metric/gate defs   18efb0db67ae0f0d6f36a7dff7e262374af831c157c7cf84ab982dc0991d5ccb

Superseded by S7.2C - historical, no longer open
1. Attempt EFIT lineage recovery? Resolving it returns up to 15 equilibrium
   quantities to the primary boundary; not resolving it means fail-closed
   removes them for some targets.
2. Is a PROVENANCE_RELAXED secondary variant wanted? Must be declared BEFORE
   results exist.
3. Primary target selection from the S7.3 eligible set (rule frozen; final
   choice needs sign-off).
4. Any override of a normally-excluded target class (ledger D-04)?
5. Promotion of second-order derivatives or widening support beyond 12
   (both require recorded review; neither may be justified by performance).
6. ADVISORY: the S7.1 freeze recorded hashes under two different rules.
   Data integrity is unaffected and all 9 artifacts verify; S7.2 works around
   it with a uniform canonical hash set. The parent file was NOT modified.
   -> RESOLVED as frozen decision H-F: do not rewrite it.

ZERO signal values were inspected during S7.2 or S7.2C.

--------------------------------------------------------------------------
S7.3 - Target feasibility and information boundary   FROZEN_READY_FOR_S7.4
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-V1
ACCEPTANCE_TESTS: 35/35 PASS
RECORD: 03_target_feasibility_and_boundary/S7_3_FREEZE.json
PARENTS VERIFIED: S7.1 (9), S7.2 V1 (35), S7.2 V2 (10) - 0 drift

SELECTED PRIMARY TARGET
- y* = vsurf   Surface loop voltage
- unit V (already canonical) | class DIRECT_MEASUREMENT | family magnetics
- native cadence 20.0 ms | frozen inventory index 5
- target-side signal-specific MAJOR flags: NONE
- recorded but NOT a selection input: vsurf is upstream-upsampled
  (resolution_flag UPSTREAM_UPSAMPLED) - constrains derivatives at S7.5

Selection chain (deterministic, no human preference, no model)
- 95 quantities -> 64 candidates (frozen class policy, metadata only)
- 64 -> 62 eligible (12 criteria, development values only)
      2 failures, both C10 meaningful variation:
      bt RRV_dev 0.0037, ip RRV_dev 0.0042 (flat-top quantities)
- 62 -> 1 by the frozen 5-level lexicographic rule
- vsurf vs runner-up density: tied L1 (0 flags), L2 (79), L3 (7);
  RESOLVED AT LEVEL 4, RRV margin 0.1297 vs 0.0483
- fs05da has the LARGEST margin (0.4140) and ranks 3rd: as a filterscope
  target it loses 3 siblings -> 76 predictors / 6 families. L2 outranks L4.

Development-only feasibility of vsurf
- RRV_dev 0.1797 (range 0.1057-0.3610 across all 20 discharges)
- distinct-value fraction 1.000 | identically-zero discharges 0
- invalid NRMSE blocks 0 of 60 | both processing eras present
- calibration blocks 75-140+ samples, evaluation blocks 19-23

PRIMARY INFORMATION BOUNDARY  O_rec = I_rec(vsurf)(O)
- 95 initial -> 16 removed -> 79 admissible primitives
  target itself                1
  duplicate / alias            0
  definitional descendant      0
  verified target ancestry     0
  unresolved target ancestry  15   (all equilibrium, fail-closed)
  sibling exclusion            0
  other P_rec reason           0
- 7 families: ECE 40 | CER 14 | beams 10 | magnetics 4 | filterscope 4 |
              gas 4 | density 3
- primary analysis cadence 20.0 ms (set by vsurf itself, no-super-resolution)
- 18 survivors carry ALIASING_RISK; pcbcoil/pcdiamag3 survive as predictors
  with permanent UNCALIBRATED_SIGNAL type
- sibling sensitivity: NOT_APPLICABLE (vsurf has no same-quantity series)

Data-access firewall
- development shots opened for values: 20 (exactly the frozen list)
- external shots opened: 0   (42 identifiers known, archives untouched)
- target-side MAJOR flag mapping frozen and hashed BEFORE any value opened

Contract sanity check (S7.3 section 4)
- PASS_WITH_NOTATIONAL_NOTE. V2 practical_equivalence.rule uses a bare
  'RMSE' token. It does NOT explicitly encode raw RMSE, so no STOP.
  Four fields fix the unit as NRMSE. Recommended purely notational fix at
  the next contract revision. Immaterial to S7.3 (no model fitted).

Gate assertions for S7.3
- external values opened ............ NO
- model fitted ...................... NO
- baseline evaluated ................ NO
- correlation used as ancestry ...... NO
- coordinates / G_rec / A_rec ....... NO
- reconstruction performance seen ... NO
- human target preference used ...... NO
- S7.4 started ...................... NO

S7.3 key hashes
- target selection result 01ee4aa2a06d661715c7bcda4616a849...
- primary boundary       fa636084cfc36bf9a1901f7f0010d52d...
- I_REC_SELECTED         7e184f32b45c8f4105b8f6b91327c288...
- O_REC_SELECTED         0ef9b4b464a33fd1397f31fad0803759...
- target ranking         258d01fb5970ccd4338e9dab0de2abb5...

What S7.4 inherits
1. y* = vsurf; 79 primitives across 7 families; 20.0 ms primary cadence.
2. 18 predictors carry ALIASING_RISK and the target carries
   UPSTREAM_UPSAMPLED - both constrain derivative construction at S7.5.
3. The 15 equilibrium quantities are OUT and stay out (fail-closed;
   no EFIT recovery, no PROVENANCE_RELAXED variant).
4. External cohort (42 shots) remains sealed until S7.10.

--------------------------------------------------------------------------
S7.4 - Mathematical interpretation X_rec    STOPPED AT ITS OWN PRECONDITION
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-V1
STATUS: TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED
X_rec INSTANTIATED: NO
ACCEPTANCE: 24/24 gate checks (X_rec structural items N/A - not reached)
RECORD: 04_mathematical_interpretation/S7_4_FREEZE.json
PARENTS VERIFIED: S7.1 (9), S7.2 V1 (35), S7.2 V2 (10), S7.3 (33) - 0 drift

BLOCKING FINDING - target temporal provenance
The frozen 20 ms analysis grid is FINER than vsurf's source-supported
cadence in 20 of 62 discharges (7 of the 20 development shots). This
conflicts directly with the frozen no-super-resolution rule, on the target.

  SOURCE_SUPPORTED_CADENCE   19.93 - 82.91 ms, median 20.24, VARIES by shot
  ARCHIVED_CADENCE           20.0 ms, uniform in all 62
  ANALYSIS_CADENCE           20.0 ms  (S7.3 primary grid)

  verdict: C_SOURCE_CADENCE_VARIES_BY_DISCHARGE

- vsurf was cubic_spline resampled in all 62 shots and UPSAMPLED in 36.
- worst shot 165027: 56 source samples -> 229 archived, source dt ~82.9 ms.
- worst development shot 165861: 198 -> 240, source dt ~24.3 ms.
- UPSTREAM_UPSAMPLED is NOT bookkeeping: it records real interpolated
  samples in the quantity the reconstruction is scored against.
- The source estimate is a LOWER BOUND on coarseness (original_length is
  what the pipeline received; the generator is absent, U001). Better U001
  information cannot rescue the finding, only worsen it.

SECOND FINDING - flagged, NOT acted on
vsurf shares the equilibrium group's time base EXACTLY in all 62 shots
(identical original/resampled lengths, t_start, t_end, n_samples as all 15
LINEAGE_PARTIAL quantities). Not proof of EFIT derivation - the registry
gives no EFIT attribution and origin class is DIRECT_MEASUREMENT at
STRONGLY_INFERRED - but it opens a question S7.3 had no reason to ask:
is the TARGET's own ancestry relative to the equilibrium reconstruction
resolved? S7.4 may not rerank or alter I_rec, so this is recorded only.

Access audit
- archives opened: ZERO. Resolved from frozen S7.1 metadata and the
  per-shot metadata sidecars (component A) alone.
- signal values read: NONE, development or external.
- external cohort remains sealed.

NOT PRODUCED (all depend on the unresolved cadence)
X_REC.json, typed_signal_blocks.csv, trajectory_index.csv,
temporal_semantics.json, interpretation_constraints.json,
predictor_dependency_edges.csv, X_REC_DEFINITION.md, TEMPORAL_SEMANTICS.md,
S7_4_MATHEMATICAL_INTERPRETATION_FINAL.md

HUMAN DECISION REQUIRED - reconciliation options (none chosen by S7.4)
1. Coarsen the analysis grid to the worst source-supported cadence.
2. Per-discharge cadence (breaks the single-grid validation geometry
   and the shared-support gate V7).
3. Restrict Omega_rec to shots consistent with 20 ms (42/62; only 13/20
   development) - changes a frozen cohort.
4. Re-open target selection under a corrected cadence definition. The
   vsurf ranking was resolved at LEVEL 4 by a margin of 0.081 over
   density, which has 1 ms archived cadence and was NOT upsampled, so a
   corrected computation could plausibly change the winner.
5. Accept and qualify (weakest; sits uneasily with an absolute rule).
Options 4 and the second finding point the same way; a combined
reconciliation is likely more efficient than two separate ones.

--------------------------------------------------------------------------
S7.3R - Source-supported temporal admissibility   FROZEN_READY_TO_RETRY_S7.4
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-SOURCE-RESOLUTION-V2
ACCEPTANCE: 31/31 PASS
PARENTS VERIFIED: S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1 - 0 drift

THE CORRECTION (one instantiation, applied uniformly)
S7.3 used ARCHIVED cadence where the frozen no-super-resolution policy
requires SOURCE-SUPPORTED cadence. Corrected for all 95 signals and all 64
candidates. NO rule, threshold, class policy, cohort or minimum changed.

  SOURCE_SUPPORTED  archived_support / (original_length - 1)
                    evidence STRONGLY_INFERRED; a support-based average, NOT
                    an exact native interval; a LOWER BOUND on coarseness
  ARCHIVED          spacing of the stored series
  ANALYSIS          per discharge, = coarsest source-supported among admitted

HISTORICAL COUNT CORRECTED: 16 -> 22 upstream-upsampled signals
  The old 16 used a per-signal MEDIAN ratio and could not see signals
  upsampled in a minority of shots. Under "upsampled in ANY shot" the count
  is 22. New: prmtan_neped, prmtan_teped (3 shots each) and the four
  filterscopes (9 shots each). Corrected, not forced to agree.

vsurf IS THE ONLY QUANTITY THAT FAILS
- 63 numerical-support removals across all 64 candidate boundaries, and
  every one of them is vsurf. No other signal forces an infeasible grid.
- Fails as TARGET (C13 TARGET_SOURCE_RESOLUTION_FAIL): at external shot
  165027 its source-supported cadence is 82.909 ms -> 48 grid samples ->
  blocks A(cal=22,eval=5) B(cal=33,eval=5) C(cal=44,eval=5). All three
  evaluation blocks below the frozen minimum of 10.
- Removed as PREDICTOR from every other candidate boundary, same mechanism.
- V1 status: RETIRED_BY_SOURCE_RESOLUTION_RECONCILIATION.
  Not a failed result - no reconstruction was ever attempted.

CORRECTED SELECTION (ranking rule UNCHANGED)
  64 candidates -> 61 eligible -> 1 target
  failures: C10 x2 (bt 0.0037, ip 0.0042, unchanged) + C13 x1 (vsurf)

  rank candidate  flags preds fams RRV_margin index resolved
   1   density      0     78    7    0.0506     21    -
   2   fs05da       0     75    6    0.4094     27    L2
   3   fs04         0     75    6    0.3088     24    L2
   4   fs04da       0     75    6    0.3088     26    L2
   5   fs03da       0     75    6    0.2145     25    L2
   6+  40 ECE       0     39    6      -         -    L2

  Resolved at LEVEL 2 on predictor count. fs05da again has the far larger
  variation margin (0.409 vs 0.051) and again loses on breadth - the same
  behaviour as V1, from the same unchanged rule. No weighted score, no
  manual promotion of density.

CORRECTED BOUNDARY  O_rec = I_rec(density)(O)
  95 -> 17 removed -> 78 admissible primitives
    target itself                1
    unresolved target ancestry  15  (equilibrium, fail-closed)
    numerical-support           1   (vsurf)
    duplicate/alias, definitional, verified ancestry, sibling:  0
  families: ECE 40 | CER 14 | beams 10 | magnetics 4 | filterscope 4 |
            gas 4 | density 2

CORRECTED CADENCE - DISCHARGE-SPECIFIC (not a single value)
  5.853 - 14.187 ms, median 6.824; max in development 14.14
  binding: prmtan_teped (26 shots), cerqrott3 (25), cerqrott8 (10),
           cerqrott13 (1)
  FINER than V1's flat 20 ms, because removing the 20 ms-class bottleneck
  frees the remaining admitted quantities - and every sample is now
  source-supported.
  All 62 discharges validation-feasible, min 325 grid samples vs 100 needed.
  density on development: 60/60 blocks valid, cal >= 130, eval >= 33.

density DEVELOPMENT FEASIBILITY (recomputed on the corrected grid)
  RRV_dev 0.1006 (range 0.0299 - 0.2621) | distinct 1.000 | zero 0
  invalid NRMSE blocks 0/60 | both eras present
  NOTE: RRV falls to 0.0299 in its weakest development discharge. The frozen
  criterion is on the MEDIAN, which passes. Spread recorded, not smoothed.

TEMPORAL HANDOFF TO S7.4 (per signal, in the corrected boundary CSV)
  6 survivors carry UPSTREAM_UPSAMPLED -> NUMERICAL_SENSITIVITY_ONLY for
    derivatives (prmtan_neped, prmtan_teped, 4 filterscopes)
  18 survivors carry ALIASING_RISK
  All admissible AS LEVELS - the corrected grid respects their source support

vsurf / EQUILIBRIUM TIME BASE (S7.4 finding, preserved)
  NOT_MATERIAL_TO_PRIMARY_Q_REC_AFTER_RECONCILIATION
  vsurf is neither target nor predictor. No inference that vsurf is an EFIT
  output is drawn from shared time base alone; no EFIT recovery undertaken.

NOTATION CLARIFICATION (inherited downstream; S7.2 V2 NOT rewritten)
  |NRMSE_A - NRMSE_B| <= max(SE_delta, 0.01)   -- normalized, not raw RMSE

WHAT WAS NOT DONE
- cohort NOT restricted (165027 stays external; 20/42 untouched)
- experiment NOT degraded to 82.9 ms to retain vsurf
- no accept-and-qualify exception, no PROVENANCE_RELAXED, no EFIT recovery
- no model, no baseline, no predictor-target correlation, no coordinate
- ZERO external signal values accessed

S7.3R key hashes
- target selection V2  20209dbc5d905725bd7005eee251a6c30bb3ed09...
- I_REC_SELECTED_V2    b340f44eac22c3f3a2596f4275be17164b68ba53...
- O_REC_SELECTED_V2    96c5551186d3a6dfd8e7efb8f065e9767188a2b5...
- source cadence audit 02508c03fed1515ff889b84cbe685dcdc7788f2a...
- numerical admissib.  d39ae964186905a1fd39ef4d824ad8def6ad08db...
- corrected ranking    61f24071416cafdb74561cc005cc4e370166f640...

--------------------------------------------------------------------------
S7.4 - Mathematical interpretation X_rec          FROZEN_READY_FOR_S7.5
       (retry after source-resolution reconciliation)
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-SOURCE-RESOLUTION-V2
ACCEPTANCE: 44/44 PASS | X_rec INSTANTIATED: YES
SUPERSEDES: S7.4 V1 (stopped at the temporal gate) - preserved unmodified
PARENTS VERIFIED: S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2 - 0 drift

TEMPORAL GATE NOW PASSES (this is what stopped V1)
- density is upstream-upsampled in 0 of 62 discharges: its archived and
  source-supported cadences coincide - exactly what failed for vsurf.
- no admitted quantity forces a grid finer than its resolution estimate
- all 62 discharges validation-feasible | vsurf remains excluded
- no external signal value was needed for the verification

X_rec = { (T_s, x_s, y_s, a_s) : s in S_rec },  |S_rec| = 62
- y_s(t) = density_s(t), electron number density, canonical m^-3
  (archived cm^-3, x10^6) | DIAGNOSTIC_RECONSTRUCTION, class not upgraded
- x_s : T_s -> X_pred, 78 target-independent primitives
- a_s = discharge ID, processing era, operational period, access class
  (realization metadata, NEVER an explanatory coordinate)
- 20 development / 42 external realizations; external values never opened

PREDICTOR SPACE - 7 broad families, 8 mathematical type blocks
  X_ECE          40  eV                    homogeneous
  X_CER_v         7  m/s                   homogeneous
  X_CER_Ti        7  eV                    homogeneous
  X_NBI          10  W, N m                HETEROGENEOUS
  X_mag           4  T, A, 2x uncalibrated HETEROGENEOUS
  X_fs            4  ph/(sr m^2 s)         homogeneous
  X_gas           4  V                     homogeneous
  X_density_aux   2  m^-3, eV              HETEROGENEOUS
  CER splits into two blocks: rotation is a velocity, Ti is a temperature.
  THREE blocks are dimensionally heterogeneous (X_NBI, X_mag,
  X_density_aux) - dimensional rules apply at COMPONENT level; a sum within
  a block is not automatically valid.
  [S7.5 erratum E-1: an earlier line here said FOUR while naming three. The
   machine-readable X_REC.json always encoded three; an independent
   component-level recount agrees. Frozen S7.4 files were NOT edited.]
  Canonicalized: 40 keV->eV, 7 km/s->m/s, 4 cm^-2->m^-2, 1 kW->W.
  Channel index is NOT asserted to be a spatial coordinate for any signal.

TEMPORAL STRUCTURE - discharge-specific by design
  dt_s      5.853 - 14.187 ms, median 6.824, 53 DISTINCT values across 62
  N_s       325 - 833 (40572 total analysis samples)
  duration  3.780 - 5.360 s
  binding   prmtan_teped (26), cerqrott3 (25), cerqrott8 (10), cerqrott13 (1)
  global_fixed_dt_required                    = false
  common_coordinate_support_required          = true
  common_time_grid_across_discharges_required = false
  Coherent because validation windows live in tau, coefficients are
  discharge-specific, and gate V7 constrains comparisons WITHIN a discharge.

TIME PARAMETERS
  physical t [s]   independent parameter; the ONLY derivative parameter
  normalized tau   ONLY for the frozen block fractions; carries no dimension
  d/dtau for primary scientific coordinates = FORBIDDEN
  (durations differ by a factor of 1.42; a tau-derivative would rescale
   differently per discharge and corrupt physical dimensions)

CADENCE SEMANTICS - terminology corrected
  dt_src_hat(i,s) = archived_support / (original_length - 1)
  = SOURCE-SUPPORTED AVERAGE CADENCE ESTIMATE, NOT an exact native cadence.
  Support/count based; original timestamps unavailable; nonuniform original
  sampling unreconstructable; upstream generator absent (U001).
  DEFENSIBLE CLAIM: the primary analysis grid is no finer than the
  provenance-supported temporal-resolution estimate used by the frozen
  numerical-admissibility policy.
  NOT CLAIMED: every analysis sample is an observation; every sample is
  source-supported; the grid recovers native diagnostic sampling.
  This is a SEMANTIC qualification only - S7.3R was not reopened.

16 vs 22 SEMANTICS
  n_upsampled_any_discharge = 22   (operative downstream)
  historical 16 used a per-signal MEDIAN ratio, which cannot see a signal
  upsampled in a minority of shots. Different measurements, NOT contradictory.

REGULARITY - three levels kept distinct
  A observational sampled trajectory : what the study possesses
  B numerical realization            : declared analyst interpolant/smoother
  C latent physical trajectory       : not assumed exactly recoverable
  Differentiability is NOT assumed. A later derivative coordinate is a
  constructor acting through a DECLARED numerical realization, not evidence
  that the samples possess an exact classical derivative. Load-bearing for
  the SIR phase / trajectory-relational derivatives at S7.5.

NUMERICAL REPRESENTATION
  X_s^num in R^{N_s x 78}, y_s^num in R^{N_s}
  = IMPLEMENTATION_REPRESENTATION_ONLY. R^78 does not carry the scientific
  semantics of X_pred. X_rec is defined in canonical units, NEVER z-scored.

FLAGS CARRIED INTO S7.5 (independent of each other)
  6  UPSTREAM_UPSAMPLED : prmtan_neped, prmtan_teped, fs03da, fs04, fs04da,
                          fs05da -> admissible AS LEVELS,
                          derivative status NUMERICAL_SENSITIVITY_ONLY
  18 ALIASING_RISK      : 14 CER + bt, ip, prmtan_neped, prmtan_teped
  A coarser analysis grid does NOT erase upstream aliasing - it is already
  embedded in the archived signal.

PREDICTOR DEPENDENCY RETAINED
  pinj = sum(pinj_*)  EXACT_DETERMINISTIC_SUM, LOCAL_DOCUMENTED
  Not target leakage for density. Nothing removed in S7.4; S7.5 must decide
  how G_rec avoids duplicate terms / exact redundancy / rank deficiency.

ASSUMPTIONS EXPLICITLY NOT MADE
  differentiability | C^1 smoothness | ODE-solution structure | Markov |
  complete physical state | latent-state recovery | dynamical closure |
  causal ordering | channel index as spatial coordinate |
  cross-discharge concatenation | iid pooling of discharges

ACCESS: ZERO archives opened. All quantities metadata-derived. No signal
value read, development or external. External cohort (42) remains sealed.

S7.4 V2 key hashes
- X_REC                9c16e9b25754b3528afa7a7dcb224d67c05f0521...
- typed blocks         219d6ec3d41c4a5f0dbacdca389f22cc3f2c00b0...
- trajectory index     988c3babef230b3e2707f0e353b239af5c2d0a30...
- temporal semantics   5807545623c1ddc576b22fb1ff69611fd38deebf...
- temporal gate        e6b4248734d2154f12ac56f8341a6aa6a00a5f30...
- dependency edges     a9df37af85558799dbe3471b88bfb371a3276eea...

--------------------------------------------------------------------------
S7.5 - Typed relational ontology G_rec              FROZEN_READY_FOR_S7.6
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.5-TYPED-RELATIONAL-ONTOLOGY-V1
ACCEPTANCE: 50/50 PASS | ontology G_REC_DENSITY_V1 v1.0.0
PARENTS VERIFIED: S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2,
                  S7.4 V2 - 0 drift

G_rec = Gamma( X_rec, O_rec, K_rec ; Lambda_rec, T_rec )
G_rec is the GRAMMAR of admissible relational constructions.
A_rec IS NOT ENUMERATED - that is S7.6.

Lambda_rec - 5 primary constructor families, MAX DEPTH 1
  C0 primitive level          depth 0  arity 1  78 eligible operands
  C1 first temporal deriv     depth 1  arity 1  70 eligible operands
  C2 pairwise product         depth 1  arity 2  76 eligible operands
  C3 pairwise ratio           depth 1  arity 2  76 eligible operands
  C4 phase derivative         depth 1  arity 2  70 eligible operands
     (trajectory-relational derivative D_{x_j} x_i)
  Constructors consume PRIMITIVES ONLY. No constructor may consume another
  depth-1 constructed coordinate. Not primary: d(x_i x_j)/dt, x_i*(dx_j/dt),
  (x_i/x_j)*x_k, D_{x_k}(x_i x_j), ratio of ratios, product of phases.

CONSTRUCTOR RULES
  C2 commutative, canonical PROD(i,j) with i<=j prevents duplicate transposes;
     self-products allowed; operands need NOT share dimensions.
  C3 directional, PARTIAL MAP domain x_j != 0; x_i/x_i excluded (constant 1).
     PROHIBITED in the symbolic definition: denominator shifts, epsilons,
     clipping, bounded reciprocals. Those are DIFFERENT constructions.
     Conditioning of instances is handled at S7.6/S7.11 WITHOUT redefining
     the constructor.
  C4 directional, PARTIAL MAP domain dx_j/dt != 0; D_f f excluded.
     Type rule [D_g f] = [f]/[g] - the TIME DIMENSIONS CANCEL.
     Does NOT imply f = F(g), causality, oscillatory phase, or any global
     functional dependency.
     Reference-shifted / bounded / sensitivity-centered phase derivatives are
     PRIMARY-EXCLUDED as distinct constructions.

SUM / DIFFERENCE DELIBERATELY ABSENT
  Against an affine-linear template, x_i +/- x_j is already representable by
  including x_i and x_j with coefficients. Adding them would enlarge the
  candidate set WITHOUT enlarging the span of the relation family. This is an
  ALGEBRAIC REDUNDANCY argument, NOT a performance result. Dimensional
  compatibility rules for sums remain in the general type system.

RAW COMPARATOR IS NESTED INSIDE THE ONTOLOGY
  A representation whose coordinates are all C0 levels is an admissible
  special case of G_rec. Baseline B2 is therefore a MEMBER of the search
  space, not an external alternative - which is what makes the B2 comparison
  a statement about REPRESENTATION rather than about two frameworks.

EIGHT OF 78 PRIMITIVES CANNOT ENTER DERIVED COORDINATES
  2 uncalibrated (pcbcoil, pcdiamag3): level PRIMARY_ADMISSIBLE, all derived
    coordinates DIMENSIONALLY_UNCERTIFIED_PRIMARY_EXCLUDED. Fail-closed
    dimensional admissibility - NOT a claim they carry no information.
  6 upstream-upsampled (prmtan_neped, prmtan_teped, fs03da, fs04, fs04da,
    fs05da): levels admissible; derivatives NUMERICAL_SENSITIVITY_ONLY,
    representable in G_rec as SENSITIVITY_ONLY_CONSTRUCTOR_OUTPUT for S7.11,
    NOT in primary A_rec.

SYMBOLIC UPPER BOUNDS (audit only - NO instance enumerated)
  C0 78 | C1 70 | C2 2926 | C3 5700 | C4 4830  ->  PRIMARY TOTAL 13604
  plus 6 sensitivity-only derivatives.

TYPE SYSTEM - COMPONENT LEVEL, NEVER BLOCK LEVEL
  78 primitives by dimension class:
    temperature/energy eV 48 | velocity m/s 7 | power W 9 | potential V 4
    photon flux 4 | uncalibrated 2 | torque, T, A, m^-3 one each
  The 48 eV components span THREE different blocks - block membership carries
  no dimensional guarantee.
  Output dims: C0 [x] | C1 [x]/time | C2 [x_i][x_j] | C3,C4 [x_i]/[x_j]
  Numerical standardization does NOT alter scientific type.

PROPAGATION
  temporal : C0 inherit | C1 inherit + DERIVED_FROM_NUMERICAL_REALIZATION
             C2,C3 limited by the COARSER operand resolution
             C4 limited by the coarser derivative-source resolution
             INVARIANT: no coordinate may claim resolution finer than either
             operand.
  flags    : ALIASING_RISK propagates from any operand (no high-frequency
             claim). UPSTREAM_UPSAMPLED keeps the level, removes the
             derivative from primary. Where both occur (prmtan_neped,
             prmtan_teped) SENSITIVITY_ONLY dominates.
             A coarser grid does NOT erase upstream aliasing.
  provenance: primitive ancestors exactly recoverable; target independence is
             TRANSITIVE and encoded as an invariant.

DERIVATIVE NUMERICAL REALIZATION - FD2_PHYSICAL_TIME_V1  (FROZEN)
  second-order finite difference wrt ACTUAL physical time t [s]
  reference implementation numpy.gradient(x, t, edge_order=2)
  uses each discharge's own T_s - never an assumed global dt
  no fitted smoothing | no target values | no whole-ensemble fit
  no cross-discharge stencil | never wrt tau
  spline / RTS belong to S7.11 sensitivity, NOT the primary ontology
  CAPABILITY CHECK PASSED: tested at 5.853 / 6.824 / 14.187 ms; halving dt
  reduced max interior error by 4.00x at both refinements (second order).
  Synthetic data only - ZERO observational values touched.
  A derivative coordinate is a CONSTRUCTOR ACTING THROUGH A DECLARED
  NUMERICAL REALIZATION, not evidence that the samples possess an exact
  classical derivative.

EXACT DEPENDENCY RETAINED
  DEP_NBI_POWER_SUM: pinj = sum(pinj_*), EXACT_DETERMINISTIC_SUM,
  LOCAL_DOCUMENTED. Neither aggregate nor components deleted at S7.5.
  SCOPE IS REPRESENTATION-LEVEL: at depth 1 arity<=2 no single coordinate can
  carry the whole exact set. A representation containing the aggregate AND
  all eight components is flagged EXACT_LINEAR_REDUNDANCY_RISK.
  The operational exclusion rule belongs to S7.6. Deterministic restatements
  are not independent scientific evidence.

COORDINATE SIGNATURES (duplicate prevention)
  ID(sig) | DOT(sig) | PROD(i,j) i<=j | RATIO(i,j) | PHASE(i|j) = D_{x_j} x_i
  Display labels are explicitly NOT identity.

RELATION TEMPLATE T_REC_V1
  y_s(t) = beta_{0,s} + sum_j beta_{j,s} c_j(x_s)(t) + eps_s(t),  1<=m<=12
  affine-linear IN THE CONSTRUCTED COORDINATES; the coordinates themselves
  may be nonlinear relational constructions.
  support C shared across discharges | coefficients beta_s discharge-specific
  intercept permitted and NOT counted toward m
  [beta_j] = m^-3 / [c_j], so coordinates need NOT share physical units.
  Uncalibrated operand -> coefficient_dimension_status = UNCALIBRATED, no
  physical dimensional interpretation claimable.
  ESTIMATOR NOT CHOSEN AND NOT RUN - belongs to the frozen search policy.

EXCLUDED FAMILIES - 23 recorded with a 4-valued status vocabulary
  GENERAL_FRAMEWORK_PERMITS / TASK_ONTOLOGY_EXCLUDES /
  PRIMARY_ONTOLOGY_EXCLUDES / SENSITIVITY_ONLY
  Exclusion from this finite primary ontology is NOT a claim of scientific
  meaninglessness.

INHERITED S7.4 DOCUMENTATION ERRATA (both DOCUMENTARY_ERRATUM_ONLY)
  E-1 "four" heterogeneous type blocks -> THREE. X_REC.json always encoded
      three (X_NBI, X_mag, X_density_aux); independent component-level
      recount agrees. S7.4 NOT reopened; frozen files NOT edited.
  E-2 cadence denominator wording. Definition AND implementation both use
      (original_length - 1), verified in source. Prose said "divided by the
      number of samples received"; correct wording is "one fewer than the
      number of source samples over the recorded support". Dividing by n
      would UNDERSTATE spacing and thus OVERSTATE resolution - the frozen
      computation already does the conservative thing.
  Record: 05_typed_relational_ontology/S7_4_INHERITED_DOCUMENTATION_ERRATA.md

ACCESS: ZERO archives opened, ZERO external values. The only numerical work
was the synthetic derivative capability check. No correlation, no regression,
no baseline, no performance, no search priority, no q_desc seeding.

S7.5 key hashes
- G_REC                 3bf69e1e4c219d4668a947bfecf70db35e88be5f...
- primitive registry    f5753e8fb1e677f3f6b476d0f2b0f87237e2a22f...
- constructor catalog   4ae5053b525a97afe5d0d198351a8d17ece726e5...
- type rules            e3474ffaff9a2184c449e948ded016d9730cdbdb...
- coordinate signature  94a2b76308355b693983d9b0f375c815d1c66d16...
- relation templates    dc39d916a35d5069c710ffe7040f2b405b872b1e...
- dependency constraints 73d35edfd3c2d2c70121859e9086f7eecc9ae6ce...

WHAT S7.6 MUST DECIDE (deliberately left open by S7.5)
1. The operational exclusion rule for coordinate SETS carrying the exact
   pinj dependency (EXACT_LINEAR_REDUNDANCY_RISK).
2. How the two partial-map domain predicates (x_j != 0, dx_j/dt != 0) become
   instance-level admissibility under numerical support.

--------------------------------------------------------------------------
S7.6 - Admissible universe A_rec                    FROZEN_READY_FOR_S7.7
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1
ACCEPTANCE: 40/40 PASS | universe A_REC_DENSITY_V1
PARENTS VERIFIED: S7.1, S7.2 V1, S7.2 V2, S7.3 V1, S7.4 V1, S7.3R V2,
                  S7.4 V2, S7.5 - 0 drift

INSTANTIATION: 13,604 symbolic -> 6,034 admissible atoms
  C0    78 ->   74     C1    70 ->   66     C2  2926 -> 2628
  C3  5700 -> 3266     C4  4830 ->    0
  6 sensitivity-only derivatives kept separate, never in primary A_rec

>> THE ENTIRE C4 (PHASE DERIVATIVE) FAMILY IS INADMISSIBLE: 0 of 4830.
>> 0 of 70 derivative denominators pass; 97.7% fail by SIGN CHANGE, because
>> dx/dt crosses zero at every local extremum and every plasma quantity rises
>> and falls within a calibration interval.
>> This is an INSTANCE-LEVEL DOMAIN FACT, not a search result. Nothing was
>> fitted; no coordinate was compared with the target. The constructor
>> remains in G_rec - A_rec records that no INSTANCE satisfies the frozen
>> domain requirement on this object. Exactly the ontology / admissible-
>> universe distinction. No reaction was taken (section 13).

DENOMINATOR RULE - FROZEN BEFORE ANY COORDINATE VALUE WAS READ
  PRE_ENUMERATION_CONTRACT_COMPLETION, not an empirical correction.
  Stage A opens no archive at all, so the ordering is structural.
    eta(d) = min(|d|) / RMS(d)  on each calibration block
    admissible iff finite AND no sign change AND eta >= 0.05
    RMS(d) == 0 -> FAIL
  NO shifts, epsilons, clipping, bounded reciprocals, branch repair - those
  are DIFFERENT coordinate constructions.
  Sensitivity eta 0.01 / 0.10 predeclared for S7.11 ONLY; may not replace
  the primary 0.05 result.
  sha 6d4004eb3ae95067b2a01dddeb90226748cfee70

  level denominators passing 46/76:
    all 40 ECE + cerqtit3/10/11 + bt + ip + prmtan_neped
  failing 30: 18 sign change | 5 eta<0.05 | 4 exact zero | 2 RMS=0
    (rotation reverses; filterscope and gas cross zero; beams switch off)
  derivative denominators passing 0/70.

REJECTION CENSUS - every rejection carries a frozen reason
  class E denominator   7080  sign change 6042 | margin 450 |
                              zero value 300 | RMS zero 288
  class D numerical      490  constant on a required calibration block
  classes B/A/C/G/F/H      0
  6034 pass + 7570 reject = 13604. Census complete.

  The 4 class-D primitives: pinj_15r, pinj_21l, pinj_21r, pinj_33l.
  pinj_21l and pinj_21r NEVER FIRED anywhere in the cohort (S7.1 finding).
  Their levels (4), derivatives (4), products (298) and ratios (184) follow.
  Constancy tested EXACTLY (min==max); no tuned variance threshold.
  Products were NOT pruned for magnitude - large-but-finite values are the
  legitimate consequence of multiplying quantities in different units.

EXACT DEPENDENCY GROUPS - 197 attempted | 0 BINDING | 197 VACUOUS
  pinj = sum_i pinj_i propagated through every LINEAR context:
    level 1 | derivative 1 | product 67 | ratio 67 | phase 61
  NO identity claimed for RATIO(z,pinj) or PHASE(z|pinj) - with the
  aggregate in the DENOMINATOR none exists; asserting one would be a
  mathematical error.
  All vacuous because ID(pinj_15r), ID(pinj_21l), ID(pinj_21r),
  ID(pinj_33l) are inadmissible, so no admissible support can contain a
  complete nine-member group. Recorded WITH REASONS, not as a bare zero.
  Phi_dependency stays ACTIVE and would bind immediately under any revision
  restoring those components.
  RULE: a support may contain the aggregate and SOME components; it may not
  contain the aggregate AND all eight restatements in the same linear
  context. No atomic coordinate is deleted for group membership; neither
  form is privileged a priori.

A_rec IS REPRESENTED FACTORIALLY
  A_rec = { (C,R) : C subset C_rec^atom, 1<=|C|<=12, Phi_set(C)=1,
                    R in R_rec(C) },  R_rec(C) = T_REC_V1 for every C
  Unconstrained subset count for sizes 1..12 = a 37-DIGIT integer.
  NOT MATERIALIZED - and this is NOT a failure to instantiate A_rec. The
  atoms plus predicates are a COMPLETE, EXACT, finite representation;
  membership of any candidate support is decidable directly.

Phi_set - six frozen predicates
  1 <= |C| <= 12 | no duplicate IDs | atoms only | no sensitivity-only
  Phi_dependency | target never appears
  EXPLICITLY NOT IMPOSED: "must contain a phase derivative", "must contain
  multiple families", "must include raw levels", or any search preference.

EXTERNAL PARTIAL-MAP RULE - frozen prospectively, no external value opened
  Same rule applies at external calibration. On failure: do NOT shift,
  regularize, replace the coordinate or refit the support. Record the
  representation as NOT_APPLICABLE on that discharge/block. Whether
  Omega_rec survives is decided at qualification, NOT in S7.6.

INHERITED S7.5 DOCUMENTATION ERRATA (both DOCUMENTARY_ERRATUM_ONLY)
  E-1 B2 nesting. TRUE: the raw REPRESENTATION FAMILY is nested in G_rec.
      NOT GENERALLY TRUE: the frozen B2 MODEL is an A_rec member - it uses
      potentially all 78 primitives against an m<=12 bound. Verified no
      executable artifact references B2. B2 was NOT modified and NOT
      restricted to 12. Fairness claim is SAME INFORMATION BOUNDARY, not an
      identical support-size constraint.
  E-2 "eight primitives cannot enter derived coordinates" is inaccurate.
      Only the 2 uncalibrated are barred from ALL derived families; the 6
      upstream-upsampled remain eligible for PRODUCTS and RATIOS. The
      machine-readable operand counts were already correct (78/70/76/76/70),
      and the registry reproduces 2926 and 5700 - impossible under the
      erroneous reading.
  Record: 06_admissible_universe/S7_5_INHERITED_DOCUMENTATION_ERRATA.md
  S7.5 NOT reopened; frozen files NOT edited.

ACCESS AUDIT - FIREWALL_INTACT
  development shots read 20 (exactly the frozen list) | 78 predictors each
  target values accessed   0   (density is absent from the 78-primitive list
                                by construction, so it was never loaded)
  external values accessed 0

S7.6 key hashes
- A_REC                 e8c5c152c7df956328d4dc8e9e51d210a21a5919...
- atomic universe       620c32fe21e3f14c15edf82c101ca49833e4dcdb...
- denominator rule      6d4004eb3ae95067b2a01dddeb90226748cfee70...
- coordinate registry   4fc95bf46e9140bbdded265d7a26201706b0335c...
- admissibility         8e8eb9c28559364f807830d06b83a93fd1d3a837...
- rejection log         6cdb35b01eefaebc9cd5ffaa1f538f62b9c6a397...
- set constraints       60be23a00cd9dcc13ab648770f32d59068accfea...

WHAT S7.7 INHERITS
1. 6034 atoms across FOUR surviving constructor families - C4 is EMPTY, so
   any search policy assuming trajectory-relational coordinates must be
   written against what actually exists.
2. The six Phi_set predicates.
3. 197 recorded dependency groups - currently vacuous but active.
4. The frozen external partial-map rule.
5. T_REC_V1 with the estimator still deferred.
6. The surviving universe is weighted toward ratios (3266) and products
   (2628) over levels (74) and derivatives (66) - relevant to budgeting a
   frontier, though NO priority is assigned by S7.6.

--------------------------------------------------------------------------
S7.5H - Primitive-space and ontology hardening   FROZEN_WITH_QUALIFICATIONS
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1
PRIMARY ONTOLOGY: G_REC_DENSITY_HARDENED_V2 v2.0.0
ACCEPTANCE: 48/48 PASS
PARENTS VERIFIED: all 8 lineage freezes - 0 hash drift

>> STAGE-SEQUENCE CONFLICT (flagged for human review)
>> The stage instruction asserted "S7.6 HAS NOT STARTED". IT HAD.
>> D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1 exists, FROZEN_READY_FOR_S7.7, 40/40,
>> 6034 atoms, built on the FULL 78-primitive G_REC_DENSITY_V1.
>> CONTAMINATION: none possible. S7.6 V1 accessed 0 target values and 0
>> external values, fitted nothing, computed no predictor-target statistic.
>> DISCRETION: every S7.5H decision was specified by the instruction
>> (thresholds, C0-C8 catalogue, representative rule). The only judgement is
>> redundancy-group SEMANTICS, decided from metadata alone. Risk
>> LOW_AND_RECORDED.
>> RESOLUTION: PROCEED_AND_SUPERSEDE. S7.6 V1 preserved unmodified, exactly
>> as S7.3 V1 and S7.4 V1 were, and must be RE-RUN on the hardened ontology.
>> The acceptance item "S7.6 not started" could NOT be asserted truthfully
>> and is recorded as reconciled, not passed.

PRE-VALUE POLICY FROZEN BEFORE ANY VALUE WAS READ
  HARDENING_POLICY_PREVALUE.json  sha d8c81421b6a9cab5ea1a859ecc044ea6d200a807
  Stage A opens NO archive at all, so the ordering is structural.
  Stage B verifies the hash before reading anything and aborts on mismatch.
  Thresholds NOT changed after value access.

TARGET-BLIND REDUNDANCY - the rule and what it did
  STABLY_NEAR_REDUNDANT iff  n_valid_cells>=54  R_med>=0.99  R_10>=0.97
                             sign_consistency>=0.95
  4 eligible groups (metadata only): X_ECE 40, X_CER_v 7, X_CER_Ti 7, X_fs 4
  4 INELIGIBLE, each with a recorded reason and never correlation-tested:
    X_NBI (distinct beamlines + aggregate + torque, two dimensions)
    X_mag (four distinct quantities incl. two uncalibrated)
    X_gas (four distinct valves/manifolds)
    X_density_aux (density vs temperature, different dimensions)

  828 pairs audited -> 9 qualified -> 8 primitives deferred
  P_full 78 | P_hard 70 | P_deferred 8
  Every deferral has a DIRECT witness. No transitive removal.
    fs04da->fs04 | ece17->ece16 | ece23->ece22 | ece24->ece25
    ece26->ece25 | ece32->ece31 | ece34->ece33 | ece40->ece39
  NEITHER CER GROUP yielded a single redundant pair; all 14 chords retained.

  PROVENANCE FLAG: fs04 and fs04da correlate at |r| = 1.000000 in ALL 60
  cells - not the behaviour of two distinct viewing chords. Flagged for
  follow-up; NOT asserted as identity; changed nothing.

QUALIFICATION 1 - INSTRUMENTATION-DENSITY BIAS NOT MATERIALLY REDUCED
  ECE share of the primitive basis: 0.513 -> 0.471 (materially_reduced=False)
  Only 9 of 828 pairs met the frozen criterion. The primitive-space component
  of this hardening is close to a NULL RESULT. Reported, not adjusted.

QUALIFICATION 2 - EFFECTIVE-RANK AUDIT DISAGREES STRONGLY (not acted on)
  group      members  reps  median rank@95%  @99%
  X_ECE          40    33         3.0         7.0
  X_CER_v         7     7         3.0         4.0
  X_CER_Ti        7     7         2.0         3.5
  X_fs            4     3         2.0         3.0
  Reconciliation: the frozen criterion is PAIRWISE and R_10>=0.97 binds.
  40 of 780 ECE pairs reach R_med>=0.99 but 32 of those FAIL R_10>=0.97.
  Low group rank does not imply any PAIR clears a direct-witness bar.
  Per policy the disagreement is RECORDED; thresholds were NOT tuned.
  A rank-based rule was forbidden as a selection mechanism - SVD components
  are not scientifically legible primitives.

QUALIFICATION 3 - THE ONTOLOGY GOT LARGER, NOT SMALLER
  M=70  Mt=68 (typed)  Md=63 (derivative-eligible = 70 - 2 uncal - 5 upsampled)
  C0 70 | C1 63 | C2 2346 | C3 4556 | C4 3906 | C5 68
  C6 4284 | C7 4284 | C8 4284       TOTAL 23,861
  vs original 13,604  =  1.75x LARGER
  Removing 8 primitives cut the five original families to 10,941; adding four
  PAIRWISE families brought the total back to 23,861. C6/C7/C8 alone add
  12,852. Narrowing the basis did not offset broadening the grammar.

EXPANDED GRAMMAR Lambda_rec^H = {C0..C8}, MAX DEPTH STILL 1
  C5 RECIP(i)             1/x_i            [x_i]^-1
  C6 LEVEL_RATE(i|j)      x_i * dx_j/dt    [x_i][x_j]/s   NO denominator gate
  C7 RATE_OVER_LEVEL(i|j) dx_i/dt / x_j    [x_i]/([x_j] s)  i=j -> s^-1
  C8 LEVEL_OVER_RATE(i|j) x_i / (dx_j/dt)  s[x_i]/[x_j]     i=j -> s
  C6-C8 fill the LEVEL-RATE gap the original grammar left empty.
  They are DEPTH 1: primitive-pair constructors with an INTERNAL rate
  operator; they do NOT consume C1 objects recursively.
  LEVEL_RATE(i|j) != LEVEL_RATE(j|i) - role-directional despite numerical
  commutativity, since x_i*dot{x}_j != x_j*dot{x}_i.
  Partial-map predicates are SYMBOLIC ONLY here; numerical domain evaluation
  is DEFERRED_TO_S7.6. No epsilon/shift/clipping/bounded reciprocal.

PRESERVED UNCHANGED
  FD2_PHYSICAL_TIME_V1 | T_REC_V1 | support bound 1-12 | target and its unit
  shared-support semantics | discharge-specific coefficients | intercept rule
  target exclusion | provenance rules | external cohort 42 sealed
  validation geometry | DEP_NBI_POWER_SUM (pinj and all 8 components remain
  in P_hard; neither form privileged; set-level constraint stays in S7.6)
  uncalibrated C0-only | upsampled level-use allowed / derivative
  sensitivity-only | aliasing propagation
  NO previously excluded family was re-admitted.

G_REC_DENSITY_V1 STATUS
  SUPERSEDED_FOR_PRIMARY_SEARCH + PRESERVED_AS_EXTENDED_SENSITIVITY_ONTOLOGY
  Hash-verified unchanged. Its 78-primitive universe remains available for
  S7.11 sensitivity. All 8 deferred channels live there.
  REDUNDANCY_DEFERRED != SCIENTIFICALLY_INADMISSIBLE != TARGET_IRRELEVANT

H0_RAW_HARDENED - DIAGNOSTIC ABLATION, FROZEN BUT NOT RUN
  Ridge on the 70 hardened primitive LEVELS only, no constructed coordinates,
  same calibration geometry / preprocessing / penalty-selection rule as B2,
  development-only tuning.
  B2 IS UNCHANGED AND WAS NOT SHRUNK. H0 is NOT a mandatory gate baseline.
  B2 vs H0 isolates primitive-space hardening.
  H0 vs relational SIR isolates relational construction on the SAME
  hardened primitive information.

ACCESS AUDIT - FIREWALL_INTACT
  development shots read 20 | predictor signals read 58 (eligible-group
  members only - the minimum the audit requires)
  DENSITY TARGET VALUES ACCESSED  0
  EXTERNAL VALUES ACCESSED        0
  no predictor-target correlation | no mutual information | no feature
  importance | no model | no baseline | no SIR result inspected
  No signal was deferred because it "probably does not matter for density".

S7.5H key hashes
- HARDENING_POLICY_PREVALUE  d8c81421b6a9cab5ea1a859ecc044ea6d200a807...
- G_REC_HARDENED             049b004e2115870ddb9c28262fdb148959bd1065...
- primitive basis hardened   8d4d68876f8ddfdedd12d55f8b25cf7398df6f1e...
- primitive basis deferred   9b1238e4337e582362d932a7eda8339dbe576633...
- pairwise redundancy        8f7da69135295455aa0cb0356cc9da6520aecdf7...
- constructor catalog        53277a841707b3c19ef4433f6e99fc09adf4369f...
- combinatorial audit        ff150da240f1e439ca46ec6f94e3e875f0b56a63...

TWO DECISIONS FOR HUMAN REVIEW BEFORE S7.6 IS RE-RUN
1. The primitive-space hardening largely did not achieve its stated purpose
   (8 of 78 deferred; ECE share 51.3% -> 47.1%). If materially stronger
   compression is wanted it requires a NEW stage with NEW thresholds frozen
   PROSPECTIVELY - never a retroactive adjustment of these. Decide now,
   before S7.6 consumes this ontology.
2. C7 and C8 both place a RATE IN A DENOMINATOR. In S7.6 V1 NO C4 instance
   survived the denominator gate, because time derivatives change sign within
   every calibration interval. The same mechanism will bear on C7 and C8. If
   it eliminates them, the four-family broadening will have added 68 usable
   coordinates (C5) rather than 12,852. Only S7.6 can determine this.

--------------------------------------------------------------------------
S7.6R - Admissible universe rebuild on the hardened ontology
                                                 FROZEN_WITH_QUALIFICATIONS
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-HARDENED-V2
UNIVERSE:  A_REC_DENSITY_HARDENED_V2
ACCEPTANCE: 49/49 PASS
PARENTS VERIFIED: all 10 lineage freezes - 0 hash drift

HISTORICAL S7.6 V1 - the required wording, verbatim
  "Historical S7.6 V1 was completed on the superseded ontology and is
   preserved as audit history. The primary admissible universe is rebuilt
   here de novo from the hardened ontology."
  NOT written: "S7.6 had never started."
  status HISTORICAL_SUPERSEDED
  role   NOT_A_PRIMARY_PARENT_FOR_ADMISSIBILITY_RESULTS
  Stage A took a byte snapshot of all 29 V1 files BEFORE the rebuild; stage C
  re-verified it AFTER: HISTORICAL_S7_6_V1_BYTE_FOR_BYTE_UNCHANGED, 0 changed.
  Contamination: V1 read 0 target values, 0 external values, computed 0
  predictor-target statistics, fitted 0 models.
  NOT used: V1 pass/fail lists, V1 registry, V1 denominator results, V1
  dependency groups. Every signature regenerated from scratch.
  The ONLY permitted use - an aggregate-count comparison - was performed in
  stage C AFTER the hardened universe and its predicates were written.

SYMBOLIC ENUMERATION - regenerated from P_hard x the frozen catalogue
  C0 70 | C1 63 | C2 2346 | C3 4556 | C4 3906 | C5 68
  C6 4284 | C7 4284 | C8 4284          TOTAL 23,861   exact agreement asserted

ADMISSIBLE ATOMIC UNIVERSE  C_REC_HARD_ATOM_V2
  family                 symbolic  admissible  survival
  C0 level                     70          66     94.3%
  C1 derivative                63          59     93.7%
  C2 product                 2346        2080     88.7%
  C3 ratio                   4556        2457     53.9%
  C4 phase derivative        3906           0      0.0%
  C5 reciprocal                68          39     57.4%
  C6 level-rate              4284        3776     88.1%
  C7 rate over level         4284        2301     53.7%
  C8 level over rate         4284           0      0.0%
  TOTAL                     23861       10778     45.2%

  rejections by class : E 11,989 | D 1,094      (13,083 total)
  by reason: sign change 10,157 | constant on a required block 1,094 |
             margin below eta 786 | zero value 524 | RMS zero 522
  Every rejection carries an auditable first cause and first rejecting class.
  METADATA GATES B/A/C/G/F: 0 rejections (the frozen operand-eligibility
  rules already encode those conditions; the gates were evaluated
  independently and agree).
  THESE COUNTS ARE NOT EVIDENCE OF IMPORTANCE.

DENOMINATOR RULE - VERIFIED BY HASH, NOT REOPENED
  6d4004eb3ae95067b2a01dddeb90226748cfee7097217d68ab5377ac50ed716d
  reopened false | threshold_changed false | regularisation NONE
  scale RMS(d) | eta = min|d|/RMS(d) >= 0.05 | finite | no sign change
  SCOPE (rule unchanged; only the family set grows with the catalogue):
    LEVEL_DENOMINATOR_STATUS  d = x_j          used by C3, C5, C7
    RATE_DENOMINATOR_STATUS   d = dx_j/dt      used by C4, C8
    no denominator gate: C0, C1, C2, C6

  LEVEL denominators  39 / 68 pass on every required block
    survivors: 33 ECE + bt, ip, prmtan_neped, cerqtit3, cerqtit10, cerqtit11
    failures : all 10 beams, all 4 gas valves, 3 filterscopes, 11 CER chords,
               prmtan_teped
  RATE denominators    0 / 63 pass
    61 fail first on E_DENOM_SIGN_CHANGE, 2 on E_DENOM_RMS_ZERO
    (pinj_21l, pinj_21r - beamlines that never fired)
    3,684 of 3,780 individual cells show a sign change.
    RECOMPUTED FROM SCRATCH on the hardened basis. The historical V1 result
    was not consulted, not assumed, not used to skip an evaluation.

QUALIFICATION 1+2 - ZERO_SURVIVING_PRIMARY_C4 and ZERO_SURVIVING_PRIMARY_C8
  "G_rec^H admitted the constructor family conceptually; the observational
   object failed to support stable primary instances under K_rec's
   numerical-domain condition."
  NOT a claim that either constructor is mathematically invalid.
  Gate NOT weakened. Ontology NOT revised. Neither family removed from the
  catalogue - both remain declared, enumerated and audited (8,190 symbolic).
  Shifted / bounded / local-domain variants are DIFFERENT constructors
  requiring their own prospective declaration; S7.11 sensitivity only.
  C6 - the one new family with NO denominator - survives at 88% and is now
  the LARGEST admissible family. The level-rate gap is filled, just not by
  the two quotient-form families.

QUALIFICATION 3 - ZERO_BINDING_EXACT_DEPENDENCY_GROUPS
  pinj = sum_b pinj_b, RE-DERIVED over C0-C8, not copied from V1.
  Exact in 8 contexts, 400 candidate groups of 9 members each:
    C0 1 | C1 1 | C2 59 | C3 59 | C4 54 | C6 54 (agg as level)
    C6 59 (agg as rate, via derivative linearity) | C7 59 | C8 54
  NO identity inferred where the aggregate is a DENOMINATOR
    RATIO(z,pinj) PHASE(z|pinj) RATE_OVER_LEVEL(z|pinj) LEVEL_OVER_RATE(z|pinj)
  NO identity under RECIP(pinj) (not linear) or PROD(pinj,pinj) (quadratic).
  ALL 400 VACUOUS, 0 BINDING: pinj_15r, pinj_21l, pinj_21r and pinj_33l are
  themselves class-D inadmissible (identically constant on at least one
  required calibration block - those beamlines were inactive), so no
  admissible support can contain a complete exact set.
  Phi_dependency is RETAINED: correct, costless, and a different cohort or
  block geometry would make it bind. Both tables written out.
  Neither the aggregate nor the component representation is privileged.

QUALIFICATION 4 - SEARCH_POLICY_MULTIPLICITY_CONTROL_REQUIRED -> S7.7
  NOT SOLVED HERE. 0 coordinates deleted for it. 0 weights assigned.
  ECE is 47.1% of P_hard but an ANCESTOR OF 84.2% of admissible atoms, and
  33 of the 39 surviving LEVEL denominators are ECE channels. Because C3, C5
  and C7 exist only where a level denominator survives, those three families
  are MORE ECE-concentrated than the basis is. This follows from which
  signals are strictly positive and smooth, not from an admissibility defect.
  ADMISSIBLE != PRIORITIZED.

FACTORIZED A_REC^H - not materialized
  S_rec^H = { C subset C_rec_hard^atom : 1 <= |C| <= 12, Phi_set(C) = PASS }
  A_rec^H = { (C, T_REC_V1) : C in S_rec^H }
  Phi_set = size 1-12 | no duplicate IDs | atoms only | no sensitivity-only
            | no COMPLETE exact dependency group | target absent
  NOT imposed: must contain a phase derivative | must span families | must
  include raw levels | must include a partial map | any heuristic, weight,
  ranking or preference.

EXTERNAL PARTIAL-MAP RULE - frozen without opening a value
  Same rule on each external local-calibration block. On failure: do NOT
  shift, do NOT regularise, do NOT replace, do NOT refit - record the
  discharge/block as NOT_APPLICABLE. Omega_rec decided downstream.
  NO EXTERNAL VALUE INSPECTED IN THIS STAGE.

HISTORICAL V1 vs HARDENED V2 - AUDIT ONLY, no rule changed as a result
                    V1 (78 prim, C0-C4)   V2 (70 prim, C0-C8)
  symbolic                      13,604              23,861   (1.75x)
  atoms                          6,034              10,778   (1.79x)
  survival rate                  44.4%               45.2%
  C0/C1/C2/C3/C4 atoms   74/66/2628/3266/0    66/59/2080/2457/0
  C5/C6/C7/C8 atoms                    -        39/3776/2301/0
  The four new families contribute 6,116 atoms; the narrower basis removes
  ~1,372 from the original five. The S7.5H expectation that the broadening
  might add only the 68 C5 coordinates was TOO PESSIMISTIC.

ACCESS AUDIT - FIREWALL_INTACT
  development shots read 20 | predictor signals read 70 (exactly P_hard)
  calibration blocks A, B, C | min block length 130 samples (required 30)
  DENSITY TARGET VALUES ACCESSED  0
  EXTERNAL VALUES ACCESSED        0
  models 0 | baselines 0 | predictor-target correlations 0
  H0_RAW_HARDENED frozen and NOT RUN | B2 unchanged and NOT RUN
  neither used in admissibility | no ranking | no search | no priority

S7.6R key hashes
- parent verification        e9a638f9112321214f49d426c8a8de112442a517...
- denominator rule (parent)  6d4004eb3ae95067b2a01dddeb90226748cfee70...
- A_REC_HARDENED             440643e9a77a53ff97b1ffd797f93792edb29507...
- atomic universe            80b6bf5ffb7ccadf42306f4565a92d86d732cd59...
- Phi_set constraints        68eeca075ed84c4aa4cb366504cfc08d39137f6b...
- symbolic registry          575ff6eb607d2d2b026cceaa5bc5439ffdd0acac...
- atomic universe csv        2933f11ad5699a89bb6519f6a809fb882b7a1286...
- coordinate admissibility   7268d881cadc620850942d886b8d2edc00b61fec...
- denominator audit          3e5b6c1081dfdc37e7a6f337418ffe7838d3d233...
- partial map record         a66f8f7640ef6459ec287fb897eb054cd85a3831...
- dependency groups          1af89959958f3c4849cc06b0409558861276dd65...
- multiplicity handoff       ccac51a046347ae9efc05910ac25f2cb9cefb417...
34 artifacts | 5 markdown

THREE THINGS FOR S7.7, NOT FOR A REVISION OF S7.6R
1. Two of nine families contribute nothing. That is settled and must not be
   revisited by weakening the gate.
2. Phi_dependency binds nothing today. Keep it anyway.
3. The multiplicity problem S7.5H could not solve is SHARPER in the atomic
   universe (84.2% ECE ancestry vs 47.1% of the basis). S7.7 must control
   exploration by scientific family, frozen PROSPECTIVELY, before any
   coordinate is scored.

--------------------------------------------------------------------------
S7.7 - Frozen search policy and explored frontier   BLOCKED_SEARCH_BUDGET
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.7-FROZEN-SEARCH-POLICY-AND-EXPLORED-FRONTIER-V1
Sigma_rec: FROZEN_PREVALUE_COMPLETE_BUT_NOT_EXECUTED
Ahat_rec:  NOT_CONSTRUCTED, cardinality 0
ACCEPTANCE: 34/34 reached | 6 NOT REACHED (gated by the block, never "passed")
PARENTS VERIFIED: all 11 lineage freezes - 0 hash drift

>> THE BLOCK (section 16), evaluated from METADATA ONLY
   atomic scoring                                       10,778
   main lane      252 seeds x 11 steps x 127 proposals = 352,044
   raw-only lane   14 seeds x 11 steps x   7 proposals =   1,078
   MAXIMUM PROJECTED                                    363,900  over by 63,900
   STRICT LOWER BOUND                                   346,484  over by 46,484
   MAX_SUPPORT_EVALUATIONS                              300,000
   EVEN THE STRICT LOWER BOUND OVERRUNS. This is not a loose-bound artifact:
   no execution of this policy can come in under 300,000.
   The binding term is 127 proposals per growth step, which is
   metadata-determined - round 1 of the round-robin gives EVERY stratum a
   shortlist slot, so all 127 strata propose at every step.

   NOT DONE: policy not truncated | policy not changed to fit | no seed count,
   cap, stratum or support bound adjusted | no admissible coordinate pruned |
   no density value opened | no atom scored.

>> HUMAN DECISION REQUIRED - remedies COMPUTED, none CHOSEN
   option                                   max projected   fits 300,000
   SEEDS_PER_STRATUM = 1                          188,736   YES
   SEEDS_PER_STRATUM = 2 (current)                363,900   no
   raise MAX_SUPPORT_EVALUATIONS >= 363,900       363,900   redefines the gate
   Seeds=1 keeps every stratum's starting path but drops the second
   independent start; raising the allowance changes NO search semantics.
   EITHER MUST BE RE-FROZEN PROSPECTIVELY with a new policy hash before any
   density value is opened. Amending after target outcomes would make the
   stage SEARCH_POLICY_CONTAMINATED.
   NON-LEVERS: lowering the 96 cap (proposals scale with STRATA, not atoms;
   a cap below a constructor's stratum count trips the section-13 STOP) |
   reducing the support bound (forbidden) | counting deduplicated supports
   (not computable from metadata, so it cannot certify the budget BEFORE
   target access) | pruning coordinates (inverts ADMISSIBLE != PRIORITIZED).

PRE-SEARCH CONTRACT COMPLETED AND HASHED BEFORE ANY TARGET ACCESS
  PRE_SEARCH_CONTRACT_COMPLETION.json  sha 1b8df4c0672686be21665c00aaf4fc8f
  S_PERS_V1  REQUIRED_REPORTING
    S_pers(M,s,b) = 1 - MSE(M,s,b)/MSE(B1,s,b) on IDENTICAL protected samples
    MSE(B1)==0 -> UNDEFINED_ZERO_PERSISTENCE_ERROR.  NO EPSILON.
    discharge level 1 - mean_b MSE(M,s,b) / mean_b MSE(B1,s,b)
    cohort summaries operate on discharge-level values
    does NOT replace frozen NRMSE | does NOT change V3, whose mandatory gate
    remains exactly the already-frozen paired NRMSE condition
    NOT used to guide search
  B1A_AR1  DIAGNOSTIC_BASELINE, REQUIRED_TO_REPORT
    calibration OLS y_k = a + phi y_{k-1} + eps_k
    protected block: initialise with the FINAL CALIBRATION target value,
    predict recursively, NEVER update the recursion with protected values,
    a and phi frozen over that block
    lag 1 | no additional lags | no hyperparameter selection | no teacher
    forcing | NOT a replacement for B1 | NOT added to mandatory V3 thresholds
  NEITHER RUN. Both belong to S7.9/S7.10 with B0-B3 and H0_RAW_HARDENED.

PRE-VALUE SEARCH POLICY FROZEN
  SEARCH_POLICY_PREVALUE.json  sha a97e690e414da7a0ace4c70ab56e7d5851eb73f9
  Contains every decision of sections 5-15. Stages A and B contain NO
  data-loading code path at all, so the ordering is structural.

SEARCH STRATA - metadata only, exactly one stratum per atom
  127 ACTIVE STRATA over all 10,778 admissible atoms
  constructor  atoms  strata  shortlist  seeds   signature
  C0              66       7         66     14   (family_i)
  C1              59       5         59     10   (family_i)
  C2            2080      28         96     56   {family_i, family_j} UNORDERED
  C3            2457      28         96     55   (numerator | denominator)
  C5              39       4         39      7   (family_i)
  C6            3776      35         96     70   (level | rate)
  C7            2301      20         96     40   (rate | denominator level)
  TOTAL        10778     127        548    252
  C4, C8: no admissible atoms -> no active strata.
  SECTION 13 CAP-SUFFICIENCY GATE: PASS (96 >= 35, the largest per-constructor
  stratum count), so every nonempty stratum receives a shortlist slot.

MULTIPLICITY CONTROL WORKS - measurable from metadata, before any value read
  family        prims  atom ancestry  projected seed share  amplification removed
  ECE              33          0.842                 0.310          -0.532
  CER              14          0.347                 0.310          -0.037
  NBI              10          0.144                 0.222          +0.078
  gas               4          0.097                 0.222          +0.125
  magnetics         4          0.071                 0.310          +0.238
  filterscope       3          0.045                 0.135          +0.090
  density-aux       2          0.041                 0.222          +0.181
  (shares sum > 1: a pairwise stratum touches two families)
  ECE falls from 84.2% of ATOMIC ANCESTRY to 31.0% of PROJECTED SEED
  OPPORTUNITY. The section-22 criterion - initial search opportunity NOT
  proportional to raw atomic multiplicity - is MET BY CONSTRUCTION.
  Whether ECE still dominates AFTER equalized opportunity is UNKNOWN and
  unknowable from this stage: that is answered by retained paths, and no path
  was run.

CONSTRUCTOR OPPORTUNITY (shortlist/seed shares vs atom share)
  C6  35.0% of atoms -> 17.5% of shortlist slots
  C0   0.6% of atoms -> 12.0% of shortlist slots
  C4, C8: DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS / ZERO_SEARCH_OPPORTUNITY
  - an inherited S7.6R admissibility outcome, NOT a search exclusion. Not
  rescued, not shifted, not bounded.

SEARCHED / UNSEARCHED BOUNDARY
  admissible atomic coordinates        10,778
  Ahat_rec size-1 supports                  0
  unique multivariate supports scored       0
  total unique supports in Ahat_rec         0
  EVERY admissible support of every size is ADMISSIBLE_UNSEARCHED.
  NO NEGATIVE SCIENTIFIC CLAIM may be made about any coordinate or support.
  The terms "global optimum", "exhaustive search" and "complete search" do
  not apply and are not used.

ACCESS AUDIT - FIREWALL_INTACT_NO_ARCHIVE_OPENED
  archives opened 0 | development target values 0 | development predictor
  values 0 | external signal values 0 | external target values 0
  atoms scored 0 | baselines run 0 | models fitted 0
  no C* | no R* | no Q_rec* | no validation claim
  A_rec, G_rec, target, P_hard, C0-C8, denominator rule, support bound 1-12
  and T_REC_V1 ALL UNCHANGED.

S7_7_SEARCH_POLICY_AND_FRONTIER_FINAL.md DELIBERATELY NOT WRITTEN
  The section-25 manuscript section is built around the explored frontier.
  There is no explored frontier. Writing it would describe exploration that
  did not happen. It is the first thing to produce on re-run.

S7.7 key hashes
- parent verification         800315b4811674ba9631f17f71b5221d130f5aa9...
- PRE_SEARCH_CONTRACT         1b8df4c0672686be21665c00aaf4fc8f36ab9e53...
- SEARCH_POLICY_PREVALUE      a97e690e414da7a0ace4c70ab56e7d5851eb73f9...
- search budget block         5974b484ffa2c297aac41774293ca107a4dcac00...
- search strata               267c44449eba26bf4ed45c7f808977ed20c3744a...
- atom stratum assignment     75aad6762fe716c7b3cc5bc9ea82b9d5d8595ea4...
- multiplicity audit          033d8e11f1c03110896503582f7bbf1ea689a821...
- constructor audit           9bda66e13e8932dd84e6d7faba51acd7023d1a2a...
19 artifacts | 4 markdown

RE-RUN PATH ONCE THE BUDGET IS DECIDED
1. Decide: SEEDS_PER_STRATUM = 1, or MAX_SUPPORT_EVALUATIONS >= 363,900.
2. Re-freeze PROSPECTIVELY - new SEARCH_POLICY_PREVALUE hash, before any
   density value is opened.
3. Re-run S7.7 from stage B. Stage A carries forward unchanged: parents
   verified, S_pers and B1A_AR1 frozen at 1b8df4c0...
NOTE: the 252-seed figure is driven by having 127 strata, which follows from
the ORDERED pair signatures for C3, C6 and C7 - the price of not collapsing
role-directional relations. That was the right call in S7.5H and remains
right; it simply makes this search intrinsically wider than a five-family
grammar would have made it. If the budget is raised, raise it knowing why.

--------------------------------------------------------------------------
S7.7R - One-seed primary search and explored frontier
                                                 FROZEN_WITH_QUALIFICATIONS
--------------------------------------------------------------------------
FREEZE_ID: D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2
Sigma_rec: SIGMA_REC_ONE_SEED_PRIMARY_V2   FROZEN_AND_EXECUTED
Ahat_rec:  AHAT_REC_DENSITY_ONE_SEED_V2    162,845 supports
ACCEPTANCE: 43/43 PASS
PARENTS VERIFIED: all 12 lineage freezes - 0 hash drift
HISTORICAL S7.7 V1: BLOCKED_SEARCH_BUDGET / PRESERVED_AS_AUDIT_HISTORY,
  re-verified HISTORICAL_S7_7_V1_BYTE_FOR_BYTE_UNCHANGED (21 files, 0 changed).
  V1 opened no archive, scored no atom, ran no baseline, built no frontier, so
  it holds no target-dependent information that could bias this policy.

THE ONE AUTHORISED CHANGE - machine-diffed, 0 unauthorised
  SEEDS_PER_STRATUM        2 -> 1
  raw-only lane seeds      top 2 -> top 1 per C0 scientific family
  projected main seeds     252 -> 127 | raw seeds 14 -> 7
  VERDICT ONLY_SEED_MULTIPLICITY_CHANGED
  UNCHANGED AND VERIFIED: MAX_SUPPORT_EVALUATIONS 300,000 |
  MAX_ATOMS_PER_CONSTRUCTOR_FOR_EXPANSION 96 | support 1-12 | all 10,778 atoms
  scored univariately | 127 active strata | constructor + family-signature
  semantics | SEARCH_PROXY_OLS_V1 | J_search | greedy proposal rule | Phi_set
  The diff runs over the FLATTENED policy trees with an explicit allow-list;
  anything outside it aborts as UNAUTHORISED_SEARCH_POLICY_DRIFT (it did fire
  once in development, on a stray provenance field - the check works).

PRIMARY VS SENSITIVITY - frozen BEFORE density access
  ONE_SEED_SEARCH = PRIMARY
  TWO_SEED_SEARCH = NOT_EXECUTED / OPTIONAL_FUTURE_SEARCH_DEPTH_SENSITIVITY
  NO OUTCOME TRIGGER DEFINED. If later authorised it is a sensitivity
  REGARDLESS of the primary result. It may NOT replace, rescue, redefine or
  retroactively optimize this primary frontier, and may NOT convert a failed
  primary q_rec into a successful primary structural-transfer claim.

PRE-SEARCH CONTRACT CARRIED FORWARD UNCHANGED
  PRE_SEARCH_CONTRACT_COMPLETION.json  sha 1b8df4c0672686be...
  hash-verified, NOT regenerated, NOT modified.
  S_PERS_V1 required reporting, not used for search, does not replace NRMSE,
  does not change V3 | B1A_AR1 diagnostic, required to report later.
  NEITHER RUN.

ORDERING - structural, not procedural
  policy V2 frozen      2026-09-05T00:17:10.479649+00:00  sha 2049cf99...
  first density access  2026-09-05T00:27:42.757620+00:00  ordering verified
  Stages A and C contain no data-loading code path at all. Stage B re-verifies
  the policy hash before opening the first archive and aborts as
  SEARCH_POLICY_CONTAMINATED on mismatch.

BUDGET
  metadata projection  10,778 + 127x11x127 + 7x11x7 = 188,736 (matches spec)
  actual proposals + atomic scoring                 = 188,142
  frozen allowance                                    300,000
  truncated at the limit: NO       verdict SEARCH_BUDGET_RUNTIME_OK
  (594 under projection: some strata exhaust their shortlisted atoms late in a
  path and stop proposing)

ATOMIC SCORING - the first target-dependent q_rec operation
  ALL 10,778 admissible atoms scored | 0 rank-deficient
  J_search  min 0.4801 | median 1.0144 | max 27.5496
  best atom per constructor: C3 0.4801 | C2 0.4937 | C0 0.4996 | C5 0.5563 |
                             C7 0.8965 | C6 0.9744 | C1 0.9814
  NO GLOBAL TOP-K PRUNING. Every atom keeps its score in the registry.

SHORTLIST / SEEDS
  548 shortlisted   C0 66 (all) | C1 59 (all) | C2 96 | C3 96 |
                    C5 39 (all) | C6 96 | C7 96
  every one of the 127 strata represented (verified by set equality)
  10,230 atoms ADMISSIBLE_NOT_IN_EXPANSION_SHORTLIST - NOT inadmissible
  seeds: 127 main (exactly one per active stratum) + 7 raw-only
  no seed was rank-deficient, so SEED_PROXY_RANK_DEFICIENT never fired

SEARCH EXECUTION
  all 127 main paths grew 1 -> 12 | all 7 raw-only paths grew 1 -> 12
  multivariate proposals            177,364
    duplicate proposals within step  25,269
    cache hits across steps               28
    REJECTED BY Phi_set                    0
  unique multivariate supports      152,067
  Phi_set was ENFORCED on every proposal and rejected none - expected, since
  S7.6R found all 400 exact-dependency groups vacuous and the other predicates
  are excluded by construction. The check runs rather than being assumed.

EXPLORED FRONTIER  Ahat_rec = 162,845
  m         1     2     3     4     5     6     7     8     9    10    11    12
  supports 10778 8126 12462 14376 14423 14366 14568 14507 14784 14855 14857 14743
  lowest J .4801 .3390 .2555 .2249 .2059 .2012 .1922 .1860 .1822 .1759 .1690 .1663
  0 rank-deficient designs in the whole frontier.
  m=1 leader RATIO(ece16,cerqtit10); by m=8 the leader spans all 7 families;
  m=12 leader is 2 C0 + 5 C2 + 3 C3 + 2 C5. No C1, C6 or C7 in any leader.
  LABELLED LOWEST_NAVIGATION_SCORE_SUPPORT_AT_SIZE_m, with explicit
  is_optimal/is_qualified/is_final/is_C_star = false. NOT a selection.

RAW-ONLY CONTROL LANE  C0_ONLY_GREEDY (NOT B2)
  J falls 0.4996 (m=1, ID(prmtan_neped)) -> 0.2200 (m=12), flattening after
  about m=9 while the relational lane continues to 0.1663.
  NAVIGATION OBSERVATION ONLY - not a comparison claim, not a baseline result,
  not evidence of relational advantage. B2 remains the frozen full-information
  raw Ridge comparator and was NOT run.

MULTIPLICITY AUDIT - opportunity and outcome kept apart
  family        P_hard  atoms  shortlist  SEEDS  explored  retained  lowest-J
  ECE            0.471  0.842      0.420  0.307     0.958     0.854     1.000
  CER            0.200  0.347      0.310  0.307     0.878     0.709     0.833
  NBI            0.143  0.144      0.172  0.220     0.508     0.382     0.250
  gas            0.057  0.097      0.173  0.220     0.552     0.376     0.500
  magnetics      0.057  0.071      0.232  0.307     0.743     0.705     0.917
  filterscope    0.043  0.045      0.102  0.134     0.716     0.604     0.583
  density-aux    0.029  0.041      0.181  0.228     0.860     0.831     0.917
  (participation shares; a two-family support counts in both, so no column
   sums to 1)

  OPPORTUNITY: BALANCED. ECE 0.842 -> 0.420 -> 0.307, BELOW its own 0.471 share
  of the primitive basis. magnetics 0.071 -> 0.307, density-aux 0.041 -> 0.228,
  gas 0.097 -> 0.220. The section-22 criterion is MET.

  OUTCOME: ECE STILL DOMINATES - 85.4% of retained paths, 100% of lowest-J
  supports. RECORDED AS FOUND, NOT REBALANCED. No family term exists anywhere
  in J_search. Because the opportunity stage had already removed the
  channel-count advantage, this is a substantive development-search finding
  rather than an artefact of how densely the device is instrumented.
  The counterpart is equally real: magnetics appears in 91.7% of the leading
  supports on 5.7% of the basis, density-aux likewise, gas in 50%.

CONSTRUCTOR AUDIT
  cons  atoms  share  shortlist  seeds  seed_sh  explored  retained
  C0       66  0.006         66      7    0.055     0.597     0.565
  C1       59  0.005         59      5    0.039     0.071     0.056
  C2     2080  0.193         96     28    0.220     0.765     0.706
  C3     2457  0.228         96     28    0.220     0.902     0.778
  C5       39  0.004         39      4    0.031     0.588     0.419
  C6     3776  0.350         96     35    0.276     0.511     0.046
  C7     2301  0.213         96     20    0.157     0.368     0.026
  C4, C8: DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS / ZERO_SEARCH_OPPORTUNITY
  - inherited from S7.6R, NOT a search exclusion, NOT rescued.

  >> FLAG FOR S7.8: C6 and C7 - the level-rate constructors S7.5H introduced -
  >> hold 56.3% of all admissible atoms between them, received 43.3% of seed
  >> opportunity, and were retained on 4.6% and 2.6% of path supports. Their
  >> best single coordinates score 0.974 and 0.897 against 0.480 for the best
  >> ratio, and neither appears in ANY lowest-J support. On this target under
  >> this proxy, the grammar broadening that made the ontology 1.75x larger
  >> contributed almost none of the retained structure. A development-search
  >> observation, NOT a qualification result. S7.8 should ask this deliberately.

SEARCHED / UNSEARCHED BOUNDARY
  admissible atomic coordinates                             10,778
  Ahat_rec size-1 supports (ALL scored)                     10,778
  unique multivariate supports scored                      152,067
  total unique supports in Ahat_rec                        162,845
  unconstrained admissible supports of size 1..12    ~5.10 x 10^39
  ADMISSIBLE_UNSEARCHED                              ~5.10 x 10^39
  fraction actually scored                            3.19 x 10^-35
  NOT SEARCHED != INADMISSIBLE. No property was tested outside Ahat_rec and NO
  NEGATIVE CLAIM of any kind attaches to it. The words "global optimum",
  "exhaustive search" and "complete search" do not apply and are not used.

NUMERICAL PROVENANCE OF THE PROXY
  SEARCH_PROXY_OLS_V1 solved in partitioned (Frisch-Waugh) form - intercept
  absorbed by centring, slopes from the normal equations of the centred
  calibration design; algebraically identical to numpy.linalg.lstsq on [1, Z]
  for a full-rank design. VERIFIED against lstsq on 48 random supports across
  sizes 2/5/9/12: MAX RELATIVE DEVIATION 1.72e-13 (tolerance 1e-9) PASS.
  Rank deficiency detected from the centred Gram eigenvalues
  (sqrt(min/max) <= max(n_prot, m+1)*eps) -> J_search = +infinity and
  SEARCH_PROXY_RANK_DEFICIENT - NEVER inadmissibility. None occurred.

ACCESS AUDIT - FIREWALL_INTACT
  development shots 20 | predictor signals 70 | target density (development)
  EXTERNAL SIGNAL VALUES 0 | EXTERNAL TARGET VALUES 0 | external shots 0
  baselines run 0 (B0, B1, B1A_AR1, B2, B3, H0_RAW_HARDENED all untouched)
  S_pers computed 0 | U_rec NOT applied | no C*, R*, Q_rec* | no qualified
  candidate | no validation claim | no two-seed search
  A_rec, G_rec, P_hard 70, C0-C8, denominator rule, support bound 1-12,
  T_REC_V1, strata definitions and Phi_set ALL UNCHANGED.

S7.7R key hashes
- parent verification         b5ba1d33222f11db5bf5454d25762b9c6f78635e...
- PRE_SEARCH_CONTRACT (carry) 1b8df4c0672686be21665c00aaf4fc8f36ab9e53...
- SEARCH_POLICY_PREVALUE V1   a97e690e414da7a0ace4c70ab56e7d5851eb73f9...
- SEARCH_POLICY_PREVALUE V2   2049cf999dd99c0a1c5aa7f3539a7caaedbae817...
- SIGMA_REC_V2                13d2cf08e362b5c2a55f2c952d6a0a7869b1cdb2...
- AHAT_REC_V2                 b09080826da5c73cd603db8ab8f45b1e4dd58e6d...
- explored support registry   a2c253d0a1f6f6a0bf7a27f664f7bdee233d2cb2...
- atomic navigation scores    2e5c8ea2076102215e525deca1f78ddce5bec1e3...
- search seed registry        16f2bb6100d5f178aeb3ce84bd5edcfe3380804d...
- proposal provenance         905866f857e8a6fe39217b50935730afbd9966bc...
- multiplicity audit          7ef60d0999286c15737dd644c8351bc0578701dc...
41 artifacts | 5 markdown

THREE QUALIFICATIONS
1. ECE dominance after balanced opportunity (85.4% retained, 100% lowest-J
   against a 30.7% seed share). Reported, not corrected.
2. One-seed depth: broad in opportunity, shallow in multi-start. Reduced
   protection against greedy-start sensitivity, accepted prospectively.
3. Coverage 3.19e-35 of the size-1..12 support space; the remainder is
   ADMISSIBLE_UNSEARCHED and carries no negative finding.

NEXT_STAGE: none authorised. S7.12 paused; optional all-data descriptive support awaits separate authorisation.
