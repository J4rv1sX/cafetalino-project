# Consumption prediction model

Predicts how much of each consumable a vending machine will need on its next
refill visit, so the business can tell which machines need a reload on a
given day. This document covers the data, the modeling process (including
the dead ends and honest negative results), the final architecture, and how
the trained models are saved and reloaded.

## Problem framing

- **Inputs**: `location_id` (which machine) and `days_since_previous_refill`
  (how long since it was last serviced), decided at the start of this work.
- **Targets** (5, predicted independently): `bottled_water_ml`, `cup_units`,
  `coffee_mix_g`, `chocolate_mix_g`, `cappuccino_mix_g`.
- **Framework**: scikit-learn, not TensorFlow. TensorFlow is a backend
  dependency (`pyproject.toml`) but was deliberately not used here — with
  ~2,550 training rows, a neural net has nowhere near enough data to
  outperform tree-based models, and would just add complexity (GPU/CUDA
  dependency, architecture search) for no benefit. This was reconfirmed
  later in the project when a second opinion was asked ("would a neural
  net do better?") — answer: no, for the same reason.
- **5 independent models, not 1 multi-output model**: the 5 targets differ
  in scale and dynamics (milliliters vs. grams vs. unit counts), so each
  gets its own regressor rather than forcing one model to predict all 5.

## Data

`backend/data/cafetalino.db` (SQLite), built from `consumo_insumos.csv` by
`backend/scripts/load_consumption.py`. Two tables:

- `locations(id, name, lat, lng)` — 17 canonical machine locations.
- `readings(id, location_id, date, raw_location_name, cups,
  water_remaining_pct, previous_refill_date, days_since_previous_refill,
  bottled_water_ml, cup_units, coffee_mix_g, chocolate_mix_g,
  cappuccino_mix_g, notes)` — 2,467 rows, one per machine visit (as of the
  `consumo_insumos.csv` refresh in the "Update consumption CSV" commit;
  earlier revisions of this doc were written against a 2,576-row snapshot,
  so metrics below aren't strictly comparable to any numbers recorded prior
  to that refresh).

`days_since_previous_refill` is nullable (rows that are a machine's very
first-ever reading have no prior refill to measure from).

## Feature engineering — what was tried, in order, and why

| Feature | R² impact (single 80/20 split, as first measured) | Kept? |
|---|---|---|
| `location_id`, `days_since_previous_refill` (baseline) | 0.088–0.123 across the 5 targets | Yes |
| `day_of_week`, `month` (from `date`) | 0.096–0.123 — small, marginal gain | Yes |
| `historical_mean_{target}` (expanding mean of that location's *prior* readings) | **Large**: 0.096–0.123 → 0.428–0.602 | Yes |
| `recent_mean_{target}` (rolling mean of the last 3 prior readings) | Small — see Evaluation methodology below, where the switch to cross-validation in the same round revealed the single-split numbers above had been overly optimistic all along | Yes |
| `historical_rate_{target}`, `recent_rate_{target}` (the two features above, each divided by the matching `historical_mean_days`/`recent_mean_days` -- i.e. a per-day-since-refill consumption rate) | Measured via 5-fold CV **MAE** (not R², to sidestep R²'s instability at this data size) on a fixed before/after comparison: all 5 targets improved, by 1.9-3.3% each (e.g. `bottled_water_ml` 1757.13±147.30 -> 1699.03±150.37). Every individual delta sits within 1 fold-to-fold std, so no single target clears significance alone, but 5/5 moving the same direction is unlikely by chance (~3%) and matches the mechanistic story: the rate feature hands the model a ratio it would otherwise have to re-derive from `days_since_previous_refill` interactions on a small dataset | Yes |

Other columns considered and explicitly **rejected**:

- `water_remaining_pct`, `cups` — these are measured *during* the same visit
  as the targets being predicted. Using them would mean "you need to already
  be at the machine to predict what the machine needs," which defeats the
  point of predicting ahead of a route. (Their *lagged*, i.e. previous-visit,
  values would have been fine — not implemented, since `historical_mean`/
  `recent_mean` already cover that idea more robustly.)
- `notes` — 87% empty free text, not useful as a model feature (still kept
  in the DB for audit purposes).
- `raw_location_name`, `lat`/`lng` — redundant with `location_id`.
- **Not implemented, flagged as a future idea**: an academic/holiday
  calendar feature. Several locations are university or hospital sites
  (`Seguro Social Universitario`, `UNIVALLE`) where traffic plausibly
  swings with the semester/holiday calendar more than with generic
  `month`. Needs an external data source not currently in this DB.

**No-leakage rule applied throughout**: every lag/historical feature is
computed with `.shift(1)` before `.expanding()`/`.rolling()`, so a row never
sees its own target value baked into its own feature. Confirmed this isn't
trivially satisfied by the existing null-`days_since_previous_refill` drop:
checked directly against the DB that 0 of 17 locations' earliest dataset row
coincides with a null `days_since_previous_refill` — every location already
had refill history before this CSV's data window started. So the row-drop
for missing lag features is a separate, explicit
`dropna(subset=FEATURE_COLUMNS)` (drops 28 rows as of the current CSV: 17
first-per-location rows whose `historical_mean`/`recent_mean` are undefined,
plus 11 rows elsewhere in the sequence with a null `days_since_previous_refill`
from a mid-history gap in that machine's refill records), not implied by the
`days_since_previous_refill` null check alone.

### Post-deployment ablations: is `day_of_week`/`month` pulling its weight?

Raised after the rate-feature deployment above, as two separate hypotheses
about whether the two calendar features are well-chosen, not just present:

1. **`day_of_week` records the day the technician visited, not the
   composition of the elapsed interval.** The visit day is an artifact of
   the route schedule, not something that should mechanically drive
   consumption — what plausibly matters is how much of the
   `days_since_previous_refill` interval was weekday (office/campus
   traffic) vs. weekend. Tested a replacement, `weekday_fraction`: the
   fraction of that interval's days that were weekdays, computed as
   `np.busday_count(previous_refill_date, date) / days_since_previous_refill`
   (both dates already in the DB).
2. **Is `month` actually capturing a seasonal effect, or is it too
   fine-grained to learn reliably from ~145 rows/location spread across 12
   months?** Tested two alternatives: dropping `month` entirely, and
   replacing it with `quarter` (a coarser 4-bucket season proxy, pooling
   ~3x more rows per bucket).

All three alternatives were evaluated with the identical CV/search setup as
production (`RandomizedSearchCV`, 30 iterations, 5-fold CV, same
hyperparameter grids), on the same 2,439-row set as the current deployed
model, varying only the feature(s) under test:

| target | `day_of_week`→`weekday_fraction` | `month` dropped | `month`→`quarter` |
|---|---|---|---|
| bottled_water_ml | +1.46 | **+11.10** | +10.62 |
| cup_units | +0.01 | +0.06 | +0.06 |
| coffee_mix_g | +0.02 | +0.05 | +0.05 |
| chocolate_mix_g | +0.20 | +0.91 | +0.85 |
| cappuccino_mix_g | +0.03 | +0.01 | −0.10 |

(MAE delta vs. the production baseline; positive = worse. `hist_gradient_boosting`
won every cell.)

**Findings:**

- **`weekday_fraction` did not beat `day_of_week`** — deltas are all
  essentially zero (≤0.09% of MAE, far inside 1 fold-to-fold std
  everywhere). The hypothesis was reasonable, but the data doesn't support
  it: `day_of_week` already captures whatever signal exists there just as
  well. **Kept `day_of_week` unchanged.**
- **`month` is genuinely pulling weight** — dropping it made every single
  target worse, most notably `bottled_water_ml` (+11.10, the largest delta
  of any ablation tested here). 5/5 targets moving the same direction is
  unlikely by chance, so this isn't noise.
- **Bucketing into `quarter` recovers almost none of that loss** — its
  deltas nearly match `month`-dropped's, target for target. That's the
  interesting negative result: it rules out "any coarse seasonal signal
  would do" — the informative part of `month` is at (or near) its native
  12-category granularity, not a broad 4-season cycle. That's consistent
  with the `month` proxy partly standing in for something more specific
  than climate season, e.g. the academic/holiday calendar idea flagged
  above as unimplemented. **Kept `month` unchanged, at full granularity.**

Net: no production code changed as a result of this round — both are
honest negative results, recorded here so the same alternatives aren't
re-tried from scratch later without knowing they were already checked.

### Post-deployment ablation: short-term trend feature

`recent_mean_{target}` captures a location's recent *level* (a 3-reading
rolling average) but not *direction* — whether consumption at that machine
is trending up or down. Tested `trend_rate_{target}`, the per-day rate of
change between the two most recent *prior* readings:

```
trend_rate_{target} = (shift(1)[target] - shift(2)[target])
                       / (shift(1)[days_since_previous_refill] + EPS)
```

normalized by elapsed time the same way the already-validated rate
features are (per-day, not per-refill-cycle), for consistency with that
precedent rather than a raw un-normalized diff.

**A real bug surfaced during construction, not just at evaluation**: the
denominator is a single prior *gap* (not a mean over many gaps like
`historical_mean_days`/`recent_mean_days`), and it can be exactly 0 — the
same 5 locations with same-day duplicate readings that already show up
elsewhere in this doc. Guarding that division with the usual small `EPS`
(as the historical/recent rate features do, safely, since *their*
denominators are means and therefore practically never near 0) instead
blew the ratio up to the billions for those rows (observed range: -8.28e9
to 5.4e9). Fixed by marking the rate `NaN` when the prior gap is `<= 0`
(a same-day duplicate has no meaningful per-day rate, so it should be
excluded, not divided-by-near-zero) rather than papering over it with
`EPS`. This drops 58 rows total (vs. 28 for the production feature set),
since it also requires a *second* prior reading per location, not just one.

Evaluated with the identical CV/search setup as production, on the
resulting 2,409-row set (baseline re-measured on that same reduced set,
so this is apples-to-apples — note the baseline MAE/model below therefore
differs slightly from the production numbers elsewhere in this doc, which
are measured on the full 2,439-row set):

| target | baseline MAE | +trend MAE | delta |
|---|---|---|---|
| bottled_water_ml | 1680.85±192.94 | 1692.10±200.07 | +11.25 |
| cup_units | 9.34±1.08 | 9.40±1.11 | +0.06 |
| coffee_mix_g | 22.17±2.17 | 22.22±2.12 | +0.05 |
| chocolate_mix_g | 86.93±5.52 | 87.29±5.22 | +0.35 |
| cappuccino_mix_g | 89.20±8.64 | 89.76±8.72 | +0.56 |

**Finding: made every target worse**, not just a wash like the
`day_of_week`/`month` alternatives above — 5/5 targets moved the same
(bad) direction, which is as statistically meaningful here as the 5/5
*improvements* that justified keeping the historical/recent rate features.
Likely explanation: a 2-point difference is a much noisier estimator than
the 3-point rolling means the existing rate features are built from, and
it costs real training data too (58 dropped rows vs. 28) for a signal that
turned out not to exist at this data size. **Not implemented.**

## Evaluation methodology — also iterated on, with an important correction

1. **Started with a single 80/20 `train_test_split`.** Reported R² of
   0.43–0.60 after adding `historical_mean`.
2. **Switched to 5-fold `KFold(shuffle=True, random_state=42)` cross-validation**
   after recognizing the single split (only ~500 test rows across 19
   locations) was too small a sample to trust. This revealed the true
   picture was **worse and much less certain** than the single split
   suggested: R² 0.07–0.38, with **standard deviation across folds often
   larger than the mean itself** (e.g. `coffee_mix_g` R² = 0.094±0.385).
   This was the single most important methodological correction in the
   whole process — the single-split number had simply gotten a favorable
   split by chance.
3. **Hyperparameter tuning via `RandomizedSearchCV`** (not exhaustive grid
   search — the full grid would be 100+ combinations × 5 folds per
   target/model, too slow for the expected gain). `n_iter=20` initially,
   later raised to `30` with a wider grid (see below). This is where the
   high-variance targets got fixed: `coffee_mix_g` R² went from
   0.094±0.385 → 0.400±0.139, `chocolate_mix_g` from 0.072±0.304 →
   0.333±0.122. `hist_gradient_boosting` won all 5 targets after tuning
   (previously mixed with `random_forest`).
4. **A second tuning round with a wider hyperparameter grid was tried**
   after noticing the first round's winning hyperparameters
   (`min_samples_leaf=30`, `learning_rate=0.05`) were sitting at the edge
   of the tested range — a possible sign the true optimum was outside the
   grid. Result: **R² moved by ≤0.01 across all targets** (well within the
   reported std) — a negative/negligible result, honestly reported as such.
   One real finding survived: `l2_regularization` converged to a
   consistent `0.5` across all 5 targets (previously mixed 0.0/0.1/1.0),
   confirming that specific hyperparameter wasn't just boundary-hugging.
   **Conclusion: hyperparameter tuning has hit its ceiling for this
   feature set and data size** — further gains need new data/features, not
   more search.

## Final model architecture

Per target, three `sklearn.pipeline.Pipeline` objects, each with the same
preprocessing (`ColumnTransformer` one-hot-encoding `location_id`,
`day_of_week`, `month`; all other features passed through) feeding into a
`HistGradientBoostingRegressor`:

- **Point estimate** (`loss="squared_error"`, the default): the winner of a
  `RandomizedSearchCV` comparison between `RandomForestRegressor` and
  `HistGradientBoostingRegressor` — `hist_gradient_boosting` wins on every
  target as of the last training run.
- **Lower/upper bound** (`loss="quantile"`, `quantile=0.05` / `0.95`): two
  more `HistGradientBoostingRegressor` fits, reusing the *same*
  `min_samples_leaf`/`max_depth`/`learning_rate`/`l2_regularization` that
  the point-estimate search already found best for that target (not
  re-tuned separately — would ~3x training time for uncertain benefit).

### Prediction intervals — an honest calibration story

Initially used the 10th/90th percentile (nominally an 80% interval).
Measured **empirical coverage** (via `cross_val_predict` on held-out folds,
not a training-set number) came back at **~70–72%** — under-covering by
about 9-10 points, a known effect of quantile regression at this data size.
Rather than accept a mislabeled interval, the quantiles were widened to
5th/95th (nominally 90%) specifically to compensate for that measured bias.
Re-measured coverage: **~80.6–83.5%** — close to the actually-desired 80%,
achieved by deliberately overshooting the nominal target to cancel out a
measured systematic bias, not by hitting the nominal number directly.

### Feature list (final)

`location_id`, `days_since_previous_refill`, `day_of_week`, `month`,
`historical_mean_bottled_water_ml`, `historical_mean_cup_units`,
`historical_mean_coffee_mix_g`, `historical_mean_chocolate_mix_g`,
`historical_mean_cappuccino_mix_g`, `recent_mean_bottled_water_ml`,
`recent_mean_cup_units`, `recent_mean_coffee_mix_g`,
`recent_mean_chocolate_mix_g`, `recent_mean_cappuccino_mix_g`,
`historical_rate_bottled_water_ml`, `historical_rate_cup_units`,
`historical_rate_coffee_mix_g`, `historical_rate_chocolate_mix_g`,
`historical_rate_cappuccino_mix_g`, `recent_rate_bottled_water_ml`,
`recent_rate_cup_units`, `recent_rate_coffee_mix_g`,
`recent_rate_chocolate_mix_g`, `recent_rate_cappuccino_mix_g` (24 total).

### Latest metrics (5-fold CV, mean±std; see `backend/data/metrics/` for the full timestamped history)

| target | model | MAE | RMSE | R² | interval coverage |
|---|---|---|---|---|---|
| bottled_water_ml | hist_gradient_boosting | 1702.78±155.47 | 3273.61±2370.77 | 0.371±0.142 | 84.2% |
| cup_units | hist_gradient_boosting | 9.46±0.86 | 18.19±13.17 | 0.371±0.142 | 84.2% |
| coffee_mix_g | hist_gradient_boosting | 22.33±1.05 | 39.20±21.56 | 0.354±0.115 | 83.5% |
| chocolate_mix_g | hist_gradient_boosting | 86.40±5.16 | 145.01±72.28 | 0.274±0.094 | 83.8% |
| cappuccino_mix_g | hist_gradient_boosting | 90.41±7.82 | 158.48±97.15 | 0.308±0.110 | 83.2% |

This table is **not** directly comparable to the R² values previously
recorded here (0.34–0.43): those were measured against the pre-refresh
2,576-row CSV, on a feature set without the rate features. The controlled
before/after comparison that justified adding the rate features (same CSV,
same CV setup, feature set as the only variable) is the MAE delta in the
Feature engineering table above, not this table's R² against the old
numbers. R² of 0.27–0.37 means a substantial share of variance is still
unexplained by these features — genuine, not a bug. `historical_mean`/
`recent_mean`/the rate features are strong but not complete predictors;
consumption also depends on things not in this dataset (foot traffic
swings, weather, local events).

## Model persistence (save & reload)

Each target gets one self-contained file:
`backend/data/models/{target}.joblib` (e.g. `bottled_water_ml.joblib`),
written by `joblib.dump` at the end of `backend/scripts/train_consumption.py`.
Each file is a dict containing:

```python
{
    "pipeline": ...,           # point-estimate fitted Pipeline
    "lower_pipeline": ...,     # 5th-percentile fitted Pipeline
    "upper_pipeline": ...,     # 95th-percentile fitted Pipeline
    "target": "bottled_water_ml",
    "model_name": "hist_gradient_boosting",
    "feature_columns": [...],  # exact column order/names the pipelines expect
    "valid_location_ids": [...],
    "hyperparameters": {...},  # best_params_ from RandomizedSearchCV
    "test_mae": ..., "test_mae_std": ...,
    "test_rmse": ..., "test_rmse_std": ...,
    "test_r2": ..., "test_r2_std": ...,
    "interval_coverage": ...,
    "n_train_rows": ...,
}
```

Reloaded by `backend/app/services/consumption_predictor.py::_load_artifacts()`,
which `joblib.load`s all 5 files once per process (`@lru_cache`) when the
FastAPI app first needs a prediction, and raises a clear `RuntimeError`
telling you to run the training script if a file is missing. This is the
only save/reload mechanism in the project — there's no separate CLI tool
and no versioned/timestamped model snapshots (only the metrics `.txt` files
in `backend/data/metrics/` are timestamped per run; the model `.joblib`
files themselves are overwritten in place on every retrain).

`backend/data/models/` and `backend/data/metrics/` are both gitignored —
fully reproducible from the committed CSV by running
`scripts/load_consumption.py` then `scripts/train_consumption.py`.

## API

`POST /predict-consumption` (`backend/app/routers/consumption.py`) — returns
predictions for **every known location at once**, not a single machine.
`location_id` and `days_since_previous_refill` are not caller inputs: the
endpoint iterates all 17 locations internally, and for each one derives
`days_since_previous_refill` from `target_date` minus that location's most
recent reading date in `cafetalino.db` (`_load_location_metadata()`).

**Request** (`ConsumptionPredictionRequest`):

```json
{"target_date": "2026-07-20"}
```

**Response** (`ConsumptionPredictionResponse`) — `target_date` plus a list
of one `LocationConsumptionPrediction` per location, each target still a
`PredictionInterval`, not a bare number:

```json
{
  "target_date": "2026-07-20",
  "predictions": [
    {
      "location_id": 1,
      "location_name": "Aeropuerto Alcantari",
      "days_since_previous_refill": 12,
      "bottled_water_ml": {"estimate": 7412.5, "low": 3973.7, "high": 10755.6},
      "cup_units": {"estimate": 41.2, "low": 22.1, "high": 59.8},
      "coffee_mix_g": {"estimate": 64.7, "low": 38.9, "high": 124.0},
      "chocolate_mix_g": {"estimate": 241.6, "low": 78.9, "high": 437.9},
      "cappuccino_mix_g": {"estimate": 294.5, "low": 125.5, "high": 517.7}
    },
    { "location_id": 2, "location_name": "Planeta Kids", "...": "..." }
  ]
}
```

`day_of_week`/`month` are derived server-side from `target_date`;
`historical_mean_*`/`recent_mean_*` are computed server-side from the
current contents of `cafetalino.db` per location (see
`_load_location_features()`). No location-level 422 path exists anymore —
there's no `location_id` in the request for the caller to get wrong.

## How to retrain

```bash
cd backend
uv run --env-file .env python scripts/load_consumption.py    # rebuild cafetalino.db from the CSV (if needed)
uv run --env-file .env python scripts/train_consumption.py   # ~5-8 minutes; writes data/models/ + data/metrics/
```

## Known limitations / future ideas (not implemented)

- **Academic/holiday calendar feature** — flagged above, needs an external
  data source.
- **More data over time** — the model would likely improve simply as more
  readings accumulate in the DB; not something to build, just to expect.
