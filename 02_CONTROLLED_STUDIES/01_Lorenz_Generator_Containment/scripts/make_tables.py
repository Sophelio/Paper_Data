"""Step 13 — machine-readable result artifacts."""
import hashlib, json, platform, sys
from pathlib import Path
import pandas as pd, numpy as np

B = Path(__file__).resolve().parent.parent
res = pd.read_csv(B/"tables"/"benchmark_results.csv")
abl = pd.read_csv(B/"tables"/"ablation_results.csv")
fr = json.loads((B/"sir"/"frozen_selection"/"FROZEN_REPRESENTATION.json").read_text())

# ---- summary ----
piv = res.pivot_table(index="representation", columns="learner",
                      values=["test_rmse","test_r2","n_coordinates"])
summ = res[["representation","learner","n_coordinates","n_terms","test_rmse",
            "test_r2","ci_lo","ci_hi","cond_number"]].copy()
order = {"C0_center":0,"C0_matched":1,"C_all":2,"C_star":3}
summ["_o"]=summ.representation.map(order); summ=summ.sort_values(["_o","learner"]).drop(columns="_o")
summ.to_csv(B/"tables"/"benchmark_summary.csv", index=False)

# ---- LaTeX ----
lbl={"C0_center":r"$\mathcal{C}_0^{\mathrm{center}}$","C0_matched":r"$\mathcal{C}_0$",
     "C_all":r"$\mathcal{C}_{\mathrm{all}}$","C_star":r"$\mathcal{C}^{*}$"}
rows=[]
for _,r in summ.iterrows():
    rmse = f"{r.test_rmse:.3g}"
    rows.append(f"{lbl[r.representation]} & {r.learner} & {int(r.n_coordinates)} & "
                f"{rmse} & {r.test_r2:.6f} \\\\")
tex = ("\begin{tabular}{llrrr}\n\hline\n"
       "Representation & Learner & $|\mathcal{C}|$ & test RMSE & $R^2$ \\\n\hline\n"
       + "\n".join(rows) + "\n\hline\n\end{tabular}\n")
(B/"tables"/"benchmark_summary.tex").write_text(tex, encoding="utf-8")

# ---- run manifest ----
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20), b''): h.update(c)
    return h.hexdigest()
artifacts={}
for p in sorted(B.rglob("*")):
    if p.is_file() and p.suffix in {".csv",".json",".txt",".yaml",".tex",".py",".md"}:
        if ".venv" in str(p): continue
        artifacts[str(p.relative_to(B)).replace("\\","/")]=sha(p)[:16]
man={
  "benchmark":"lorenz_nested_representation",
  "python":sys.version.split()[0],
  "platform":platform.platform(),
  "frozen_representation_sha256":fr["sha256"],
  "C_star":fr["selected_coordinates"],
  "splits":{k:len(v) for k,v in fr["splits"].items()},
  "support_retained_fraction":fr["support_retained_fraction"],
  "n_artifacts":len(artifacts),
  "artifact_sha256_prefix":artifacts,
}
(B/"benchmark_run_manifest.json").write_text(json.dumps(man,indent=2),encoding="utf-8")
print("wrote benchmark_summary.csv/.tex and benchmark_run_manifest.json")
print(summ.to_string(index=False,float_format=lambda v:f"{v:.6g}"))
