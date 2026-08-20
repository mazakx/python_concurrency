from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterable
import math
import sys
import threading
import time


def is_prime(args: tuple[int, float]) -> tuple[int, bool, str, float, float, float]:
    n, script_start = args

    worker_start = time.perf_counter()
    cpu_start = time.thread_time()

    if n < 2:
        result = False
    else:
        result = True

        for divisor in range(2, math.isqrt(n) + 1):
            if n % divisor == 0:
                result = False
                break

    worker_end = time.perf_counter()
    cpu_end = time.thread_time()

    return (
        n,
        result,
        threading.current_thread().name,
        worker_start - script_start, # start offset
        worker_end - worker_start,   # wall time
        cpu_end - cpu_start,         # cpu time
    )


def main(iterable: Iterable[int]) -> None:
    script_start = time.perf_counter()

    # Use the CLI value if supplied; otherwise default to 3 worker threads.
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    # Every job receives the same script_start timestamp so we can measure
    # when each worker actually begins relative to the start of the whole run.
    work = [(number, script_start) for number in iterable]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # map() schedules the jobs across the thread pool and returns results
        # in input order, even if the jobs start or finish in another order.
        results = executor.map(is_prime, work)

        # The three timings below describe different parts of the task lifecycle:
        #
        # start_offset -> time from script start until this worker actually
        #                 enters is_prime().
        #
        #                 A larger value usually means the job spent time in
        #                 the executor's work queue waiting for a worker thread
        #                 to become available.
        #
        # wall_time    -> real elapsed time from entering is_prime() until it
        #                 returns.
        #
        #                 This includes BOTH time spent actually executing
        #                 Python code and time spent waiting while other
        #                 CPU-bound threads get turns with the GIL.
        #
        # cpu_time     -> CPU time actually consumed by this specific worker
        #                 thread while executing the task.
        #
        # Important: the GIL does NOT mean one thread acquires it and keeps it
        # until its whole function finishes. CPython periodically allows worker
        # threads to take turns executing Python bytecode.
        #
        # Conceptually:
        #
        # Thread A: run  -> wait -> run  -> wait -> run
        # Thread B: wait -> run  -> wait -> run  -> wait
        # Thread C: wait -> wait -> run  -> wait -> run
        #
        # Several CPU-bound threads can therefore be alive concurrently, but
        # only one can execute Python bytecode at any instant.
        #
        # Because wall-clock time keeps advancing while a thread is waiting,
        # wall_time can be much larger than cpu_time.
        #
        # Example:
        #
        # wall_time = 9.6s
        # cpu_time  = 3.2s
        #
        # means that the task existed for 9.6 seconds in real time, but that
        # particular worker thread only consumed about 3.2 seconds of CPU time.
        # Much of the remaining time was spent contending with the other
        # CPU-bound threads for opportunities to execute Python bytecode.
        for (
            number,
            prime,
            thread_name,
            start_offset,
            wall_time,
            cpu_time,
        ) in results:
            print(
                f"{thread_name} | "
                f"{number} | prime = {prime} | "
                f"started at +{start_offset:.4f}s | "
                f"wall = {wall_time:.4f}s | "
                f"thread CPU = {cpu_time:.4f}s"
            )

    # Total wall-clock runtime for the whole workload. This is the main number
    # to compare against the sequential and process-based implementations.
    print(
        f"Total script runtime = "
        f"{time.perf_counter() - script_start:.4f}s"
    )


if __name__ == "__main__":
    NUMBERS = [
        30000000000000029,
        50000000000000051,
        70000000000000003,
        90000000000000011,
        120000000000000079,
        150000000000000011,
    ]

    main(NUMBERS)