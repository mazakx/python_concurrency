import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def fetch(delay: int) -> str:
    start = time.perf_counter()
    print(f"{threading.current_thread().name} started delay = {delay}")
    url = f"https://httpbin.org/delay/{delay}"
    response = requests.get(url)
    response.raise_for_status()
    print(f"{threading.current_thread().name} finished delay = {delay}, time taken = {time.perf_counter() - start:.4f} seconds")
    return response.json()["url"]

def main() -> None:
    start = time.perf_counter()
    delays = [0,1,2,3,4,5,6]
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(fetch,delays)
        output = list(results)
    print(output)
    print(f"Script finished in {time.perf_counter() - start:.4f} seconds")

if __name__ == "__main__":
    main()