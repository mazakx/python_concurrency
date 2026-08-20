import requests
import time
import threading
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(delay: int) -> str:
    start = time.perf_counter()
    print(f"{threading.current_thread().name} started delay = {delay}")
    url = f"http://localhost:8080/delay/{delay}"
    response = requests.get(url)
    response.raise_for_status()
    print(f"{threading.current_thread().name} finished delay = {delay}, time taken = {time.perf_counter() - start:.4f} seconds")
    return response.json()["url"]

def main() -> None:
    start = time.perf_counter()
    delays = [0,1,2,3,4,5,6]
    output = []
    futures = [] 
    with ThreadPoolExecutor(max_workers=int(sys.argv[1])) as executor:
        for delay in delays:
            futures.append(executor.submit(fetch,delay))
        # It's important that this remains within the context of the ThreadPoolExecutor otherwise
        # ThreadPoolExecutor.__exit__() waits for all worker threads to finish before continuing.
        # So we still have concurrency but we lose the ability to react to results as they arrive
        # if the following loop isn't nested within the ThreadPoolExecutor context.
        for future in as_completed(futures): # Using as_completed(futures) yields futures in completion order
            try:
                output.append(future.result())
            except requests.HTTPError as e:
                print(e)
        # for future in futures:
        # output.append(future.result())
        # use if you want to preserve submission order
    print(output)
    print(f"Script finished in {time.perf_counter() - start:.4f} seconds")

if __name__ == "__main__":
    main()