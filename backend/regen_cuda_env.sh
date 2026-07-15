#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
VENV_SITE=".venv/lib/python3.11/site-packages"
LDP=$(find "$VENV_SITE/nvidia" -maxdepth 2 -type d -name lib | tr '\n' ':')
echo "LD_LIBRARY_PATH=${LDP%:}" > .env
cat .env
