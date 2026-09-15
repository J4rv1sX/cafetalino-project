# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Working prototype of a "predictive brain + logistics optimization" system for beverage vending machines (UNIR master's innovation project). Three independent top-level parts:

- `backend/` — FastAPI app with two endpoints (consumption prediction, route optimization), a scikit-learn model pipeline, and offline data/training scripts.
- `frontend/` — Vite + React 19 SPA that calls those two endpoints and renders the route on a Google map.
- `documentation/` — the LaTeX source of the written project report (Spanish, UNIR template), plus the course's official documents and the script for the presentation video under `documentation/docs/`. Prose only, bar one chart-regeneration script.

There is still **no test suite** anywhere, and no linter for the backend.

## Environment

Backend and frontend run inside **WSL2 (Ubuntu)**, not native Windows. Open the project from a WSL terminal (or an editor/`claude` launched from one). Native Windows TensorFlow has been CPU-only since 2.10, so the GPU setup here only works under WSL2.

## Commands

### Backend (`backend/`, Python via uv)

```bash
cd backend
uv sync                                            # install/sync deps into .venv
./regen_cuda_env.sh                                # (re)generate .env from the synced .venv
uv run --env-file .env uvicorn main:app --reload   # run the FastAPI app
uv run --env-file .env scripts/load_consumption.py # rebuild data/cafetalino.db from the CSV
uv run --env-file .env scripts/train_consumption.py # retrain the 5 target models
uv run --env-file .env scripts/eda_consumption.py  # exploratory analysis
```

Always invoke Python through `--env-file .env` — TensorFlow's pip-installed CUDA libraries need `LD_LIBRARY_PATH` pointed at the `nvidia-*` packages inside `.venv`, and `backend/.env` carries that precomputed path. `.env` is gitignored and machine-specific, so generate it after the first `uv sync` and re-run `./regen_cuda_env.sh` whenever `uv sync`/`uv add` recreates `.venv` with different nvidia versions.

Secrets do **not** go in `.env` — `regen_cuda_env.sh` overwrites that file wholesale. The routing endpoint's `GOOGLE_MAPS_API_KEY` lives in `backend/.env.local` (gitignored), read by `app/core/config.py`.

Retraining order matters: `load_consumption.py` rewrites the `locations`/`readings` tables in `data/cafetalino.db` from `data/consumo_insumos.csv`; `train_consumption.py` reads from that database (not the CSV) and writes `data/models/*.joblib` plus a timestamped report to `data/metrics/`. The app loads models at startup, so restart uvicorn after retraining.

### Frontend (`frontend/`, Vite + React + TypeScript)

```bash
cd frontend
npm run dev       # start dev server (port 5173, allow-listed in the backend's CORS config)
npm run build     # tsc -b && vite build
npm run lint      # oxlint
npm run preview   # preview production build
```

