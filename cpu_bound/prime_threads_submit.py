from concurrent.futures import ThreadPoolExecutor, as_completed
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
    futures = []
    script_start = time.perf_counter()

    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    workload = [(number, script_start) for number in iterable]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for work in workload:
            futures.append(executor.submit(is_prime, work))

        for future in as_completed(futures):
            (
                number,
                prime,
                thread_name,
                start_offset,
                wall_time,
                cpu_time,
            ) = future.result()

            print(
            f"{thread_name} | "
            f"{number} | prime = {prime} | "
            f"started at +{start_offset:.4f}s | "
            f"wall = {wall_time:.4f}s | "
            f"thread CPU = {cpu_time:.4f}s"
            )

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