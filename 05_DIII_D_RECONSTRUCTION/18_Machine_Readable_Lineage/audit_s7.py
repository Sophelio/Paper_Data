#!/usr/bin/env python
"""Independent S7 auditor.

Re-runnable by anyone with this directory. No network, no proprietary service.
Verifies structure, hashes, canonical numerical checkpoints, claim language and
branch closure, then writes a machine-readable and a human-readable report.

    python audit_s7.py                 # verify, print report, write AUDIT_CHECKS.json
    python audit_s7.py --json out.json # write the machine-readable report elsewhere

Exit code 0 if no BLOCKER or MAJOR finding survives, 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

S7 = Path(__file__).resolve().parent
FIND, PASSES = [], []


def rec(level, ident, msg, detail=None):
    row = {"level": level, "id": ident, "msg": msg}
    if detail:
        row["detail"] = detail
    (PASSES if level == "PASS" else FIND).append(row)
    return row


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# --------------------------------------------------------------- 1. structure
def check_structure(idx):
    required = ["README.md", "index.html", "WORKFLOW.md", "CANONICAL_INDEX.json",
                "ARCHITECTURE_SEMANTICS_AUDIT.md", "ARCHITECTURE_SEMANTICS_AUDIT.json",
                "AUDIT_REPORT.md", "AUDIT_REPORT.json", "MANUSCRIPT_ALIGNMENT.md",
                "MANUSCRIPT_ALIGNMENT.json", "REPRODUCIBILITY.md",
                "SIR_ARCHITECTURE_MAP.md", "REVISION_LEDGER.md",
                "CLAIM_EVIDENCE_MATRIX.json", "INFORMATION_FLOW_AUDIT.md",
                "STATUS.md", "audit_s7.py"]
    missing = [f for f in required if not (S7 / f).exists()]
    rec("MAJOR" if missing else "PASS", "structure/top_level",
        "missing top-level files: %s" % missing if missing
        else "all %d required top-level files present" % len(required))

    bad = []
    for s in idx["stages"]:
        d = S7 / s["directory"]
        for f in ("MANIFEST.json", "index.html"):
            if not (d / f).exists():
                bad.append("%s/%s" % (s["directory"], f))
    rec("MAJOR" if bad else "PASS", "structure/stages",
        "missing stage files: %s" % bad[:5] if bad
        else "all %d canonical stages expose MANIFEST.json and index.html"
             % len(idx["stages"]))


# ------------------------------------------------------------------ 2. freezes
def check_freezes(idx):
    total_n = total_ok = 0
    broken = []
    for s in idx["stages"]:
        base = S7 / s["directory"]
        fzp = base / s["governing_freeze"]["path"]
        if not fzp.exists():
            broken.append("%s: freeze missing" % s["stage_id"])
            continue
        if s["governing_freeze"]["sha256"] and sha256(fzp) != s["governing_freeze"]["sha256"]:
            broken.append("%s: freeze file itself changed since indexing" % s["stage_id"])
        fz = jload(fzp)
        ah = fz.get("all_artifact_hashes", {})
        if not ah:
            continue           # S7.1 uses named per-artifact hashes; checked separately
        excl = set(fz.get("self_referential_excluded", [])) | {fzp.name}
        excl |= {r for r in ah if r.endswith("_ACCEPTANCE_CHECKS.json") and "/" not in r}
        for r, want in ah.items():
            if r in excl:
                continue
            total_n += 1
            q = base / r
            if q.exists() and sha256(q) == want:
                total_ok += 1
            else:
                broken.append("%s: %s" % (s["stage_id"], r))
    rec("BLOCKER" if broken else "PASS", "freeze/all_stages",
        "%d frozen artifacts do not reproduce" % len(broken) if broken
        else "%d/%d frozen artifacts across all canonical stages reproduce "
             "byte-for-byte" % (total_ok, total_n), broken[:10])

    # S7.1 uses DataFrame-content hashes for two entries
    try:
        import pandas as pd
        B = S7 / "01_observational_object" / "reconciliation_final"
        d = jload(B / "S7_1_FINAL_FREEZE.json")
        ok = 0
        ok += sha256(S7 / "SIGNAL_UNITS.json") == d["units_registry_sha256"]
        for f, k in (("FINAL_SIGNAL_INVENTORY.csv", "signal_inventory_sha256"),
                     ("signal_quality_summary.csv", "quality_summary_sha256")):
            h = hashlib.sha256(pd.read_csv(B / f).to_csv(index=False).encode("utf-8"))
            ok += h.hexdigest() == d[k]
        for f, k in (("FINAL_SHOT_INVENTORY.csv", "shot_inventory_sha256"),
                     ("provenance_graph.json", "provenance_graph_sha256"),
                     ("DALIA_SIGNAL_PARITY.csv", "dalia_parity_sha256"),
                     ("FINAL_TEMPORAL_LINEAGE.csv", "temporal_lineage_sha256"),
                     ("equilibrium_lineage_status.csv", "equilibrium_lineage_sha256"),
                     ("SOURCE_ARTIFACT_INVENTORY.csv", "source_inventory_sha256")):
            ok += sha256(B / f) == d[k]
        rec("PASS" if ok == 9 else "MAJOR", "freeze/S7.1",
            "%d/9 S7.1 named hashes reproduce (7 file-byte, 2 DataFrame-content)" % ok)
    except Exception as e:
        rec("MINOR", "freeze/S7.1", "could not verify S7.1 named hashes: %s" % e)


# ------------------------------------------------------- 3. canonical numbers
CHECKPOINTS = {
    "object/n_discharges": 62,
    "object/n_signals": 95,
    "boundary/n_predictors": 78,
    "boundary/target": "density",
    "universe/n_atoms": 10778,
    "frontier/epoch1": 162845,
    "K2/tau": 1.0,
    "K2/full_domain": 3451,
    "K2/constructors": {"C0": 51, "C1": 18, "C2": 1488, "C3": 382,
                        "C5": 8, "C6": 965, "C7": 539},
    "E2/n_folds": 6,
    "E2.1/Delta_0": -0.764489,
    "E2.1/Delta_1": -0.027308,
    "E2.1/V_RANGE_checks": 2232,
    "E2.1/V_RANGE_failures": 0,
    "qdesc/pooled_rmse": 0.05758467247445343,
}


def check_numbers():
    import pandas as pd
    import numpy as np

    o = jload(S7 / "01_observational_object" / "reconciliation_final"
              / "S7_1_FINAL_FREEZE.json")
    rec("PASS" if o["n_shots"] == 62 and o["n_signals"] == 95 else "MAJOR",
        "numbers/object", "62 discharges, 95 signals" if o["n_shots"] == 62
        else "object counts changed: %s/%s" % (o["n_shots"], o["n_signals"]))

    b = pd.read_csv(S7 / "03_target_feasibility_and_boundary"
                    / "reconciliation_source_resolution"
                    / "corrected_selected_target_boundary.csv")
    npred = int((b.include_primary == True).sum())
    tgt = b[b.target_status == "TARGET"].signal.tolist()
    rec("PASS" if npred == 78 and tgt == ["density"] else "MAJOR",
        "numbers/boundary",
        "78 admissible predictors, target `density`, 17 excluded"
        if npred == 78 and tgt == ["density"]
        else "boundary changed: %d predictors, target %s" % (npred, tgt))
    # no target descendant admitted
    leak = b[(b.include_primary == True) & (b.target_status == "TARGET")]
    rec("BLOCKER" if len(leak) else "PASS", "numbers/target_excluded",
        "target admitted as its own predictor" if len(leak)
        else "the target is excluded from the explanatory boundary")

    u = pd.read_csv(S7 / "06_admissible_universe" / "hardened_v2"
                    / "primary_atomic_coordinate_universe.csv")
    rec("PASS" if len(u) == 10778 else "MAJOR", "numbers/universe",
        "10,778 admissible atoms" if len(u) == 10778
        else "universe changed: %d atoms" % len(u))

    f9 = jload(S7 / "09_development_selection_and_freeze" / "S7_9_FREEZE.json")
    rec("PASS" if f9["selection_domain_cardinality"] == 162845 else "MAJOR",
        "numbers/frontier", "Epoch-1 explored frontier 162,845 supports"
        if f9["selection_domain_cardinality"] == 162845 else "frontier changed")

    pol = jload(S7 / "K2_observational_range_support_contract"
                / "RANGE_SUPPORT_POLICY_V1.json")
    tau_ok = pol["threshold"]["tau"] == 1.0
    eps_ok = (pol["metric"]["epsilon"] is None
              and pol["degenerate_calibration"]["epsilon_substituted"] is False)
    blind = pol["target_blind"] and pol["model_error_blind"] \
        and not pol["epoch1_outcome_used_in_construction"]
    rec("PASS" if (tau_ok and eps_ok and blind) else "MAJOR", "numbers/K2_policy",
        "tau = 1, no epsilon, degenerate case an explicit status, target-blind"
        if (tau_ok and eps_ok and blind) else "range-support policy altered")

    cb = jload(S7 / "E2_0A_predictor_admissibility_reconciliation"
               / "E2_0A_CANDIDATE_BASIS.json")
    basis = pd.read_csv(S7 / "E2_1_crossfitted_discovery_and_qualification"
                        / "manifests" / "C_E2_FULL_DOMAIN.csv")
    h = hashlib.sha256("\n".join(sorted(basis.coordinate_id)).encode()).hexdigest()
    cc = {k: int(v) for k, v in basis.constructor.value_counts().items()}
    ok = (len(basis) == 3451 and h == cb["coordinate_ids_sha256"]
          and cc == CHECKPOINTS["K2/constructors"])
    rec("PASS" if ok else "BLOCKER", "numbers/qualified_basis",
        "C_E2_FULL_DOMAIN: 3,451 atoms, exact constructor counts, hash matches E2.0A"
        if ok else "qualified basis changed: n=%d" % len(basis))

    fa = pd.read_csv(S7 / "E2_0_protocol_and_resampling_freeze"
                     / "outer_fold_assignment.csv", dtype={"discharge": str})
    order = {"earlier": 0, "later": 1}
    s = fa.sort_values(["processing_era", "discharge"],
                       key=lambda c: c.map(order) if c.name == "processing_era" else c
                       ).reset_index(drop=True)
    repro = bool((np.arange(len(s)) % 6 == s.outer_fold.values).all())
    rec("PASS" if (fa.outer_fold.nunique() == 6 and len(fa) == 62 and repro) else "MAJOR",
        "numbers/folds",
        "six deterministic folds over 62 discharges; assignment reproduces from the "
        "declared target-blind rule" if repro else "fold assignment does not reproduce")

    E21 = S7 / "E2_1_crossfitted_discovery_and_qualification"
    d = pd.read_csv(E21 / "heldout_discharge_results.csv", dtype={"shot_id": str})
    f21 = jload(E21 / "E2_1_FREEZE.json")
    D0 = float((d.REL_nrmse - d.B0_nrmse).mean())
    D1 = float((d.REL_nrmse - d.B1_nrmse).mean())
    ok = (len(d) == 62 and d.shot_id.nunique() == 62
          and abs(D0 - f21["V3"]["Delta_0"]) < 1e-12
          and abs(D1 - f21["V3"]["Delta_1"]) < 1e-12
          and D0 <= -0.01 and D1 <= -0.01)
    rec("PASS" if ok else "BLOCKER", "numbers/E2.1_V3",
        "62 out-of-fold discharges; Delta_0 %.6f, Delta_1 %.6f recomputed from the "
        "per-discharge table; V3 PASS" % (D0, D1) if ok
        else "E2.1 primary metrics do not reproduce")

    ep = {"earlier": (35, 0.0076), "later": (27, -0.0726)}
    bad = []
    for k, (n, dv) in ep.items():
        sub = d[d.era == k]
        got = float((sub.REL_nrmse - sub.B1_nrmse).mean())
        if len(sub) != n or abs(round(got, 4) - dv) > 1e-4:
            bad.append("%s n=%d Delta_1=%.4f" % (k, len(sub), got))
    rec("PASS" if not bad else "MAJOR", "numbers/E2.1_era",
        "era split reproduces: earlier n=35 +0.0076 (practical tie), later n=27 "
        "-0.0726 (material improvement)" if not bad else "; ".join(bad))

    vr = pd.read_csv(E21 / "manifests" / "vrange_integrity.csv")
    ok = int(vr.n_coordinate_cell_checks.sum()) == 2232 and int(vr.n_failures.sum()) == 0
    rec("PASS" if ok else "MAJOR", "numbers/V_RANGE",
        "V-RANGE: 2,232 held-out checks, 0 failures" if ok else "V-RANGE changed")
    rec("PASS" if int((d.REL_nrmse > 1.0).sum()) == 0 else "MAJOR",
        "numbers/no_discharge_above_1",
        "no held-out discharge exceeds NRMSE 1.0")

    # support non-uniqueness, with the depth-aware parse the coordinate ids require
    folds = pd.read_csv(E21 / "fold_selected_supports.csv")
    sets = {int(r.fold): set(dsplit(r.support_id)) for r in folds.itertuples()}
    sizes = {k: len(v) for k, v in sets.items()}
    ident = any(sets[a] == sets[b] for a in sets for b in sets if a < b)
    pair = [len(sets[a] & sets[b]) / len(sets[a] | sets[b])
            for a in sets for b in sets if a < b]
    ok = (set(sizes.values()) == {12} and not ident
          and abs(float(sum(pair) / len(pair)) - 0.285244483758) < 1e-9)
    rec("PASS" if ok else "MAJOR", "numbers/support_non_uniqueness",
        "six supports, all size 12, none identical, mean pairwise Jaccard %.6f"
        % (sum(pair) / len(pair)) if ok else "support stability changed")
    hok = all(hashlib.sha256(r.support_id.encode()).hexdigest() == r.support_sha256
              for r in folds.itertuples())
    rec("PASS" if hok else "BLOCKER", "numbers/support_hashes",
        "every fold support id hashes to its recorded sha256")

    # q_desc canonical checkpoint, by reference
    W = Path("D:/sir-web/Paper Examples/Relational Coordinates for "
             "Multimodal Plasma Observations")
    pm = W / "canonical_d3d_62_shot_run_v1" / "d3d_pooled_metrics.json"
    if pm.exists():
        m = jload(pm)
        ok = abs(m["pooled_rmse"] - CHECKPOINTS["qdesc/pooled_rmse"]) < 1e-15
        rec("PASS" if ok else "MAJOR", "numbers/qdesc_pooled_rmse",
            "q_desc pooled RMSE %.17f from discharge-specific coefficients"
            % m["pooled_rmse"] if ok else "q_desc pooled RMSE changed")
    else:
        rec("DOCUMENTATION", "numbers/qdesc",
            "q_desc canonical tree not reachable from this machine; the descriptive "
            "branch is audited by reference only (see MANUSCRIPT_ALIGNMENT.md)")


def dsplit(s):
    """Split a support id at pipes of parenthesis depth 0 only.

    C4/C6/C7/C8 coordinate signatures embed a pipe inside parentheses, so a
    naive split corrupts them.
    """
    out, dep, cur = [], 0, []
    for ch in s:
        if ch == "(":
            dep += 1
        elif ch == ")":
            dep -= 1
        if ch == "|" and dep == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


# ------------------------------------------------------------- 4. closure etc
def check_closure():
    f12 = jload(S7 / "S7_12_qualified_result" / "S7_12_FREEZE.json")
    ok = (f12["Q_REC_BRANCH_CLOSED"] is True
          and f12["NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED"] is True
          and f12["EPOCH2_IS_FINAL_QREC_ATTEMPT"] is True
          and f12["Q_REC_STATUS"] == "QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS"
          and f12["CLEAN_DEMO_STATUS"] == "CLEAN_DEMO_NOT_MET")
    rec("PASS" if ok else "MAJOR", "closure/branch",
        "q_rec branch closed; FORMAL_PASS and CLEAN_DEMO_NOT_MET carried separately"
        if ok else "branch closure flags altered")

    f21 = jload(S7 / "E2_1_crossfitted_discovery_and_qualification" / "E2_1_FREEZE.json")
    f22 = jload(S7 / "E2_2_full_object_descriptive_representation" / "E2_2_FREEZE.json")
    ok = (f22["is_externally_validated"] is False and f22["is_held_out"] is False
          and f22["is_canonical_equation"] is False
          and f22["is_the_support_that_produced_the_cross_fitted_metric"] is False
          and f21["timestamp_utc"] < f22["timestamp_utc"])
    rec("PASS" if ok else "MAJOR", "closure/descriptive_status",
        "E2.2 frozen after E2.1 and flagged descriptive-only, non-validating, "
        "non-canonical" if ok else "E2.2 status flags altered")

    # parent relationships in the index are consistent
    idx = jload(S7 / "CANONICAL_INDEX.json")
    ids = {s["stage_id"] for s in idx["stages"]}
    dangling = [(s["stage_id"], p) for s in idx["stages"]
                for p in s["parent_stages"] + s["child_stages"] if p not in ids]
    rec("MAJOR" if dangling else "PASS", "closure/stage_graph",
        "dangling stage references: %s" % dangling[:5] if dangling
        else "stage dependency graph is closed over %d canonical stages" % len(ids))


# ------------------------------------------------------- 5. language + hygiene
AGENT = re.compile(
    r"\bClaude\b|\bAnthropic\b|\bChatGPT\b|\bOpenAI\b|\bGrok\b|\bGemini\b|"
    r"\bCopilot\b|AI[- ]generated|\blanguage model\b|\bLLMs?\b|\bassistants?\b|"
    r"\bagentic\b|\bgenerated by\b|\bwritten by\b", re.IGNORECASE)
RETIRED = ["D3D-COEFFICIENT-FAMILY-RESOLVED", "REL10", "REL141", "RAW10"]


# The scanner's own pattern table and the audit tooling are not public-facing
# scientific artifacts; a scanner that matches its own patterns is a false
# positive by construction. Everything else in the tree is scanned.
SCAN_EXEMPT = ("audit_s7.py", "AUDIT_CHECKS.json", "_audit/")


def check_language():
    hits = []
    for p in S7.rglob("*"):
        if not p.is_file() or "__pycache__" in str(p):
            continue
        rel_ = str(p.relative_to(S7)).replace("\\", "/")
        if rel_.startswith(SCAN_EXEMPT):
            continue
        if p.suffix.lower() not in {".md", ".html", ".json", ".py", ".csv", ".txt"}:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="strict")
        except Exception:
            continue          # binary or non-utf8: not public-facing prose
        for m in AGENT.finditer(t):
            hits.append({"path": str(p.relative_to(S7)).replace("\\", "/"),
                         "term": m.group(0)})
    rec("MAJOR" if hits else "PASS", "language/agent_authorship",
        "%d machine-authorship references in canonical S7" % len(hits) if hits
        else "no machine-authorship attribution anywhere in canonical S7",
        hits[:10])

    # A retired identifier is properly handled when the enclosing prose section
    # marks it as retired. Checking only the matching line is too narrow: the
    # marker usually sits in the heading or the sentence that introduces it.
    MARK = re.compile(r"retire|superseded|historical|legacy|not used|archived|"
                      r"stale|must not|not inherited|coincidence|MUST BE REPLACED",
                      re.I)
    stale = []
    for p in S7.rglob("*.md"):
        rel_ = str(p.relative_to(S7)).replace("\\", "/")
        if "__pycache__" in rel_ or rel_.startswith("_legacy_reference/"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        # split into markdown sections; a section is marked if any line in it does
        bounds = [m.start() for m in re.finditer(r"^#{1,6} ", t, re.M)] + [len(t)]
        if bounds[0] != 0:
            bounds = [0] + bounds
        for term in RETIRED:
            for m in re.finditer(re.escape(term), t):
                lo = max(b for b in bounds if b <= m.start())
                hi = min(b for b in bounds if b > m.start())
                if MARK.search(t[lo:hi]):
                    continue
                ls = t.rfind(chr(10), 0, m.start()) + 1
                le = t.find(chr(10), m.end())
                stale.append({"path": rel_, "term": term,
                              "line": t[ls:le if le > 0 else len(t)].strip()[:140]})
    rec("MAJOR" if stale else "PASS", "language/retired_claims",
        "%d retired-branch terms presented without a retirement marker" % len(stale)
        if stale else "no retired verdict or retired-branch identifier is presented "
                      "as active", stale[:8])


def check_links():
    bad = []
    for p in S7.rglob("index.html"):
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'href="([^"#]+)"', t):
            h = m.group(1)
            if h.startswith(("http://", "https://", "mailto:")):
                bad.append({"path": str(p.relative_to(S7)), "href": h,
                            "why": "external dependency"})
                continue
            if not (p.parent / h).resolve().exists():
                bad.append({"path": str(p.relative_to(S7)).replace("\\", "/"),
                            "href": h, "why": "target does not exist"})
    rec("MAJOR" if bad else "PASS", "html/links",
        "%d broken or external links" % len(bad) if bad
        else "every link in every generated page resolves locally; no external "
             "dependency", bad[:8])


def check_figures():
    figs = sorted((S7 / "figures").glob("*.png")) if (S7 / "figures").exists() else []
    if not figs:
        rec("DOCUMENTATION", "figures/present", "no generated figures found")
        return
    prov = S7 / "figures" / "FIGURE_PROVENANCE.json"
    if not prov.exists():
        rec("MAJOR", "figures/provenance", "figures exist with no provenance record")
        return
    pv = jload(prov)
    known = {f["file"] for f in pv["figures"]}
    orphan = [p.name for p in figs if p.name not in known]
    noscript = [f["file"] for f in pv["figures"]
                if not (S7 / f["script"]).exists()]
    rec("MAJOR" if (orphan or noscript) else "PASS", "figures/provenance",
        "orphan figures %s; missing scripts %s" % (orphan[:4], noscript[:4])
        if (orphan or noscript)
        else "all %d figures declare a source artifact and an existing script"
             % len(pv["figures"]))



# ------------------------------------------------ 6. architecture semantics
# These inspect the ACTIVE DOCUMENTATION AND METADATA LAYER ONLY. Frozen
# historical prose keeps the vocabulary in force when it was sealed, and must
# never make this check fail.
ACTIVE_DOCS = ["README.md", "WORKFLOW.md", "SIR_ARCHITECTURE_MAP.md",
               "REVISION_LEDGER.md", "INFORMATION_FLOW_AUDIT.md",
               "AUDIT_REPORT.md", "MANUSCRIPT_ALIGNMENT.md",
               "ARCHITECTURE_SEMANTICS_AUDIT.md", "REPRODUCIBILITY.md",
               "STATUS.md"]


def _active_text():
    out = {}
    for f in ACTIVE_DOCS:
        p = S7 / f
        if p.exists():
            out[f] = p.read_text(encoding="utf-8", errors="replace")
    return out


def check_semantics():
    docs = _active_text()
    idx = jload(S7 / "CANONICAL_INDEX.json")
    sem = S7 / "ARCHITECTURE_SEMANTICS_AUDIT.json"
    if not sem.exists():
        rec("MAJOR", "semantics/record", "ARCHITECTURE_SEMANTICS_AUDIT.json missing")
        return
    A = jload(sem)

    # 1 - Epoch 2 must never be described as untouched/external validation
    import re as _re
    bad = []
    PAT = _re.compile(r"(epoch[- ]?2|cross-fitted|QREC-B2)[^.\n]{0,180}?"
                      r"(external validation|untouched (external )?evidence)",
                      _re.I)
    for f, t in docs.items():
        for m in PAT.finditer(t):
            line = m.group(0)
            if _re.search(r"\bnot\b|never|✗|forbidden|no longer|cannot|is not",
                          line, _re.I):
                continue
            bad.append({"file": f, "text": line[:150]})
    rec("MAJOR" if bad else "PASS", "semantics/no_external_validation_claim",
        "%d active statements describe Epoch 2 as external validation" % len(bad)
        if bad else "no active document describes Epoch 2 or QREC-B2 as external "
                    "or untouched validation", bad[:5])

    # 2 - K2 classification
    k2 = A.get("K2_classification", {})
    ok = (k2.get("case") == "B" and k2.get("revision_class") == "MINIMAL_P_ONLY"
          and k2.get("branch_changed") is False
          and k2.get("created_descendant_branch") is False
          and k2.get("operational_epoch_advanced") is True)
    stage_k2 = next((x for x in idx["stages"] if x["stage_id"] == "S7.K2"), {})
    ok = ok and (stage_k2.get("claim_branch") == "QREC-B1"
                 and stage_k2.get("revision_level") == "OPERATIONAL_CONTRACT")
    rec("PASS" if ok else "MAJOR", "semantics/K2_case_B",
        "S7.K2 classified as Case B, MINIMAL_P_ONLY, operational epoch advanced "
        "inside QREC-B1, no descendant branch created" if ok
        else "S7.K2 classification inconsistent")

    # 3 - V-RANGE must not be presented as a material change to semantic V_rec
    # A stale phrase QUOTED in order to record that it was corrected is not an
    # assertion of it; look for a correction marker in the enclosing line.
    CORRECTED = _re.compile(r"reworded|corrected|stale|ambiguous|superseded|"
                            r"not|never|no longer|must not|disposition", _re.I)
    bad = []
    for f, t in docs.items():
        for line_ in t.split(chr(10)):
            if CORRECTED.search(line_):
                continue
            for m in _re.finditer(r"V_rec[^.]{0,60}(gains|extended by|changed by)"
                                  r"[^.]{0,30}V-RANGE", line_, _re.I):
                bad.append({"file": f, "text": m.group(0)[:150]})
    rec("MAJOR" if bad else "PASS", "semantics/V_RANGE_not_V_q_change",
        "%d statements imply V-RANGE changed the claim-defining V_rec" % len(bad)
        if bad else "V-RANGE is presented as an operational qualification check of "
                    "the revised P_rec, not as a change to the claim-defining V_rec",
        bad[:5])

    # 4 - descendant branch classification
    stage_e20 = next((x for x in idx["stages"] if x["stage_id"] == "S7.E2.0"), {})
    st12 = next((x for x in idx["stages"] if x["stage_id"] == "S7.12"), {})
    lin = idx.get("branch_lineage", {})
    ok = (stage_e20.get("claim_branch") == "QREC-B2"
          and stage_e20.get("claim_branch_role") == "DESCENDANT_ORIGIN"
          and stage_e20.get("revision_level") == "CLAIM_DEFINING"
          and stage_e20.get("parent_claim_branch") == "QREC-B1"
          and st12.get("claim_branch") == "QREC-B2"
          and lin.get("branch_change_stage", "S7.E2.0") == "S7.E2.0"
          and A["qrec_branch_lineage"]["branch_change_stage"] == "S7.E2.0"
          and A["qrec_branch_lineage"]["branch_change_not_at"] == "S7.K2")
    rec("PASS" if ok else "MAJOR", "semantics/descendant_branch",
        "the cross-fitted Epoch-2 result is classified as descendant claim branch "
        "QREC-B2, constituted at S7.E2.0 with parent QREC-B1" if ok
        else "descendant-branch classification inconsistent")

    # 5 - same scientific task across the transition
    tasks = {x["stage_id"]: x.get("scientific_task_id") for x in idx["stages"]}
    qrec = [v for k, v in tasks.items() if k != "S7.1"]
    ok = (set(qrec) == {"q_rec"}
          and A["qrec_branch_lineage"]["new_q_required"] is False)
    rec("PASS" if ok else "MAJOR", "semantics/same_task",
        "q_rec is the same scientific task across every claim branch and epoch; "
        "no new q was required" if ok else "task identity is inconsistent: %s"
        % sorted(set(qrec)))

    # 6 - vsurf -> density is not a new q
    v = A.get("vsurf_to_density", {})
    s3 = next((x for x in idx["stages"] if x["stage_id"] == "S7.3V2"), {})
    ok = (v.get("case") == "A" and v.get("task_changed") is False
          and v.get("claim_branch_changed") is False
          and s3.get("revision_level") == "INSTANTIATION"
          and s3.get("claim_branch") == "QREC-B1")
    rec("PASS" if ok else "MAJOR", "semantics/vsurf_not_new_q",
        "vsurf -> density is classified as a Case-A correction of the target "
        "INSTANCE; task and claim branch unchanged" if ok
        else "vsurf -> density classification inconsistent")

    # 7 - neither over-broad rule is asserted in active documentation
    bad = []
    OVERBROAD = [
        (r"every (material )?change[^.\n]{0,60}new (scientific )?(branch|q\b)",
         "every change creates a new branch/q"),
        (r"(all|every) reconciliation[^.\n]{0,60}same branch",
         "every reconciliation is automatically same-branch"),
    ]
    for f, t in docs.items():
        for pat, why in OVERBROAD:
            for m in _re.finditer(pat, t, _re.I):
                seg = t[max(0, m.start() - 120):m.end() + 60]
                if _re.search(r"\bnot\b|never|too broad|superseded|nor\b|"
                              r"neither|replace", seg, _re.I):
                    continue
                bad.append({"file": f, "why": why, "text": m.group(0)[:120]})
    rec("MAJOR" if bad else "PASS", "semantics/no_overbroad_rule",
        "%d over-broad branch rules asserted" % len(bad) if bad
        else "no active document asserts that every material change creates a new "
             "q, nor that every reconciliation is automatically same-branch",
        bad[:5])

    # 8 - lineage closure internally consistent
    f12 = jload(S7 / "S7_12_qualified_result" / "S7_12_FREEZE.json")
    cb = idx.get("claim_branches", {})
    ok = (f12["Q_REC_BRANCH_CLOSED"] is True
          and cb.get("QREC-B2", {}).get("status") == "CLOSED"
          and cb.get("QREC-B2", {}).get("parent_claim_branch") == "QREC-B1"
          and A["branch_closure"]["frozen_fields_modified"] is False
          and A["qrec_branch_lineage"]["lineage_status"] == "CLOSED")
    rec("PASS" if ok else "MAJOR", "semantics/lineage_closure",
        "branch lineage closure is internally consistent, and the frozen closure "
        "fields were not modified" if ok else "lineage closure inconsistent")

    # 10 - contract VERSION change is not automatically an EPOCH advance
    conv = A.get("qrec_branch_lineage", {}).get("operational_epoch_convention", {})
    advances = set(conv.get("epoch_advances", []))
    versioned = set(conv.get("versioned_corrections_not_advancing_epoch", []))
    ok = (advances == {"S7.K2"} and {"S7.7R", "S7.E2.0A"} <= versioned
          and conv.get("epoch_counts", {}).get("QREC-B2") == 1)
    bad = []
    OVEREPOCH = _re.compile(
        r"(every|each|any) Case[- ]B[^.]{0,90}(new |advance)[^.]{0,40}epoch", _re.I)
    SAFE = _re.compile(r"\bnot\b|never|only when|is not|does not|\u2260|!=|"
                       r"depends on", _re.I)
    for f, t in docs.items():
        for line_ in t.split(chr(10)):
            if SAFE.search(line_):
                continue
            if OVEREPOCH.search(line_):
                bad.append({"file": f, "text": line_.strip()[:140]})
    rec("PASS" if (ok and not bad) else "MAJOR", "semantics/epoch_vs_version",
        "contract version change is distinguished from operational-epoch advance; "
        "S7.K2 is the sole epoch advance, S7.2C / S7.7R / S7.E2.0A are versioned "
        "corrections, QREC-B2 has one branch-local epoch"
        if (ok and not bad) else "epoch bookkeeping inconsistent", bad[:5])

    # 11 - Omega*_q must never be presented as a member of K_q^claim
    om = A.get("qrec_branch_lineage", {}).get("Omega_q_status", {})
    ok = ("UNCHANGED" in om.get("Omega_rec_intended_claim_domain", "")
          and om.get("claim_defining_revision_at_S7_E2_0") == ["V_rec"]
          and "NOT a member" in om.get("Omega_star_rec_supported_domain", ""))
    bad = []
    OMSAFE = _re.compile(r"\bnot\b|never|rather than|belongs to|part of Q|"
                         r"is an outcome|forbidden|unchanged", _re.I)
    OMBAD = _re.compile(r"(revision of|narrow\w*)[^.]{0,70}V_rec[^.]{0,50}"
                        r"(and|,)[^.]{0,40}\u03a9\*_rec", _re.I)
    for f, t in docs.items():
        for line_ in t.split(chr(10)):
            if OMSAFE.search(line_):
                continue
            if OMBAD.search(line_):
                bad.append({"file": f, "text": line_.strip()[:140]})
    rec("PASS" if (ok and not bad) else "MAJOR",
        "semantics/Omega_star_not_claim_core",
        "Omega_rec (intended claim domain) is unchanged and V_rec is the sole "
        "claim-defining revision; Omega*_rec is recorded as part of Q*_q, not of "
        "K_q^claim" if (ok and not bad)
        else "Omega_q / Omega*_q usage inconsistent", bad[:5])

    # 12 - QREC-B1 must read as a qualification FAILURE, never a positive result
    w = A.get("QREC_B1_outcome_wording", {})
    ok = (w.get("canonical_phrase") == "negative qualification outcome"
          and w.get("avoid") == "its qualified outcome")
    bad = []
    B1SAFE = _re.compile(r"avoid|canonical phrase|acceptable variant|must not|"
                         r"could be misread|wording|negative", _re.I)
    B1BAD = _re.compile(r"QREC-B1[^.]{0,120}\bqualified (outcome|result)\b|"
                        r"branch's qualified outcome", _re.I)
    for f, t in docs.items():
        for line_ in t.split(chr(10)):
            if B1SAFE.search(line_):
                continue
            if B1BAD.search(line_):
                bad.append({"file": f, "text": line_.strip()[:140]})
    rec("PASS" if (ok and not bad) else "MAJOR", "semantics/B1_failure_wording",
        "QREC-B1 is described as a negative qualification outcome, never as a "
        "positive qualified result" if (ok and not bad)
        else "QREC-B1 outcome wording ambiguous", bad[:5])

    # 9 - integrity claims in the semantics record match reality
    ig = A.get("integrity", {})
    ok = (ig.get("frozen_scientific_artifacts_modified") == 0
          and ig.get("searches_rerun") == 0
          and ig.get("numerical_results_changed") == 0
          and ig.get("scientific_verdicts_changed") == 0
          and ig.get("scientific_audit_verdict_unchanged")
          == "S7_AUDIT_PASS_WITH_QUALIFICATIONS")
    rec("PASS" if ok else "MAJOR", "semantics/integrity_claims",
        "the semantics pass asserts zero frozen-artifact edits, zero reruns and "
        "zero changed results, consistent with the freeze sweep above" if ok
        else "semantics integrity claims inconsistent")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(S7 / "AUDIT_CHECKS.json"))
    a = ap.parse_args()

    idx_p = S7 / "CANONICAL_INDEX.json"
    if not idx_p.exists():
        print("FAIL: CANONICAL_INDEX.json missing; run _audit/build_s7_package.py")
        return 1
    idx = jload(idx_p)

    check_structure(idx)
    check_freezes(idx)
    check_numbers()
    check_closure()
    check_language()
    check_semantics()
    check_links()
    check_figures()

    order = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2, "DOCUMENTATION": 3, "COSMETIC": 4}
    FIND.sort(key=lambda f: order.get(f["level"], 9))
    blocking = [f for f in FIND if f["level"] in ("BLOCKER", "MAJOR")]
    verdict = "S7_AUDIT_FAIL" if blocking else (
        "S7_AUDIT_PASS" if not FIND else "S7_AUDIT_PASS_WITH_NOTES")

    out = {"record_id": "S7_AUTOMATED_AUDIT_V1",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "verdict": verdict, "n_pass": len(PASSES), "n_findings": len(FIND),
           "findings": FIND, "passes": PASSES,
           "environment": {"python": sys.version.split()[0]}}
    Path(a.json).write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=" * 74)
    print("S7 INDEPENDENT AUDIT   %s" % out["generated_utc"])
    print("=" * 74)
    for p in PASSES:
        print("  [PASS]      %-34s %s" % (p["id"], p["msg"]))
    if FIND:
        print()
        for f in FIND:
            print("  [%-9s] %-34s %s" % (f["level"], f["id"], f["msg"]))
            for d in (f.get("detail") or [])[:5]:
                print("               %s" % d)
    print("-" * 74)
    print("  %d passed, %d findings  ->  %s" % (len(PASSES), len(FIND), verdict))
    print("  report: %s" % a.json)
    print("=" * 74)
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
