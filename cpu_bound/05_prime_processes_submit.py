from concurrent.futures import ProcessPoolExecutor, as_completed
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

    # Every job receives the same script_start timestamp so we can see when
    # each worker process actually begins relative to the whole script.
    work = [(number, script_start) for number in iterable]

    futures = []

    with ProcessPoolExecutor(max_workers=workers) as executor:

        # submit() creates one explicit Future per is_prime() call.
        # Unlike map(), we own the Future objects and can process each result
        # independently rather than consuming them in input order.
        for item in work:
            futures.append(executor.submit(is_prime, item))

        # as_completed() yields Futures as their underlying process work
        # finishes, so result-consumption order follows completion order
        # rather than the original NUMBERS order.
        #
        # The execution model is still process-based:
        # each worker is a separate OS process with its own interpreter and
        # its own GIL, allowing pure-Python CPU work to execute in parallel
        # across multiple CPU cores.
        for future in as_completed(futures):
            (
                number,
                prime,
                process_id,
                start_offset,
                wall_time,
                cpu_time,
            ) = future.result()

            print(
                f"PID {process_id} | "
                f"{number} | prime = {prime} | "
                f"started at +{start_offset:.4f}s | "
                f"wall = {wall_time:.4f}s | "
                f"process CPU = {cpu_time:.4f}s"
            )

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