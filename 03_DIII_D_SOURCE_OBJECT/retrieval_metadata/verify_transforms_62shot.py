"""62-shot DIII-D consistency check: corrected Dalia blocks vs Archaieus.

Runs every applicable transform on the real resampled_data_v6 cohort and
reports max|diff|, RMS diff, correlation and finite counts against the
canonical Archaieus implementation.

Also reproduces the pre-audit sensitivity-centered failure
(|corr(output, u_n)| == 1) and demonstrates that it is gone.

    python DIIID_example/verify_transforms_62shot.py
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE / "data" / "resampled_data_v6"
ARCH_UTILS = Path(r"D:\sir-web\submodules\Archaieus\src\Archaieus\sir\utils")

NUM, DEN = "pcdiamag3", "ip"
RHO, KAPPA, METHOD = 0.1, 1.0, "pooled_rms"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _load_archaieus():
    pkg = types.ModuleType("_arch_shim")
    pkg.__path__ = [str(ARCH_UTILS)]
    sys.modules["_arch_shim"] = pkg
    for mod in ("channel_normalization", "conditioning_aware"):
        spec = importlib.util.spec_from_file_location(
            f"_arch_shim.{mod}", ARCH_UTILS / f"{mod}.py"
        )
        m = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = m
        spec.loader.exec_module(m)
    return sys.modules["_arch_shim.conditioning_aware"]


arch = _load_archaieus()
new = _load("_dalia_new", HERE / "_dalia_runtime_transforms.py")

OLD_PATH = HERE / "_dalia_prefix_transforms.py"
old = _load("_dalia_old", OLD_PATH) if OLD_PATH.is_file() else None


def _stats(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 2:
        return None
    d = a[m] - b[m]
    denom = np.std(b[m]) or 1.0
    sa, sb = np.std(a[m]), np.std(b[m])
    corr = (
        float(np.corrcoef(a[m], b[m])[0, 1]) if sa > 0 and sb > 0 else float("nan")
    )
    return {
        "n": int(m.sum()),
        "max_abs": float(np.max(np.abs(d))),
        "rms": float(np.sqrt(np.mean(d**2))),
        "rms_rel": float(np.sqrt(np.mean(d**2)) / denom),
        "corr": corr,
    }


def main() -> None:
    T = new
    ids = T._shot_ids(ROOT)
    print(f"cohort: {len(ids)} shots   numerator={NUM}  denominator={DEN}")
    print(f"params: rho={RHO}  kappa={KAPPA}  scale_method={METHOD}\n")

    blocks = T.build_transforms(ROOT)

    # ---- cohort fits -----------------------------------------------------
    S_n_rate = T._fit_rate_scale(ROOT, NUM, METHOD)
    S_d_rate = T._fit_rate_scale(ROOT, DEN, METHOD)
    S_n_lvl = T._fit_operand_scale(ROOT, NUM, METHOD)
    S_d_lvl = T._fit_operand_scale(ROOT, DEN, METHOD)
    s_0 = T._fit_clearance_normalized(ROOT, DEN, True, S_d_rate, METHOD)
    s_eff = s_0 + KAPPA
    g_bar = T._fit_mean_gain(ROOT, DEN, True, S_d_rate, METHOD, RHO, s_eff)

    print("fitted quantities (corrected)")
    print(f"  S_n rate  = {S_n_rate:.6g}")
    print(f"  S_d rate  = {S_d_rate:.6g}")
    print(f"  s_0       = {s_0:.6g}   (normalized denominator)")
    print(f"  s_eff     = {s_eff:.6g}")
    print(f"  g_bar     = {g_bar:.6g}")
    if old is not None:
        old_s_eff = old._fit_clearance(ROOT, DEN, is_rate=True) + KAPPA
        print(f"  pre-audit s_eff = {old_s_eff:.6g}  "
              f"({old_s_eff / s_eff:.1f}x too large)")
    print()

    # ---- per-transform comparison ---------------------------------------
    cases = {
        "reference_shifted_phase": dict(num_rate=True, kind="rs"),
        "level_rate_relational": dict(num_rate=False, kind="rs"),
        "sensitivity_centered_phase": dict(num_rate=True, kind="sc"),
        "tangent_direction": dict(num_rate=False, kind="td"),
    }

    for block, cfg in cases.items():
        fn = blocks[block]["function"]
        params = {
            "denominator": DEN,
            "rho": RHO,
            "kappa": KAPPA,
            "scale_method": METHOD,
        }
        rows = []
        for rid in ids:
            t_n, v_n = T._load_signal(ROOT, rid, NUM)
            t_d, v_d = T._load_signal(ROOT, rid, DEN)
            _, got = fn(t_n, v_n, params, {"signal_name": NUM, "record_id": rid})

            if cfg["kind"] == "td":
                u_n = np.asarray(v_n) / S_n_lvl
                u_d = T._align_to(t_n, t_d, v_d) / S_d_lvl
                want, _ = arch.tangent_direction_components(u_n, u_d, RHO)
            else:
                num = T._dt_derivative(t_n, v_n) if cfg["num_rate"] else np.asarray(v_n)
                S_num = S_n_rate if cfg["num_rate"] else S_n_lvl
                u_n = num / S_num
                u_d = T._align_to(t_n, t_d, T._dt_derivative(t_d, v_d)) / S_d_rate
                if cfg["kind"] == "sc":
                    want = arch.sensitivity_centered_clearance_ratio(
                        u_n, u_d, RHO, s_eff, g_bar
                    )
                else:
                    want = arch.clearance_shifted_regularized_ratio(
                        u_n, u_d, RHO, s_eff
                    )
            st = _stats(np.asarray(got), np.asarray(want))
            if st:
                rows.append(st)

        mx = max(r["max_abs"] for r in rows)
        rm = max(r["rms"] for r in rows)
        cr = [r["corr"] for r in rows if np.isfinite(r["corr"])]
        ntot = sum(r["n"] for r in rows)
        print(f"{block}")
        print(f"  shots compared        : {len(rows)}")
        print(f"  finite samples        : {ntot}")
        print(f"  worst max|diff|       : {mx:.3e}")
        print(f"  worst RMS diff        : {rm:.3e}")
        print(f"  min correlation       : {min(cr):.12f}" if cr else "  corr: n/a")
        print(f"  verdict               : "
              f"{'AGREE to float precision' if mx < 1e-12 else 'DIFFERS'}")
        print()

    # ---- the headline regression ----------------------------------------
    print("sensitivity-centered collapse check  |corr(output, u_n)|")
    fn_new = blocks["sensitivity_centered_phase"]["function"]
    params = {"denominator": DEN, "rho": RHO, "kappa": KAPPA, "scale_method": METHOD}
    for label, fn, mod in (
        ("pre-audit ", None if old is None else old.build_transforms(ROOT)[
            "sensitivity_centered_phase"]["function"], old),
        ("corrected ", fn_new, T),
    ):
        if fn is None:
            print(f"  {label}: (pre-audit copy not available)")
            continue
        cors = []
        for rid in ids:
            t_n, v_n = T._load_signal(ROOT, rid, NUM)
            _, out = fn(t_n, v_n, params, {"signal_name": NUM, "record_id": rid})
            u_n = T._dt_derivative(t_n, v_n) / S_n_rate
            m = np.isfinite(out) & np.isfinite(u_n)
            if m.sum() > 10 and np.std(out[m]) > 0:
                cors.append(abs(float(np.corrcoef(out[m], u_n[m])[0, 1])))
        cors = np.array(cors)
        print(f"  {label}: median={np.median(cors):.10f}  "
              f"min={cors.min():.10f}  max={cors.max():.10f}")

    print()
    print("sensitivity-centering property  mean_fit(g - g_bar)")
    chunks = []
    for series in T._cohort_operand(ROOT, DEN, True):
        u_d = np.asarray(series) / S_d_rate
        chunks.append(T._finite(T._denominator_gain(u_d, RHO, s_eff)))
    pool = np.concatenate(chunks)
    print(f"  mean(g - g_bar) = {float(np.mean(pool - g_bar)):.3e}   (must be ~0)")


if __name__ == "__main__":
    main()
