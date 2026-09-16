"""Build the S7 dashboard (index.html). Self-contained; no external dependency."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
S7 = HERE.parent
sys.path.insert(0, str(HERE))
from build_s7_package import CSS, esc, status_class  # noqa: E402

idx = json.loads((S7 / "CANONICAL_INDEX.json").read_text(encoding="utf-8"))
fnd = json.loads((S7 / "AUDIT_REPORT.json").read_text(encoding="utf-8"))
figs = json.loads((S7 / "figures" / "FIGURE_PROVENANCE.json").read_text(encoding="utf-8"))
sem = json.loads((S7 / "ARCHITECTURE_SEMANTICS_AUDIT.json").read_text(encoding="utf-8"))

EPOCH_ROWS = [
    ("Δ₀ vs calibration mean", "−0.764489", "ok"),
    ("Δ₁ vs persistence", "−0.027308", "ok"),
    ("V3 (needs both ≤ −0.01)", "PASS", "ok"),
    ("V6 processing-era robustness", "PASS_WITH_QUALIFICATION", "warn"),
    ("V-RANGE applicability", "PASS — 2,232 checks, 0 failures", "ok"),
    ("discharges with NRMSE > 1", "0", "ok"),
    ("reporting tier", "CLEAN_DEMO_NOT_MET", "warn"),
]
BASE = [("relational", "0.1891", "0.1515", "—", "—"),
        ("B0 calibration mean", "0.9536", "0.9365", "−0.7645", "62/0/0"),
        ("<b>B1 persistence</b>", "0.2164", "0.1744", "<b>−0.0273</b>", "<b>32/5/25</b>"),
        ("B1A AR(1)", "0.3563", "0.3329", "−0.1671", "55/2/5"),
        ("B2 raw ridge (78)", "0.2851", "0.1972", "−0.0960", "39/7/16"),
        ("B3 raw HistGB (78)", "0.3464", "0.1960", "−0.1573", "37/4/21"),
        ("H0 hardened ridge (70)", "0.2842", "0.1914", "−0.0951", "37/7/18")]

CHAIN = ("𝒪 → 𝒪<sub>q</sub> → X<sub>q</sub> → 𝒢<sub>q</sub> → 𝔄<sub>q</sub> → "
         "𝔄̂<sub>q</sub> → (C*,R*) → 𝒬*<sub>q</sub>")

tiles = "".join(
    '<a class="tile" href="%s/index.html" style="text-decoration:none;color:inherit">'
    '<div class="id">%s &middot; epoch %s</div><div class="t">%s</div>'
    '<div class="note">%s</div>'
    '<div class="badges"><span class="b %s">%s</span></div></a>'
    % (esc(s["directory"]), esc(s["stage_id"]), esc(s["operational_epoch"] or "—"),
       esc(s["title"]), esc(s["verdict"][:118]),
       status_class(s["status"]), esc(s["status"]))
    for s in idx["stages"])

hist = "".join("<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td></tr>"
               % (esc(h["path"]), esc(h["label"]), esc(h["status"]), esc(h["reason"]))
               for h in idx["historical"])

find = "".join(
    "<tr><td><code>%s</code></td><td><span class='b %s'>%s</span></td><td>%s</td>"
    "<td class='note'>%s</td></tr>"
    % (esc(f["finding_id"]),
       {"MAJOR": "bad", "MINOR": "warn", "DOCUMENTATION": "acc",
        "COSMETIC": ""}.get(f["level"], ""), esc(f["level"]),
       esc(f["title"]), esc(f["location"]))
    for f in fnd["findings"])

figblocks = "".join(
    '<figure style="margin:16px 0"><img src="figures/%s" alt="%s" '
    'style="width:100%%;border:1px solid var(--line);border-radius:6px">'
    '<figcaption class="note" style="margin-top:6px">%s</figcaption></figure>'
    % (esc(f["file"]), esc(f["file"]), esc(f["caption"])) for f in figs["figures"])

html = """<title>SIR — DIII-D Supplementary Note S7</title><style>%(css)s
img{max-width:100%%;height:auto}</style>
<div class="wrap"><header>
<div class="kicker">SIR — DIII-D Supplementary Note S7</div>
<h1>Task-conditioned relational discovery on 62 DIII-D discharges</h1>
<div class="badges">
<span class="b ok">Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT</span>
<span class="b ok">FORMAL_PASS</span>
<span class="b warn">CLEAN_DEMO_NOT_MET</span>
<span class="b acc">lineage closed</span>
<span class="b acc">%(semverdict)s</span>
<span class="b">21 canonical stages</span>
<span class="b">527/527 frozen artifacts reproduce</span></div>
</header>

