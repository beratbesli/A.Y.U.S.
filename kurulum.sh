#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== A.Y.U.S. Linux Kurulumu ==="

if [ ! -d ".venv" ]; then
    echo "Python sanal ortamı oluşturuluyor..."
    if command -v uv >/dev/null 2>&1; then
        uv venv --python 3.13 .venv 2>/dev/null || uv venv .venv
    else
        python3 -m venv .venv
    fi
fi

echo "Bağımlılıklar kuruluyor..."
if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements-dev.txt
else
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements-dev.txt
fi

echo "Kurulum tamamlandı. Uygulamayı başlatmak için ./baslat.sh çalıştırabilirsiniz."
