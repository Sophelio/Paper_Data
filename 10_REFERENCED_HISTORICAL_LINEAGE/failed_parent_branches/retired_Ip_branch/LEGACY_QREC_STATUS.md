# Legacy q_rec — status

    STATUS: RETIRED
    USE IN S7: NOT USED FOR TARGET, ONTOLOGY, OR OBSERVATIONAL-OBJECT SELECTION

## Retirement record

`DIIID_example/fig6data/RETIREMENT_RECORD.json`
(`D3D-FIG6-QREC-RETIREMENT-V1`), with the supporting audit at
`DIIID_example/Figure6_qualification_audit/FIGURE6_QUALIFICATION_AUDIT_REPORT.md`.

The retired artifact `Figure_data/d3d_reconstruction_summary.json` is preserved
byte-for-byte and was not modified.

## Why it was retired

1. **Target-provenance leakage.** 6/10 of the selected relational features and
   4/10 of the comparator features carried upstream dependence on the
   reconstruction target. One admitted quantity was very nearly an algebraic
   function of the target in this archive.
2. **No demonstrated skill.** A constant persistence predictor outperformed all
   three reported models on the protected evaluation window, which carried
   roughly 0.3% of the calibration-segment variance.

## Firewall for S7

The following were deliberately **not** consulted when constructing the S7.1
observational object:

* the retired admissible set and its eight-signal reduction;
* the retired selected supports (REL10 / REL141) or the comparator (RAW10);
* any reconstruction performance number from the retired branch;
* the retired target.

The S7.1 census enumerated all 95 quantities directly from the archives. The
historical eight appear in `signal_inventory.csv` only as a boolean provenance
flag (`historical_eight`), and the historical cohort roles appear in
`shot_inventory.csv` only as provenance flags. Neither influenced inclusion.

**S7.2 must not assume the target is plasma current.** The retired study's target
carries no privileged status, and selecting it again on the strength of the
retired result would reintroduce exactly the reasoning that was retired.
