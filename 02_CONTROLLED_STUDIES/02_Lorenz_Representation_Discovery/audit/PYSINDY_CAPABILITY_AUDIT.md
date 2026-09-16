# PySINDy capability audit

**Date:** 2026-08-27 · **Version audited:** PySINDy **2.1.0** (PyPI wheel,
`D:/SIR_paper/.venv_lorenz_benchmark/`)

Purpose: ensure the manuscript makes **no claim about PySINDy that its actual
API contradicts.** Everything below was verified by inspecting the installed
package, not assumed.

---

## 1. What PySINDy 2.1.0 actually provides

**Feature libraries** (`pysindy.feature_library`):
`ConcatLibrary`, `CustomLibrary`, `FourierLibrary`, `GeneralizedLibrary`,
`IdentityLibrary`, `PDELibrary`, `ParameterizedLibrary`, `PolynomialLibrary`,
`SINDyPILibrary`, `TensoredLibrary`, `WeakPDELibrary`.

**Optimizers** (`pysindy.optimizers`):
`STLSQ`, `SR3`, `SSR`, `FROLS`, `EnsembleOptimizer`, `WrappedOptimizer`,
`BaseOptimizer`.

**Core API:** `SINDy.fit(x, t, x_dot=None, u=None, feature_names=None)`, with
`coefficients()`, `equations()`, `complexity`, `predict()`, `score()`,
`simulate()`.

| Capability | Verified | Notes |
|---|---|---|
| Custom feature libraries | **yes** | `CustomLibrary(library_functions, function_names, interaction_only, include_bias)` |
| Arbitrary precomputed features | **yes** | `IdentityLibrary` passes a supplied matrix through unchanged |
| Heterogeneous libraries on different input subsets | **yes** | `GeneralizedLibrary(libraries, inputs_per_library=...)` |
| Library composition / tensoring | **yes** | `ConcatLibrary`, `TensoredLibrary` |
| Supplying derivatives externally | **yes** | `fit(..., x_dot=...)` bypasses internal differentiation |
| Multiple sparse optimizers | **yes** | five, plus a sklearn wrapper |
| Ensembling / bootstrap | **yes** | `EnsembleOptimizer` |
| Weak/integral formulation | **yes** | `WeakPDELibrary` |

**Conclusion: PySINDy is genuinely extensible.** Any claim that it "cannot use"
expanded, rational, phase-derived, or otherwise custom coordinates would be
false. In this benchmark it is *given* every coordinate SIR generates.

## 2. What PySINDy does not represent as a first-class object

This is a statement about the library's data model, not its numerical power.

PySINDy's fitted object is `(library, optimizer, coefficients)`. It has no
built-in representation of:

- a **scientific object** bundling observational support, uncertainty model,
  provenance and admissibility constraints;
- an **admissibility constraint** such as "no coordinate may depend on z"
  (enforceable by the user when constructing the library, but not carried,
  checked, or exported by the object);
- a **task utility** distinct from regression loss (e.g. worst-case error over a
  declared observational-uncertainty envelope);
- a **qualified model set** (accuracy-equivalent candidates under a stated
  equivalence rule);
- **validation requirements** (grouped CV, held-out contracts) as part of the
  fitted artifact rather than surrounding user code.

All of these can be *built around* PySINDy — and Step 12 of this benchmark does
exactly that, deliberately, as a control.

## 3. Language the manuscript may and may not use

**Defensible:**
- "PySINDy can consume SIR-generated coordinates when supplied with them."
- "PySINDy may serve as the relation-fitting solver inside a SIR contract."
- "In the conventional workflow examined here, the scientific problem
  formulation — information boundary, admissible coordinates, relation family,
  utility, validation — is supplied upstream of the estimator."
- "SIR makes that formulation an explicit computational object that
  participates in discovery."

**Not defensible, and avoided:**
- "PySINDy cannot do task conditioning." (False — a user can implement it.)
- "PySINDy cannot use rational or phase coordinates." (False — `CustomLibrary`.)
- "PySINDy requires polynomial libraries." (False.)
- Any comparison in which PySINDy is given only a linear fit on raw
  coordinates. This benchmark therefore includes degree-2 and degree-3
  polynomial baselines over the full information-matched stencil.

## 4. Recommended phrasing for Section 1.4

> In the conventional workflow examined here, PySINDy solves a
> model-identification problem after much of the scientific problem formulation
> has been supplied. SIR makes that problem formulation — the scientific object,
> information boundary, admissible coordinates, relational families, utility and
> validation requirements — an explicit computational object that participates
> in discovery.

The qualifier "In the conventional workflow examined here" is recommended: the
unqualified form could be read as a claim about the software's capability rather
than about where the formulation sits in the workflow. With the qualifier the
sentence is accurate and survives this audit.

## 5. Citation (for the bibliography — not inserted automatically)

```bibtex
@article{deSilva2020pysindy,
  title   = {PySINDy: A Python package for the sparse identification of
             nonlinear dynamical systems from data},
  author  = {de Silva, Brian M. and Champion, Kathleen and Quade, Markus and
             Loiseau, Jean-Christophe and Kutz, J. Nathan and Brunton, Steven L.},
  journal = {Journal of Open Source Software},
  volume  = {5}, number = {49}, pages = {2104}, year = {2020},
  doi     = {10.21105/joss.02104}
}

@article{Kaptanoglu2022pysindy,
  title   = {PySINDy: A comprehensive Python package for robust sparse system
             identification},
  author  = {Kaptanoglu, Alan A. and de Silva, Brian M. and Fasel, Urban and
             Kaheman, Kadierdan and Goldschmidt, Andy J. and Callaham, Jared L.
             and Delahunt, Charles B. and Nicolaou, Zachary G. and Champion,
             Kathleen and Loiseau, Jean-Christophe and Kutz, J. Nathan and
             Brunton, Steven L.},
  journal = {Journal of Open Source Software},
  volume  = {7}, number = {69}, pages = {3994}, year = {2022},
  doi     = {10.21105/joss.03994}
}
```

Also cite the original SINDy paper (Brunton, Proctor & Kutz, PNAS 113(15):3932,
2016) where the method rather than the software is meant. **Verify these entries
against the SIR bibliography before insertion — they were written from standard
knowledge, not fetched, and the DOIs should be confirmed.**
