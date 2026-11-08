import sys
import zipfile
from pathlib import Path

src, zip_path = Path(sys.argv[1]), Path(sys.argv[2])
lib = next(src.glob("cpython/installs/python-*/lib/python3.*"))
package = lib / "sqlite3"
if not (package / "__init__.py").is_file():
    raise SystemExit(f"sqlite3 package not found under {lib}")
with zipfile.ZipFile(zip_path) as archive:
    present = set(archive.namelist())
with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(package.rglob("*.py")):
        arcname = path.relative_to(lib).as_posix()
        if arcname not in present:
            archive.write(path, arcname)
with zipfile.ZipFile(zip_path) as archive:
    if "sqlite3/__init__.py" not in archive.namelist():
        raise SystemExit("sqlite3 missing from stdlib zip after append")
print("sqlite3 present in stdlib zip")
