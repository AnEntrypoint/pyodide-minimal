import json
import sys
import tarfile
from pathlib import Path

lock_path, wanted_path, tarball, out_dir = (Path(arg) for arg in sys.argv[1:5])
lock = json.loads(lock_path.read_text())
packages = lock["packages"]
pending = [line.strip() for line in wanted_path.read_text().splitlines() if line.strip()]
keep = set()
while pending:
    name = pending.pop()
    if name in keep:
        continue
    if name not in packages:
        raise SystemExit(f"not in lockfile: {name}")
    keep.add(name)
    pending.extend(packages[name].get("depends", []))

selected = {name: packages[name] for name in sorted(keep)}
wanted_files = {entry["file_name"] for entry in selected.values()}
missing = set(wanted_files)
out_dir.mkdir(parents=True, exist_ok=True)
with tarfile.open(tarball) as archive:
    for member in archive.getmembers():
        base = Path(member.name).name
        if member.isfile() and base in wanted_files:
            (out_dir / base).write_bytes(archive.extractfile(member).read())
            missing.discard(base)
if missing:
    raise SystemExit(f"missing from tarball: {sorted(missing)}")
(out_dir / "pyodide-lock.json").write_text(json.dumps(dict(lock, packages=selected), indent=2) + "\n")
print(f"packages: {len(selected)} {sorted(selected)}")
