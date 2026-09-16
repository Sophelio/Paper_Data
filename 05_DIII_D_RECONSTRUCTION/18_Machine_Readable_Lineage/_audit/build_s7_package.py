"""Build the S7 normalization layer.

Generates, without touching any frozen artifact:
  <stage>/MANIFEST.json   a uniform machine-readable stage record that INDEXES
                          the stage's existing freeze rather than replacing it
  <stage>/index.html      a self-contained static stage summary
  S7/CANONICAL_INDEX.json the canonical stage map
  S7/index.html           the S7 dashboard

Presentation and indexing only. Category A/B/C under the audit taxonomy.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S7 = HERE.parent
sys.path.insert(0, str(HERE))
from stage_registry import (STAGES, HISTORICAL, EXTERNAL_BRANCH,  # noqa: E402
                            TASKS, CLAIM_BRANCHES)

CHAIN = ["O", "O_q", "X_q", "G_q", "A_q", "Ahat_q", "CR", "Q_q"]
CHAIN_LABEL = {"O": "𝒪", "O_q": "𝒪<sub>q</sub>", "X_q": "X<sub>q</sub>",
               "G_q": "𝒢<sub>q</sub>", "A_q": "𝔄<sub>q</sub>",
               "Ahat_q": "𝔄̂<sub>q</sub>", "CR": "(C*,R*)", "Q_q": "𝒬*<sub>q</sub>"}
AUDIT_CHAIN = ["delta", "rho", "j_min"]
AUDIT_LABEL = {"delta": "δ<sup>(e)</sup>", "rho": "ρ<sub>q</sub>", "j_min": "j<sub>min</sub>"}
CONTRACT = ["K_claim", "K_op", "Sigma_q"]
CONTRACT_LABEL = {"K_claim": "𝒦<sup>claim</sup>", "K_op": "𝒦<sup>op,(e)</sup>",
                  "Sigma_q": "Σ<sub>q</sub>"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


CSS = """
:root{--bg:#fbfaf8;--fg:#1c1b19;--mut:#6b6862;--line:#dedbd4;--card:#fff;
--ok:#1d6f42;--warn:#8a5a00;--bad:#9b2226;--acc:#2b4c7e;--acc2:#f0f4fa}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:28px 22px 80px}
header{border-bottom:2px solid var(--fg);padding-bottom:14px;margin-bottom:22px}
.kicker{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}
h1{font-size:26px;margin:6px 0 8px;line-height:1.25}
h2{font-size:17px;margin:30px 0 10px;padding-bottom:5px;border-bottom:1px solid var(--line)}
h3{font-size:14px;margin:20px 0 6px;color:var(--acc)}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.b{font-size:11px;padding:3px 9px;border-radius:11px;border:1px solid var(--line);
background:var(--card);white-space:nowrap}
.b.ok{background:#e8f3ec;border-color:#bcdcc8;color:var(--ok)}
.b.warn{background:#fdf3e0;border-color:#e8d3a8;color:var(--warn)}
.b.bad{background:#fbeaea;border-color:#e6bebe;color:var(--bad)}
.b.acc{background:var(--acc2);border-color:#c3d3e8;color:var(--acc)}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}
th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line);
vertical-align:top}
th{font-weight:600;color:var(--mut);font-size:11px;text-transform:uppercase;
letter-spacing:.05em}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}
code{background:#f1efeb;padding:1px 5px;border-radius:3px}
.card{background:var(--card);border:1px solid var(--line);border-radius:7px;
padding:14px 16px;margin:12px 0}
.strip{display:flex;flex-wrap:wrap;align-items:center;gap:5px;background:var(--card);
border:1px solid var(--line);border-radius:7px;padding:11px 13px;margin:12px 0;
font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px}
.node{padding:3px 9px;border-radius:5px;background:#f1efeb;border:1px solid var(--line);
color:var(--mut)}
.node.on{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
.arrow{color:#b8b4ad}
.nav{display:flex;justify-content:space-between;gap:12px;margin-top:34px;
padding-top:14px;border-top:1px solid var(--line);font-size:13px}
a{color:var(--acc)}
ul{margin:8px 0;padding-left:20px}li{margin:3px 0}
.note{color:var(--mut);font-size:12.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:11px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:7px;padding:11px 13px}
.tile .id{font-size:11px;letter-spacing:.08em;color:var(--mut);text-transform:uppercase}
.tile .t{font-weight:600;margin:3px 0 5px;font-size:13.5px}
.q{border-left:3px solid var(--acc);padding-left:12px;color:var(--mut);margin:8px 0}
.scroll{overflow-x:auto}
@media(prefers-color-scheme:dark){:root{--bg:#16151a;--fg:#e8e6e1;--mut:#9a968e;
--line:#33313a;--card:#1e1d23;--acc:#8fb4e8;--acc2:#22283a}
code{background:#26252c}.node{background:#26252c}
.b.ok{background:#16281d;border-color:#2c4a36}
.b.warn{background:#2b2312;border-color:#4d3d1c}
.b.bad{background:#2c1618;border-color:#4d2427}}
"""


def strip_html(active):
    out = ['<div class="strip">']
    for i, k in enumerate(CHAIN):
        cls = "node on" if k in active else "node"
        out.append('<span class="%s">%s</span>' % (cls, CHAIN_LABEL[k]))
        if i < len(CHAIN) - 1:
            out.append('<span class="arrow">→</span>')
    out.append("</div>")
    con = [k for k in CONTRACT if k in active]
    aud = [k for k in AUDIT_CHAIN if k in active]
    out.append('<div class="strip">')
    out.append('<span class="node%s">contract</span>' % (" on" if con else ""))
    for k in CONTRACT:
        out.append('<span class="node%s">%s</span>'
                   % (" on" if k in active else "", CONTRACT_LABEL[k]))
    out.append('<span class="arrow">&nbsp;&nbsp;audit&nbsp;</span>')
    for i, k in enumerate(AUDIT_CHAIN):
        out.append('<span class="node%s">%s</span>'
                   % (" on" if k in active else "", AUDIT_LABEL[k]))
        if i < 2:
            out.append('<span class="arrow">→</span>')
    out.append("</div>")
    return "".join(out)


def status_class(st):
    if "NEGATIVE" in st:
        return "bad"
    if "SUPERSEDED" in st or "DESCRIPTIVE" in st:
        return "warn"
    if "PRIMARY" in st or "FINAL" in st:
        return "ok"
    return "acc"


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    by_id = {s["stage_id"]: s for s in STAGES}
    index = {"record_id": "S7_CANONICAL_INDEX_V2", "generated_utc": now,
             "root": "DIIID_example/S7",
             "scientific_tasks": TASKS,
             "claim_branches": CLAIM_BRANCHES,
             "branch_lineage": {
                 "hierarchy": "scientific task q -> provenance-linked claim branch "
                              "-> operational epoch(s)",
                 "q_rec": ["QREC-B1", "QREC-B2"],
                 "QREC-B1 -> QREC-B2": "descendant claim branch: the evidentiary "
                                       "commitment V_q was materially narrowed after "
                                       "protected evidence was spent, constituted at "
                                       "S7.E2.0",
                 "final_qualified_result": {"branch": "QREC-B2", "stage": "S7.12",
                                            "status": "CLOSED"},
                 "lineage_status": "q_rec scientific lineage closed; no further "
                                   "discovery epoch authorized on any q_rec branch"},
             "branches": {"q_rec": "audited and stabilized in this directory",
                          "q_desc": EXTERNAL_BRANCH},
             "n_canonical_stages": len(STAGES), "stages": [], "historical": [],
             "sir_architecture": {
                 "forward_chain": CHAIN,
                 "contract": ["K_claim = (q, I_q, U_q, V_q, Omega_q)",
                              "K_op(e) = (P_q, B_q, H_q)"],
                 "audit_chain": AUDIT_CHAIN,
                 "note": "G_q != A_q != Ahat_q != Sigma_q; the ontology is a "
                         "task-conditioned grammar, not a feature library, not the "
                         "concrete universe, not the explored frontier, and not "
                         "the search policy."}}

    for i, s in enumerate(STAGES):
        d = S7 / s["dir"]
        if not d.exists():
            print("MISSING STAGE DIR:", s["dir"])
            continue
        fz = d / s["freeze"]
        files = sorted(str(p.relative_to(d)).replace("\\", "/")
                       for p in d.rglob("*") if p.is_file()
                       and "__pycache__" not in str(p))
        scripts = [f for f in files if f.endswith(".py")]
        man = {
            "record_id": "S7_STAGE_MANIFEST_V1",
            "generated_utc": now,
            "stage_id": s["stage_id"],
            "title": s["title"],
            "directory": s["dir"],
            "scientific_task_id": s["scientific_task_id"],
            "claim_branch": s["claim_branch"],
            "claim_branch_role": s["claim_branch_role"],
            "parent_claim_branch": (CLAIM_BRANCHES[s["claim_branch"]]
                                    ["parent_claim_branch"]
                                    if s["claim_branch"] else None),
            "operational_epoch": s["epoch"],
            "revision_level": s["revision_level"],
            "branch": s["branch"],
            "status": s["status"],
            "sir_architecture_mapping": s["sir"],
            "scientific_question": s["question"],
            "operation": s["operation"],
            "verdict": s["verdict"],
            "parent_stages": s["parents"],
            "child_stages": s["children"],
            "key_numbers": s["key_numbers"],
            "notes": s["notes"],
            "governing_freeze": {
                "path": s["freeze"],
                "freeze_id": s["freeze_id"],
                "sha256": sha256(fz) if fz.exists() else None,
                "authoritative": True,
                "note": "This MANIFEST indexes the stage freeze; it does not "
                        "replace it. The freeze remains the authority for hashes, "
                        "acceptance checks and numerical facts.",
            },
            "executables": scripts,
            "n_files": len(files),
            "indexes_not_replaces": True,
        }
        (d / "MANIFEST.json").write_text(json.dumps(man, indent=2), encoding="utf-8")

        prev = STAGES[i - 1] if i > 0 else None
        nxt = STAGES[i + 1] if i < len(STAGES) - 1 else None
        rel_up = "/".join([".."] * len(s["dir"].split("/")))
        kn = "".join("<tr><td>%s</td><td class='num'>%s</td></tr>"
                     % (esc(k), esc(v)) for k, v in s["key_numbers"].items())
        html = """<title>%(sid)s — %(title)s</title><style>%(css)s</style>
<div class="wrap"><header>
<div class="kicker">SIR — DIII-D Supplementary Note S7</div>
<h1>%(sid)s &middot; %(title)s</h1>
<div class="badges">
<span class="b acc">task %(task)s</span>
<span class="b acc">claim branch %(cbranch)s</span>
<span class="b acc">operational epoch %(epoch)s</span>
<span class="b">%(rev)s</span>
<span class="b %(scls)s">%(status)s</span>
<span class="b">%(nf)d files</span></div>
</header>
<h2>Position in the SIR architecture</h2>
%(strip)s
<p class="note">Highlighted elements are the ones this stage instantiates, audits
or revises. A stage may touch more than one.</p>
<table><tr><th>scientific task</th><th>claim branch</th><th>role</th>
<th>operational epoch</th><th>revision level</th></tr>
<tr><td>%(task)s</td><td>%(cbranch)s%(pbranch)s</td><td>%(role)s</td>
<td>%(epoch)s</td><td>%(rev)s</td></tr></table>
<p class="note">A claim branch fixes (q, ℐ<sub>q</sub>, U<sub>q</sub>,
𝒱<sub>q</sub>, Ω<sub>q</sub>); an operational epoch revises
(𝒫<sub>q</sub>, ℬ<sub>q</sub>, ℋ<sub>q</sub>). A material revision of a
claim-defining commitment produces a <em>descendant</em> claim branch under the
same task — see <a href="%(up)s/REVISION_LEDGER.md">REVISION_LEDGER.md</a>.</p>
<h2>Scientific question</h2>
<div class="q">%(question)s</div>
<h2>Operation</h2><p>%(op)s</p>
<h2>Verdict</h2><div class="card"><strong>%(verdict)s</strong></div>
%(kntab)s
<h2>Qualifications</h2><p class="note">%(notes)s</p>
<h2>Governing freeze</h2>
<div class="card"><code>%(fid)s</code><br>
<span class="note">%(fpath)s &middot; sha256 <code>%(fsha)s</code></span><br>
<span class="note">This page indexes the freeze; the freeze remains authoritative
for all hashes, acceptance checks and numerical facts.</span></div>
<h2>Executables</h2>%(scripts)s
<div class="nav"><div>%(prev)s</div><div><a href="%(up)s/index.html">S7 dashboard</a></div>
<div>%(next)s</div></div></div>""" % {
            "sid": esc(s["stage_id"]), "title": esc(s["title"]), "css": CSS,
            "branch": esc(s["branch"]), "epoch": esc(s["epoch"] or "—"),
            "task": esc(s["scientific_task_id"]),
            "cbranch": esc(s["claim_branch"] or "—"),
            "role": esc(s["claim_branch_role"]),
            "rev": esc(s["revision_level"]),
            "pbranch": ("" if not s["claim_branch"]
                        or not CLAIM_BRANCHES[s["claim_branch"]]["parent_claim_branch"]
                        else " <span class='note'>(descendant of %s)</span>"
                        % esc(CLAIM_BRANCHES[s["claim_branch"]]
                              ["parent_claim_branch"])),
            "status": esc(s["status"]), "scls": status_class(s["status"]),
            "nf": len(files), "strip": strip_html(set(s["sir"])),
            "question": esc(s["question"]), "op": esc(s["operation"]),
            "verdict": esc(s["verdict"]),
            "kntab": ("<table><tr><th>quantity</th><th>value</th></tr>%s</table>" % kn)
                     if kn else "",
            "notes": esc(s["notes"]), "fid": esc(s["freeze_id"]),
            "fpath": esc(s["freeze"]),
            "fsha": (sha256(fz)[:24] + "…") if fz.exists() else "n/a",
            "scripts": ("<ul>%s</ul>" % "".join("<li><code>%s</code></li>" % esc(x)
                                                for x in scripts)) if scripts
                       else "<p class='note'>No executable in this stage directory.</p>",
            "up": rel_up,
            "prev": ('<a href="%s/%s/index.html">&larr; %s</a>'
                     % (rel_up, prev["dir"], esc(prev["stage_id"]))) if prev else "",
            "next": ('<a href="%s/%s/index.html">%s &rarr;</a>'
                     % (rel_up, nxt["dir"], esc(nxt["stage_id"]))) if nxt else "",
        }
        (d / "index.html").write_text(html, encoding="utf-8")

        index["stages"].append({k: man[k] for k in
                                ("stage_id", "title", "directory",
                                 "scientific_task_id", "claim_branch",
                                 "claim_branch_role", "parent_claim_branch",
                                 "revision_level", "branch",
                                 "operational_epoch", "status",
                                 "sir_architecture_mapping", "scientific_question",
                                 "verdict", "parent_stages", "child_stages",
                                 "key_numbers", "governing_freeze")})

    for path, label, status, why in HISTORICAL:
        p = S7 / path
        index["historical"].append({
            "path": path, "label": label, "status": status, "reason": why,
            "exists": p.exists(),
            "sha256": sha256(p) if p.exists() else None,
            "preserved_unmodified": True})

    (S7 / "CANONICAL_INDEX.json").write_text(json.dumps(index, indent=2),
                                             encoding="utf-8")
    print("stage manifests + pages: %d" % len(index["stages"]))
    print("historical entries: %d" % len(index["historical"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
