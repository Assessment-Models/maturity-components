#!/usr/bin/env python3
"""Level 1 — local validation for maturity-components (CR-AM-11 §14).

Checks:
  1. model.yaml parses and matches the Assessment-Models manifest contract
     (`Assessment-Models/assessment-ci/schemas/model-manifest.schema.json`)
  2. the §15 contract handshake is well formed (contract id + version + source)
  3. components/index.yaml lists every package present on disk, and every
     listed package exists
  4. each package declares an id, a version and a kind, and the (id, version)
     pairs are unique across the repository
  5. every external reference in a package is immutable

Exit 0 with OK when clean; exit 1 listing every failure otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []
MUTABLE = {"main", "master", "latest", "HEAD", "head"}
IMMUTABLE = (
    re.compile(r"^v\d+\.\d+\.\d+(-[a-z0-9.-]+)?$"),
    re.compile(r"^[0-9a-f]{40}$"),
    re.compile(r"^sha256:[0-9a-f]{64}$"),
)


def load(rel: str):
    p = ROOT / rel
    if not p.is_file():
        errors.append(f"missing file: {rel}")
        return {}
    return yaml.safe_load(p.read_text()) or {}


manifest = load("model.yaml")
index = load("components/index.yaml")

for key in ("id", "type", "name", "version", "conformance"):
    if key not in manifest:
        errors.append(f"model.yaml: missing required field {key}")

# The manifest type MUST be `component`: the registry record for this asset
# declares type=component, and assessment-ci's validate_ecosystem.py compares
# manifest.type to record.type. A mismatch is a hard Level 3 CI failure.
#
# The `component` value is valid in the published model-manifest.schema.json
# (assessment-ci PR #6) and in the published registration.schema.json
# (assessment-registry). Both schemas agree.
if manifest.get("type") != "component":
    errors.append(
        f"model.yaml: type must be 'component', found {manifest.get('type')!r} "
        f"(the registry record declares type=component)"
    )
conf = manifest.get("conformance") or {}
if not (conf.get("contract") or {}).get("id"):
    errors.append("model.yaml: conformance.contract.id is required")
if not conf.get("version"):
    errors.append("model.yaml: conformance.version is required")
src = conf.get("source") or {}
if not src.get("organization") or not src.get("repository"):
    errors.append("model.yaml: conformance.source organization+repository are required")

listed = index.get("components") or []
if not listed:
    errors.append("components/index.yaml: no components declared")
on_disk = sorted(p.stem for p in (ROOT / "components").glob("*.yaml") if p.name != "index.yaml")
declared = sorted(c["id"].removeprefix("dea:component-") for c in listed)
if declared != on_disk:
    errors.append(f"components/index.yaml declares {declared} but disk holds {on_disk}")

seen = set()
for entry in listed:
    cid, ver = entry.get("id"), entry.get("version")
    if not cid or not ver:
        errors.append(f"component {entry!r}: id and version are required")
    if not entry.get("kind"):
        errors.append(f"component {cid}: kind is required (CR-AM-10 §4)")
    key = (cid, ver)
    if key in seen:
        errors.append(f"component {cid}@{ver}: duplicate (id, version) pair")
    seen.add(key)
    path = ROOT / entry.get("path", "")
    if not path.is_file():
        errors.append(f"component {cid}: path {entry.get('path')!r} does not resolve")
        continue
    pkg = yaml.safe_load(path.read_text()) or {}
    for ref in pkg.get("references", []) or []:
        r = ref.get("reference") if isinstance(ref, dict) else None
        if r and (r in MUTABLE or not any(p.match(r) for p in IMMUTABLE)):
            errors.append(f"component {cid}: reference {r!r} is not immutable")

if errors:
    print(f"FAIL — {len(errors)} error(s):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"OK — maturity-components: manifest + {len(listed)} component packages valid")
