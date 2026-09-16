# S7.1R-FINAL — Source-of-truth map

Machine-readable form: `SOURCE_ARTIFACT_INVENTORY.csv`.

Path names were not trusted. Every artifact below was opened and classified by
what it actually does.

## The hierarchy

```
PRIMARY_SOURCE      the 62-shot archive and the code that reads it
  data/resampled_data_v6/shot_*.npz            the observational object itself
  data/resampled_data_v6/shot_*_metadata.json  per-signal resampling records -> A
  sir-web/providers/diiid_elm_data_provider.py full 95-signal provider
  Paper Examples/diiid_elm_data_provider.py    canonical 8-signal Paper provider

MANIFEST            what is declared to load, and in what units
  DIIID_example/diiid_sir_data_provider.py     frozen 95-signal manifest
  S7/SIGNAL_UNITS.json                         frozen units registry

BACKEND_INTERFACE   how the object is reached interactively
  dalia project 36a4813a... data_provider.py v164   95/95 catalog parity

DERIVED_DATA / SUMMARY_EXPORT   products, not sources
  SIR_to_dFL_provider_..._with_phaseders.py    feature-export provider
  sir-web/FEATURE_EXPORTS/pcdiamag3_none_...   target-conditioned bundle

DOCUMENTATION
  D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md   449-line ledger
  build_d3d_discharge_ledger.py                        independent grid check
  General/sir_representational_prism.py                architecture figure source

LEGACY_RESULT
  S7/_legacy_reference/LEGACY_QREC_STATUS.md   retired q_rec firewall

UNKNOWN / ABSENT
  smallELM_freq_v6_ZL_data/{shot}_metadata.json   cited units source, NOT LOCAL
```

## Three things worth stating plainly

**The archive is the object.** `resampled_data_v6` is where O begins. Everything
above it in the acquisition chain is outside what this study possesses.

**The units registry is authoritative-as-received, not re-derivable.** It cites
`smallELM_freq_v6_ZL_data/{shot}_metadata.json` as its source and
`build_signal_units.py` as its generator. **Neither is present in any local
tree.** The registry's internal evidence is strong — it records per-shot unit
variant counts across all 62 discharges, which is the signature of a real audit
rather than an assertion — but it is classified `LOCAL_DOCUMENTED`, not
`CODE_VERIFIED`, because it cannot be reproduced here.

**Three surfaces are routinely confused.** The 95-signal provider, the 8-signal
Paper provider, and the dFL feature export are different things with different
purposes. See `PROVIDER_SURFACE_COMPARISON.md`.
