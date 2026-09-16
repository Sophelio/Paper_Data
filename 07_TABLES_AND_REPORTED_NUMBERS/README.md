# Tables and reported numbers

## The claim ledger

`numerical_claims/claim_ledger.json` and
`00_START_HERE/CLAIM_TO_ARTIFACT_INDEX.csv` map every major numerical claim to a
canonical machine-readable artifact, with the exact field or column.

Every value was **re-extracted from the artifacts**, not transcribed from the
manuscript, so displayed rounding never becomes the source of truth. The ledger
carries both the rounded value as displayed and the full-precision value.

Three statuses appear:

| status | meaning |
|---|---|
| `VERIFIED` | the artifact reproduces the claim |
| `VERIFIED_BUT_MANUSCRIPT_DISAGREES` | the artifact is canonical and the staged manuscript says something else |
| `VERIFIED_MISSING_FROM_MANUSCRIPT` | the artifact exists and the manuscript does not report it at all |

The last two categories exist because the staged manuscript is stale on the
reconstruction branch.

## Tables

`00_START_HERE/TABLE_TO_SOURCE_INDEX.csv` maps each manuscript/Supplement table
to the artifact behind it.
