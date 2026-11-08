# pyodide-minimal

A minimal Pyodide distribution, built from the upstream tag pinned in `pins.env` (314.0.7, CPython 3.14.2, Emscripten 5.0.3).

The build keeps only what the browser runtime needs, plus the packages that carry freetype, and publishes everything as one Brotli-compressed file.

## What ships

- Core runtime from `make all-but-packages`: `pyodide.asm.mjs`, `pyodide.asm.wasm`, `pyodide.js`, `python_stdlib.zip`.
- sqlite3: the runtime links libsqlite3 (`-lsqlite3` in upstream `Makefile.envs`), and upstream removes the Python `sqlite3` package from the stdlib zip. `scripts/keep_sqlite3.py` appends it back, and the build fails if it is missing.
- freetype: shipped inside the `matplotlib`, `pillow` and `fonttools` packages listed in `packages.txt`, with their dependency closure taken from the pyodide-recipes lockfile.
- `pyodide-lock.json` restricted to the selected packages.

## The bundle file

Everything is published as one file, `pyodide-minimal.br`. It is a single Brotli stream (quality 11, 16 MiB window) over this plain layout:

1. 4 bytes, unsigned 32-bit little-endian: the length of the header
2. The header: UTF-8 JSON `{ "format": "pyodide-minimal/1", "files": [{ "name", "offset", "bytes", "sha256" }] }`
3. The payload: each file in name order. `offset` is relative to the start of the payload, not the start of the stream.

One request, one decode. Every file is checked against its sha256 in the header.

## Serving

GitHub Pages does not apply Brotli content encoding to this file, so the consumer decodes it itself. `DecompressionStream` does not support Brotli, so the consumer needs a Brotli decoder, for example a small WebAssembly decoder. The decoded bytes are then read as described above.

## Build

    scripts/build.sh

The script clones upstream Pyodide at `PYODIDE_VERSION`, runs `make all-but-packages`, takes the package archive and lockfile from the pyodide-recipes release in `pins.env`, and writes `dist/pyodide-minimal.br`. The build needs autoconf, automake and libtool; CI installs them.

## CI

The workflow in `.github/workflows/build.yml` runs on pushes to main and on manual dispatch. It builds with `scripts/build.sh` and deploys `dist/` to GitHub Pages. The workflow does not run tests or other automated checks; checks are run by hand.

## Updating the pin

Change `PYODIDE_VERSION`, `PACKAGES_URL` and `LOCK_URL` together in `pins.env`, using the pyodide-recipes release that matches the Pyodide tag.
