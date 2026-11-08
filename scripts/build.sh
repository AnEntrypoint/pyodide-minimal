#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/pins.env"
work="$root/work"
dist="$root/dist"

rm -rf "$dist" "$work/core"
mkdir -p "$work/core" "$dist"

curl -fsSL -o "$work/core.tar.bz2" "$CORE_URL"
tar -xjf "$work/core.tar.bz2" -C "$work/core"

for file in pyodide.asm.mjs pyodide.asm.wasm pyodide.js pyodide.mjs python_stdlib.zip; do
  cp "$work/core/pyodide/$file" "$dist/$file"
done

python3 "$root/scripts/verify_sqlite3.py" "$dist/python_stdlib.zip"

curl -fsSL -o "$work/packages.tar.gz" "$PACKAGES_URL"
curl -fsSL -o "$work/pyodide-lock.json" "$LOCK_URL"
python3 "$root/scripts/select_packages.py" "$work/pyodide-lock.json" "$root/packages.txt" "$work/packages.tar.gz" "$dist"

node "$root/scripts/bundle.mjs" "$dist" "$dist/pyodide-minimal.br"
