# Backend

Python managed with [uv](https://docs.astral.sh/uv/), TensorFlow (GPU/CUDA) for modeling, FastAPI for serving.

Everything here runs inside **WSL2 (Ubuntu)**, not native Windows — open this project from a WSL terminal (or `nvim`/`claude` launched from one).

TensorFlow's pip-installed CUDA libraries need `LD_LIBRARY_PATH` pointed at the `nvidia-*` packages inside `.venv` — native Windows TF has been CPU-only since 2.10, so this GPU setup only works here in WSL2. `backend/.env` holds those paths precomputed, but it's gitignored (machine-specific, tied to your local `.venv` layout), so generate it after syncing; **always run through `--env-file .env`**:

```bash
cd backend
uv sync                                            # install/sync dependencies into .venv
./regen_cuda_env.sh                                # generate .env from the synced .venv
uv run --env-file .env uvicorn main:app --reload   # run the FastAPI app
```

Re-run `./regen_cuda_env.sh` any time `uv sync`/`uv add` recreates `.venv` and the nvidia package versions change.

`main:app` also needs a Google Maps API key for the routing endpoint. This lives separately in `backend/.env.local` (not `.env` — that file is fully overwritten by `regen_cuda_env.sh`) as `GOOGLE_MAPS_API_KEY=...`; it's gitignored and not committed.
