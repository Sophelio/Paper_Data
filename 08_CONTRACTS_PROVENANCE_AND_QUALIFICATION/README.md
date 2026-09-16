# Contracts, provenance and qualification

Most contract and qualification material lives with the stage that produced it,
under `05_DIII_D_RECONSTRUCTION/`, so that chronology is preserved. This folder
holds the cross-cutting records.

| Where to look | What it holds |
|---|---|
| `05_.../00_Pretarget_Contract/` | `K_REC_PRE`, cohort partition, validation protocol, baseline protocol, claim boundary |
| `05_.../09_Range_Support_Case_B_Revision/` | `K_REC_V2`, the V1→V2 changeset, range-support policy |
| `05_.../11_Descendant_Case_C_Contract/` | Epoch-2 protocol, access policy, search budget, qualification policy, stop rule |
| `05_.../18_Machine_Readable_Lineage/` | stage index, **revision ledger**, information-flow audit, claim-evidence matrix, architecture map |
| `04_DIII_D_DESCRIPTIVE/.../Correction_audit/` | the correction that superseded the original conditioning verdict |
| `artifact_lineage/` | the transform-family audit |

## The revision ledger

`05_.../18_Machine_Readable_Lineage/REVISION_LEDGER.md` classifies every
revision in the reconstruction lineage as one of:

- **Case A** — an object was instantiated incorrectly; contract adequate.
- **Case B** — every object satisfied the contract as written, but the
  operational contract was incomplete.
- **Case C** — a claim-defining commitment materially changed, producing a
  descendant claim branch under the same task.

That table is the fastest way to see what changed after the qualification
failure, and why each change was legitimate rather than post hoc tuning.
