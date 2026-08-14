import requests
import time
import threading

def fetch(delay: int) -> str:
    start = time.perf_counter()

    print(
        f"{threading.current_thread().name} "
        f"started delay = {delay}"
    )

    url = f"http://localhost:8080/delay/{delay}"
    response = requests.get(url)
    response.raise_for_status()
    
    print(
        f"{threading.current_thread().name} "
        f"finished delay = {delay}, "
        f"time taken = {time.perf_counter() - start:.4f} seconds"
    )

    return response.json()["url"]

def main() -> None:
    start = time.perf_counter()
    delays = [0,1,2,3,4,5,6]
    output = []

    for delay in delays:
        result = fetch(delay)
        output.append(result)

    print(output)
    total = time.perf_counter() - start
    print(f"Script total run time: {total:.4f} seconds")

if __name__ == "__main__":
    main()