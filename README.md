# pyodide-minimal

A minimal Pyodide distribution, built from the upstream tag pinned in `pins.env` (314.0.7, CPython 3.14.2, Emscripten 5.0.3).

The build keeps only what the browser runtime needs, plus the packages that carry freetype, and compresses every file with Brotli.

## What ships

- Core runtime from `make all-but-packages`: `pyodide.asm.mjs`, `pyodide.asm.wasm`, `pyodide.js`, `python_stdlib.zip`.
- sqlite3: the runtime links libsqlite3 (`-lsqlite3` in upstream `Makefile.envs`), and upstream removes the Python `sqlite3` package from the stdlib zip. `scripts/keep_sqlite3.py` appends it back, and the build fails if it is missing.
- freetype: shipped inside the `matplotlib`, `pillow` and `fonttools` packages listed in `packages.txt`, with their dependency closure taken from the pyodide-recipes lockfile.
- `pyodide-lock.json` restricted to the selected packages, and `manifest.json` with the sha256 and sizes of each raw file.

Every file is published as `<name>.br` (Brotli quality 11). The raw files are not published.

## Serving

GitHub Pages does not apply Brotli content encoding to these files, so a consumer fetches `<name>.br` and decodes it itself. `DecompressionStream` does not support Brotli, so the consumer needs a Brotli decoder (for example a small WebAssembly decoder). Check each decoded file against `manifest.json`.

## Build

    scripts/build.sh

The script clones upstream Pyodide at `PYODIDE_VERSION`, runs `make all-but-packages`, takes the package archive and lockfile from the pyodide-recipes release in `pins.env`, and writes `dist/`.

## CI

The workflow in `.github/workflows/build.yml` runs on pushes to main and on manual dispatch. It builds with `scripts/build.sh` and deploys `dist/` to GitHub Pages. The workflow does not run tests or other automated checks; checks are run by hand.

## Updating the pin

Change `PYODIDE_VERSION`, `PACKAGES_URL` and `LOCK_URL` together in `pins.env`, using the pyodide-recipes release that matches the Pyodide tag.
