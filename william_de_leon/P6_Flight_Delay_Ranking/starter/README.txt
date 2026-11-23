Project P6 - Flight Delay Ranking (sorting at scale)
STARTER FOLDER
============================================================

problem.py       Loads a data file into a Python dict (inst), checks an answer (validate) and lists the technique keys.
                 READ ITS DOCSTRING FIRST: it defines the instance fields and the exact format every technique must return.
my_solutions.py  Template. Fill in your two techniques; keep the TECHNIQUES dictionary at the bottom.
run_checks.py    Test harness. It runs your functions on the files listed in ../data/manifest.json, validates every answer
                 and compares it with the reference value.

Quick start (Python 3.10+, standard library only):
    python run_checks.py my_solutions.py --only insertion,merge --labels small

Technique keys for this project:
    insertion   Decrease-and-conquer (insertion sort)  [exact]
    merge       Divide-and-conquer (mergesort)  [exact]
    heap        Transform-and-conquer (heapsort)  [exact]
    counting    Space-time trade-off (counting sort)  [exact]

The harness is for CORRECTNESS. For the timing / operation-count experiments in your report, write your own benchmark script
(time.perf_counter, repeated runs, growing n) - the project brief and the master document explain the protocol.
