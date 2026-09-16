# DIIID_example (DIIID_SIR_Paper)

Self-contained Dalia project for the DIII-D ELM / SIR paper example.

## Layout

- `.dalia/projects/` — Dalia project document (`DIIID_SIR_Paper`)
- `data/resampled_data_v6/` — NPZ shot archive used by the provider
- `autolabeling_utilities.py` — ELM burst detectors imported by `autolabelers.py`
- `models/plasma_mode_model.onnx` — optional Fusion-sample plasma-mode classifier

Provider file `transforms.py` is the implementation. Matching `blocks/*.py`
wrappers re-export those transforms so they appear in **both** dFL and SIR prep
(SIR prep only discovers `blocks/*.py`, not provider `custom_transform_dictionary`).

## Load in Dalia

From the dalia repo (or installed `dalia.exe`):

```powershell
$env:DALIA_PROJECTS_DIR = "D:\SIR_paper\DIIID_example\.dalia\projects"
.\scripts\run.ps1
```

Open **DIIID_SIR_Paper** from Home (activates its Python env with `onnxruntime`), then reload the provider if needed.

To return to the normal projects folder later, stop Dalia and start without `DALIA_PROJECTS_DIR`.
