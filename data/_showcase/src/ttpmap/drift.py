"""ATT&CK version drift of the label space (prereg 21): status of each technique id in a STIX 2.1 bundle."""
from __future__ import annotations

from typing import Dict, Iterable

import pandas as pd

_RANK = {"active": 0, "deprecated": 1, "revoked": 2}


def final_id(stix_id: str, revoked_by: Dict[str, str]) -> str:
    """Follow revoked-by links to the last object; cycle-safe."""
    seen = {stix_id}
    while stix_id in revoked_by and revoked_by[stix_id] not in seen:
        stix_id = revoked_by[stix_id]; seen.add(stix_id)
    return stix_id


def _ext(o: dict) -> str | None:
    return next((r["external_id"].upper() for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack" and r.get("external_id")), None)


def _status(o: dict) -> str:
    return "revoked" if o.get("revoked") else "deprecated" if o.get("x_mitre_deprecated") else "active"


def status_table(objects: Iterable[dict]) -> pd.DataFrame:
    """One row per ATT&CK id: id, status (active / deprecated / revoked), final_id, final_status, name.
    final_id is the id after following revocations; None for a revoked object with no revoked-by link (no replacement).
    final_status is the status of that final object, so a chain ending at a deprecated target is visible."""
    objects = list(objects)
    ap = {o["id"]: o for o in objects if o.get("type") == "attack-pattern" and _ext(o)}
    rb = {o["source_ref"]: o["target_ref"] for o in objects if o.get("type") == "relationship" and o.get("relationship_type") == "revoked-by"}
    best: Dict[str, dict] = {}
    for sid, o in ap.items():
        st = _status(o)
        if st == "revoked":
            end = final_id(sid, rb); fin = ap.get(end) if end != sid else None
        else:
            fin = o
        row = {"id": _ext(o), "status": st, "final_id": _ext(fin) if fin else None, "final_status": _status(fin) if fin else None, "name": o.get("name", "")}
        if row["id"] not in best or _RANK[st] < _RANK[best[row["id"]]["status"]]:
            best[row["id"]] = row
    return pd.DataFrame(list(best.values()), columns=["id", "status", "final_id", "final_status", "name"])
