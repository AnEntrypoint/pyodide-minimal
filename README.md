# pyodide-minimal

A minimal Pyodide distribution for the browser, published as one Brotli-compressed file.

The runtime comes from Pyodide 314.0.7 (CPython 3.14.2). Pyodide publishes that core as a release tarball, so this repository repacks it instead of compiling CPython in CI.

## What ships

- Core runtime from `pyodide-core-314.0.7.tar.bz2`: `pyodide.asm.mjs`, `pyodide.asm.wasm`, `pyodide.js`, `pyodide.mjs`, `python_stdlib.zip`.
- sqlite3: `scripts/verify_sqlite3.py` checks that `sqlite3/` is in the stdlib zip, and the build fails if it is missing. The release runtime links libsqlite3, so the module is kept.
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

The script downloads the core tarball, the pyodide-recipes package archive and lockfile (URLs pinned in `pins.env`), and writes `dist/pyodide-minimal.br`. It needs only curl, tar, python3 and node.

## CI

The workflow in `.github/workflows/build.yml` runs on pushes to main and on manual dispatch. It runs `scripts/build.sh` and deploys `dist/` to GitHub Pages. The workflow does not run tests or other automated checks; checks are run by hand.

## Updating the pin

Change `PYODIDE_VERSION`, `CORE_URL`, `PACKAGES_URL` and `LOCK_URL` together in `pins.env`, using the Pyodide release and the pyodide-recipes release that match.
