"""Step 24 — machine-readable result artifacts."""
import hashlib, json, platform, sys
from pathlib import Path
import numpy as np, pandas as pd

T = Path(__file__).resolve().parent.parent
res = pd.read_csv(T/"tables"/"confirmation_results.csv")
per = pd.read_csv(T/"tables"/"confirmation_per_trajectory.csv")
sel = json.loads((T/"contracts"/"contract_selections.json").read_text())
mcp = json.loads((T/"sir_mcp"/"containment"/"mcp_containment.json").read_text())
fr  = json.loads((T/"PRECONFIRMATION_FREEZE.json").read_text())

# containment.csv
rows=[]
for eq,r in mcp["runs"].items():
    for k,v in r["true_coefficients"].items():
        rows.append({"equation":eq,"term":k,"true":v,"sir_mcp":r["coefficients"][k],
                     "abs_error":abs(v-r["coefficients"][k]),"run_id":r["run_id"],
                     "final_error":r["final_error"],
                     "support":mcp["support_recovery"][eq]})
pd.DataFrame(rows).to_csv(T/"tables"/"containment.csv",index=False)

# contract_selections.csv
rows=[]
for q,s in sel.items():
    i=s["selection_info"]
    rows.append({"contract":q,"selected":s["selected_candidate"],
                 "n_coordinates":s["n_coordinates"],"n_features":s["n_features"],
                 "n_terms":s["n_terms"],"condition_number":s["condition_number"],
                 "coverage":s["coverage"],"mean_cv_utility":s["mean_cv_utility"],
                 "se_cv_utility":s["se_cv_utility"],
                 "fold_stability":s["fold_stability"],
                 "n_equivalent":i.get("n_equivalent",1),
                 "margin_source":i.get("margin_source","n/a"),
                 "equivalent_set":"; ".join(i["equivalent_set"]),
                 "coordinates":"; ".join(s["coordinates"])})
pd.DataFrame(rows).to_csv(T/"tables"/"contract_selections.csv",index=False)

# comparator splits
res[res.method=="STLSQ"].to_csv(T/"tables"/"pysindy_comparators.csv",index=False)
res[res.method=="MLP"].to_csv(T/"tables"/"mlp_comparators.csv",index=False)
res[res.regime.str.startswith("noise")].to_csv(T/"tables"/"noise_robustness.csv",index=False)
res[["regime","method","representation","n_coordinates","n_features","n_terms",
     "condition_number","coverage"]].to_csv(
    T/"tables"/"representation_complexity.csv",index=False)

# summary tex
lbl={"C0_matched":r"$\mathcal{C}_0$","C0_poly2":r"$\mathcal{C}_0$ poly2",
     "C0_poly3":r"$\mathcal{C}_0$ poly3","C_all":r"$\mathcal{C}_{\rm all}$",
     "C*_accuracy":r"$\mathcal{C}^{*}_{\rm acc}$",
     "C*_compact":r"$\mathcal{C}^{*}_{\rm cmp}$",
     "C*_robust":r"$\mathcal{C}^{*}_{\rm rob}$"}
lines=[]
for reg in ("clean",[r for r in res.regime.unique() if r.startswith("noise")][0]):
    for _,r in res[(res.regime==reg)&(res.method=="STLSQ")].iterrows():
        lines.append(f"{lbl.get(r.representation,r.representation)} & "
                     f"{reg.replace('_',' ')} & {int(r.n_coordinates)} & "
                     f"{r.pooled_rmse:.4g} \\\\")
tex=("\begin{tabular}{llrr}\n\hline\nRepresentation & Regime & "
     "$|\mathcal{C}|$ & confirmation RMSE \\\n\hline\n"
     +"\n".join(lines)+"\n\hline\n\end{tabular}\n")
(T/"tables"/"benchmark_summary.tex").write_text(tex,encoding="utf-8")

# run manifest
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()[:16]
arts={}
for p in sorted(T.rglob("*")):
    if p.is_file() and p.suffix in {".csv",".json",".txt",".yaml",".tex",".py",".md"}:
        arts[str(p.relative_to(T)).replace("\\","/")]=sha(p)
man={"benchmark":"lorenz_task_conditioning",
     "sir_implementation_status":fr["sir_implementation_status"],
     "python":sys.version.split()[0],"platform":platform.platform(),
     "selections":fr["selections"],
     "practical_equivalence_abs":fr["practical_equivalence_abs"],
     "confirmation_trajectories":int(per.trajectory.nunique()),
     "n_artifacts":len(arts),"artifact_sha256_prefix":arts}
(T/"benchmark_run_manifest.json").write_text(json.dumps(man,indent=2),encoding="utf-8")
print("wrote 8 tables + manifest")
for f in sorted((T/"tables").glob("*")): print("  ",f.name)
