import sys
import zipfile

archive = zipfile.ZipFile(sys.argv[1])
if "sqlite3/__init__.py" not in archive.namelist():
    raise SystemExit("sqlite3 missing from stdlib zip")
print("sqlite3 present in stdlib zip")
