#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f ".venv/bin/python" ]; then
    echo "İlk kullanım: Kurulum başlatılıyor..."
    ./kurulum.sh
fi

exec .venv/bin/python -m ayus "$@"
