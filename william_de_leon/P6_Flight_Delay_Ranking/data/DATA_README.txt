Project P6 - Flight Delay Ranking (sorting at scale)
DATA FOLDER
============================================================

These datasets are SYNTHETIC: produced by generate_data.py from a fixed random seed so that every student gets identical files,
with distributions modelled on the real-world situation described in the project brief.

FORMAT
flights_nNNNNNN_<order>.csv : flight_id, carrier, origin, dest, sched_dep_min, arr_delay_min.
order = schedule (normal), nearly_sorted (already ranked except ~2 %), reversed (ranked best-first = worst case).

REFERENCE VALUES
There is exactly one correct output per file; see 'reference' (md5, first five ids; full order for the 15-row file).

MORE DATA
    python generate_data.py --help      (any size, any seed; the same seed always gives the same file)

FILES (from manifest.json)
    file                               label       size  suitable techniques                reference
    flights_n000015_schedule.csv       small         15  insertion,merge,heap,counting      exact_order
    flights_n001000_schedule.csv       small       1000  insertion,merge,heap,counting      exact_order
    flights_n010000_schedule.csv       medium     10000  insertion,merge,heap,counting      exact_order
    flights_n010000_nearly_sorted.csv  medium     10000  insertion,merge,heap,counting      exact_order
    flights_n010000_reversed.csv       medium     10000  insertion,merge,heap,counting      exact_order
    flights_n100000_schedule.csv       large     100000  merge,heap,counting                exact_order
    flights_n100000_nearly_sorted.csv  large     100000  merge,heap,counting,insertion      exact_order

Labels: small = hand-checkable / every technique; medium = exponential techniques still feasible; large = only the efficient techniques; stress = slow even for them (use for the top of your scaling curve).
A technique listed as 'suitable' for a file is expected to finish in under about a minute in CPython; a technique NOT listed is expected to be too slow (that is part of what you will measure).