<div class="card"><strong>What this directory contains.</strong> The complete
<code>q_rec</code> reconstruction lineage: a scientific object, a discovery
contract, a first discovery that <em>failed</em> qualification, an audit that
refuted the obvious explanation, a minimal revision of the operational contract,
a reconciled evidence design, a fresh cross-fitted discovery that passed, and the
closure of the lineage. The failure is preserved as prominently as the pass,
because the sequence is the demonstration.</div>

<h2>The SIR architecture</h2>
<div class="strip"><span class="node on">%(chain)s</span></div>
<div class="strip"><span class="node">𝒦<sup>claim</sup> = (q, ℐ<sub>q</sub>,
U<sub>q</sub>, 𝒱<sub>q</sub>, Ω<sub>q</sub>)</span>
<span class="node">𝒦<sup>op,(e)</sup> = (𝒫<sub>q</sub>, ℬ<sub>q</sub>,
ℋ<sub>q</sub>)</span><span class="arrow">&nbsp;audit&nbsp;</span>
<span class="node">δ<sup>(e)</sup></span><span class="arrow">→</span>
<span class="node">ρ<sub>q</sub></span><span class="arrow">→</span>
<span class="node">j<sub>min</sub></span></div>
<p class="note">𝒢<sub>q</sub> ≠ 𝔄<sub>q</sub> ≠ 𝔄̂<sub>q</sub> ≠ Σ<sub>q</sub> —
grammar, universe (10,778 atoms), explored frontier (162,845 supports) and search
policy are distinct throughout. Full mapping:
<a href="SIR_ARCHITECTURE_MAP.md">SIR_ARCHITECTURE_MAP.md</a>.</p>

<h2>The q_rec lineage</h2>
<div class="card"><pre style="margin:0;font-size:12.5px;line-height:1.55;overflow-x:auto">q_rec  (scientific task)
&#9474;
&#9500;&#9472;&#9472; QREC-B1   sealed-external claim branch
&#9474;     &#9500;&#9472;&#9472; operational epoch 1   S7.2 &hellip; S7.10   &rarr; QUALIFICATION FAILED
&#9474;     &#9500;&#9472;&#9472; audit                 S7.11, S7.R1   &rarr; Case A refuted
&#9474;     &#9492;&#9472;&#9472; operational epoch 2   S7.K2          &rarr; Case B, branch unchanged
&#9474;
&#9492;&#9472;&#9472; QREC-B2   cross-fitted finite-object DESCENDANT branch (parent QREC-B1)
      &#9500;&#9472;&#9472; S7.E2.0    Case C &mdash; constitutes the descendant branch
      &#9500;&#9472;&#9472; S7.E2.0A   Case B &mdash; tau_train retired
      &#9500;&#9472;&#9472; S7.E2.1    FORMAL PASS
      &#9500;&#9472;&#9472; S7.E2.2    descriptive realization
      &#9492;&#9472;&#9472; S7.12      Q_rec*  &mdash;  CLOSED</pre></div>
