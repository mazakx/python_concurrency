import math
import time
import threading

def is_prime(n: int) -> bool:
    if n < 2:
        return False

    for divisor in range(2, math.isqrt(n) + 1):
        if n % divisor == 0:
            return False

    return True

if __name__ == "__main__":
    start = time.perf_counter()

    NUMBERS = [
        30000000000000029,
        50000000000000051,
        70000000000000003,
        90000000000000011,
        120000000000000079,
        150000000000000011,
    ]

    for number in NUMBERS:
        item_start = time.perf_counter()
        result = is_prime(number)

        print(
            f"{threading.current_thread().name} | "
            f"{number} | prime = {result} | "
            f"Time taken: {time.perf_counter() - item_start:.4f}s"
        )

    print(f"Total script runtime: {time.perf_counter() - start:.4f}s")