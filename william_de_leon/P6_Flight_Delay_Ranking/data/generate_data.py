"""
generate_data.py - make a flight-performance file of any size for Project P6.

    python generate_data.py --n 250000 --order schedule --seed 8 --out flights_n250000.csv

Columns: flight_id, carrier, origin, dest, sched_dep_min, arr_delay_min
  * flight_id = carrier + number + day-of-year, e.g. UA0482-D076
  * sched_dep_min = scheduled departure as minutes after midnight (0-1439)
  * arr_delay_min = arrival delay in whole minutes, negative = early, clipped to [-60, 900]
Delay model (loosely shaped like US on-time-performance statistics):
    70 % of flights arrive early or about on time  (normal, mean -5, sd 9)
    25 % are moderately late                       (exponential, mean 25)
     5 % are badly late                            (exponential, mean 120)
  and delays creep up through the day (knock-on effects), as in real operations.

--order controls the ORDER OF THE ROWS in the file:
    schedule      rows sorted by scheduled departure (the normal case)
    nearly_sorted rows already ranked by delay (worst first) except for about 2 % of the rows that were moved
                  (what a nightly re-ranking job sees: the list is almost sorted already)
    reversed      rows ranked best-first, i.e. the worst case for an algorithm that wants worst-first
The same seed always gives the same file.
"""
import argparse
import csv
import random

CARRIERS = ["AA", "DL", "UA", "WN", "B6", "AS", "NK", "F9"]
AIRPORTS = ["ATL", "LAX", "ORD", "DFW", "DEN", "JFK", "SFO", "SEA", "LAS", "MCO", "PHX", "BOS", "MSP", "DTW", "CLT", "BFL"]


def generate(n, order, seed):
    """Up to 20,000 rows = one busy day (day-of-year 076); more rows = a whole year of flights (days 1-365)."""
    rng = random.Random(seed)
    rows = []
    used = set()
    for _ in range(n):
        doy = 76 if n <= 20000 else rng.randint(1, 365)
        dep = int(min(1439, max(0, rng.gauss(13 * 60, 5 * 60))))
        u = rng.random()
        if u < 0.70:
            d = rng.gauss(-5, 9)
        elif u < 0.95:
            d = rng.expovariate(1 / 25.0)
        else:
            d = rng.expovariate(1 / 120.0)
        d += (dep / 1439.0) * 6.0                      # knock-on delay grows through the day
        d = int(max(-60, min(900, round(d))))
        c = rng.choice(CARRIERS)
        while True:
            fid = f"{c}{rng.randint(1, 9999):04d}-D{doy:03d}"
            if fid not in used:
                used.add(fid)
                break
        o, t = rng.sample(AIRPORTS, 2)
        rows.append([fid, c, o, t, dep, d, doy])
    rows.sort(key=lambda r: (r[6], r[4], r[0]))               # schedule order (day, then time of day)
    if order == "nearly_sorted":
        rows.sort(key=lambda r: -r[5])
        for _ in range(max(1, n // 100)):                     # about 2 % of rows displaced (two per swap)
            i, j = rng.randrange(n), rng.randrange(n)
            rows[i], rows[j] = rows[j], rows[i]
    elif order == "reversed":
        rows.sort(key=lambda r: r[5])
    return [r[:6] for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--order", choices=["schedule", "nearly_sorted", "reversed"], default="schedule")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["flight_id", "carrier", "origin", "dest", "sched_dep_min", "arr_delay_min"])
        w.writerows(generate(a.n, a.order, a.seed))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