Linting is via [Oxlint](https://oxc.rs) (`.oxlintrc.json`), not ESLint. No test runner is configured yet. The app reads `VITE_API_BASE_URL` and `VITE_GOOGLE_MAPS_API_KEY` from a gitignored `frontend/.env.local`.

### Documentation (`documentation/`, LaTeX)

Compiled locally with **LuaLaTeX** (via `latexmk`) + **biblatex-apa** (APA 7). Requires MiKTeX or TeX Live 2023+ with Calibri/Calibri Light fonts installed (come with Microsoft Office).

```bash
cd documentation
latexmk -lualatex -interaction=nonstopmode main.tex
```

Or from VS Code: "Build LaTeX project" (configured in `.vscode/settings.json` to run latexmk + LuaLaTeX by default). The magic comment `% !TEX program = lualatex` in `main.tex` tells any LaTeX editor to use the correct engine.

`fontspec` loads the real Calibri/Calibri Light fonts from the system (fidelity to the Word template), avoiding substitutes. `preambulo.tex` has no Overleaf fallback — one compilation path only.

Everything LaTeX generates is gitignored (including `*.pdf`), so `main.pdf` is local build output — don't expect it in the repo or commit it.

## Architecture

### Backend

Layered FastAPI app; `main.py` only builds the app, adds CORS for `localhost:5173`, and mounts two routers.

- `app/routers/` — endpoints: `POST /predict-consumption`, `POST /reload-route`.
- `app/schemas/` — Pydantic request/response models per router.
- `app/services/` — the actual logic: `consumption_predictor.py` (feature building + model loading + remaining-stock conversion), `distance_matrix.py` (Google Maps), `tsp_solver.py` (single-vehicle round trip via OR-Tools).
- `scripts/` — offline pipeline (`load_consumption.py`, `train_consumption.py`, `eda_consumption.py`) sharing `_shared.py`. Not imported by the app.
- `data/` — `consumo_insumos.csv` is the tracked input; `cafetalino.db`, `models/`, `metrics/`, `eda_output/` are all generated and gitignored.

Modeling is **scikit-learn**, not TensorFlow: five targets (`bottled_water_ml`, `cup_units`, `coffee_mix_g`, `chocolate_mix_g`, `cappuccino_mix_g`), each with a `HistGradientBoostingRegressor` point estimate plus two quantile fits (5th/95th) for prediction intervals. TensorFlow is installed and the CUDA env exists for it, but no current code path uses it — don't reach for TF when touching the consumption model.

`backend/docs/CONSUMPTION_MODEL.md` is the model's design record: problem framing, the feature-engineering attempts in order with their measured deltas, ablation experiments, the interval-calibration story, and current CV metrics. Read it before changing features, the evaluation setup, or the model architecture, and append new experiments there — including the ones that didn't work.

### Frontend

`src/api/` (fetch wrappers per endpoint) → `src/types/` (response shapes) → `src/hooks/` → `src/components/` (`ConsumptionList`/`ConsumptionCard`, `ReloadList`, `RoutePlanner` using `@react-google-maps/api`). Types are hand-mirrored from the backend Pydantic schemas — there's no generated client, so a schema change needs a matching edit in `src/types/`.

### Documentation

`main.tex` is the master document (project metadata + `\input` order); `preambulo.tex` holds packages, margins, title styles and the bibliography switch; `portada.tex` is the UNIR cover. Content lives in `capitulos/01-07` (introduction, objectives, conceptual development, methodology, implementation, validation, conclusions) and `anexos/a-f` (two interviews, the customer survey, prototype diagrams, Jira screenshots and the initial backlog), with 34 references in `bibliografia/referencias.bib`.

Known state:

- **The report is written end to end** — all seven chapters and six annexes are complete and their `\input` lines active. The remaining structural problem is **length**: `docs/instrucciones.md` caps the countable body at 30 pages and it currently sits at 48. `documentation/README.md` tracks the per-chapter page split and the cuts still under consideration.
- Chapter 6 *designs* the eight-week operational pilot but does not execute it, and chapter 7 says so explicitly. Don't write as if operational results existed — only the offline cross-validation metrics do.
- Survey charts were rebuilt from the original .docx's embedded chart XML by `imagenes/regenerar-graficos.py` into `imagenes/grafico1-5.png`; regenerate through that script rather than editing the PNGs.
- The chapter-5 performance table leaves the cups R² blank on purpose: the value in `backend/docs/CONSUMPTION_MODEL.md` duplicates the bottled-water one, which looks like a transcription error. Filling it in needs a retrain.

`documentation/docs/` holds the course's official UNIR documents — the work guide, the
document-writing instructions (structure, 20–30 page limit, APA, template formats), the
weekly schedule with deliverable deadlines and grade weights, the grading rubric, and the
mandatory Word and PowerPoint templates. Each original has a faithful Markdown transcription
next to it (`guia.md`, `instrucciones.md`, `programacion.md`, `plantilla.md`, `rubrica.md`,
all indexed by `README.md`); read the `.md`, not the PDF/DOCX. `plantilla.md` defines the
expected section structure of the report — the chapters, their order and what each must
contain — and `rubrica.md` is the matrix the work is graded against. Check these before
changing the report's structure, length or citation style.

The same directory also holds two files that are **not** transcriptions. `observaciones-primera-entrega.md`
and `observaciones-segunda-entrega.md` are the tutor's feedback on the two interim submissions,
i.e. corrections to act on. `guion-video.md` is our own draft script for the presentation video:
16 slides over the seven sections `plantilla_video.ppt` prescribes, timed against the 10-minute
limit, plus the images and screenshots still to be produced. The final submission is the document
(40 %) plus a video recorded **individually** by each team member (30 %).
