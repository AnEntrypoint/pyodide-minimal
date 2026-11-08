#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
. "$root/pins.env"
work="$root/work"
src="$work/pyodide"
dist="$root/dist"

rm -rf "$dist"
mkdir -p "$work" "$dist"

if [ ! -d "$src/.git" ]; then
  git clone --depth 1 --branch "$PYODIDE_VERSION" https://github.com/pyodide/pyodide.git "$src"
fi

make -C "$src" all-but-packages -j"$(nproc)"

for file in pyodide.asm.mjs pyodide.asm.wasm pyodide.js python_stdlib.zip; do
  cp "$src/dist/$file" "$dist/$file"
done

python3 "$root/scripts/keep_sqlite3.py" "$src" "$dist/python_stdlib.zip"

curl -fsSL -o "$work/packages.tar.gz" "$PACKAGES_URL"
curl -fsSL -o "$work/pyodide-lock.json" "$LOCK_URL"
python3 "$root/scripts/select_packages.py" "$work/pyodide-lock.json" "$root/packages.txt" "$work/packages.tar.gz" "$dist"

node "$root/scripts/bundle.mjs" "$dist" "$dist/pyodide-minimal.br"
