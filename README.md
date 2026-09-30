# cafetalino-project

Predictive consumption + route optimization for beverage vending machines (UNIR master's innovation project).

- [`backend/`](backend/README.md) — Python/uv, FastAPI, scikit-learn models, OR-Tools routing
- [`frontend/`](frontend/README.md) — Vite + React + TypeScript
- [`documentation/`](documentation/README.md) — LaTeX source of the written report

The backend and frontend run inside **WSL2 (Ubuntu)**, not native Windows — open them from a WSL terminal (or `nvim`/`claude` launched from one). Native Windows TensorFlow has been CPU-only since 2.10, so the GPU setup only works under WSL2.

The LaTeX report is the exception: it's built either on Overleaf or with a native TeX install (see below), so editing it from Windows is fine.

## Editor setup

`.vscode/extensions.json` recommends [**LaTeX Workshop**](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) (`james-yu.latex-workshop`) for `documentation/`, and VS Code will prompt you to install it when you open the folder. It also marks `tomoki1207.pdf` as unwanted, and `.vscode/settings.json` routes `*.pdf` to LaTeX Workshop's own viewer, so the compiled PDF opens with SyncTeX support instead of in a plain PDF preview.

> **Note:** `.vscode/` is gitignored, so these files are local-only — if you don't have them, install `james-yu.latex-workshop` by hand (or create the two files yourself).

LaTeX Workshop **does not bundle a TeX distribution**. Read its requirements before expecting local builds to work:

<https://github.com/James-Yu/LaTeX-Workshop/wiki/Install#requirements>

On Windows, [**MiKTeX**](https://miktex.org/) is what's in use here — install it, let it fetch missing packages on the fly, and make sure `pdflatex`/`biber` are on your `PATH`. TeX Live works too; on WSL/Linux use TeX Live (`texlive-full`, or a smaller scheme plus `babel-spanish` and `biblatex-apa`).

If you'd rather not install anything locally, skip all of this and compile on Overleaf — see [`documentation/README.md`](documentation/README.md) for the settings and the compile sequence.

