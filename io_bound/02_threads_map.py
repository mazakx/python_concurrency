import requests
import time
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

def fetch(delay: int) -> str:
    start = time.perf_counter()
    print(f"{threading.current_thread().name} started delay = {delay}")
    url = f"http://localhost:8080/delay/{delay}"
    response = requests.get(url)
    response.raise_for_status()
    print(
        f"{threading.current_thread().name} finished delay = {delay}, "
        f"time taken = {time.perf_counter() - start:.4f} seconds")
    return response.json()["url"]

def main() -> None:
    start = time.perf_counter()
    delays = [0,1,2,3,4,5,6]

    # A requests.Session() could be used here to provide connection pooling and
    # reuse TCP connections across requests. However, a Session maintains mutable 
    # state (e.g. cookies and headers), and Requests does not document a single
    # Session as being thread-safe.
    #
    # If a shared Session is used, create it before the ThreadPoolExecutor and nest
    # the ThreadPoolExecutor context within the Session context. This ensures the
    # Session remains alive for the lifetime of all worker threads and is only
    # closed after they have finished making requests.
    #
    # Configure the Session (e.g. headers and authentication) before and outside 
    # the ThreadPoolExecutor context and treat it as effectively read-only while 
    # requests are in flight.

    with ThreadPoolExecutor(max_workers=int(sys.argv[1])) as executor:
        results = executor.map(fetch,delays)
        output = list(results)
    print(output)
    print(f"Script finished in {time.perf_counter() - start:.4f} seconds")

if __name__ == "__main__":
    main()