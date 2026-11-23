"""
my_solutions.py - starter file for Project P6: Flight Delay Ranking (sorting at scale)

Implement the TWO techniques assigned to you (the keys are listed in TECHNIQUES below). Delete or ignore the others.
Every function receives the loaded instance (a dict; its fields are described at the top of problem.py)
and must return: a list of flight ids, worst delay first (equal delays keep file order).

Test your work from this folder:
    python run_checks.py my_solutions.py --only <key>[,<key>]      e.g.  --only insertion,merge
Rules: write the algorithms under study yourself (see the project brief for which library helpers are allowed).
"""
from pathlib import Path
import problem


def solve_insertion(inst):
    """Decrease-and-conquer (insertion sort).

    Return: a list of flight ids, worst delay first (equal delays keep file order).
    """
    raise NotImplementedError("write the insertion technique here")


def solve_merge(inst):
    """Divide-and-conquer (mergesort).

    Return: a list of flight ids, worst delay first (equal delays keep file order).
    """
    flight_ids = inst["ids"]
    delays = inst["delay"]
    num_flights = len(delays)

    if num_flights == 0:
        return []
    if num_flights == 1:
        return [flight_ids[0]]

    ranked_indices = list(range(num_flights))
    temp_indices = [0] * num_flights

    def merge_halves(left_start, mid_idx, right_end):
        for idx in range(left_start, right_end + 1):
            temp_indices[idx] = ranked_indices[idx]

        left_ptr = left_start
        right_ptr = mid_idx + 1

        for write_ptr in range(left_start, right_end + 1):
            if left_ptr > mid_idx:
                ranked_indices[write_ptr] = temp_indices[right_ptr]
                right_ptr += 1
            elif right_ptr > right_end:
                ranked_indices[write_ptr] = temp_indices[left_ptr]
                left_ptr += 1
            else:
                left_delay = delays[temp_indices[left_ptr]]
                right_delay = delays[temp_indices[right_ptr]]
                # >= keeps earlier items first when delays tie (worst delay first)
                if left_delay >= right_delay:
                    ranked_indices[write_ptr] = temp_indices[left_ptr]
                    left_ptr += 1
                else:
                    ranked_indices[write_ptr] = temp_indices[right_ptr]
                    right_ptr += 1

    def sort_range(left_start, right_end):
        if left_start >= right_end:
            return
        mid_idx = (left_start + right_end) // 2
        sort_range(left_start, mid_idx)
        sort_range(mid_idx + 1, right_end)
        merge_halves(left_start, mid_idx, right_end)

    sort_range(0, num_flights - 1)
    return [flight_ids[idx] for idx in ranked_indices]


def solve_heap(inst):
    """Transform-and-conquer (heapsort).

    Return: a list of flight ids, worst delay first (equal delays keep file order).
    """
    raise NotImplementedError("write the heap technique here")


def solve_counting(inst):
    """Space-time trade-off (counting sort).

    Return: a list of flight ids, worst delay first (equal delays keep file order).
    """
    flight_ids = inst["ids"]
    delays = inst["delay"]
    num_flights = len(delays)

    if num_flights == 0:
        return []

    min_delay = min(delays)
    max_delay = max(delays)
    offset = -min_delay
    num_buckets = max_delay - min_delay + 1

    bucket_counts = [0] * num_buckets
    for delay in delays:
        bucket_idx = delay + offset
        bucket_counts[bucket_idx] += 1

    # Start positions from largest delay down to smallest so worst delay comes first
    next_slot = [0] * num_buckets
    running_total = 0
    for bucket_idx in range(num_buckets - 1, -1, -1):
        next_slot[bucket_idx] = running_total
        running_total += bucket_counts[bucket_idx]

    ordered_indices = [0] * num_flights
    for original_idx, delay in enumerate(delays):
        bucket_idx = delay + offset
        pos = next_slot[bucket_idx]
        ordered_indices[pos] = original_idx
        next_slot[bucket_idx] += 1

    return [flight_ids[idx] for idx in ordered_indices]

TECHNIQUES = {
    "insertion": solve_insertion,
    "merge": solve_merge,
    "heap": solve_heap,
    "counting": solve_counting,
}

def main():
    data_file = Path(__file__).resolve().parent.parent / "data" / "flights_n000015_schedule.csv"
    inst = problem.load_instance(data_file)

    merge_order = solve_merge(inst)
    counting_order = solve_counting(inst)

    ok_merge, _, msg_merge = problem.validate(inst, merge_order)
    ok_counting, _, msg_counting = problem.validate(inst, counting_order)

    print("merge valid:", ok_merge, msg_merge, "| top 5:", merge_order[:5])
    print("counting valid:", ok_counting, msg_counting, "| top 5:", counting_order[:5])


if __name__ == "__main__":
    main()