<p class="note">One scientific <strong>task</strong>, two claim branches. A claim
branch fixes (q, &#8464;<sub>q</sub>, U<sub>q</sub>, &#119985;<sub>q</sub>,
&Omega;<sub>q</sub>); an operational epoch revises (&#119979;<sub>q</sub>,
&#8492;<sub>q</sub>, &#8459;<sub>q</sub>). The branch changes at
<strong>S7.E2.0</strong>, not at S7.K2, because that is where the evidentiary
commitment narrowed after protected evidence was spent.
<code>vsurf &rarr; density</code> corrected a target <em>instance</em>, not the
task. See <a href="REVISION_LEDGER.md">REVISION_LEDGER.md</a> and
<a href="ARCHITECTURE_SEMANTICS_AUDIT.md">ARCHITECTURE_SEMANTICS_AUDIT.md</a>.</p>

<h2>The iterative arc</h2>
<figure style="margin:12px 0"><img src="figures/fig_s7_iterative_arc.png"
alt="the q_rec iterative arc"
style="width:100%%;border:1px solid var(--line);border-radius:6px"></figure>
<p class="note">The scientific <strong>task</strong> is unchanged throughout —
no new <code>q</code> was ever required. S7.K2 advances the operational epoch
inside <code>QREC-B1</code>; S7.E2.0 narrows the evidentiary commitment and
constitutes the descendant branch <code>QREC-B2</code>. See
<a href="REVISION_LEDGER.md">REVISION_LEDGER.md</a>.</p>

<h2>The qualified result</h2>
<div class="scroll"><table><tr><th>quantity</th><th>value</th></tr>%(epoch)s</table></div>
<div class="scroll"><table>
<tr><th>method</th><th>mean</th><th>median</th><th>paired Δ</th><th>W/T/L</th></tr>
%(base)s</table></div>
<p class="note"><strong>The claim.</strong> Within the predictor-qualified frozen
62-discharge observational object, relational supports discovered without a
discharge's own target values reconstruct that discharge nontrivially relative to
the frozen baselines. <strong>Not</strong> external validation, future-discharge
transfer, zero-shot inference, a universal relation or a unique equation.
Boundary: <a href="S7_12_qualified_result/S7_12_CLAIM_BOUNDARY.md">S7_12_CLAIM_BOUNDARY.md</a>.</p>

<h2>Evidence</h2>
%(figs)s

<h2>Canonical stages</h2>
<div class="grid">%(tiles)s</div>

<h2>Preserved history</h2>
<p class="note">Superseded and retired work is kept, never overwritten.</p>
<div class="scroll"><table><tr><th>path</th><th>what</th><th>status</th>
<th>why</th></tr>%(hist)s</table></div>

<h2>Audit</h2>
<p>Verdict <span class="b warn">%(verdict)s</span> — the S7 workflow is sound and
independently reproducible; <strong>no BLOCKER and no MAJOR finding inside
S7</strong>. Both MAJOR findings concern the manuscript.</p>
<div class="scroll"><table><tr><th>#</th><th>level</th><th>finding</th>
<th>where</th></tr>%(find)s</table></div>

<h2>Documents</h2>
<div class="scroll"><table><tr><th>file</th><th>purpose</th></tr>
<tr><td><a href="README.md">README.md</a></td><td>entry point</td></tr>
<tr><td><a href="WORKFLOW.md">WORKFLOW.md</a></td><td>dependency graph, chronology, presentation order</td></tr>
<tr><td><a href="SIR_ARCHITECTURE_MAP.md">SIR_ARCHITECTURE_MAP.md</a></td><td>every stage placed in the SIR graph</td></tr>
<tr><td><a href="REVISION_LEDGER.md">REVISION_LEDGER.md</a></td><td>14 revisions, classified Case A / B / C</td></tr>
<tr><td><a href="INFORMATION_FLOW_AUDIT.md">INFORMATION_FLOW_AUDIT.md</a></td><td>leakage and target-ancestry audit</td></tr>
<tr><td><a href="AUDIT_REPORT.md">AUDIT_REPORT.md</a></td><td>full forensic audit</td></tr>
<tr><td><a href="MANUSCRIPT_ALIGNMENT.md">MANUSCRIPT_ALIGNMENT.md</a></td><td>27 manuscript statements classified</td></tr>
<tr><td><a href="ARCHITECTURE_SEMANTICS_AUDIT.md">ARCHITECTURE_SEMANTICS_AUDIT.md</a></td><td>task / branch / epoch reconciliation with the current §1.1</td></tr>
<tr><td><a href="REPRODUCIBILITY.md">REPRODUCIBILITY.md</a></td><td>how to check all of this yourself</td></tr>
<tr><td><a href="STATUS.md">STATUS.md</a></td><td>living stage index</td></tr>
</table></div>
<p class="note">Machine-readable: <code>CANONICAL_INDEX.json</code> ·
<code>AUDIT_REPORT.json</code> · <code>AUDIT_CHECKS.json</code> ·
<code>MANUSCRIPT_ALIGNMENT.json</code> · <code>INFORMATION_FLOW_AUDIT.json</code> ·
<code>CLAIM_EVIDENCE_MATRIX.json</code> · <code>ARCHITECTURE_SEMANTICS_AUDIT.json</code> · <code>figures/FIGURE_PROVENANCE.json</code></p>

<h2>Verify</h2>
<div class="card"><code>cd D:\\SIR_paper\\DIIID_example\\S7 &amp;&amp; python audit_s7.py</code>
<br><span class="note">Offline. Exit 0 if no BLOCKER or MAJOR check fails.</span></div>

<div class="nav"><div class="note">generated %(now)s</div>
<div class="note">no network dependency &middot; no tracking</div></div>
</div>""" % {
    "css": CSS, "chain": CHAIN, "tiles": tiles, "hist": hist, "find": find,
    "figs": figblocks, "verdict": esc(fnd["verdict"]),
    "epoch": "".join("<tr><td>%s</td><td><span class='b %s'>%s</span></td></tr>"
                     % (k, c, v) for k, v, c in EPOCH_ROWS),
    "base": "".join("<tr><td>%s</td><td class='num'>%s</td><td class='num'>%s</td>"
                    "<td class='num'>%s</td><td class='num'>%s</td></tr>" % r
                    for r in BASE),
    "semverdict": esc(sem["verdict"].replace("S7_", "").replace("_", " ").lower()),
    "now": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
}
(S7 / "index.html").write_text(html, encoding="utf-8")
print("wrote index.html (%d stages, %d findings, %d figures)"
      % (len(idx["stages"]), len(fnd["findings"]), len(figs["figures"])))
