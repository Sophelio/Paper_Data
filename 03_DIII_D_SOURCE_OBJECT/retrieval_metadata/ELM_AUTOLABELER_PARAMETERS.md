# ELM Autolabeler Parameter Glossary

Reference for the four ELM autolabelers registered by `diiid_elm_dfl_provider.py`. All of them
live in `autolabeling_utilities.py` and emit individual ELM bursts as `ELM` labels — an interval
carries `ELM`, and anything unlabeled is implicitly ELM-free.

## How the inputs behave

Every parameter is a **text box** except the two dropdowns (D-alpha channel, filter type).

- **The box shows `Default: 8.0` as a greyed placeholder, not a value.** dFL renders autolabeler
  parameters with no initial value, so the default can only appear as a hint. This is expected.
- **Leaving a box blank uses the default shown in the placeholder.** You only need to type in a
  box to override it.
- Times are **milliseconds** everywhere *except* the two Tomas parameters, which are in
  **seconds**. This is inherited from the original detector and is the easiest mistake to make.

## Which labeler to use

They disagree by design — they are different detectors, not tunings of one. Typical counts on
shot 155537, full shot, all defaults:

| Labeler | Labels | What it marks |
|---|---|---|
| `osborne` | 1654 | Every individual burst; most sensitive |
| `v3_bursts` | 91 | Individual bursts, shape-validated |
| `tomas` | 30 | Individual bursts, conservative |
| `elm` | 4 | Whole ELMing **periods**, not bursts |

`elm` is the odd one out: it merges bursts within `merge_time` into long periods, so it returns
a handful of long intervals rather than many short ones. Set `merge_time` to `0` if you want it
to mark individual bursts instead. It is also much slower (it always scans the whole shot,
regardless of your trim window) and prints a lot of diagnostics to the console.

---

## `osborne` — Osborne (pyD3D findelms)

Tom Osborne's operational DIII-D detector. Builds a 10th-percentile baseline, then an adaptive
threshold envelope, and turns ELMs on/off with **hysteresis** — a burst starts when the signal
rises above `blhigh` x envelope and only ends when it falls below `bllow` x envelope. Thresholds
are fractions of the signal maximum, so raw amplitude is fine.

| Parameter | Default | Units | Meaning |
|---|---|---|---|
| D-alpha channel | `fs04` | — | Filterscope channel to run on |
| ELM-on envelope multiplier (`blhigh`) | `0.8` | fraction | Burst **starts** above this x envelope. Raise → fewer, later starts |
| ELM-off envelope multiplier (`bllow`) | `0.3` | fraction | Burst **ends** below this x envelope. Raise → shorter bursts |
| Baseline window (`tbl`) | `5.0` | **ms** | Baseline averaging window. Raise → smoother, less reactive baseline |
| Minimum ELM duration (`dtmin_elm`) | `0.2` | **ms** | Bursts shorter than this are dropped. Raise → fewer |

Keep `bllow` < `blhigh`. Inverting them defeats the hysteresis and produces unstable
start/end times. Only these four knobs are exposed; the rest of the detector (matched filter,
noise floor, derivative edge jumps) stays at its original defaults.

> If the console logs `Osborne: noisy trace on shot ... channel ...`, the detector's own noise
> check judged the trace too noisy relative to its peak. Labels are still returned, but treat
> them with suspicion — try a different channel.

---

## `tomas` — Tomas (order-filter envelope)

Tomas Odstrcil's recipe. Decimates x10, subtracts an order-filter baseline, builds a median
envelope, and thresholds against it.

**Both time parameters here are in seconds, not milliseconds.**

| Parameter | Default | Units | Meaning |
|---|---|---|---|
| D-alpha channel | `fs04` | — | Filterscope channel to run on |
| Envelope threshold multiplier (`threshold`) | `8.0` | multiplier | Signal must exceed this x envelope. Raise → fewer |
| Minimum ELM duration (`min_elm_len_s`) | `0.0005` | **seconds** (0.5 ms) | Bursts shorter than this are dropped |
| Veto time before first ELM (`veto_time_s`) | `0.5` | **seconds** (500 ms) | No ELMs detected before this time |

`0.0005` is half a millisecond. Typing `0.5` here — as if it were ms — would silently discard
almost every burst.

---

## `v3_bursts` — v3 bursts (DoS + MAD)

