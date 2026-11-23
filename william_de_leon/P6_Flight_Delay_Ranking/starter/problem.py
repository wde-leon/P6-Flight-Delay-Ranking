"""
P6 - Flight Delay Ranking (sorting at scale)
Instance loader, solution validator and technique registry used by run_checks.py.

Instance (dict returned by load_instance):
    n         number of flight records
    ids       ids[k]     flight id, e.g. "UA0482-0317"   (unique)
    delay     delay[k]   arrival delay in whole minutes (negative = early), between -60 and 900
    rows      rows[k] = (flight_id, carrier, origin, dest, sched_dep_min, delay)
Records are given in file order (normally the schedule order of the day).

Required ordering (the sort key):
    1. larger delay first (worst delays at the top);
    2. flights with equal delay keep their file order (the sort must be STABLE with respect to the file).
This makes the correct output unique, so every technique must return exactly the same list.

Solution format (what every technique returns):
    a list of the flight ids in the required order (length n).
"""
import csv

SENSE = "none"
TECHNIQUES = {
    "insertion": {"name": "Decrease-and-conquer (insertion sort)", "exact": True},
    "merge":     {"name": "Divide-and-conquer (mergesort)", "exact": True},
    "heap":      {"name": "Transform-and-conquer (heapsort)", "exact": True},
    "counting":  {"name": "Space-time trade-off (counting sort)", "exact": True},
}


def load_instance(path, params=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append((r["flight_id"], r["carrier"], r["origin"], r["dest"], int(r["sched_dep_min"]), int(r["arr_delay_min"])))
    return {"n": len(rows), "ids": [r[0] for r in rows], "delay": [r[5] for r in rows], "rows": rows}


def validate(inst, sol, params=None):
    ids = inst["ids"]
    try:
        out = list(sol)
    except TypeError:
        return False, None, "solution must be a list of flight ids"
    if len(out) != len(ids):
        return False, None, f"expected {len(ids)} ids, got {len(out)}"
    pos = inst.get("_pos")
    if pos is None:
        pos = {fid: k for k, fid in enumerate(ids)}
        inst["_pos"] = pos
    seen = set()
    prev = None
    for fid in out:
        k = pos.get(fid)
        if k is None:
            return False, None, f"unknown flight id {fid!r}"
        if k in seen:
            return False, None, f"flight {fid!r} listed twice"
        seen.add(k)
        key = (-inst["delay"][k], k)
        if prev is not None and key < prev:
            return False, None, f"order violated at {fid!r} (delay must fall; equal delays keep file order)"
        prev = key
    return True, None, ""
