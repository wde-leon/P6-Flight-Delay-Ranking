"""
run_checks.py  -  test harness shared by all eight final-project packages.

Usage (from the project's  starter/  folder):

    python run_checks.py my_solutions.py                 # every technique you defined, every suitable dataset
    python run_checks.py my_solutions.py --only bf,dp    # only these technique keys
    python run_checks.py my_solutions.py --labels small  # only datasets labelled small
    python run_checks.py my_solutions.py --timeout 120   # seconds allowed per run (default 60)

my_solutions.py must define a dictionary

    TECHNIQUES = {"bf": solve_bf, "dp": solve_dp, ...}

whose keys come from problem.TECHNIQUES (see the project brief) and whose values are functions
taking the loaded instance and returning a solution in the format described in the brief.
The harness loads each dataset listed in ../data/manifest.json, runs the technique in a separate
process (so a slow run can be stopped by the time-out), validates the answer with problem.validate()
and, where the manifest holds a reference value, compares it.

Status codes:   PASS   valid answer that matches the reference (exact techniques) or is valid (heuristics)
                FAIL   invalid answer, or an exact technique that missed the reference value
                TIME   stopped by the time-out (normal for exponential techniques on big inputs)
                ERROR  your function raised an exception
"""
import argparse
import importlib.util
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, HERE)
import problem  # noqa: E402  (project-specific loader / validator)


def _load_module(path):
    spec = importlib.util.spec_from_file_location("student_solutions", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _worker(queue, mod_path, key, data_file, params):
    try:
        sys.path.insert(0, HERE)
        mod = _load_module(mod_path)
        inst = problem.load_instance(data_file, params)
        t0 = time.perf_counter()
        sol = mod.TECHNIQUES[key](inst)
        dt = time.perf_counter() - t0
        ok, score, msg = problem.validate(inst, sol, params)
        queue.put((ok, score, msg, dt))
    except Exception as exc:  # noqa: BLE001
        queue.put(("ERROR", None, repr(exc), None))


def run_one(mod_path, key, data_file, params, timeout):
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker, args=(q, mod_path, key, data_file, params))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return "TIME", None, f"stopped after {timeout}s", timeout
    try:
        return q.get(timeout=5)
    except Exception:  # noqa: BLE001
        return "ERROR", None, "process ended without a result", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("solutions", help="path to your solutions file (defines TECHNIQUES)")
    ap.add_argument("--only", default="", help="comma-separated technique keys")
    ap.add_argument("--labels", default="", help="comma-separated dataset labels (small,medium,large,stress)")
    ap.add_argument("--timeout", type=float, default=60.0)
    args = ap.parse_args()

    mod_path = os.path.abspath(args.solutions)
    mod = _load_module(mod_path)
    keys = [k for k in mod.TECHNIQUES if (not args.only or k in args.only.split(","))]
    unknown = [k for k in keys if k not in problem.TECHNIQUES]
    if unknown:
        print("Unknown technique keys:", unknown, "- allowed:", sorted(problem.TECHNIQUES))
        return 2
    labels = set(args.labels.split(",")) if args.labels else None

    with open(os.path.join(DATA, "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)

    print(f"{'dataset':34s} {'tech':10s} {'status':6s} {'score':>14s} {'reference':>14s} {'time(s)':>9s}  note")
    print("-" * 110)
    n_pass = n_fail = 0
    for ds in manifest["datasets"]:
        if labels and ds["label"] not in labels:
            continue
        ref = ds.get("reference", {})
        for key in keys:
            if key not in ds["suitable"]:
                continue
            ok, score, msg, dt = run_one(mod_path, key, os.path.join(DATA, ds["file"]), ds.get("params", {}), args.timeout)
            exact = problem.TECHNIQUES[key]["exact"]
            status = ok if isinstance(ok, str) else ("PASS" if ok else "FAIL")
            note = msg or ""
            if status == "PASS" and exact and "score" in ref and ref.get("kind") == "optimal":
                if score != ref["score"]:
                    status = "FAIL"
                    note = f"exact technique must return the optimum {ref['score']}"
            if status == "PASS" and (not exact) and "score" in ref and score is not None:
                gap = (score - ref["score"]) / ref["score"] * 100.0 if ref["score"] else 0.0
                if problem.SENSE == "max":
                    gap = -gap
                note = (note + f" {gap:+.1f}% vs reference (positive = worse)").strip()
            n_pass += status == "PASS"
            n_fail += status in ("FAIL", "ERROR")
            sc = "-" if score is None else str(score)
            rf = "-" if "score" not in ref else str(ref["score"])
            tm = "-" if dt is None else f"{dt:9.3f}"
            print(f"{ds['file']:34s} {key:10s} {status:6s} {sc:>14s} {rf:>14s} {tm:>9s}  {note}")
    print("-" * 110)
    print(f"{n_pass} passed, {n_fail} failed/errored  (TIME = stopped by time-out; not counted as failure)")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    mp.freeze_support()
    sys.exit(main())