The burst core of the v3 regime detector. Computes a difference-of-smoothing (mildly smoothed
minus heavily smoothed), thresholds it with a sliding-window MAD, then validates that each
candidate has a real ELM rise-and-fall shape rather than a sustained baseline rise.

Only the burst stage is used. v3's regime merging is deliberately left out — it over-merges, and
burst markers are what this provider labels.

| Parameter | Default | Units | Meaning |
|---|---|---|---|
| D-alpha channel | `fs04` | — | Filterscope channel to run on |
| Burst MAD factor (`burst_mad_factor`) | `8.0` | multiplier | Detection threshold in MADs above local median. **The main sensitivity knob** |
| Max burst duty fraction (`burst_max_fraction`) | `0.01` | fraction | Floor on the threshold, as a fraction of the global maximum. Stops quiet stretches producing spurious bursts. Raise → fewer |
| Minimum peak / local median ratio (`burst_min_peak_ratio`) | `1.5` | ratio | A burst's peak must exceed this x the local median. Raise → fewer |

`burst_mad_factor` is the knob to reach for first: on shot 155537 (2000–2500 ms), `8.0` gives 11
labels and `20.0` gives 6.

> **Known quirk.** This labeler normalizes by the peak of the *trimmed* window, but the detector
> is tuned for signals normalized over the whole shot. Its output therefore shifts depending on
> your trim window. Worth knowing when comparing runs.

---

## `elm` — Slope outliers + betan

Detects positive-slope outliers in the filtered D-alpha derivative, merges nearby ones into
**ELMing periods**, then gates those periods on betan. Structurally different from the other
three — see "Which labeler to use" above.

| Parameter | Default | Units | Meaning |
|---|---|---|---|
| Positive derivative threshold (`pos_deriv_thresh`) | `2.7` | std devs | Slope must exceed this many standard deviations above the mean. **The main sensitivity knob**; raise → fewer |
| ELM merge time (`merge_time`) | `100.0` | ms | Outliers closer than this merge into one period. **Set to `0` for individual bursts** — on shot 155537 that turns 4 long periods into 36 bursts. Raise → fewer, longer periods |
| Start time padding (`start_time_padding`) | `0.0` | ms | Extra time added before each label |
| End time padding (`end_time_padding`) | `0.0` | ms | Extra time added after each label |
| Filter type (`filter_type`) | `mean` | dropdown | Smoothing before the derivative: `mean`, `median`, `ema`, `gaussian`, `none` |
| Filter size (`filter_size`) | `5` | samples | Smoothing window. Raise → smoother, fewer small bursts |
| BETANF filter threshold (`betanf_filter_threshold`) | `1.0` | betan | Regions whose mean absolute betan is below this are discarded. Raise → more filtered out |
| BETANF window size (`window_size_ms`) | `50` | ms | Sliding window for the betan gate |
| BETANF window overlap (`window_overlap_ms`) | `25` | ms | Overlap between betan windows; must be < window size |

Notes specific to this labeler:

- **It always runs on the whole shot**, ignoring your trim window; the resulting labels are then
  clipped to the window. So a narrow trim does not make it faster.
- **The first 700 ms are always excluded** — hardcoded, not exposed in the GUI.
- It picks its own D-alpha channel by signal-to-noise (from `fs04da`, `fs03da`, `fs05da`,
  `fs04`), which is why it has no channel dropdown.
- Internally it also produces `ELMfree` regions. This provider's vocabulary is bursts-only, so
  those rows are dropped and only `ELM` intervals reach the table.

---

## Quick tuning guide

**Too many labels / noise being caught:** raise the main sensitivity knob — `blhigh` (osborne),
`threshold` (tomas), `burst_mad_factor` (v3), `pos_deriv_thresh` (elm). Raising the minimum
duration also removes short spurious bursts.

**Missing real ELMs:** lower the same knob. If small ELMs are still missed, try another
D-alpha channel — `fs04` is the primary divertor filterscope, but `fs04da` / `fs03da` / `fs05da`
can be cleaner on a given shot.

**Labels are merged into long blocks when you wanted individual bursts:** you are on `elm`. Set
`merge_time` to `0`, or use `osborne` / `tomas` / `v3_bursts` instead.

**Nothing at all comes back:** check the units (Tomas is in seconds), check you aren't inside
the first 700 ms with `elm` or before `veto_time_s` with `tomas`, and check the console for a
noise warning.
