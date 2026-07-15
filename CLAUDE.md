# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is an early-stage scaffold: `backend/` is an unmodified `uv init` + FastAPI/TensorFlow skeleton (`main.py` just prints the TF version and detected GPUs), and `frontend/` is an unmodified Vite React-TS template. There is no application code, routing, API surface, or test suite yet — don't assume architecture beyond what's described below.

## Environment

Everything runs inside **WSL2 (Ubuntu)**, not native Windows. Open this project from a WSL terminal (or an editor/`claude` instance launched from one). Native Windows TensorFlow has been CPU-only since 2.10, so the GPU setup here only works under WSL2.

## Commands

### Backend (`backend/`, Python via uv)

```bash
cd backend
uv sync                                            # install/sync deps into .venv
uv run --env-file .env main.py                     # run a script
uv run --env-file .env uvicorn main:app --reload   # run the FastAPI app
```

Always invoke Python through `--env-file .env` — TensorFlow's pip-installed CUDA libraries need `LD_LIBRARY_PATH` pointed at the `nvidia-*` packages inside `.venv`, and `backend/.env` carries that precomputed path. If `uv sync`/`uv add` recreates `.venv` (e.g. the nvidia package versions change), regenerate it:

```bash
./regen_cuda_env.sh
```

No test suite or linter is configured yet for the backend.

### Frontend (`frontend/`, Vite + React + TypeScript)

```bash
cd frontend
npm run dev       # start dev server
npm run build     # tsc -b && vite build
npm run lint      # oxlint
npm run preview   # preview production build
```

Linting is via [Oxlint](https://oxc.rs) (`.oxlintrc.json`), not ESLint. No test runner is configured yet.

## Architecture

- **Backend**: FastAPI for serving, TensorFlow (`tensorflow[and-cuda]`) for modeling/GPU inference, pandas/numpy/scikit-learn/matplotlib for data work. Managed with `uv`; dependency list lives in `backend/pyproject.toml`.
- **Frontend**: React 19 + TypeScript, built with Vite, using the `@vitejs/plugin-react` (Oxc-based) plugin.
- The two are independent projects with no wiring between them yet (no API client, no proxy config in `vite.config.ts`).
