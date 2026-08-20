from concurrent.futures import ProcessPoolExecutor
from collections.abc import Iterable
import math
import os
import sys
import time


def is_prime(args: tuple[int, float]) -> tuple[int, bool, int, float, float, float]:
    n, script_start = args

    worker_start = time.perf_counter()
    cpu_start = time.process_time()

    if n < 2:
        result = False
    else:
        result = True

        for divisor in range(2, math.isqrt(n) + 1):
            if n % divisor == 0:
                result = False
                break

    worker_end = time.perf_counter()
    cpu_end = time.process_time()

    return (
        n,
        result,
        os.getpid(),
        worker_start - script_start,  # start offset
        worker_end - worker_start,    # wall time
        cpu_end - cpu_start,          # process CPU time
    )


def main(iterable: Iterable[int]) -> None:
    script_start = time.perf_counter()

    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    # Every job gets the same script_start timestamp so we can see when each
    # worker process actually begins relative to the start of the whole run.
    work = [(number, script_start) for number in iterable]

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # map() distributes one is_prime() call per input across the worker
        # processes and preserves input order when yielding the results.
        results = executor.map(is_prime, work)

        # The timing interpretation is similar to the threaded version, but
        # the crucial difference is that each worker is now a separate process.
        #
        # start_offset -> time from script start until this worker process
        #                 actually enters is_prime().
        #
        # wall_time    -> real elapsed time for this particular task.
        #
        # cpu_time     -> CPU time consumed by this worker process while
        #                 performing the task.
        #
        # Unlike CPU-bound threads, these processes do not have to take turns
        # under one shared GIL. Each process has its own Python interpreter and
        # its own GIL, so multiple workers can execute Python bytecode truly in
        # parallel on different CPU cores.
        #
        # If enough CPU cores are available, wall_time and process CPU time
        # should therefore be much closer together than they were with threads.
        for (
            number,
            prime,
            process_id,
            start_offset,
            wall_time,
            cpu_time,
        ) in results:
            print(
                f"PID {process_id} | "
                f"{number} | prime = {prime} | "
                f"started at +{start_offset:.4f}s | "
                f"wall = {wall_time:.4f}s | "
                f"process CPU = {cpu_time:.4f}s"
            )

    # This is the main number to compare with sequential and threaded runs.
    # With CPU-bound pure-Python work, multiple processes should provide real
    # parallel speedup when multiple CPU cores are available.
    print(
        f"Total script runtime = "
        f"{time.perf_counter() - script_start:.4f}s"
    )


if __name__ == "__main__":
    NUMBERS = [
    150000000000000011,  # slow
    30000000000000029,   # fast
    120000000000000079,
    50000000000000051,
    90000000000000011,
    70000000000000003,
    ]

    main(NUMBERS)