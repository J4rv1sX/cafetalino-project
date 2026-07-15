# cafetalino-project

Everything here runs inside **WSL2 (Ubuntu)**, not native Windows — open this project from a WSL terminal (or `nvim`/`claude` launched from one).

## Backend (`backend/`)

Python managed with [uv](https://docs.astral.sh/uv/), TensorFlow (GPU/CUDA) for modeling, FastAPI for serving.

TensorFlow's pip-installed CUDA libraries need `LD_LIBRARY_PATH` pointed at the `nvidia-*` packages inside `.venv` — native Windows TF has been CPU-only since 2.10, so this GPU setup only works here in WSL2. This repo commits a `backend/.env` with those paths precomputed; **always run through `--env-file .env`**:

```bash
cd backend
uv sync                                            # install/sync dependencies into .venv
uv run --env-file .env uvicorn main:app --reload   # run the FastAPI app
```

If `uv sync`/`uv add` recreates `.venv` and the nvidia package versions change, regenerate `.env`:

```bash
./regen_cuda_env.sh
```

`main:app` also needs a Google Maps API key for the routing endpoint. This lives separately in `backend/.env.local` (not `.env` — that file is fully overwritten by `regen_cuda_env.sh`) as `GOOGLE_MAPS_API_KEY=...`; it's gitignored and not committed.

## Frontend (`frontend/`)

Vite + React + TypeScript.

```bash
cd frontend
npm run dev
```
